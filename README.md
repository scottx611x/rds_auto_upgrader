# rds_postgres_upgrader [![Build Status](https://travis-ci.org/scottx611x/rds_postgres_upgrader.svg?branch=master)](https://travis-ci.org/scottx611x/rds_postgres_upgrader) [![codecov](https://codecov.io/gh/scottx611x/rds_postgres_upgrader/branch/master/graph/badge.svg)](https://codecov.io/gh/scottx611x/rds_postgres_upgrader)

### What is does:

`rds_postgres_upgrader` allows one to perform major version upgrades on many PostgreSQL RDS Instances in parallel. While doing so, it will automatically resolve the proper [major version upgrade path](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html#USER_UpgradeDBInstance.PostgreSQL.MajorVersion), and wait for RDS Instance availability before performing subsequent upgrades. 

If you're really out of date (like I was), upgrading to the latest major version of Postgres on RDS can be pretty time consuming since you have to perform major version upgrades like so:
![screen shot 2018-09-27 at 4 41 30 pm](https://user-images.githubusercontent.com/5629547/46173437-3f5f3880-c274-11e8-90c5-ff2268e340e5.png)

Now, imagine upgrading an entire fleet! 

With `rds_postgres_upgrader`, a single command could take care of that for you: 
   
  **`$ python upgrade.py -tags {"taggedForUpgrade": True}`**
  
---

### Pre-Reqs:
- `python 3`
- AWS credentials [configured properly for `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- A PostgreSQL RDS Instance in need of a major version upgrade

### Installation:
- `pip install -r requirements.txt`

### Examples:

- **Upgrade many RDS instances to their latest available major version by DbInstanceIdentifers**:
    - `python upgrade.py -ids my-cool-db-a my-cool-db-b`

- **Upgrade many RDS instances to their latest available major version by DbInstanceTags**:
    - `python upgrade.py -tags {"Name": "test-rds-name", "owner": "test@example.com"}`

- **Upgrade a single RDS instance to a specific major version by DbInstanceIdentifer**:
    - `python upgrade.py -ids my-cool-db-a -v 9.6.9`

### Running Tests:
- `python tests.py`
