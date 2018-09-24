import unittest
from unittest import mock
from pg_upgrader import RDSPostgresUpgrader, create_parser


class RDSPostgresUpgraderTests(unittest.TestCase):
    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade(self, modify_db_mock):
        db_instance_ids = ["test-rds-id-a", "test-rds-id-b"]
        pg_engine_versions = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        RDSPostgresUpgrader(db_instance_ids, pg_engine_versions).upgrade()
        self.assertEqual(modify_db_mock.call_count,
                         len(pg_engine_versions) * len(db_instance_ids))

    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_after_parse(self, modify_db_mock):
        parser = create_parser()
        args = parser.parse_args(
            ['-id', 'test-rds-id', '-v', "9.4.18"]
        )
        RDSPostgresUpgrader(args.rds_db_instance_ids,
                            args.pg_target_versions).upgrade()
        self.assertEqual(modify_db_mock.call_count, 1)


if __name__ == '__main__':
    unittest.main()
