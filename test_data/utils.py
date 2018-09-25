from unittest import mock

import boto3
from moto import mock_rds
from pg_upgrader import RDSPostgresInstance, RDSClient
from test_data.fixtures import describe_db_engine_versions


@mock_rds
@mock.patch.object(
    RDSClient.rds_client, "describe_db_engine_versions",
    side_effect=describe_db_engine_versions
)
def make_postgres_instance(describe_db_engine_versions_mock,
                           instance_id="test_id"):
    boto3.client("rds").create_db_instance(
        AllocatedStorage=10,
        DBName="test",
        DBInstanceIdentifier=instance_id,
        DBInstanceClass="db.t2.small",
        Engine="postgres",
        EngineVersion="9.3.14",
        Tags=[
            {
                'Key': "Name",
                'Value': "test"
            }
        ]
    )
    return RDSPostgresInstance(instance_id)

