# rds_postgres_upgrader

### Pre-Reqs:
- `python 3`
- AWS credentials in a place where `boto3` can find them
- An RDS Instance in need of upgrading

### Installation:
- `pip install -r requirements.txt`

### Usage:
- `python pg_upgrader.py <rds_db_instance_identifier>`


### Tests:
- `python tests.py`