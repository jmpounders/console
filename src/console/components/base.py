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