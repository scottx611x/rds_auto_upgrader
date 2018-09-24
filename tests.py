import unittest
from unittest import mock
from pg_upgrader import RDSPostgresUpgrader, create_parser
from test_fixtures.fixtures import (describe_db_instances,
                                    list_tags_for_resource)


class RDSPostgresUpgraderTests(unittest.TestCase):
    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade(self, modify_db_mock):
        db_instance_ids = ["test-rds-id-a", "test-rds-id-b"]
        pg_engine_versions = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        RDSPostgresUpgrader(pg_engine_versions, ids=db_instance_ids).upgrade()
        self.assertEqual(modify_db_mock.call_count,
                         len(pg_engine_versions) * len(db_instance_ids))

    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_after_parse_ids(self, modify_db_mock):
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

        self.assertEqual(describe_dbs_mock.call_count, 1)
        self.assertEqual(list_tags_mock.call_count, 1)
        self.assertEqual(modify_db_mock.call_count, 1)
        self.assertEqual(rds_postgres_upgrader.db_instance_ids, ["rds-test"])

if __name__ == '__main__':
    unittest.main()
