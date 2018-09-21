FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD python pg_upgrader.py -id $RDS_DB_INSTANCE_ID -v $PG_ENGINE_TARGET_VERSIONS