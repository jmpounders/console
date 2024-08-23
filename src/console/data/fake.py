import random

from console.data.source import DataSource
from console.data.utils import pad

REFRESH_RATE = 10

# sample a normal random variable

def request_data() -> dict[str, float]:
    return {
        'Temperature': 72 + random.normalvariate(0, 5),
        'Humidity': 50,
        'Pressure': 30.0,
        'Wind Speed': 5,
        'Wind Gusts': 10,
        'Wind Direction': 180,
        'Precipitation': 0,
    }


def make_data_source() -> DataSource:
    return DataSource("weather", request_data, REFRESH_RATE)


def present_data(data: dict[str, float]) -> list[str]:
    return [pad(key, value, 30) for key, value in data.items()]
