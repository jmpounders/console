import random

import pygame
import numpy as np

from console.components.base import LinePlot
from console.components.ca import hex_point, get_neighbors, count_hex_states, HexCA3




WIDTH, HEIGHT = 600, 600

GREEN = 0x0abdc6
BLACK = 0x091833
RED = 0xea00d9
LIGHT_RED = 0xea00d9

FPS = 4

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

black = (0, 0, 0)
white = (255, 255, 255, 15)
val = pygame.Color(*black)
# pygame.Color()
screen.fill(val)
pygame.draw.circle(screen, pygame.Color(*white), (300, 300), 100, 0)
pygame.display.flip()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
exit()

color_fg, color_bg = pygame.Color(GREEN), pygame.Color(BLACK)

hexca_params = {
    'num_rows': 50,
    'num_cols': 40,
    'rules': 'beehive',
    'colormap': {
        0: color_fg,
        1: RED,
        2: LIGHT_RED
    },
    'color_bg': BLACK,
    'color_fg': GREEN,
    'side_length': 5
}
hexca = HexCA3(**hexca_params)


delta_t = 0


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(color_bg)
    screen.blit(hexca.get_surface(), (0, 0))

    pygame.display.flip()
    delta_t = clock.tick(FPS) / 1000

    # hex_states[select] = False
    # for n in neighbors[select]:
    #     hex_states[n] = False

    # select = (select + 1) % num_hexes
    # hex_states[select] = True
    # for n in neighbors[select]:
    #     hex_states[n] = True

pygame.quit()