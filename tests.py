import unittest
from unittest import mock
from pg_upgrader import RDSPostgresUpgrader, create_parser
from test_fixtures.fixtures import (describe_db_instances,
                                    list_tags_for_resource,
                                    non_postgres_describe_db_instances)


class RDSPostgresUpgraderTests(unittest.TestCase):
    @mock.patch.object(
        RDSPostgresUpgrader.client, "describe_db_instances",
        return_value=describe_db_instances
    )
    @mock.patch.object(RDSPostgresUpgrader.client, "get_waiter")
    @mock.patch.object(RDSPostgresUpgrader.client, "modify_db_instance")
    @mock.patch("time.sleep")
    def test_upgrade(self, sleep_mock, modify_db_mock, get_waiter_mock,
                     describe_dbs_mock):
        db_instance_ids = ["test-rds-id-a", "test-rds-id-b"]
        pg_engine_versions = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        RDSPostgresUpgrader(pg_engine_versions, ids=db_instance_ids).upgrade()
        db_modication_count = len(pg_engine_versions) * len(db_instance_ids)
        self.assertEqual(get_waiter_mock.call_count, db_modication_count * 2)
        self.assertEqual(modify_db_mock.call_count, db_modication_count)

    @mock.patch.object(
        RDSPostgresUpgrader.client, "describe_db_instances",
        return_value=describe_db_instances
    )
    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_after_parse_ids(self, modify_db_mock, describe_dbs_mock):
        parser = create_parser()
        args = parser.parse_args(
            ['-ids', 'test-rds-id', '-versions', "9.4.18"]
        )
        RDSPostgresUpgrader(args.pg_target_versions,
                            ids=args.rds_db_instance_ids).upgrade()
        self.assertEqual(modify_db_mock.call_count, 1)

    @mock.patch.object(
        RDSPostgresUpgrader.client, "list_tags_for_resource",
        return_value=list_tags_for_resource
    )
    @mock.patch.object(
        RDSPostgresUpgrader.client, "describe_db_instances",
        return_value=describe_db_instances
    )
    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_after_parse_tags(self, modify_db_mock, describe_dbs_mock,
                                      list_tags_mock):
        parser = create_parser()
        args = parser.parse_args(
            ['-tags', '{"Name": "test-rds-name", "owner": "test@example.com"}',
             '-versions', "9.6.9 10.4"]
        )
        rds_postgres_upgrader = RDSPostgresUpgrader(
            args.pg_target_versions,
            tags=args.rds_db_instance_tags
        )
        rds_postgres_upgrader.upgrade()

        self.assertEqual(describe_dbs_mock.call_count, 2)
        self.assertEqual(list_tags_mock.call_count, 1)
        self.assertEqual(modify_db_mock.call_count, 1)
        self.assertEqual(rds_postgres_upgrader.db_instance_ids, ["rds-test"])

    @mock.patch.object(
        RDSPostgresUpgrader.client, "list_tags_for_resource",
        return_value=list_tags_for_resource
    )
    @mock.patch.object(
        RDSPostgresUpgrader.client, "describe_db_instances",
        return_value=describe_db_instances
    )
    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_nothing_upgraded_after_parsed_tags_not_matched(
        self, modify_db_mock, describe_dbs_mock, list_tags_mock
    ):
        parser = create_parser()
        args = parser.parse_args(
            ['-tags', '{"Name": "This Tag does not exist",'
                ' "owner": "test@example.com"}',
             '-versions', "9.6.9 10.4"]
        )
        RDSPostgresUpgrader(args.pg_target_versions,
                            tags=args.rds_db_instance_tags).upgrade()

        self.assertEqual(describe_dbs_mock.call_count, 1)
        self.assertEqual(list_tags_mock.call_count, 1)
        self.assertEqual(modify_db_mock.call_count, 0)

    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_nothing_upgraded_if_postgres_engine_not_found(self,
                                                           modify_db_mock):
        parser = create_parser()
        args = parser.parse_args(
            ['-ids', 'test-rds-id',
             '-versions', "9.6.9 10.4"]
        )
        with mock.patch.object(
            RDSPostgresUpgrader.client, "describe_db_instances",
            return_value=non_postgres_describe_db_instances
        ) as describe_dbs_non_postgres_mock:
            RDSPostgresUpgrader(args.pg_target_versions,
                                ids=args.rds_db_instance_ids).upgrade()

        self.assertEqual(describe_dbs_non_postgres_mock.call_count, 1)
        self.assertEqual(modify_db_mock.call_count, 0)

if __name__ == '__main__':
    unittest.main()
