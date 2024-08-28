import logging
from datetime import datetime
import numpy as np

import pygame

from console.components.base import Container, Text, VStack, Image, LinePlot
from console.components.composite import TextInBorder, AnnotatedLinePlots
from console.data import fake, weather, iaq

# TODO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1920, 1080

GREEN = 0x0abdc6ff
BLACK = 0x091833ff
RED = 0xff0000ff

FPS = 4

# print(pygame.font.get_fonts())

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

color_fg, color_bg = pygame.Color(GREEN), pygame.Color(BLACK)

# Setup data sources
fake_data_source = fake.make_data_source()
weather_data_source = weather.make_data_source()
iaq_data_source = iaq.make_data_source()

xx = np.linspace(0, 10, 500)
yy = np.sin(xx)

dt = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # update data sources
    weather_data = weather_data_source.update()
    # logger.debug(weather_data['current'])
    iaq_data = iaq_data_source.update()
    # logger.debug(iaq_data)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(color_bg)

    # Make title
    params = {
        'font_name': '3270medium',
        'font_size': 56,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    title = Text('TITLE CARD', **params)

    # Make clock
    params['font_size'] = 24
    date = Text(datetime.now().strftime('%Y-%m-%d %I:%M:%S'), **params)

    # Show data source statuses
    data_source_status = [
        weather_data_source.status,
        iaq_data_source.status,
    ]
    status_surface = pygame.Surface((len(data_source_status) * 30, 30))
    status_surface.fill(color_bg)
    for i, status in enumerate(data_source_status):
        color = pygame.Color(GREEN) if status == 'idle' else pygame.Color(RED)
        indicaor = pygame.draw.rect(status_surface, color, (5 + 30 * i, 5, 20, 20))

    # Offset to start of main dashboard
    origin_y = title.height + 10
    origin_x = 10

    # Weather data
    weather_data_fmt = weather.present_data(weather_data.get('current', {}))
    text_params = {
        'font_name': '3270medium',
        'font_size': 32,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    container_params = {
        'border_thickness': 2,
        'border_radius': 10,
        'border_margin': 10,
        'border_color': GREEN,
        'background_color': BLACK,
        'child_padding': 15,
    }
    container_weather = TextInBorder(weather_data_fmt, text_params, container_params)

    # IAQ data
    iaq_data_fmt = iaq.present_data(iaq_data)
    container_iaq = TextInBorder(iaq_data_fmt, text_params, container_params)


    forecast_temp = weather_data.get('hourly', {}).get('Temp [F]', [])
    forecast_cloud = weather_data.get('hourly', {}).get('Cloud Cover [%]', [])
    forecast_precip = weather_data.get('hourly', {}).get('Precip Prob [%]', [])
    forecast_wind = weather_data.get('hourly', {}).get('Wind Speed [mph]', [])
    forecast_time_ind = list(range(len(forecast_temp)))
    forecast_plots = AnnotatedLinePlots(
        ['TEMP','CLCO','PREC','WIND'],
        forecast_time_ind,
        [forecast_temp, forecast_cloud, forecast_precip, forecast_wind],
        text_params,
        container_params
    )

    # IAQ history
    if len(iaq_data_source.history) < 2:
        iaq_utc_times = []
        iaq_history = []
    else:
        iaq_utc_times, iaq_history = zip(*iaq_data_source.history)
    n_points = len(iaq_utc_times)
    temp_data = [data['Temperature [F]'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    humidity_data = [data['Rel Hum [%]'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    c02_data = [data['CO2 [ppm]'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    pm25_data = [data['PM2.5 [ug/m3]'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    tvoc_data = [data['VOC Index'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    nox_data = [data['NOx Index'] for data in iaq_history] #+ [0]*(iaq_data_source.max_history_len - n_points)
    iaq_plots = AnnotatedLinePlots(
        ['TEMP', ' CO2', 'PM25', ' VOC', ' NOx'],
        list(range(n_points)),
        [temp_data, c02_data, pm25_data, tvoc_data, nox_data],
        text_params,
        container_params
    )

    screen.blit(title.get_surface(), (origin_x, 10))
    screen.blit(date.get_surface(), (WIDTH-10-date.width, 10))
    screen.blit(status_surface, (WIDTH-status_surface.get_width()-10, date.height + 10))

    screen.blit(container_weather.get_surface(), (origin_x, origin_y))
    screen.blit(forecast_plots.get_surface(), (origin_x + container_weather.width + 15, origin_y))

    screen.blit(container_iaq.get_surface(), (origin_x, origin_y + container_weather.height + 10))
    screen.blit(iaq_plots.get_surface(), (origin_x + container_iaq.width + 15, origin_y + container_weather.height + 10))

    pygame.draw.rect(screen, color_fg, (WIDTH-100, HEIGHT-100, 100,100), 2)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(FPS) / 1000

pygame.quit()
