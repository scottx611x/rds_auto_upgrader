import datetime
from dateutil.tz import tzutc

describe_db_instances = {
    "DBInstances": [
        {
            'DBInstanceIdentifier': 'rds-test',
            'DBInstanceClass': 'db.t2.small',
            'Engine': 'postgres',
            'DBInstanceStatus': 'available',
            'MasterUsername': 'root',
            'Endpoint': {
                'Address': 'rds-test.example.us-east-1.rds.amazonaws.com',
                'Port': 5432,
                'HostedZoneId': 'xxxxxxxxxxxxxx'
            },
            'AllocatedStorage': 10,
            'InstanceCreateTime': datetime.datetime(
                2018, 1, 1, 1, 1, 1, 100000, tzinfo=tzutc()
            ),
            'PreferredBackupWindow': '06:46-07:16',
            'BackupRetentionPeriod': 0,
            'DBSecurityGroups': [],
            'VpcSecurityGroups': [
                {
                    'VpcSecurityGroupId': 'sg-xxxxxxxx',
                    'Status': 'active'
                }
            ],
            'DBParameterGroups': [
                {
                    'DBParameterGroupName': 'default.postgres9.3',
                    'ParameterApplyStatus': 'in-sync'
                }
            ],
            'AvailabilityZone': 'us-east-1d',
            'DBSubnetGroup': {
                'DBSubnetGroupName': 'default',
                'DBSubnetGroupDescription': 'default',
                'VpcId': 'vpc-xxxxxxxx',
                'SubnetGroupStatus': 'Complete',
                'Subnets': [
                    {
                        'SubnetIdentifier': 'subnet-xxxxxxxa',
                        'SubnetAvailabilityZone': {
                            'Name': 'us-east-1a'
                        },
                        'SubnetStatus': 'Active'
                    },
                    {
                        'SubnetIdentifier': 'subnet-xxxxxxxb',
                        'SubnetAvailabilityZone': {
                            'Name': 'us-east-1b'
                        },
                        'SubnetStatus': 'Active'
                    },
                    {
                        'SubnetIdentifier': 'subnet-xxxxxxxc',
                        'SubnetAvailabilityZone': {
                            'Name': 'us-east-1c'
                        },
                        'SubnetStatus': 'Active'
                    },
                    {
                        'SubnetIdentifier': 'subnet-xxxxxxxd',
                        'SubnetAvailabilityZone': {
                            'Name': 'us-east-1d'
                        },
                        'SubnetStatus': 'Active'
                    }
                ]
            },
            'PreferredMaintenanceWindow': 'fri:09:41-fri:10:11',
            'PendingModifiedValues': {},
            'MultiAZ': False,
            'EngineVersion': '9.3.14',
            'AutoMinorVersionUpgrade': False,
            'ReadReplicaDBInstanceIdentifiers': [],
            'LicenseModel': 'postgresql-license',
            'OptionGroupMemberships': [
                {
                    'OptionGroupName': 'default:postgres-9-3',
                    'Status': 'in-sync'
                }
            ],
            'PubliclyAccessible': False,
            'StorageType': 'gp2',
            'DbInstancePort': 0,
            'StorageEncrypted': False,
            'DbiResourceId': 'db-XXXXXXXXXXXXXXXXXXXXXXXXX',
            'CACertificateIdentifier': 'rds-ca-2015',
            'DomainMemberships': [],
            'CopyTagsToSnapshot': False,
            'MonitoringInterval': 0,
            'DBInstanceArn': 'arn:aws:rds:us-east-1:000000000000:db:rds-test',
            'IAMDatabaseAuthenticationEnabled': False,
            'PerformanceInsightsEnabled': False
        }
    ]
}

list_tags_for_resource = {
    'TagList': [
        {
            'Key': 'Owner',
            'Value': 'test@example.com'
        },
        {
            'Key': 'Name',
            'Value': 'test-rds-name'
        }
    ],
    'ResponseMetadata': {
        'RequestId': '00000000-0000-0000-0000-00000000000',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '00000000-0000-0000-0000-00000000000',
            'content-type': 'text/xml',
            'content-length': '1000',
            'date': 'Mon, 24 Sep 2018 13:38:19 GMT'
        },
        'RetryAttempts': 0
    }
}
