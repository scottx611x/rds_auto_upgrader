# rds_postgres_upgrader

### Pre-Reqs:
- `python 3 or docker`
- AWS credentials [configured properly for `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
- An RDS Instance in need of upgrading

### Installation:
- `pip install -r requirements.txt`

### Usage:
- `python pg_upgrader.py <rds_db_instance_identifier>`

### Running Tests:
- `python tests.py`

### With Docker:
- `docker build -t pg_upgrader .`
- `docker run -it --rm -v ~/.aws:/root/.aws -e RDS_DB_INSTANCE_ID=db-upgrade-test -e PG_ENGINE_TARGET_VERSIONS="9.6.9 10.4" pg_upgrader`
