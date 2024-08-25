"""Weather data from https://open-meteo.com/."""
from typing import Any

import datetime as dt
import zoneinfo as zi

from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse

import httpx

from console.data.source import DataSource
from console.data.utils import pad


REFRESH_RATE = 100

LAT, LONG = 32.038537, -81.09347
TIMEZONE = 'US/Eastern'
BASE_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation_probability",
    "surface_pressure",
    "cloud_cover",
    "visibility",
    "wind_speed_10m",
    "wind_gusts_10m"
]
CURRENT_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
	"apparent_temperature",
	"cloud_cover",
	"pressure_msl",
	"surface_pressure",
	"wind_speed_10m",
	"wind_direction_10m",
	"wind_gusts_10m"
]
DATA_LABELS = {
	'temperature_2m': 'Temp [F]',
	'relative_humidity_2m': 'Rel Hum [%]',
	'dew_point_2m': 'Dew Point [F]',
	'apparent_temperature': 'App Temp [F]',
	'precipitation_probability': 'Precip Prob [%]',
	'surface_pressure': 'Press Surf [hPa]',
    'pressure_msl': 'Press MSL [hPa]',
	'cloud_cover': 'Cloud Cover [%]',
	'visibility': 'Visibility [m]',
	'wind_speed_10m': 'Wind Speed [mph]',
	'wind_gusts_10m': 'Wind Gusts [mph]',
	'wind_direction_10m': 'Wind Dir [deg]',
}

def weather_api(url: str, params: any) -> list[WeatherApiResponse]:
    params["format"] = "flatbuffers"

    response = httpx.get(url, params=params)

    if response.status_code in [400, 429]:
        response_body = response.json()
        raise Exception(response_body)

    response.raise_for_status()

    data = response.content
    messages = []
    total = len(data)
    pos = int(0)
    while pos < total:
        length = int.from_bytes(data[pos : pos + 4], byteorder="little")
        message = WeatherApiResponse.GetRootAs(data, pos + 4)
        messages.append(message)
        pos += length + 4

    return messages


def request_data() -> dict[str, Any]:
    # Setup the Open-Meteo API client with cache and retry on error

    # The order of variables in hourly or daily is important to assign them correctly below
    params = {
        "latitude": LAT,
        "longitude": LONG,
        "hourly": HOURLY_VARIABLES,
        "current": CURRENT_VARIABLES,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
            "timezone": "America/New_York"
        }
    response = weather_api(BASE_URL, params=params)[0]

    output = {}

    # Process first location. Add a for-loop for multiple locations or weather models
    # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation {response.Elevation()} m asl")
    # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Current values
    output['current'] = {}
    current = response.Current()
    for ind,var_name in enumerate(CURRENT_VARIABLES):
        var = current.Variables(ind)
        output['current'][DATA_LABELS.get(var_name, var_name)] = var.Value()


    # Hourly values
    output['hourly'] = {}
    hourly = response.Hourly()
    time_start_utc = hourly.Time()
    time_end_utc = hourly.TimeEnd()
    time_interval = hourly.Interval()
    times_utc = [dt.datetime.fromtimestamp(time_start_utc + i*time_interval, tz=dt.UTC) for i in range((time_end_utc - time_start_utc) // time_interval)]
    output['hourly']['Time'] = [t.astimezone(zi.ZoneInfo(TIMEZONE)).strftime('%Y-%m-%d %I:%M:%S %p %Z') for t in times_utc]

    for ind,var_name in enumerate(HOURLY_VARIABLES):
        var = hourly.Variables(ind)
        output['hourly'][DATA_LABELS.get(var_name, var_name)] = var.ValuesAsNumpy()

    return output


def make_data_source() -> DataSource:
    default = {
        'current': {key: 'NULL' for key in DATA_LABELS.values()},
        'hourly': {key: 'NULL' for key in DATA_LABELS.values()}
    }
    return DataSource("weather", request_data, REFRESH_RATE, default)


def present_data(data: dict[str, float]) -> list[str]:
    return [pad(key, value, 30) for key, value in data.items()]
