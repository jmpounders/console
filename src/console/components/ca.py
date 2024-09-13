import random
import math

import pygame

from src.console.components.base import Component, LinePlot


N_NEIGHBORS_MAX = 6


def hex_point(ox: float, oy: float, s: float):
    """Get a "point-up" hexagon's vertices with origin the upper left corner."""
    return (
        (ox, oy),
        (ox + math.sqrt(3)*s/2, oy - s/2),
        (ox + math.sqrt(3)*s, oy),
        (ox + math.sqrt(3)*s, oy + s),
        (ox + math.sqrt(3)*s/2, oy + 3*s/2),
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

safe_log = lambda x: math.log(x) if x > 0 else 0


def make_random_rules(state_values: tuple):
    assert len(state_values) == 3
    neighbors_include_self = False
    rules = {
        (i, j - i, N_NEIGHBORS_MAX - j): state_values[random.randint(0, len(state_values) - 1)]
        for i in range(N_NEIGHBORS_MAX + 1)
        for j in range(i, N_NEIGHBORS_MAX + 1)
    }
    return rules, neighbors_include_self

def make_beehive_rules(state_values: tuple):
    neighbors_include_self = False
    beehive_matrix = [
        [0, 1, 2, 1, 2, 0, 0],
        [0, 2, 2, 2, 1, 1],
        [0, 0, 2, 2, 0],
        [0, 2, 2, 0],
        [0, 0, 2],
        [2, 0],
        [0]
    ]
    rules = {
        (N_NEIGHBORS_MAX - i - j, j, i): state_values[beehive_matrix[i][j]]
        for i in range(N_NEIGHBORS_MAX + 1)
        for j in range(0, N_NEIGHBORS_MAX + 1 - i)
    }
    return rules, neighbors_include_self

def make_spiral_rules(state_values: tuple):
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
        (N_NEIGHBORS_MAX + 1 - i - j, j, i): sprial_matrix[i][j]
        for i in range(N_NEIGHBORS_MAX + 2)
        for j in range(0, N_NEIGHBORS_MAX + 2 - i)
    }
    return rules, neighbors_include_self

RULES = {
    'random': make_random_rules,
    'beehive': make_beehive_rules,
    'spiral': make_spiral_rules
}


class HexCA3(Component):

    def __init__(
            self,
            num_rows: int,
            num_cols: int,
            rules: str,
            colormap: dict,
            color_bg: int,
            color_fg: int,
            side_length: float
        ):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.colormap = colormap
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.side_length = side_length

        self.line_plot_height = 50
        height = num_rows * 3 * side_length / 2 + + side_length + self.line_plot_height
        width = (num_cols + 1) * math.sqrt(3)*side_length + math.sqrt(3)*side_length/2
        self.ox, self.oy = math.sqrt(3) / 2 * self.side_length, self.side_length/2
        self.surface = pygame.Surface((width, height))
        super().__init__(width, height)

        self.state_values = (0, 1, 2)
        self.rules, self.neighbors_include_self = RULES[rules](self.state_values)
        self.num_hexes = num_rows * num_cols + int(num_rows/2)
        self.neighbors = get_neighbors(num_rows, num_cols)
        self.__initialize()

    def __initialize(self, rules: str = 'spiral'):
        self.rules, self.neighbors_include_self = RULES[rules](self.state_values)
        self.hex_states = [
            random.choices(self.state_values, weights=(10, 1, 1), k=1)[0]
            for _ in range(self.num_hexes)
        ]
        self.entropy_history = []

    def reinitialize(self):
        self.__initialize()

    def __draw_hexes(self):
        index = -1
        for i in range(self.num_rows):
            short_row = i % 2 == 0
            row_offset = (i % 2) * math.sqrt(3)*self.side_length/2
            for j in range(self.num_cols):
                x = self.ox + j * math.sqrt(3)*self.side_length - row_offset
                y = self.oy + i * 3*self.side_length/2
                hex_points = hex_point(x, y, self.side_length)
                index += 1
                fill = self.hex_states[index]
                width = 1 if fill == self.state_values[0] else 0
                pygame.draw.polygon(
                    self.surface,
                    pygame.Color(*self.colormap[self.hex_states[index]]),
                    hex_points,
                    width=width
                )

            # Odd rows have one more hex
            # This will never be the first row, it may be the last row
            if not short_row:
                x = self.ox + self.num_cols * math.sqrt(3)*self.side_length - row_offset
                y = self.oy + i * 3*self.side_length/2
                hex_points = hex_point(x, y, self.side_length)
                index += 1
                fill = self.hex_states[index]
                width = 1 if fill == self.state_values[0] else 0
                pygame.draw.polygon(
                    self.surface,
                    pygame.Color(*self.colormap[self.hex_states[index]]),
                    hex_points,
                    width=width
                )

    def get_surface(self):
        # update hexes
        new_hex_states = self.hex_states.copy()
        for i in range(self.num_hexes):
            counts = count_hex_states(
                i, self.hex_states,
                self.neighbors,
                self.state_values,
                self.neighbors_include_self
            )
            new_hex_states[i] = self.rules[tuple(counts[state] for state in self.state_values)]

        self.hex_states = new_hex_states
        total_counts = {state: 0 for state in self.state_values}
        for i in range(self.num_hexes):
            total_counts[self.hex_states[i]] += 1
        entropy = -sum([
            total_counts[state] * safe_log(total_counts[state] / self.num_hexes)
            for state in self.state_values
        ])
        self.entropy_history.append(entropy)
        if len(self.entropy_history) > 50:
            self.entropy_history = self.entropy_history[-50:]

        # draw everything
        self.surface.fill(pygame.Color(*self.color_bg))
        self.__draw_hexes()
        if len(self.entropy_history) > 2:
            plot = LinePlot(
                self.width - self.ox,
                50,
                list(range(len(self.entropy_history))),
                self.entropy_history,
                self.color_bg,
                self.color_fg,
                0, 0
            )
            self.surface.blit(plot.get_surface(), (self.ox, self.height - self.line_plot_height))

        # re-initialize if all states are the same
        if any([count==self.num_hexes for count in total_counts.values()]):
            self.__initialize()

        return self.surface