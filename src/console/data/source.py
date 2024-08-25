from typing import Callable
import datetime as dt
from concurrent import futures


class DataRetriever:

    def __init__(self, max_workers: int = 2):
        self.executor = futures.ThreadPoolExecutor(max_workers=max_workers)
        self.pool = {}

    def submit(self, name: str, func: Callable):
        self.pool[name] = self.executor.submit(func)

    def is_done(self, name: str):
        return self.pool[name].done()

    def get_result(self, name: str):
        if self.pool[name].done():
            return self.pool[name].result()
        else:
            return None

    def shutdown(self):
        self.executor.shutdown()


REQUEST = DataRetriever()


class DataSource:
    def __init__(
            self,
            name: str,
            request_func: Callable,
            refresh_frequency: int,
            default_data: dict = {},
        ):
        self.name = name
        self.request_func = request_func
        self.refresh_frequency = refresh_frequency

        self.start_time = dt.datetime.now(dt.UTC)
        self.last_update = dt.datetime(1960,1,1).astimezone(dt.UTC)

        self.data = default_data
        self.status = 'idle'

    def update(self):
        needs_refresh = (dt.datetime.now(dt.UTC) - self.last_update).seconds > self.refresh_frequency
        if needs_refresh and self.status == 'idle':
            REQUEST.submit(self.name, self.request_func)
            self.status = 'pending'
            # self.data = self.request_func()

        if self.status == 'pending':
            response = REQUEST.get_result(self.name)
            if response is not None:
                self.data = response
                self.last_update = dt.datetime.now(dt.UTC)
                self.status = 'idle'

        return self.data
