import boto3

from utils import ExceptionCatchingThread, RDSPostgresWaiter

rds_client = boto3.client('rds')


class RDSPostgresInstance:
    """Representation of a single RDS Instance to be upgraded"""

    def __init__(self, db_instance_id, target_version=None):
        self.target_version = target_version
        self.db_instance_id = db_instance_id
        self.db_instance_data = self._get_db_instance_data()
        self.engine_version = self.db_instance_data["EngineVersion"]
        self.upgrade_path = self.get_engine_upgrade_path()

    def __repr__(self):
        return ("RDSPostgresInstance id: {} status: {} engine_version: {}"
                .format(self.db_instance_id, self.db_instance_status,
                        self.engine_version, self.target_version,
                        self.upgrade_path))

    def _get_db_instance_data(self):
        return rds_client.describe_db_instances(
            DBInstanceIdentifier=self.db_instance_id
        )["DBInstances"][0]

    @property
    def db_instance_status(self):
        return self._get_db_instance_data()["DBInstanceStatus"]

    @property
    def is_upgradable(self):
        """
        Run through checks to determine if we are able to perform the engine
        version upgrade on a given instance
        :return: bool

        >>> from test_data.utils import make_postgres_instance
        >>> rds_postgres_instance = make_postgres_instance()
        >>> rds_postgres_instance.is_upgradable
        True
        """
        if self.target_version is not None:
            return self.uses_postgres and (
                self.target_version in self.upgrade_path
            )
        return self.uses_postgres

    def get_engine_upgrade_path(self):
        """
        Gather the proper "upgrade path" based on the current Postgres engine
        version associated with the given RDS Instance.

        For PostgreSQL major version upgrades one has to go from:
         9.3.x -> 9.4.x -> 9.5.x -> 9.6.x -> 10.x

        See: https://amzn.to/2IdKOel

        :return: list of compatible major engine versions to upgrade to

        >>> from test_data.utils import make_postgres_instance
        >>> rds_postgres_instance = make_postgres_instance()
        >>> rds_postgres_instance.upgrade_path
        ['9.4.18', '9.5.13', '9.6.9', '10.4']
        """
        return self._get_upgrade_path(self.engine_version)

    def _get_upgrade_path(self, engine_version, major_version_upgrades=None):
        """
        Traverse AWS API recursively to figure out the valid major version
        upgrade targets from a given Postgres engine version.
        :param engine_version: str
        :param major_version_upgrades: placeholder for recursive calls
        :return: list of compatible major engine versions to upgrade to
        """
        if major_version_upgrades is None:
            major_version_upgrades = []

        db_engine_versions = rds_client.describe_db_engine_versions(
            Engine='postgres', EngineVersion=engine_version
        )["DBEngineVersions"]

        for db_engine_version in db_engine_versions:
            available_major_versions = [
                upgrade_target["EngineVersion"] for upgrade_target in
                db_engine_version["ValidUpgradeTarget"]
                if upgrade_target["IsMajorVersionUpgrade"]
            ]
            if self.target_version in available_major_versions:
                print("Target version: {} found in "
                      "available_major_versions: {}".format(
                       self.target_version, available_major_versions))
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
                )  # recursive call

    def _modify_db(self):
        """
        Perform a major version upgrade (modify_db_instance) for each available
         major postgres engine version in our self.upgrade_path.

        Note: The RDSPostgresWaiter is crucial in this method as it will
        ensure that the corresponding AWS RDS Instances are in a state of
        availability before attempting to modify them.
        """
        for pg_engine_version in self.upgrade_path:
            with RDSPostgresWaiter(rds_client, self.db_instance_id,
                                   pg_engine_version):
                rds_client.modify_db_instance(
                    DBInstanceIdentifier=self.db_instance_id,
                    EngineVersion=pg_engine_version,
                    AllowMajorVersionUpgrade=True,
                    ApplyImmediately=True
                )

    def upgrade(self):
        """
        Run the _modify_db method within a Thread.
        :return: the Thread instance running the _modify_db()
        """
        thread = ExceptionCatchingThread(target=self._modify_db)
        thread.start()
        return thread

    @property
    def uses_postgres(self):
        """
        Check that the engine of the RDS Instnace we're to upgrade is indeed
        a Postgres one.
        :return: bool

        >>> from test_data.utils import make_postgres_instance
        >>> rds_postgres_instance = make_postgres_instance()
        >>> rds_postgres_instance.uses_postgres
        True
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


class RDSPostgresUpgrader:
    """
    Applys major Postgres engine version upgrades to all user-specified
    RDS Instances matching the upgradeable criteria
    (RDSPostgresInstance.is_upgradable)
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
        """
        Fetch RDS DBInstanceIdentifiers matching the user-specified tags
        :param tags: dict containing AWS tags that are to be used to gather
        a list of DBInstanceIdentifiers to be upgraded
        :return: list of DBInstanceIdentifiers

        >>> from test_data.utils import make_postgres_upgrader
        >>> postgres_upgrader = make_postgres_upgrader(tags=True)
        >>> # _get_db_instance_ids_from_tags is run
        >>> [rds_instance.db_instance_id
        ...    for rds_instance in postgres_upgrader.rds_instances]
        ['test-rds-id']
        """
        matching_instance_ids = set([])
        for db_instance in rds_client.describe_db_instances()[
            "DBInstances"
        ]:
            tag_list = rds_client.list_tags_for_resource(
                ResourceName=db_instance["DBInstanceArn"]
            )["TagList"]

            if all(tags.get(tag["Key"]) == tag["Value"] for tag in tag_list):
                matching_instance_ids.add(db_instance["DBInstanceIdentifier"])
        if not matching_instance_ids:
            print("No instances found matching tags: {}".format(tags))
        return list(matching_instance_ids)

    def upgrade_all(self):
        for rds_instance in self.rds_instances:
            upgrade_thread = rds_instance.upgrade()
            upgrade_thread.join()
