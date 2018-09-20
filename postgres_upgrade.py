import sys
import time

import boto3


class RDSPostgresUpgrader():
    client = boto3.client('rds')

    def __init__(self, db_instance_id, pg_engine_versions):
        self.db_instance_id = db_instance_id
        self.pg_engine_versions = pg_engine_versions

    def get_db_status(self):
        return self.client.describe_db_instances(
            DBInstanceIdentifier=self.db_instance_id
        )["DBInstances"][0]["DBInstanceStatus"]

    def wait_for_db_status(self, status, message, wait_time=60,
                           is_undesired_status=False):
        db_instance_status = self.get_db_status()
        print("{} DBInstanceStatus: {}".format(self.db_instance_id,
                                               db_instance_status))
        while db_instance_status != status and is_undesired_status:
            print(message)
            time.sleep(wait_time)

    def _modify_db(self, pg_engine_version):
        self.client.modify_db_instance(
            DBInstanceIdentifier=self.db_instance_id,
            EngineVersion=pg_engine_version,
            AllowMajorVersionUpgrade=True,
            ApplyImmediately=True
        )

    def upgrade(self):
        for pg_engine_version in self.pg_engine_versions:
            print("Upgrading {} to: {}"
                  .format(self.db_instance_id, pg_engine_version))

            self.wait_for_db_status(
                "available",
                "Waiting a minute for {} to become available"
                .format(self.db_instance_id)
            )

            self._modify_db(pg_engine_version)

            self.wait_for_db_status(
                "available",
                "Waiting for upgrade of {} to: {} to initiate"
                .format(self.db_instance_id, pg_engine_version),
                wait_time=30,
                is_undesired_status=True
            )
            self.wait_for_db_status(
                "upgrading",
                "Still upgrading {} to: {}"
                .format(self.db_instance_id, pg_engine_version),
                is_undesired_status=True
            )
            print("Upgrade to {} complete!".format(pg_engine_version))

if __name__ == '__main__':
    TARGETED_PG_ENGINE_VERSIONS = ["9.4.18", "9.5.13", "9.6.9", "10.4"]

    rds_db_instance_identifier = sys.argv[1]

    RDSPostgresUpgrader(
        rds_db_instance_identifier,
        TARGETED_PG_ENGINE_VERSIONS
    ).upgrade()
