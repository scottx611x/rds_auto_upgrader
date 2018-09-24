import argparse
import json
from threading import Thread
import time

import boto3

rds_client = boto3.client('rds')


class RDSPostgresWaiter():
    """ """
    def __init__(self, db_instance_id, pg_engine_version, sleep_time=30):
        self.engine_version = pg_engine_version
        self.instance_id = db_instance_id
        self.sleep_time = sleep_time

    def __enter__(self):
        rds_client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.instance_id
        )
        print("Waiting for {} to become available".format(self.instance_id))

    def __exit__(self, type, value, traceback):
        print("Upgrading {} to: {}"
              .format(self.instance_id, self.engine_version))
        time.sleep(self.sleep_time)
        rds_client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.instance_id
        )
        print("Successfully upgraded {} to: {}"
              .format(self.instance_id, self.engine_version))


class RDSPostgresInstance():
    """ """
    def __init__(self, db_instance_id):
        self.db_instance_id = db_instance_id
        self.db_instance_data = rds_client.describe_db_instances(
            DBInstanceIdentifier=self.db_instance_id
        )["DBInstances"][0]

    def get_engine_upgrade_path(self):
        """ """
        return self._get_upgrade_path(self.db_instance_data["EngineVersion"])

    def _get_upgrade_path(self, engine_version, major_version_upgrades=None):
        """ """
        if major_version_upgrades is None:
            major_version_upgrades = []

        db_engine_versions = rds_client.describe_db_engine_versions(
            Engine='postgres', EngineVersion=engine_version
        )["DBEngineVersions"]

        for db_engine_version in db_engine_versions:
            available_major_versions = [
                valid_upgrade_target["EngineVersion"]
                for valid_upgrade_target in
                db_engine_version["ValidUpgradeTarget"]
                if valid_upgrade_target["IsMajorVersionUpgrade"]
            ]
            try:
                newest_major_version = available_major_versions[-1]
                major_version_upgrades.append(newest_major_version)
            except IndexError:
                return major_version_upgrades
            else:
                # recursive call
                return self._get_upgrade_path(
                    newest_major_version, upgrade_path=major_version_upgrades
                )

    def _modify_db(self):
        """ """
        for pg_engine_version in self.get_engine_upgrade_path():
            with RDSPostgresWaiter(self.db_instance_id, pg_engine_version):
                rds_client.modify_db_instance(
                    DBInstanceIdentifier=self.db_instance_id,
                    EngineVersion=pg_engine_version,
                    AllowMajorVersionUpgrade=True,
                    ApplyImmediately=True
                )

    def upgrade(self):
        """ """
        thread = Thread(target=self._modify_db)
        thread.start()
        return thread

    @property
    def uses_postgres(self):
        """ """
        db_engine = self.db_instance_data["Engine"]
        uses_postgres = db_engine == "postgres"
        if not uses_postgres:
            print(
                "Excluding DB instance: {} as it does not use postgres."
                " DB Engine: '{}' was reported"
                .format(self.db_instance_id, db_engine)
            )
        return uses_postgres


class RDSPostgresUpgrader():
    """ """
    def __init__(self, ids=None, tags=None):
        if tags is not None:
            ids = self._get_db_instance_ids_from_tags(tags)
        rds_instances = [
            RDSPostgresInstance(db_instance_id) for db_instance_id in ids
        ]
        self.rds_instances = [
            instance for instance in rds_instances if instance.uses_postgres
        ]

    def _get_db_instance_ids_from_tags(self, tags):
        """ """
        matching_instance_ids = set([])
        for db_instance in rds_client.describe_db_instances()["DBInstances"]:
            tag_list = rds_client.list_tags_for_resource(
                ResourceName=db_instance["DBInstanceArn"]
            )["TagList"]

            if all(tags.get(tag["Key"]) == tag["Value"] for tag in tag_list):
                matching_instance_ids.add(db_instance["DBInstanceIdentifier"])
        if not matching_instance_ids:
            print("No instances found matching tags: {}".format(tags))
        return list(matching_instance_ids)

    def upgrade_all(self):
        """ """
        for rds_instance in self.rds_instances:
            upgrade_thread = rds_instance.upgrade()
            upgrade_thread.join()


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
    return parser


def main():
    args = create_parser().parse_args()
    RDSPostgresUpgrader(ids=args.rds_db_instance_ids,
                        tags=args.rds_db_instance_tags).upgrade_all()

if __name__ == '__main__':
    main()
