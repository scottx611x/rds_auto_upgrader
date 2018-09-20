import unittest
from unittest import mock
from postgres_upgrade import RDSPostgresUpgrader


class RDSPostgresUpgraderTests(unittest.TestCase):
    def setUp(self):
        self.rds_pg_upgrader = RDSPostgresUpgrader(
            "test-rds-id",
            ["test-targeted-upgrade-version"]
        )

    @mock.patch.object(RDSPostgresUpgrader, "_modify_db")
    @mock.patch("time.sleep")
    def test_upgrade(self, sleep_mock, modify_db_mock):
        with mock.patch(
            "postgres_upgrade.RDSPostgresUpgrader.get_db_status",
            side_effect=["backing_up", "available", "upgrading",
                         "modifying", "available"]
        ) as modify_db_mock:
            self.rds_pg_upgrader.upgrade()
        self.assertTrue(modify_db_mock.called)

if __name__ == '__main__':
    unittest.main()
