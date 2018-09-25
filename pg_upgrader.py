import argparse
import json
from threading import Thread
import time

import boto3


class RDSClient:
    rds_client = boto3.client('rds')


class RDSPostgresWaiter(RDSClient):
    """

    """

    def __init__(self, db_instance_id, pg_engine_version, sleep_time=30):
        self.engine_version = pg_engine_version
        self.instance_id = db_instance_id
        self.sleep_time = sleep_time

    def __enter__(self):
        self.rds_client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.instance_id
        )
        print("Waiting for {} to become available".format(self.instance_id))

    def __exit__(self, type, value, traceback):
        print("Upgrading {} to: {}"
              .format(self.instance_id, self.engine_version))
        time.sleep(self.sleep_time)
        self.rds_client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.instance_id
        )
        print("Successfully upgraded {} to: {}"
              .format(self.instance_id, self.engine_version))


class RDSPostgresInstance(RDSClient):
    """

    """

    def __init__(self, db_instance_id, target_version=None):
        self.target_version = target_version
        self.db_instance_id = db_instance_id
        self.db_instance_data = self.rds_client.describe_db_instances(
            DBInstanceIdentifier=self.db_instance_id
        )["DBInstances"][0]
        self.upgrade_path = self.get_engine_upgrade_path()

    @property
    def is_upgradable(self):
        """

        :return:
        """
        has_target_version = self.target_version is not None
        if has_target_version:
            return self.uses_postgres and (self.target_version in self.upgrade_path)
        return self.uses_postgres

    def get_engine_upgrade_path(self):
        """

        :return:
        """
        return self._get_upgrade_path(self.db_instance_data["EngineVersion"])

    def _get_upgrade_path(self, engine_version, major_version_upgrades=None):
        """

        :param engine_version:
        :param major_version_upgrades:
        :return:
        """
        if major_version_upgrades is None:
            major_version_upgrades = []

        db_engine_versions = self.rds_client.describe_db_engine_versions(
            Engine='postgres', EngineVersion=engine_version
        )["DBEngineVersions"]

        for db_engine_version in db_engine_versions:
            available_major_versions = [
                upgrade_target["EngineVersion"] for upgrade_target in
                db_engine_version["ValidUpgradeTarget"]
                if upgrade_target["IsMajorVersionUpgrade"]
            ]
            if self.target_version in available_major_versions:
                print(
                    "Target version: {} found in available_major_versions: {}"
                    .format(self.target_version, available_major_versions)
                )
                major_version_upgrades.append(self.target_version)
                return major_version_upgrades

            try:
                most_recent_major_version = available_major_versions[-1]
            except IndexError:
                return major_version_upgrades
            else:
                major_version_upgrades.append(most_recent_major_version)
                return self._get_upgrade_path(
                    most_recent_major_version,
                    major_version_upgrades=major_version_upgrades
                )

    def _modify_db(self):
        """

        :return:
        """
        for pg_engine_version in self.upgrade_path:
            with RDSPostgresWaiter(self.db_instance_id, pg_engine_version):
                self.rds_client.modify_db_instance(
                    DBInstanceIdentifier=self.db_instance_id,
                    EngineVersion=pg_engine_version,
                    AllowMajorVersionUpgrade=True,
                    ApplyImmediately=True
                )

    def upgrade(self):
        """

        :return:
        """
        thread = Thread(target=self._modify_db)
        thread.start()
        return thread

    @property
    def uses_postgres(self):
        """

        :return:
        """
        db_engine = self.db_instance_data["Engine"]
        uses_postgres = db_engine == "postgres"
        if not uses_postgres:
            print(
                "Excluding DB instance: {} as it does not use postgres."
                " DB Engine: '{}' was reported"
                .format(self.db_instance_id, db_engine)
            )
        return uses_postgres


class RDSPostgresUpgrader(RDSClient):
    """

    """

    def __init__(self, ids=None, tags=None, target_version=None):
        if tags is not None:
            ids = self._get_db_instance_ids_from_tags(tags)
        self.rds_instances = [
            instance for instance in [
                RDSPostgresInstance(db_instance_id,
                                    target_version=target_version)
                for db_instance_id in ids
            ] if instance.is_upgradable
        ]

    def _get_db_instance_ids_from_tags(self, tags):
        matching_instance_ids = set([])
        for db_instance in self.rds_client.describe_db_instances()[
            "DBInstances"
        ]:
            tag_list = self.rds_client.list_tags_for_resource(
                ResourceName=db_instance["DBInstanceArn"]
            )["TagList"]

            if all(tags.get(tag["Key"]) == tag["Value"] for tag in tag_list):
                matching_instance_ids.add(db_instance["DBInstanceIdentifier"])
        if not matching_instance_ids:
            print("No instances found matching tags: {}".format(tags))
        return list(matching_instance_ids)

    def upgrade_all(self):
        """

        """
        for rds_instance in self.rds_instances:
            upgrade_thread = rds_instance.upgrade()
            upgrade_thread.join()


def create_parser():
    """

    :return:
    """
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
