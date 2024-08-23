"""See https://github.com/airgradienthq/arduino/blob/master/docs/local-server.md for more information on the AirGradient local server API."""

from typing import Any

from requests import Session
from retry_requests import retry

from console.data.source import DataSource
from console.data.utils import pad

REFRESH_RATE = 10
RETRIES = 5
BACKOFF_FACTOR = 0.2

SERIAL_NO = '404cca6b9fd4'
BASE_URL = f'http://airgradient_{SERIAL_NO}.local'

VARIABLES = [
    # 'wifi',
    'rco2',
    'pm01',
    'pm02',
    'pm10',
    'pm003Count',
    # 'atmp',
    'atmpCompensated',
    # 'rhum',
    'rhumCompensated',
    'tvocIndex',
    # 'tvocRaw',
    'noxIndex',
    # 'noxRaw',
    'boot',
    # 'bootCount',
    # 'ledMode',  # maybe add this somewhere later
    # 'firmware',
    'model'
]
DATA_LABELS = {
    'wifi': 'WiFi Sig Str [dBm]',
    'rco2': 'CO2 [ppm]',
    'pm01': 'PM1.0 [ug/m3]',
    'pm02': 'PM2.5 [ug/m3]',
    'pm10': 'PM10 [ug/m3]',
    'pm003Count': 'PM0.3 [count/dL]',
    'atmp': 'Uncorrected Temperature [C]',
    'atmpCompensated': 'Temperature [C]',
    'rhum': 'Uncorrected Rel Hum [%]',
    'rhumCompensated': 'Rel Hum [%]',
    'tvocIndex': 'VOC Index', # Sensiron VOC Index
    'tvocRaw': 'VOC Raw Value',
    'noxIndex': 'NOx Index', # Sensiron NOx Index
    'noxRaw': 'NOx Raw Value',
    'boot': 'Meas Cycle Count',
    'ledMode': 'LED Mode',
    'firmware': 'F/W Vers',
    'model': 'Model'
}

def request_data() -> dict[str, Any]:
    retry_session = retry(Session(), retries = RETRIES, backoff_factor = BACKOFF_FACTOR)

    response = retry_session.get(BASE_URL + '/measures/current')

    output = {}
    for variable in VARIABLES:
        output[DATA_LABELS[variable]] = response.json().get(variable, 'NULL')

    return output


def make_data_source() -> DataSource:
    return DataSource("airgradient", request_data, REFRESH_RATE)


def present_data(data: dict[str, Any]) -> list[str]:
    return [pad(key, value, 30) for key, value in data.items()]