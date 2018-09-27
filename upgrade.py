import argparse
import json

from models import RDSPostgresUpgrader


def create_parser():
    parser = argparse.ArgumentParser(
        description='Gather RDSPostgresUpgrader configurables.'
    )
    db_instance_id_group = parser.add_mutually_exclusive_group(required=True)
    db_instance_id_group.add_argument(
        '-ids', '--rds_db_instance_ids', type=str, nargs='+',
        help='RDS DBInstanceIdentifier(s) to target for an upgrade'
    )
    db_instance_id_group.add_argument(
        '-tags', '--rds_db_instance_tags', type=json.loads,
        help='Tags of RDS DBInstances to target for an upgrade'
    )
    parser.add_argument(
        "-v", "--targeted_major_version", type=str,
        help='Postgres major DBEngineVersion to target for the upgrade'
    )
    return parser


def main():
    args = create_parser().parse_args()
    RDSPostgresUpgrader(
        ids=args.rds_db_instance_ids,
        tags=args.rds_db_instance_tags,
        target_version=args.targeted_major_version
    ).upgrade_all()


if __name__ == '__main__':
    main()
