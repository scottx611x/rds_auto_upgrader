from unittest import mock

import boto3
from moto import mock_rds
from models import RDSPostgresInstance, RDSPostgresUpgrader, rds_client
from test_data.fixtures import describe_db_engine_versions, \
    list_tags_for_resource, test_instance_id, test_instance_name_value, \
    test_instance_name_key, test_instance_owner_key, test_instance_owner_value, \
    test_tags


@mock_rds
def make_rds_instance(db_instance_identifier=test_instance_id):
    boto3.client("rds").create_db_instance(
        AllocatedStorage=10,
        DBName=test_instance_name_value,
        DBInstanceIdentifier=db_instance_identifier,
        DBInstanceClass="db.t2.small",
        Engine="postgres",
        EngineVersion="9.3.14",
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


@mock_rds
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
def make_postgres_instance(describe_db_engine_versions_mock):
    return RDSPostgresInstance(make_rds_instance())


@mock_rds
@mock.patch.object(
    rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
def make_postgres_upgrader(describe_db_engine_versions_mock, tags=False):
    make_rds_instance()
    with mock.patch.object(rds_client, "list_tags_for_resource",
                           return_value=list_tags_for_resource):
        if not tags:
            return RDSPostgresUpgrader(ids=[test_instance_id])
        return RDSPostgresUpgrader(
            tags=test_tags
        )