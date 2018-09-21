import unittest
from unittest import mock
from pg_upgrader import RDSPostgresUpgrader


class RDSPostgresUpgraderTests(unittest.TestCase):
    def setUp(self):
        self.pg_engine_versions = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        self.rds_pg_upgrader = RDSPostgresUpgrader(
            "test-rds-id",
            self.pg_engine_versions
        )

    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_many_versions(self, modify_db_mock):
        self.rds_pg_upgrader.upgrade()
        self.assertEqual(modify_db_mock.call_count,
                         len(self.pg_engine_versions))

    @mock.patch("pg_upgrader.RDSPostgresUpgrader._modify_db")
    def test_upgrade_single_version(self, modify_db_mock):
        RDSPostgresUpgrader("test-rds-id", "9.4.18").upgrade()
        self.assertEqual(modify_db_mock.call_count, 1)

if __name__ == '__main__':
    unittest.main()
