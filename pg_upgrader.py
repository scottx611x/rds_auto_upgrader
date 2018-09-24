import argparse
import time

import boto3


class RDSPostgresUpgrader():
    client = boto3.client('rds')

    def __init__(self, db_instance_ids, pg_engine_versions):
        self.db_instance_ids = db_instance_ids
        self.pg_engine_versions = pg_engine_versions

    def _modify_db(self, db_instance_id, pg_engine_version):
        print("Waiting for {} to become available".format(db_instance_id))
        self.client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=db_instance_id
        )
        self.client.modify_db_instance(
            DBInstanceIdentifier=db_instance_id,
            EngineVersion=pg_engine_version,
            AllowMajorVersionUpgrade=True,
            ApplyImmediately=True
        )
        print("Upgrading {} to: {}".format(db_instance_id, pg_engine_version))
        time.sleep(30)

    def upgrade(self):
        for db_instance_id in self.db_instance_ids:
            for pg_engine_version in self.pg_engine_versions:
                self._modify_db(db_instance_id, pg_engine_version)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Gather RDSPostgresUpgrader configurables.'
    )
    parser.add_argument(
        '-id', '--rds_db_instance_ids', type=str, nargs='+',
        help='RDS DBInstanceIdentifier(s) to target for an upgrade',
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
    RDSPostgresUpgrader(args.rds_db_instance_ids,
                        args.pg_target_versions).upgrade()

if __name__ == '__main__':
    main()
