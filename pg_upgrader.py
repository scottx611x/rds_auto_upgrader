import argparse
import time

import boto3


class RDSPostgresUpgrader():
    client = boto3.client('rds')

    def __init__(self, db_instance_id, pg_engine_versions):
        self.db_instance_id = db_instance_id
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
        print("Upgrading {} to: {}".format(
              self.db_instance_id, pg_engine_version))
        time.sleep(30)

    def upgrade(self):
        [self._modify_db(pg_engine_version)
            for pg_engine_version in self.pg_engine_versions]


def create_parser():
    parser = argparse.ArgumentParser(
        description='Gather RDSPostgresUpgrader configurables.'
    )
    parser.add_argument(
        '-id', '--rds_db_instance_id', type=str,
        help='RDS DBInstanceIdentifier to target for an upgrade',
        required=True
    )
    parser.add_argument(
        '-v', '--pg_target_versions', type=str, nargs='+',
        help='One or more postgres engine version(s) to target for an upgrade',
        default=["9.4.18", "9.5.13", "9.6.9", "10.4"]
    )
    return parser


def main():
    args = create_parser().parse_args()
    RDSPostgresUpgrader(args.rds_db_instance_id,
                        args.pg_target_versions).upgrade()

if __name__ == '__main__':
    main()
