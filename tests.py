import json
import unittest
from unittest import mock

import boto3
from moto import mock_rds

from pg_upgrader import (RDSPostgresInstance, RDSPostgresUpgrader,
                         create_parser, rds_client)
from test_fixtures.fixtures import (list_tags_for_resource,
                                    describe_db_engine_versions,
                                    test_instance_name_value,
                                    test_instance_owner_value,
                                    test_instance_name_key,
                                    test_instance_owner_key)


@mock_rds
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
@mock.patch("time.sleep")
class RDSPostgresUpgraderTests(unittest.TestCase):
    def setUp(self):
        self.rds_client = boto3.client("rds")
        self.test_instance_name_value = test_instance_name_value
        self.test_instance_owner_value = test_instance_owner_value
        self.test_instance_id = "test-rds-id"
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBName=self.test_instance_name_value,
            DBInstanceIdentifier=self.test_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="postgres",
            EngineVersion="9.3.14",
            Tags=[
                {
                    'Key': test_instance_name_key,
                    'Value': self.test_instance_name_value
                },
                {
                    'Key': test_instance_owner_key,
                    'Value': self.test_instance_owner_value
                },
            ],
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
        instance_ids_to_upgrade = [self.test_instance_id, another_instance_id]
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
        args = parser.parse_args(['-ids', self.test_instance_id])
        RDSPostgresUpgrader(ids=args.rds_db_instance_ids).upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "10.4"
        )

    def test_upgrade_after_parse_tags(
            self, sleep_mock, describe_db_engine_versions_mock
    ):
        parser = create_parser()
        args = parser.parse_args(
            ['-tags',
             json.dumps(
                 {
                     d['Key']: d['Value']
                     for d in list_tags_for_resource['TagList']
                 }
             )
            ]
        )
        with mock.patch.object(rds_client, "list_tags_for_resource",
                               return_value=list_tags_for_resource):
            rds_postgres_upgrader = RDSPostgresUpgrader(
                tags=args.rds_db_instance_tags
            )
        rds_postgres_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "10.4"
        )

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


if __name__ == '__main__':
    unittest.main()
