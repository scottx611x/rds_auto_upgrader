from unittest import mock

import boto3
from moto import mock_rds2
from models import RDSInstance, RDSUpgrader, rds_client
from test_data.fixtures import describe_postgres_db_engine_versions, \
    list_tags_for_resource, test_instance_id, test_instance_name_value, \
    test_instance_name_key, test_instance_owner_key, test_instance_owner_value, \
    test_tags, describe_mysql_db_engine_versions


@mock_rds2
def _make_rds_instance(**kwargs):
    db_instance_identifier = kwargs["db_instance_identifier"]
    db_engine = kwargs["db_engine"]
    db_engine_version = kwargs["db_engine_version"]

    boto3.client("rds").create_db_instance(
        AllocatedStorage=10,
        DBName=test_instance_name_value,
        DBInstanceIdentifier=db_instance_identifier,
        DBInstanceClass="db.t2.small",
        Engine=db_engine,
        EngineVersion=db_engine_version,
        Tags=[
            {
                'Key': test_instance_name_key,
                'Value': test_instance_name_value
            },
            {
                'Key': test_instance_owner_key,
                'Value': test_instance_owner_value
            },
        ],
    )
    return db_instance_identifier


@mock_rds2
def make_rds_instance(db_engine="postgres",
                      db_engine_version="9.3.14",
                      db_instance_identifier=test_instance_id):

    if db_engine == "postgres":
        describe_db_engine_versions_mock = mock.patch.object(
            rds_client, "describe_db_engine_versions",
            side_effect=describe_postgres_db_engine_versions
        )
    else:
        describe_db_engine_versions_mock = mock.patch.object(
            rds_client, "describe_db_engine_versions",
            side_effect=describe_mysql_db_engine_versions
        )

    with describe_db_engine_versions_mock.start():
        return RDSInstance(
            _make_rds_instance(
                db_engine=db_engine,
                db_engine_version=db_engine_version,
                db_instance_identifier=db_instance_identifier
            )
        )


@mock_rds2
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_postgres_db_engine_versions
)
def make_rds_upgrader(describe_db_engine_versions_mock, tags=False):
    _make_rds_instance(
        db_engine="postgres",
        db_engine_version="9.3.14",
        db_instance_identifier=test_instance_id
    )
    with mock.patch.object(rds_client, "list_tags_for_resource",
                           return_value=list_tags_for_resource):
        if not tags:
            return RDSUpgrader(ids=[test_instance_id])
        return RDSUpgrader(
            tags=test_tags
        )
