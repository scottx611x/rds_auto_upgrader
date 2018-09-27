# coding=utf-8

test_instance_id = "test-rds-id"
test_instance_name_key = "Name"
test_instance_owner_key = "owner"
test_instance_name_value = "test-rds-name"
test_instance_owner_value = "test@example.com"


list_tags_for_resource = {
    'TagList': [
        {
            'Key': 'Name',
            'Value': test_instance_name_value
        },
        {
            'Key': 'owner',
            'Value': test_instance_owner_value
        }
    ]
}

test_tags = {
    d['Key']: d['Value']
    for d in list_tags_for_resource['TagList']
}

describe_db_engine_versions = [
    {'DBEngineVersions': [{'Engine': 'postgres', 'EngineVersion': '9.3.14', 'DBParameterGroupFamily': 'postgres9.3', 'DBEngineDescription': 'PostgreSQL', 'DBEngineVersionDescription': 'PostgreSQL 9.3.14-R1', 'ValidUpgradeTarget': [{'Engine': 'postgres', 'EngineVersion': '9.3.16', 'Description': 'PostgreSQL 9.3.16-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.3.17', 'Description': ' PostgreSQL 9.3.17-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.3.19', 'Description': 'PostgreSQL 9.3.19-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.3.20', 'AutoUpgrade': True, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.3.22', 'Description': 'PostgreSQL 9.3.22-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.3.23', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': False}, {'Engine': 'postgres', 'EngineVersion': '9.4.9', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.11', 'Description': 'PostgreSQL 9.4.11-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.12', 'Description': 'PostgreSQL 9.4.12-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.14', 'Description': 'PostgreSQL 9.4.14-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.15', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.17', 'Description': 'PostgreSQL 9.4.17-R1', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}, {'Engine': 'postgres', 'EngineVersion': '9.4.18', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}], 'SupportsLogExportsToCloudwatchLogs': False, 'SupportsReadReplica': True}], 'ResponseMetadata': {'RequestId': '24a4c85a-936b-4418-9c28-c1d9caaabb3f', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '24a4c85a-936b-4418-9c28-c1d9caaabb3f', 'content-type': 'text/xml', 'content-length': '6234', 'vary': 'Accept-Encoding', 'date': 'Tue, 25 Sep 2018 14:44:56 GMT'}, 'RetryAttempts': 0}},
    {'DBEngineVersions': [{'Engine': 'postgres', 'EngineVersion': '9.4.18', 'DBParameterGroupFamily': 'postgres9.4', 'DBEngineDescription': 'PostgreSQL', 'DBEngineVersionDescription': 'PostgreSQL 9.4.18-R1', 'ValidUpgradeTarget': [{'Engine': 'postgres', 'EngineVersion': '9.5.13', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}], 'SupportsLogExportsToCloudwatchLogs': False, 'SupportsReadReplica': True}], 'ResponseMetadata': {'RequestId': '08d666e3-12f6-40b2-b244-0968694bfa4d', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '08d666e3-12f6-40b2-b244-0968694bfa4d', 'content-type': 'text/xml', 'content-length': '1394', 'date': 'Tue, 25 Sep 2018 14:44:56 GMT'}, 'RetryAttempts': 0}},
    {'DBEngineVersions': [{'Engine': 'postgres', 'EngineVersion': '9.5.13', 'DBParameterGroupFamily': 'postgres9.5', 'DBEngineDescription': 'PostgreSQL', 'DBEngineVersionDescription': 'PostgreSQL 9.5.13-R1', 'ValidUpgradeTarget': [{'Engine': 'postgres', 'EngineVersion': '9.6.9', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}], 'SupportsLogExportsToCloudwatchLogs': False, 'SupportsReadReplica': True}], 'ResponseMetadata': {'RequestId': 'be018959-e0e5-40f5-9a54-4c6c82068675', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'be018959-e0e5-40f5-9a54-4c6c82068675', 'content-type': 'text/xml', 'content-length': '1392', 'date': 'Tue, 25 Sep 2018 14:44:56 GMT'}, 'RetryAttempts': 0}},
    {'DBEngineVersions': [{'Engine': 'postgres', 'EngineVersion': '9.6.9', 'DBParameterGroupFamily': 'postgres9.6', 'DBEngineDescription': 'PostgreSQL', 'DBEngineVersionDescription': 'PostgreSQL 9.6.9-R1', 'ValidUpgradeTarget': [{'Engine': 'postgres', 'EngineVersion': '10.4', 'AutoUpgrade': False, 'IsMajorVersionUpgrade': True}], 'SupportsLogExportsToCloudwatchLogs': False, 'SupportsReadReplica': True}], 'ResponseMetadata': {'RequestId': '38dc0e02-5c2f-41d3-ba82-819fbf3fbcbc', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '38dc0e02-5c2f-41d3-ba82-819fbf3fbcbc', 'content-type': 'text/xml', 'content-length': '1387', 'date': 'Tue, 25 Sep 2018 14:44:56 GMT'}, 'RetryAttempts': 0}},
    {'DBEngineVersions': [{'Engine': 'postgres', 'EngineVersion': '10.4', 'DBParameterGroupFamily': 'postgres10', 'DBEngineDescription': 'PostgreSQL', 'DBEngineVersionDescription': 'PostgreSQL 10.4-R1', 'ValidUpgradeTarget': [], 'SupportsLogExportsToCloudwatchLogs': False, 'SupportsReadReplica': True}], 'ResponseMetadata': {'RequestId': '74f095b3-a065-466d-bee1-0f82d1812d6b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '74f095b3-a065-466d-bee1-0f82d1812d6b', 'content-type': 'text/xml', 'content-length': '995', 'date': 'Tue, 25 Sep 2018 14:44:56 GMT'}, 'RetryAttempts': 0}}
]


def describe_db_instances(status=None):
    describe_db_instances_response = {'DBInstances': [{'DBInstanceIdentifier': 'test-rds-id', 'DBInstanceClass': 'db.t2.small', 'Engine': 'postgres', 'DBInstanceStatus': 'available', 'MasterUsername': 'None', 'DBName': 'test-rds-name', 'Endpoint': {'Address': 'test-rds-id.aaaaaaaaaa.us-east-1.rds.amazonaws.com', 'Port': 5432}, 'AllocatedStorage': 10, 'PreferredBackupWindow': '03:50-04:20', 'BackupRetentionPeriod': 1, 'DBSecurityGroups': [], 'VpcSecurityGroups': [], 'DBParameterGroups': [{'DBParameterGroupName': 'default.postgres9.3', 'ParameterApplyStatus': 'in-sync'}], 'PreferredMaintenanceWindow': 'wed:06:38-wed:07:08', 'MultiAZ': False, 'EngineVersion': '9.3.14', 'AutoMinorVersionUpgrade': False, 'ReadReplicaDBInstanceIdentifiers': [], 'LicenseModel': 'None', 'OptionGroupMemberships': [], 'PubliclyAccessible': False, 'StatusInfos': [], 'StorageType': 'standard', 'StorageEncrypted': False, 'DbiResourceId': 'db-M5ENSHXFPU6XHZ4G4ZEI5QIO2U', 'DBInstanceArn': 'arn:aws:rds:us-east-1:1234567890:db:test-rds-id', 'IAMDatabaseAuthenticationEnabled': False}], 'ResponseMetadata': {'RequestId': '523e3218-afc7-11c3-90f5-f90431260ab4', 'HTTPStatusCode': 200, 'HTTPHeaders': {'Content-Type': 'text/plain', 'server': 'amazon.com'}, 'RetryAttempts': 0}}
    describe_db_instances_response["DBInstances"][0]["DBInstanceStatus"] = status
    return describe_db_instances_response