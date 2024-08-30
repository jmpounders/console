
import pygame
import numpy as np

from console.components.base import Meter, Container
from console.components.composite import SunPath


# TODO
# - Make a "meter" class
# - Stack these into a border-less component

WIDTH, HEIGHT = 600, 600

GREEN = 0x0abdc6ff
BLACK = 0x091833ff
RED = 0xff0000ff

FPS = 4

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

color_fg, color_bg = pygame.Color(GREEN), pygame.Color(BLACK)


delta_t = 0

sun_path = SunPath(500, GREEN, BLACK, RED, 2, 10)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(color_bg)

    screen.blit(sun_path.get_surface(), (50, 50))


    pygame.display.flip()
    delta_t = clock.tick(FPS) / 1000

pygame.quit()