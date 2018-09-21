import argparse
import sys
import time

import boto3
import paramiko


class RDSPostgresUpgrader():
    rds_client = boto3.client('rds')

    def __init__(self, refinery_ec2_ip, db_instance_id, pg_engine_versions):
        self.db_instance_id = db_instance_id
        self.pg_engine_versions = pg_engine_versions
        self.refinery_ec2_ip = refinery_ec2_ip

    def _check_for_unsupported_usage(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.refinery_ec2_ip, username="ubuntu",
                           password=input("PrivateKey Password: "))
        with open("unsupported_usage_checks.txt") as f:
            for command in f.readlines():
                stdin, stdout, stderr = ssh_client.exec_command(command)
                rows_found = int(str(stdout.read()).split("\\n")[2])
                if rows_found != 0:
                    sys.exit(
                        "Pre-check failed.\n Command {} yielded {} row(s)"
                        .format(command, rows_found)
                    )

    def _modify_db(self, pg_engine_version):
        print("Waiting for {} to become available".format(self.db_instance_id))
        self.rds_client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.db_instance_id
        )
        self.rds_client.modify_db_instance(
            DBInstanceIdentifier=self.db_instance_id,
            EngineVersion=pg_engine_version,
            AllowMajorVersionUpgrade=True,
            ApplyImmediately=True
        )
        print("Upgrading {} to: {}".format(
              self.db_instance_id, pg_engine_version))
        time.sleep(30)

    def upgrade(self):
        for pg_engine_version in self.pg_engine_versions:
            self._check_for_unsupported_usage()
            self._modify_db(pg_engine_version)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Gather RDSPostgresUpgrader configurables.'
    )
    parser.add_argument(
        '-ip', '--refinery_ec2_ip', type=str,
        help=(
            "IP of Refinery EC2 to run Postgres upgrade "
            "compatibility queries on. Refinery's RDSInstances reside in "
            "private subnets and can't be queried directly"
        ),
        required=True
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
    RDSPostgresUpgrader(args.refinery_ec2_ip, args.rds_db_instance_id,
                        args.pg_target_versions).upgrade()

if __name__ == '__main__':
    main()
