from typing import Any
from datetime import datetime, timedelta
import zoneinfo as zi
from functools import partial

import pygame
import numpy as np

from console.components.base import Component, Container, Text, VStack, LinePlot
from console.computation.solar import get_soloar_parameters, get_sun_path, TIMEZONE


class TextInBorder(Component):

    def __init__(
            self,
            data: list[str],
            text_params: dict[str, Any],
            container_params: dict[str, Any]
        ):

        data_fields = [
            Text(item, **text_params)
            for item in data
        ]

        vstack = VStack(data_fields, container_params['background_color'], 10)

        pad_amount = 2 * (container_params['child_padding'] + container_params['border_margin'])
        width, height = vstack.width + pad_amount, vstack.height + pad_amount
        self.component = Container(width, height, [vstack], **container_params)
        super().__init__(self.component.width, self.component.height)

    def get_surface(self):
        return self.component.get_surface()


class AnnotatedLinePlots(Component):

    def __init__(
            self,
            labels: list[str],
            x_data: list[float],
            y_datas: list[list[float]],
            text_params: dict[str, Any],
            container_params: dict[str, Any]
        ):

        plots = []
        plot_container_params = {
            'border_thickness': 0,
            'border_radius': 0,
            'border_margin': 0,
            'border_color': container_params['background_color'],
            'background_color': container_params['background_color'],
            'child_padding': 0,
        }
        small_text_params = {key: value for key, value in text_params.items()}
        small_text_params['font_size'] = text_params['font_size']//2
        for label, y_data in zip(labels, y_datas):
            label_comp = Text(label, **text_params)

            try:
                annotations = [min(y_data), sum(y_data)/len(y_data), max(y_data)]
            except:
                annotations = [0, 0, 0]
            # values = VStack(
            #     [Text(f'{y:.2f}', **text_params) for y in annotations],
            #     text_params['font_background'],
            #     padding=2
            # )
            values_comp = Text(
                f'{"/".join([f"{y:.0f}" for y in annotations])}',
                **small_text_params
            )

            height = max([label_comp.height, values_comp.height])

            plot = LinePlot(
                300,
                height,
                x_data,
                y_data,
                container_params['background_color'],
                container_params['border_color'],
                x_padding = 5,
                y_padding = 2
            )

            # height += 2*container_params['child_padding']
            width = label_comp.width + values_comp.width + plot.width
            # width += 2*container_params['child_padding']

            plots.append(Container(
                width,
                height,
                [label_comp, plot, values_comp],
                **plot_container_params
            ))

        self.plots_component = VStack(plots, container_params['background_color'], 5)

        height = self.plots_component.height + 2*container_params['border_margin'] + 2*container_params['child_padding']
        width = self.plots_component.width + 2*container_params['border_margin'] + 2*container_params['child_padding']
        self.component = Container(width, height, [self.plots_component], **container_params)
        super().__init__(width, height)

    def get_surface(self):
        return self.component.get_surface()


class SunPath(Component):
    """Sun path plot."""

    def __init__(
            self,
            width: int,
            color_fg: int,
            color_bg: int,
            color_highlight: int,
            border_thickness: int,
            border_radius: int,
        ):
        super().__init__(width, width)
        self.width = width
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_highlight = color_highlight
        self.border_thickness = border_thickness
        self.border_radius = border_radius

        self.text_params = {
            'font_name': '3270medium',
            'font_size': int(width/20),
            'font_color': self.color_fg,
            'font_background': self.color_bg,
        }

        self.surface = pygame.Surface((width, width))
        self.surface.fill(pygame.Color(color_bg))

        margin = 50
        self.ox, self.oy = width//2, width//2
        self.max_radius = min(self.ox, self.oy) - margin

        self.line_width = 2
        self.base_plot = self.__draw_base_plot()

    def polar_to_screen_coords(self, r, theta):
        """Convert polar coordinates to screen coordinates."""
        y = self.ox + (90-r)/90*self.max_radius * np.cos(np.deg2rad(theta))
        x = self.oy - (90-r)/90*self.max_radius * np.sin(np.deg2rad(theta))
        return x, y

    def __draw_base_plot(self) -> pygame.Surface:
        """Draw the base sun path plot."""
        now = datetime.now(TIMEZONE)

        winter_solstice = datetime(now.year, 12, 21, tzinfo=TIMEZONE)
        solar_params_winter_solstice = get_sun_path(winter_solstice)

        summer_solstice = datetime(now.year, 6, 21, tzinfo=TIMEZONE)
        solar_params_summer_solstice = get_sun_path(summer_solstice)

        base_plot = pygame.Surface((self.width, self.height))
        base_plot.fill(pygame.Color(self.color_bg))

        tick_label_params = {k: v for k, v in self.text_params.items()}
        tick_label_params['font_size'] = int(self.width/35)
        radial_ticks = list(range(0, 90, 10))
        for angle in radial_ticks:
            pygame.draw.circle(
                base_plot,
                pygame.Color(self.color_fg),
                (self.ox, self.oy),
                (90-angle)/90*self.max_radius, width=1
            )
        radial_tick_marks = list(range(10, 90, 20))
        for angle in radial_tick_marks:
            tick_mark = Text(f'{angle}°', **tick_label_params)
            base_plot.blit(
                tick_mark.get_surface(),
                (
                    self.ox + 1,
                    self.oy + (90-angle)/90*self.max_radius + 1)
            )

        polar_ticks = list(range(0, 360, 30))
        for angle in polar_ticks:
            x1 = self.ox + self.max_radius * np.cos(np.deg2rad(angle))
            y1 = self.oy - self.max_radius * np.sin(np.deg2rad(angle))
            pygame.draw.line(
                base_plot,
                pygame.Color(self.color_fg),
                (self.ox, self.oy),
                (x1, y1),
                width=1
            )
        polar_tick_marks = list(range(30, 360, 30))
        for angle in polar_tick_marks:
            if angle % 90 == 0:
                continue
            tick_mark = Text(f'{angle}°', **tick_label_params)
            base_plot.blit(
                tick_mark.get_surface(),
                (
                    self.ox + self.max_radius * np.cos(np.deg2rad(angle+90)) - tick_mark.width//2,
                    self.oy + self.max_radius * np.sin(np.deg2rad(angle+90)) - tick_mark.height//2
                )
            )

        _, args1, args2 = zip(*solar_params_winter_solstice)
        pygame.draw.lines(
            base_plot,
            pygame.Color(self.color_fg),
            False,
            tuple(map(self.polar_to_screen_coords, args1, args2)),
            width=self.line_width
        )

        _, args1, args2 = zip(*solar_params_summer_solstice)
        pygame.draw.lines(
            base_plot,
            pygame.Color(self.color_fg),
            False,
            tuple(map(self.polar_to_screen_coords, args1, args2)),
            width=self.line_width
        )

        north_label = Text('N', **self.text_params)
        base_plot.blit(
            north_label.get_surface(),
            (self.ox - north_label.width//2, self.oy + self.max_radius + 10)
        )

        south_label = Text('S', **self.text_params)
        base_plot.blit(
            south_label.get_surface(),
            (self.ox - south_label.width//2, self.oy - self.max_radius - 10 - south_label.height)
        )

        west_label = Text('W', **self.text_params)
        base_plot.blit(
            west_label.get_surface(),
            (self.ox + self.max_radius + 10, self.oy - west_label.height//2)
        )

        east_label = Text('E', **self.text_params)
        base_plot.blit(
            east_label.get_surface(),
            (self.ox - self.max_radius - 10 - east_label.width, self.oy - east_label.height//2)
        )



        pygame.draw.rect(
            base_plot,
            pygame.Color(self.color_fg),
            (0, 0, self.width, self.width),
            width=self.border_thickness,
            border_radius=self.border_radius
        )

        return base_plot

    def get_surface(self):
        """Draw the sun path plot for today with the current position."""
        now = datetime.now(TIMEZONE)
        solar_params_current = get_soloar_parameters(now)
        sunrise, sunset = solar_params_current[6], solar_params_current[7]
        altitude_angle_current, azimuth_angle_current = solar_params_current[4], solar_params_current[5]
        solar_params_today = get_sun_path(now)

        self.surface.blit(self.base_plot, (0, 0))

        if now > sunrise and now < sunset:
            x, y = self.polar_to_screen_coords(altitude_angle_current, azimuth_angle_current)
            pygame.draw.circle(
                self.surface,
                pygame.Color(self.color_highlight),
                (x, y),
                self.line_width*3
            )

        _, args1, args2 = zip(*solar_params_today)
        pygame.draw.lines(
            self.surface,
            pygame.Color(self.color_highlight),
            False,
            tuple(map(self.polar_to_screen_coords, args1, args2)),
            width=self.line_width
        )

        sunrise = Text(sunrise.strftime("%H:%M"), **self.text_params)
        self.surface.blit(
            sunrise.get_surface(),
            (10, self.width - sunrise.height - 10)
        )
        sunset = Text(sunset.strftime("%H:%M"), **self.text_params)
        self.surface.blit(
            sunset.get_surface(),
            (self.width - sunset.width - 10, self.width - sunset.height - 10)
        )

        altitude = Text(f'{altitude_angle_current:.0f}°', **self.text_params)
        self.surface.blit(
            altitude.get_surface(),
            (10, 10)
        )
        azimuth = Text(f'{azimuth_angle_current:.0f}°', **self.text_params)
        self.surface.blit(
            azimuth.get_surface(),
            (self.width - azimuth.width - 10, 10)
        )
        return self.surface