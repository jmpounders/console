import random

import pygame
import numpy as np

from console.components.base import LinePlot




# TODO
# - Make a "meter" class
# - Stack these into a border-less component

WIDTH, HEIGHT = 600, 600

GREEN = 0x0abdc6ff
BLACK = 0x091833ff
RED = 0xff0000ff
LIGHT_RED = 0xaa0000ff

FPS = 4

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

color_fg, color_bg = pygame.Color(GREEN), pygame.Color(BLACK)


delta_t = 0

ox, oy = 100, 100


def hex_point(ox: float, oy: float, s: float):
    """Get a "point-up" hexagon's vertices with origin the upper left corner."""
    return (
        (ox, oy),
        (ox + np.sqrt(3)*s/2, oy - s/2),
        (ox + np.sqrt(3)*s, oy),
        (ox + np.sqrt(3)*s, oy + s),
        (ox + np.sqrt(3)*s/2, oy + 3*s/2),
        (ox, oy + s),
    )


def get_neighbors(num_rows: int, num_cols: int):
    """Get the neighbor array of the grid."""
    num_hexes = num_rows * num_cols + int(num_rows/2)
    coords_to_index = lambda i, j: i*(num_cols) + int(i/2) + j

    neighbors = [[] for _ in range(num_hexes)]
    index = -1

    for i in range(num_rows):
        short_row = i % 2 == 0
        for j in range(num_cols):
            index += 1
            if short_row:
                # These rows have num_cols hexes
                # Because they are shorter rows, they alwas have neighbors above and below
                # except the first and last rows
                if i > 0 :
                    # Add the neighbors above
                    neighbors[index].append(coords_to_index(i-1, j))
                    neighbors[index].append(coords_to_index(i-1, j+1))
                if i < num_rows - 1:
                    # Add the neighborsbelow
                    neighbors[index].append(coords_to_index(i+1, j))
                    neighbors[index].append(coords_to_index(i+1, j+1))
                if j > 0:
                    # Add the neighbor to the left
                    neighbors[index].append(coords_to_index(i, j-1))
                if j < num_cols - 1:
                    # Add the neighbor to the right
                    neighbors[index].append(coords_to_index(i, j+1))
            else:
                # These rows have num_cols + 1 hexes
                # They always have neighbors above
                # Add the neighbors above
                if j > 0:
                    neighbors[index].append(coords_to_index(i-1, j-1))
                if j < num_cols:
                    neighbors[index].append(coords_to_index(i-1, j))
                if i < num_rows - 1:
                    # Add the neighbors below
                    if j > 0:
                        neighbors[index].append(coords_to_index(i+1, j-1))
                    if j < num_cols:
                        neighbors[index].append(coords_to_index(i+1, j))
                if j > 0:
                    # Add the neighbor to the left
                    neighbors[index].append(coords_to_index(i, j-1))
                # Add the neighbor to the right (always there, last node added below)
                neighbors[index].append(coords_to_index(i, j+1))

        # Odd rows have one more hex
        # This will never be the first row, it may be the last row
        if not short_row:
            index += 1
            j = num_cols
            # Add the neighbor above
            neighbors[index].append(coords_to_index(i-1, j-1))
            if i < num_rows - 1:
                # Add the neighbors below
                if j > 0:
                    neighbors[index].append(coords_to_index(i+1, j-1))
                if j < num_cols:
                    neighbors[index].append(coords_to_index(i+1, j))
            # Add the neighbor to the left
            neighbors[index].append(coords_to_index(i, j-1))

    return neighbors


def count_hex_states(
        index: int,
        hex_states: list,
        neighbors: list,
        state_values: tuple,
        include_self: bool = False
    ):
    """Count the number of active neighbors of a hex."""
    counts = {state: 0 for state in state_values}
    if include_self:
        counts[hex_states[index]] = 1
        total_count = 1
    else:
        total_count = 0
    for n in neighbors[index]:
        counts[hex_states[n]] += 1
        total_count += 1

    max_count = 7 if include_self else 6
    counts[state_values[0]] = max_count - (total_count - counts[state_values[0]])

    return counts


n_neighbors_max = 6
num_rows = 50
num_cols = 40
num_hexes = num_rows * num_cols + int(num_rows/2)
neighbors = get_neighbors(num_rows, num_cols)
s = 5
max_x = ox + num_cols * np.sqrt(3)*s
max_y = oy + num_rows * 3*s/2

# state_values = (0, 1)
# neighbors_include_self = True
# hex_states = [state_values[0]] * num_hexes
# # Random rule
# rules = {
#     (i, n_neighbors_max + 1 - i): state_values[random.randint(0, len(state_values) - 1)]
#     for i in range(n_neighbors_max + 2)
# }
# print(rules)

neighbors_include_self = False
state_values = (0, 1, 2)
hex_states = [state_values[0]] * num_hexes
# Random rule
rules = {
    (i, j - i, n_neighbors_max - j): state_values[random.randint(0, len(state_values) - 1)]
    for i in range(n_neighbors_max + 1)
    for j in range(i, n_neighbors_max + 1)
}
# beehive_matrix = [
#     [0, 1, 2, 1, 2, 0, 0],
#     [0, 2, 2, 2, 1, 1],
#     [0, 0, 2, 2, 0],
#     [0, 2, 2, 0],
#     [0, 0, 2],
#     [2, 0],
#     [0]
# ]
# rules = {
#     (n_neighbors_max - i - j, j, i): beehive_matrix[i][j]
#     for i in range(n_neighbors_max + 1)
#     for j in range(0, n_neighbors_max + 1 - i)
# }

neighbors_include_self = True
sprial_matrix = [
    [0, 1, 2, 1, 2, 2, 2, 2],
    [0, 2, 2, 1, 2, 2, 2],
    [0, 0, 2, 1, 2, 2],
    [0, 2, 2, 1, 2],
    [0, 0, 2, 1],
    [0, 0, 2],
    [0, 0],
    [0]
]
rules = {
    (n_neighbors_max + 1 - i - j, j, i): sprial_matrix[i][j]
    for i in range(n_neighbors_max + 2)
    for j in range(0, n_neighbors_max + 2 - i)
}
print(rules)

colormap = {
    0: color_fg,
    1: RED,
    2: LIGHT_RED
}

# Random initial conditions
for i in range(num_hexes):
    hex_states[i] = random.choices(state_values, weights=[100, 10, 10], k=1)[0]

entropy_history = []
# select = 0
# hex_states[select] = True
# for n in neighbors[select]:
#     hex_states[n] = True

safe_log = lambda x: np.log(x) if x > 0 else 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # update hexes
    new_hex_states = hex_states.copy()
    for i in range(num_hexes):
        counts = count_hex_states(i, hex_states, neighbors, state_values, neighbors_include_self)
        new_hex_states[i] = rules[tuple(counts[state] for state in state_values)]

    hex_states = new_hex_states
    total_counts = {state: 0 for state in state_values}
    for i in range(num_hexes):
        total_counts[hex_states[i]] += 1
    entropy = -sum([total_counts[state] * safe_log(total_counts[state] / num_hexes) for state in state_values])
    entropy_history.append(entropy)
    if len(entropy_history) > 50:
        entropy_history = entropy_history[-50:]
    print(total_counts, entropy)

    screen.fill(color_bg)

    if len(entropy_history) > 2:
        plot = LinePlot(max_x - ox, 50, list(range(len(entropy_history))), entropy_history, color_bg, color_fg, 0, 0)
        screen.blit(plot.get_surface(), (ox, max_y + 10))

    index = -1
    for i in range(num_rows):
        short_row = i % 2 == 0
        row_offset = (i % 2) * np.sqrt(3)*s/2
        for j in range(num_cols):
            x = ox + j * np.sqrt(3)*s - row_offset
            y = oy + i * 3*s/2
            hex_points = hex_point(x, y, s)
            index += 1
            fill = hex_states[index]
            width = 1 if fill == state_values[0] else 0
            pygame.draw.polygon(screen, pygame.Color(colormap[hex_states[index]]), hex_points, width=width)

        # Odd rows have one more hex
        # This will never be the first row, it may be the last row
        if not short_row:
            x = ox + num_cols * np.sqrt(3)*s - row_offset
            y = oy + i * 3*s/2
            hex_points = hex_point(x, y, s)
            index += 1
            fill = hex_states[index]
            width = 1 if fill == state_values[0] else 0
            pygame.draw.polygon(screen, pygame.Color(colormap[hex_states[index]]), hex_points, width=width)


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