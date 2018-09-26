import json
import unittest
from unittest import mock

import boto3
from moto import mock_rds

from pg_upgrader import (RDSPostgresUpgrader, create_parser, rds_client)
from test_data.fixtures import (list_tags_for_resource,
                                describe_db_engine_versions, test_instance_id,
                                test_instance_name_key,
                                test_instance_owner_key,
                                test_instance_name_value,
                                test_instance_owner_value, test_tags)
from test_data.utils import make_postgres_instance


@mock_rds
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
class RDSPostgresInstanceTests(unittest.TestCase):
    def setUp(self):
        self.postgres_instance = make_postgres_instance()

    def test_repr(self, describe_db_engine_versions_mock):
        self.assertEqual(
            str(self.postgres_instance),
            "RDSPostgresInstance id: test-rds-id status: available "
            "engine_version: 9.3.14"
        )

    def test_upgrade_path(self, describe_db_engine_versions_mock):
        self.assertEqual(self.postgres_instance.upgrade_path,
                         ['9.4.18', '9.5.13', '9.6.9', '10.4'])


@mock_rds
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
@mock.patch("time.sleep")
class RDSPostgresUpgraderTests(unittest.TestCase):
    def setUp(self):
        self.rds_client = boto3.client("rds")
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBName=test_instance_name_value,
            DBInstanceIdentifier=test_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="postgres",
            EngineVersion="9.3.14",
            Tags=[
                {
                    'Key': test_instance_name_key,
                    'Value': test_instance_name_value
                },
                {
                    'Key': test_instance_owner_key,
                    'Value': test_instance_owner_value
                },
            ],
        )

    def tearDown(self):
        self.rds_client.delete_db_instance(
            DBInstanceIdentifier=test_instance_id
        )

    def test_upgrade_many(self, sleep_mock, describe_db_engine_versions_mock):
        describe_db_engine_versions_mock.side_effect = (
                describe_db_engine_versions * 2
        )
        another_instance_id = "another_instance_id"
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBInstanceIdentifier=another_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="postgres",
            EngineVersion="9.3.14"
        )
        instance_ids_to_upgrade = [test_instance_id, another_instance_id]
        rds_postgres_upgrader = RDSPostgresUpgrader(
            ids=instance_ids_to_upgrade
        )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(
            describe_db_engine_versions_mock.call_count,
            len(describe_db_engine_versions) * len(instance_ids_to_upgrade)
        )
        for rds_instance in rds_postgres_upgrader.rds_instances:
            self.assertEqual(
                self.rds_client.describe_db_instances(
                    DBInstanceIdentifier=rds_instance.db_instance_id
                )["DBInstances"][0]["EngineVersion"],
                "10.4"
            )

    def test_upgrade_after_parse_ids(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        parser = create_parser()
        args = parser.parse_args(['-ids', test_instance_id])
        rds_postgres_upgrader = RDSPostgresUpgrader(
            ids=args.rds_db_instance_ids
        )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "10.4"
        )

    def test_upgrade_after_parse_tags(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        parser = create_parser()
        args = parser.parse_args(['-tags', json.dumps(test_tags)])
        with mock.patch.object(rds_client, "list_tags_for_resource",
                               return_value=list_tags_for_resource):
            rds_postgres_upgrader = RDSPostgresUpgrader(
                tags=args.rds_db_instance_tags
            )
            rds_postgres_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "10.4"
        )

    def test_upgrade_to_user_specified_target_version(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        target_version = "9.5.13"
        rds_postgres_upgrader = RDSPostgresUpgrader(
            ids=[test_instance_id],
            target_version=target_version
        )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            target_version
        )

    def test_upgrade_to_user_specified_target_version_version_not_found(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        target_version = "96.9"
        rds_postgres_upgrader = RDSPostgresUpgrader(
            ids=[test_instance_id],
            target_version=target_version
        )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(len(rds_postgres_upgrader.rds_instances), 0)

    def test_nothing_upgraded_after_parsed_tags_not_matched(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        parser = create_parser()
        args = parser.parse_args(
            ['-tags',
             '{"Name": "Bad Tag Value", "owner": "test@example.com"}']
        )
        with mock.patch.object(rds_client, "list_tags_for_resource",
                               return_value=list_tags_for_resource):
            rds_postgres_upgrader = RDSPostgresUpgrader(
                tags=args.rds_db_instance_tags
            )
            rds_postgres_upgrader.upgrade_all()
        self.assertEqual(len(rds_postgres_upgrader.rds_instances), 0)

    def test_nothing_upgraded_if_postgres_engine_not_found(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        mysql_instance_id = "test-mysql"
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBInstanceIdentifier=mysql_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="mysql"
        )
        parser = create_parser()
        args = parser.parse_args(['-ids', mysql_instance_id])
        rds_postgres_upgrader = RDSPostgresUpgrader(
            ids=args.rds_db_instance_ids
        )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(len(rds_postgres_upgrader.rds_instances), 0)
        self.rds_client.delete_db_instance(
            DBInstanceIdentifier=mysql_instance_id
        )


if __name__ == '__main__':
    unittest.main()
