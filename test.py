import logging
from datetime import datetime
import numpy as np

import pygame

from console.components.base import Container, Text, VStack, Image, LinePlot
from console.data import fake, weather, iaq

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1920, 1080

GREEN = 0x0abdc6ff
BLACK = 0x091833ff

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

    # Offset to start of main dashboard
    origin_y = title.height + 10
    origin_x = 10

    # Weather data
    params = {
        'font_name': '3270medium',
        'font_size': 32,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    data_fields = [
        Text(item, **params)
        for item in weather.present_data(weather_data.get('current', {}))
    ]

    vstack = VStack(data_fields, BLACK, 10)

    # Container 1
    params = {
        'border_thickness': 2,
        'border_radius': 10,
        'border_margin': 10,
        'border_color': GREEN,
        'background_color': BLACK,
        'child_padding': 15,
    }
    pad_amount = 2 * (params['child_padding'] + params['border_margin'])
    width, height = vstack.width + pad_amount, vstack.height + pad_amount
    container_weather = Container(width, height, [vstack], **params)


    # IAQ data
    params = {
        'font_name': '3270medium',
        'font_size': 32,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    data_fields = [
        Text(item, **params)
        for item in iaq.present_data(iaq_data)
    ]

    vstack = VStack(data_fields, BLACK, 10)

    # Container 1
    params = {
        'border_thickness': 2,
        'border_radius': 10,
        'border_margin': 10,
        'border_color': GREEN,
        'background_color': BLACK,
        'child_padding': 15,
    }
    pad_amount = 2 * (params['child_padding'] + params['border_margin'])
    width, height = vstack.width + pad_amount, vstack.height + pad_amount
    container_iaq = Container(width, height, [vstack], **params)

    # xx += dt
    plot = LinePlot(600,50, xx, yy, BLACK, GREEN, 5)


    screen.blit(title.get_surface(), (origin_x, 10))
    screen.blit(date.get_surface(), (WIDTH-10-date.width, 10))
    screen.blit(container_weather.get_surface(), (origin_x, origin_y))
    screen.blit(container_iaq.get_surface(), (origin_x, origin_y + container_weather.height + 10))
    screen.blit(plot.get_surface(), (WIDTH - 700, HEIGHT - 500))

    pygame.draw.rect(screen, color_fg, (WIDTH-100, HEIGHT-100, 100,100), 2)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 30
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(30) / 1000

pygame.quit()
