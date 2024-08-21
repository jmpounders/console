"""Weather data from https://open-meteo.com/."""

import datetime as dt
import zoneinfo as zi

import openmeteo_requests

import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
lat, long = 32.038537, -81.09347
url = "https://api.open-meteo.com/v1/forecast"
hourly_variables = [
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
current_variables = [
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
labels = {
	'temperature_2m': 'Temperature (°F)',
	'relative_humidity_2m': 'Relative Humidity (%)',
	'dew_point_2m': 'Dew Point (°F)',
	'apparent_temperature': 'Apparent Temperature (°F)',
	'precipitation_probability': 'Precipitation Probability (%)',
	'surface_pressure': 'Surface Pressure (hPa)',
	'cloud_cover': 'Cloud Cover (%)',
	'visibility': 'Visibility (m)',
	'wind_speed_10m': 'Wind Speed (mph)',
	'wind_gusts_10m': 'Wind Gusts (mph)',
	'wind_direction_10m': 'Wind Direction (°)',
	'pressure_msl': 'Pressure MSL (hPa)',
}
params = {
	"latitude": lat,
	"longitude": long,
	"hourly": hourly_variables,
    "current": current_variables,
	"temperature_unit": "fahrenheit",
	"wind_speed_unit": "mph",
	"precipitation_unit": "inch",
	"timezone": "America/New_York"
}
response = openmeteo.weather_api(url, params=params)[0]

# Process first location. Add a for-loop for multiple locations or weather models
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values
current = response.Current()
for ind,var_name in enumerate(current_variables):
	var = current.Variables(ind)
	print(f'{labels.get(var_name, var_name)}: {var.Value()}')


# Hourly values
hourly = response.Hourly()
time_start_utc = hourly.Time()
time_end_utc = hourly.TimeEnd()
time_interval = hourly.Interval()
times_utc = [dt.datetime.fromtimestamp(time_start_utc + i*time_interval, tz=dt.UTC) for i in range((time_end_utc - time_start_utc) // time_interval)]
times_ext_str = [t.astimezone(zi.ZoneInfo('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p %Z') for t in times_utc]

for ind,var_name in enumerate(hourly_variables):
	var = hourly.Variables(ind)
	print(f'{labels.get(var_name, var_name)}: {len(var.ValuesAsNumpy())}')




exit()


# hourly_data = {"date": pd.date_range(
# 	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
# 	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
# 	freq = pd.Timedelta(seconds = hourly.Interval()),
# 	inclusive = "left"
# )}
hourly_data = {}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["apparent_temperature"] = hourly_apparent_temperature
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["surface_pressure"] = hourly_surface_pressure
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["visibility"] = hourly_visibility
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m

# hourly_dataframe = pd.DataFrame(data = hourly_data)
# print(hourly_dataframe)