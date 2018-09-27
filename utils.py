import sys
import time
from threading import Thread


class ExceptionCatchingThread(Thread):
    """
    The interface provided by ExceptionCatchingThread is identical to that of
    threading.Thread, however, if an exception occurs in the thread
    the error will be caught and printed to stderr.
    """
    def __init__(self, **kwargs):
        super(ExceptionCatchingThread, self).__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run

    def _wrap_run(self):
        try:
            self._real_run()
        except Exception as exc:
            print(exc, file=sys.stderr)


class RDSPostgresWaiter:
    """
    Context manager that provides the waiting functionality when
    modifying/upgrading an RDSInstance

    >>> from models import rds_client
    >>> from moto import mock_rds2; mock_rds2().start()
    >>> from test_data.utils import make_postgres_instance
    >>> make_postgres_instance()
    RDSPostgresInstance id: test-rds-id status: available engine_version: 9.3.14
    >>> with RDSPostgresWaiter(rds_client, "test-rds-id", "9.4.18", sleep_time=0):
    ...    print("Upgrading soon!")
    Polling: test-rds-id for availability
    Status of: test-rds-id is: available
    Upgrading soon!
    Upgrading test-rds-id to: 9.4.18
    Successfully upgraded test-rds-id to: 9.4.18
    """
    def __init__(self, client, db_instance_id, pg_engine_version, sleep_time=60):
        self.engine_version = pg_engine_version
        self.instance_id = db_instance_id
        self.sleep_time = sleep_time
        self.client = client
        self.rds_waiter = self.client.get_waiter("db_instance_available")

        _operation_method = self.rds_waiter._operation_method

        def wait_with_status_reporting(**kwargs):
            print("Polling: {} for availability".format(self.instance_id))
            response = _operation_method(**kwargs)
            print("Status of: {} is: {}".format(
                self.instance_id,
                response["DBInstances"][0]["DBInstanceStatus"]
            ))
            return response

        self.rds_waiter._operation_method = wait_with_status_reporting

    def __enter__(self):
        self.rds_waiter.wait(DBInstanceIdentifier=self.instance_id)

    def __exit__(self, type, value, traceback):
        print("Upgrading {} to: {}"
              .format(self.instance_id, self.engine_version))
        time.sleep(self.sleep_time)
        self.client.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier=self.instance_id
        )
        print("Successfully upgraded {} to: {}"
              .format(self.instance_id, self.engine_version))