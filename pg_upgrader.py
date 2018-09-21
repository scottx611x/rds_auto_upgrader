import os
import sys
import time
import boto3


class RDSPostgresUpgrader():
    client = boto3.client('rds')

    def __init__(self, db_instance_id, pg_engine_versions):
        self.db_instance_id = db_instance_id
        if type(pg_engine_versions) in [str, float]:
            pg_engine_versions = [str(pg_engine_versions)]
        self.pg_engine_versions = pg_engine_versions

    def _modify_db(self, pg_engine_version):
        print("Waiting for {} to become available".format(self.db_instance_id))
        self.client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.db_instance_id
        )
        self.client.modify_db_instance(
            DBInstanceIdentifier=self.db_instance_id,
            EngineVersion=pg_engine_version,
            AllowMajorVersionUpgrade=True,
            ApplyImmediately=True
        )
        time.sleep(30)

    def upgrade(self):
        for pg_engine_version in self.pg_engine_versions:
            print("Upgrading {} to: {}"
                  .format(self.db_instance_id, pg_engine_version))
            self._modify_db(pg_engine_version)
            print("Upgrade to {} complete!".format(pg_engine_version))

if __name__ == '__main__':
    # TARGETED_PG_ENGINE_VERSIONS = ["9.4.18", "9.5.13", "9.6.9", "10.4"]
    TARGETED_PG_ENGINE_VERSIONS = ["9.5.13", "9.6.9", "10.4"]

    try:
        rds_db_instance_identifier = sys.argv[1]
    except IndexError:
        rds_db_instance_identifier = os.environ.get("RDS_DB_INSTANCE_ID")

    RDSPostgresUpgrader(rds_db_instance_identifier,
                        TARGETED_PG_ENGINE_VERSIONS).upgrade()
