# rds_postgres_upgrader [![Build Status](https://travis-ci.org/scottx611x/rds_postgres_upgrader.svg?branch=master)](https://travis-ci.org/scottx611x/rds_postgres_upgrader) [![codecov](https://codecov.io/gh/scottx611x/rds_postgres_upgrader/branch/master/graph/badge.svg)](https://codecov.io/gh/scottx611x/rds_postgres_upgrader)

See: [AWS RDS Postgresql Major version Upgrade notes](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html#USER_UpgradeDBInstance.PostgreSQL.MajorVersion)

### Pre-Reqs:
- `python 3`
- AWS credentials [configured properly for `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- A PostgreSQL RDS Instance in need of a major version upgrade

### Installation:
- `pip install -r requirements.txt`

### Examples:
- `python pg_upgrader.py -ip X.X.X.X -id my-cool-db -v 9.6.9 10.4`

- **Upgrade many RDS instances to their latest available major version by DbInstanceIdentifers**:
    - `python pg_upgrader.py -ids my-cool-db-a my-cool-db-b`

- **Upgrade many RDS instances to their latest available major version by DbInstanceTags**:
    - `python pg_upgrader.py -tags {"Name": "test-rds-name", "owner": "test@example.com"}`

- **Upgrade a single RDS instance to a specific major version by DbInstanceIdentifer**:
    - `python pg_upgrader.py -ids my-cool-db-a -v 9.6.9`

### Running Tests:
- `python tests.py`
- `python -m doctest -v pg_upgrader.py`
