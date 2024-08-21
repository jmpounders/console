from datetime import datetime

import pygame

from console.components.base import Container, Text, VStack, Image

WIDTH, HEIGHT = 1280, 720

GREEN = 0x0abdc6ff
BLACK = 0x091833ff

# print(pygame.font.get_fonts())

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

color_fg, color_bg = pygame.Color(GREEN), pygame.Color(BLACK)

dt = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(color_bg)

    params = {
        'font_name': '3270medium',
        'font_size': 56,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    title = Text('TITLE CARD', **params)

    params['font_size'] = 24
    date = Text(datetime.now().strftime('%Y-%m-%d %I:%M:%S'), **params)

    origin_y = title.height + 10
    origin_x = 10

    params = {
        'border_thickness': 2,
        'border_radius': 10,
        'border_margin': 10,
        'border_color': GREEN,
        'background_color': BLACK,
        'child_padding': 15,
    }
    container = Container(750, 250, [], **params)

    params = {
        'font_name': '3270medium',
        'font_size': 32,
        'font_color': GREEN,
        'font_background': BLACK,
    }
    text = Text('This is a test.', **params)

    image = pygame.Surface((100, 100))
    image.fill(pygame.Color(BLACK))
    pygame.draw.circle(image, pygame.Color(GREEN), (50,50), 50)
    circle = Image(image)

    vstack = VStack([text, text], BLACK, 10)
    container.children.append(vstack)
    container.children.append(text)


    screen.blit(title.get_surface(), (origin_x, 10))
    screen.blit(date.get_surface(), (WIDTH-10-date.width, 10))
    screen.blit(container.get_surface(), (origin_x, origin_y))
    screen.blit(circle.get_surface(), (WIDTH - 100, HEIGHT - 100))

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 30
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(30) / 1000

pygame.quit()
