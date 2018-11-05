import argparse
import json

from models import RDSUpgrader


def create_parser():
    parser = argparse.ArgumentParser(description="Gather RDSUpgrader configurables.")
    db_instance_id_group = parser.add_mutually_exclusive_group(required=True)
    db_instance_id_group.add_argument(
        "-ids",
        "--rds_db_instance_ids",
        type=str,
        nargs="+",
        help="RDS DBInstanceIdentifier(s) to target for an upgrade",
    )
    db_instance_id_group.add_argument(
        "-tags",
        "--rds_db_instance_tags",
        type=json.loads,
        help="Tags of RDS DBInstances to target for an upgrade",
    )
    parser.add_argument(
        "-v",
        "--targeted_major_version",
        type=str,
        help="Major DBEngineVersion to target for the upgrade",
    )
    parser.add_argument(
        "-dry",
        "--dry_run",
        action='store_true',
        help="Report the upgrade paths to be taken for each given DB Instance Id and exit",
    )
    return parser


def main():
    args = create_parser().parse_args()
    rds_upgrader = RDSUpgrader(
        ids=args.rds_db_instance_ids,
        tags=args.rds_db_instance_tags,
        target_version=args.targeted_major_version,
    )

    if not args.dry_run:
        rds_upgrader.upgrade_all()
    else:
        print(rds_upgrader.get_dry_run_info())


if __name__ == "__main__":
    main()
