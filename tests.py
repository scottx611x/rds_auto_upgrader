import doctest
import json
import unittest
from unittest import mock

import boto3
from moto import mock_rds2

from models import RDSUpgrader, rds_client
from test_data.fixtures import (
    list_tags_for_resource,
    describe_postgres_db_engine_versions,
    test_instance_id,
    test_instance_name_key,
    test_instance_owner_key,
    test_instance_name_value,
    test_instance_owner_value,
    test_tags,
    describe_db_instances,
)
from test_data.utils import make_rds_instance
from upgrade import create_parser


@mock_rds2
class RDSInstanceTests(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(
            str(make_rds_instance()),
            "RDSInstance id: test-rds-id, status: available, "
            "engine: postgres, engine_version: 9.3.14",
        )

    def test_upgrade_path_postgres(self):
        self.assertEqual(
            make_rds_instance().upgrade_path, ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        )

    def test_upgrade_path_mysql(self):
        rds_instance = make_rds_instance(db_engine="mysql", db_engine_version="5.5.46")
        self.assertEqual(rds_instance.upgrade_path, ["5.6.40", "5.7.22"])


@mock_rds2
@mock.patch.object(
    rds_client,
    "describe_db_engine_versions",
    side_effect=describe_postgres_db_engine_versions,
)
@mock.patch("time.sleep")
class RDSUpgraderTests(unittest.TestCase):
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
                {"Key": test_instance_name_key, "Value": test_instance_name_value},
                {"Key": test_instance_owner_key, "Value": test_instance_owner_value},
            ],
        )

    def tearDown(self):
        self.rds_client.delete_db_instance(DBInstanceIdentifier=test_instance_id)

    def test_upgrade_many(self, sleep_mock, describe_db_engine_versions_mock):
        describe_db_engine_versions_mock.side_effect = (
            describe_postgres_db_engine_versions * 2
        )
        another_instance_id = "another_instance_id"
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBInstanceIdentifier=another_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="postgres",
            EngineVersion="9.3.14",
        )
        instance_ids_to_upgrade = [test_instance_id, another_instance_id]
        rds_upgrader = RDSUpgrader(ids=instance_ids_to_upgrade)
        rds_upgrader.upgrade_all()
        self.assertEqual(
            describe_db_engine_versions_mock.call_count,
            len(describe_postgres_db_engine_versions) * len(instance_ids_to_upgrade),
        )
        for rds_instance in rds_upgrader.rds_instances:
            self.assertEqual(rds_instance.engine_version, "10.4")

    def test_upgrade_after_parse_ids(self, *args):
        parser = create_parser()
        args = parser.parse_args(["-ids", test_instance_id])
        rds_upgrader = RDSUpgrader(ids=args.rds_db_instance_ids)
        rds_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "10.4",
        )

    def test_upgrade_after_parse_tags(self, *args):
        parser = create_parser()
        args = parser.parse_args(["-tags", json.dumps(test_tags)])
        with mock.patch.object(
            rds_client, "list_tags_for_resource", return_value=list_tags_for_resource
        ):
            rds_upgrader = RDSUpgrader(tags=args.rds_db_instance_tags)
            rds_upgrader.upgrade_all()
        for rds_instance in rds_upgrader.rds_instances:
            self.assertEqual(rds_instance.engine_version, "10.4")

    def test_upgrade_to_user_specified_target_version(self, *args):
        target_version = "9.5.13"
        rds_upgrader = RDSUpgrader(
            ids=[test_instance_id], target_version=target_version
        )
        rds_upgrader.upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            target_version,
        )

    def test_upgrade_to_user_specified_target_version_version_not_found(self, *args):
        target_version = "96.9"
        rds_upgrader = RDSUpgrader(
            ids=[test_instance_id], target_version=target_version
        )
        rds_upgrader.upgrade_all()
        self.assertEqual(len(rds_upgrader.rds_instances), 0)

    def test_nothing_upgraded_after_parsed_tags_not_matched(self, *args):
        parser = create_parser()
        args = parser.parse_args(
            ["-tags", '{"Name": "Bad Tag Value", "owner": "test@example.com"}']
        )
        with mock.patch.object(
            rds_client, "list_tags_for_resource", return_value=list_tags_for_resource
        ):
            rds_upgrader = RDSUpgrader(tags=args.rds_db_instance_tags)
            rds_upgrader.upgrade_all()
        self.assertEqual(len(rds_upgrader.rds_instances), 0)

    def test_upgrade_handles_varying_db_instance_statuses(self, *args):
        with mock.patch.object(
            rds_client,
            "describe_db_instances",
            side_effect=[
                describe_db_instances(status=status)
                for status in [
                    "upgrading",
                    "upgrading",
                    "upgrading",
                    "modifying",
                    "backing-up",
                    "available",
                    "available",
                ]
            ],
        ):
            rds_upgrader = RDSUpgrader(ids=[test_instance_id], target_version="9.4.18")
            rds_upgrader.upgrade_all()
        for rds_instance in rds_upgrader.rds_instances:
            self.assertEqual(rds_instance.engine_version, "9.4.18")

    def test_nothing_upgraded_if_supported_engine_not_found(self, *args):
        new_instance_id = "test-instance-new"
        self.rds_client.create_db_instance(
            AllocatedStorage=10,
            DBInstanceIdentifier=new_instance_id,
            DBInstanceClass="db.t2.small",
            Engine="mariadb",
        )
        parser = create_parser()
        args = parser.parse_args(["-ids", new_instance_id])
        rds_upgrader = RDSUpgrader(ids=args.rds_db_instance_ids)
        rds_upgrader.upgrade_all()
        self.assertEqual(len(rds_upgrader.rds_instances), 0)
        self.rds_client.delete_db_instance(DBInstanceIdentifier=new_instance_id)

    def test_nothing_upgraded_if_rds_instance_never_available(self, *args):
        self.rds_client.stop_db_instance(DBInstanceIdentifier=test_instance_id)
        RDSUpgrader(ids=[test_instance_id], target_version="9.4.18").upgrade_all()
        self.assertEqual(
            self.rds_client.describe_db_instances(
                DBInstanceIdentifier=test_instance_id
            )["DBInstances"][0]["EngineVersion"],
            "9.3.14",
        )

    def test_get_dry_run_info(self, *args):
        rds_upgrader = RDSUpgrader(ids=[test_instance_id])
        self.assertEqual(
            rds_upgrader.get_dry_run_info(),
            "RDSInstance: {} will be upgraded as follows: 9.4.18 -> 9.5.13 -> 9.6.9 -> 10.4\n"
            .format(test_instance_id)
        )


class DocTests(unittest.TestCase):
    def test_models(self):
        import models

        assert doctest.testmod(models, verbose=True, raise_on_error=True)

    def test_utils(self):
        import utils

        assert doctest.testmod(utils, verbose=True, raise_on_error=True)


if __name__ == "__main__":
    unittest.main()
