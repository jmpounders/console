import datetime as dt

from console.data.source import DataSource
from console.data.weather import make_data_source

# TODO
# - Think about interplay between cache and refresh frequency
# - Fix weather labels

request = lambda : dt.datetime.now()

source = DataSource("test", request, 10)
weather = make_data_source()

while True:
    time_data = source.update()
    weather_data = weather.update()
    print(time_data)
    pause = input("Press enter to continue")