from abc import ABC, abstractmethod

import pygame


class Component(ABC):

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def get_surface(self):
        pass


class Container(Component):
    """This class is a bordered container for other components.

    Children components will be stacked horizontally with padding."""

    def __init__(
            self,
            width: int,
            height: int,
            children: list,
            border_thickness: int,
            border_radius: int,
            border_margin: int,
            border_color: int,
            background_color: int,
            child_padding: int,
        ):
        super().__init__(width, height)
        self.border_margin = border_margin
        self.child_padding = child_padding
        self.children = children

        self.surface = pygame.Surface((width, height))
        self.surface.fill(pygame.Color(background_color))
        pygame.draw.rect(
            self.surface,
            pygame.Color(border_color),
            (border_margin, border_margin, width-border_margin, height-border_margin),
            border_radius=border_radius,
            width=border_thickness
        )

    def get_surface(self):
        place_x, place_y = self.border_margin + self.child_padding, self.border_margin + self.child_padding
        for child in self.children:
            self.surface.blit(child.get_surface(), (place_x, place_y))
            place_x += child.width + self.child_padding

        return self.surface


class VStack(Component):
    """This class is a vertical stack of components.

    Padding is added between each child component, but there is no padding
    added to the top, bottom, left or right of the stack."""

    def __init__(
            self,
            children: list,
            background_color: int,
            padding: int,
        ):
        width = max([child.width for child in children])
        height = sum([child.height for child in children]) + padding*(len(children)-1)
        super().__init__(width, height)

        self.padding = padding
        self.children = children

        self.surface = pygame.Surface((width, height))
        self.surface.fill(pygame.Color(background_color))

    def get_surface(self):
        place_x, place_y = 0, 0
        for child in self.children:
            self.surface.blit(child.get_surface(), (place_x, place_y))
            place_y += child.height + self.padding

        return self.surface


class Text(Component):
    """A simple text component with no padding."""

    def __init__(
            self,
            text: str,
            font_name: str,
            font_size: int,
            font_color: int,
            font_background: int,
        ):
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_color = pygame.Color(font_color)
        self.font_background = pygame.Color(font_background)

        self.surface = self.font.render(self.text, True, self.font_color, self.font_background)

        width, height = self.surface.get_size()
        super().__init__(width, height)

    def get_surface(self):
        return self.surface


class LinePlot(Component):
    """Line plot.  Padding is added all around."""

    def __init__(
            self,
            width: int,
            height: int,
            x_data: list[float],
            y_data: list[float],
            bg_color: int,
            fg_color: int,
            x_padding: int,
            y_padding: int,
            x_max: float | None = None,
        ):
        super().__init__(width, height)
        self.x_data = x_data
        self.y_data = y_data
        self.fg_color = fg_color

        self.surface = pygame.Surface((width, height))
        self.surface.fill(pygame.Color(bg_color))

        if len(x_data) == 0 or len(y_data) == 0:
            return

        try:
            self.x0, self.y0 = x_padding, y_padding
            self.x1, self.y1 = width-x_padding, height-y_padding
            self.x_max, self.y_max = x_max if x_max is not None else max(x_data), max(y_data)
            self.x_min, self.y_min = min(x_data), min(y_data)

            y_mean = sum(y_data) / len(y_data)
            y_mean_scaled = self.__scale_y(y_mean)

            self.__draw_axes(y_mean_scaled)
            self.__draw_data(x_data, y_data)
        except Exception as e:
            pass

    def __scale_x(self, x: float):
        if self.x_max == self.x_min:
            return self.x0
        return int((x - self.x_min) / (self.x_max - self.x_min) * (self.x1 - self.x0) + self.x0)

    def __scale_y(self, y: float):
        if self.y_max == self.y_min:
            return self.y0
        return int(-(y - self.y_min) / (self.y_max - self.y_min) * (self.y1 - self.y0) + self.y1)

    def __draw_axes(self, y_location: float):
        pygame.draw.line(
            self.surface,
            pygame.Color(self.fg_color),
            (self.x0, self.y0),
            (self.x0, self.y1),
            1
        )
        pygame.draw.line(
            self.surface,
            pygame.Color(self.fg_color),
            (self.x0, y_location),
            (self.x1, y_location),
            1
        )

    def __draw_data(self, x_data: list[float], y_data: list[float]):
        px0, py0 = self.__scale_x(x_data[0]), self.__scale_y(y_data[0])
        for xi, yi in zip(x_data[1:], y_data[1:]):
            px = self.__scale_x(xi)
            py = self.__scale_y(yi)
            pygame.draw.line(self.surface, pygame.Color(self.fg_color), (px0, py0), (px, py), 1)
            px0, py0 = px, py

    def get_surface(self):
        return self.surface


class Image(Component):

    def __init__(self, image_surface: pygame.Surface):
        self.image_surface = image_surface
        width, height = image_surface.get_size()
        super().__init__(width, height)

    @classmethod
    def from_file(cls, filename: str):
        image_surface = pygame.image.load(filename)
        return cls(image_surface)

    def get_surface(self):
        return self.image_surface


class Meter(Component):
    """A simple meter component with no padding.

    The meter is filled from the top down.
    """

    def __init__(
            self,
            width: int,
            height: int,
            value: float,
            max_value: float,
            min_value: float,
            fg_color: int,
            bg_color: int,
        ):
        super().__init__(width, height)

        self.surface = pygame.Surface((width, height))
        self.surface.fill(pygame.Color(bg_color))

        value_height = int(height * (value - min_value) / (max_value - min_value))
        pygame.draw.rect(
            self.surface,
            pygame.Color(fg_color),
            (0, 0, width, value_height)
        )
        pygame.draw.rect(
            self.surface,
            pygame.Color(fg_color),
            (0, value_height, width, height-value_height),
            width=2
        )

    def get_surface(self):
        return self.surface