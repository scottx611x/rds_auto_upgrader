import unittest
from unittest import mock
from postgres_upgrade import RDSPostgresUpgrader


@mock.patch("time.sleep")
class RDSPostgresUpgraderTests(unittest.TestCase):
    def setUp(self):
        self.pg_engine_versions = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
        self.db_instance_statuses = [
            "backing_up", "available", "upgrading", "modifying", "available"
        ] * len(self.pg_engine_versions)
        self.rds_pg_upgrader = RDSPostgresUpgrader(
            "test-rds-id",
            self.pg_engine_versions
        )

    def test_wait_for_db_status_desired(self, sleep_mock):
        with mock.patch(
            "postgres_upgrade.RDSPostgresUpgrader.get_db_status",
            return_value="available"
        ):
            self.rds_pg_upgrader.wait_for_db_status("available")

    def test_wait_for_db_status_undesired(self, sleep_mock):
        with mock.patch(
            "postgres_upgrade.RDSPostgresUpgrader.get_db_status",
            return_value="upgrading"
        ):
            self.rds_pg_upgrader.wait_for_db_status(
                "available", is_undesired_status=True
            )

    @mock.patch.object(RDSPostgresUpgrader, "_modify_db")
    def test_upgrade(self, sleep_mock, modify_db_mock):
        with mock.patch(
            "postgres_upgrade.RDSPostgresUpgrader.get_db_status",
            side_effect=self.db_instance_statuses
        ):
            self.rds_pg_upgrader.upgrade()
        self.assertEqual(modify_db_mock.call_count,
                         len(self.pg_engine_versions) + 1)

if __name__ == '__main__':
    unittest.main()
