from typing import Callable
import datetime as dt

class DataSource:
    def __init__(
            self,
            name: str,
            request_func: Callable,
            refresh_frequency: int,
        ):
        self.name = name
        self.request_func = request_func
        self.refresh_frequency = refresh_frequency

        self.start_time = dt.datetime.now(dt.UTC)
        self.last_update = dt.datetime(1960,1,1).astimezone(dt.UTC)

        self.data = None

    def update(self):
        needs_refresh = (dt.datetime.now(dt.UTC) - self.last_update).seconds > self.refresh_frequency
        if self.data is None or needs_refresh:
            self.data = self.request_func()
            self.last_update = dt.datetime.now(dt.UTC)

        return self.data
