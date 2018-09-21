# rds_postgres_upgrader

See: [AWS RDS Postgresql Major version Upgrade notes](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html#USER_UpgradeDBInstance.PostgreSQL.MajorVersion)

### Pre-Reqs:
- `python 3`
- AWS credentials [configured properly for `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- An RDS Instance in need of upgrading

### Installation:
- `pip install -r requirements.txt`

### Examples:
- `python pg_upgrader.py -ip X.X.X.X -id my-cool-db -v 9.6.9 10.4`

### Running Tests:
- `python tests.py`
