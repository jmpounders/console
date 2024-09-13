from datetime import datetime, timedelta
import zoneinfo as zi

import pygame
import numpy as np

from console.components.base import Component, Text


from datetime import datetime, timedelta
import zoneinfo as zi

import numpy as np


LAT, LONG = 32.038537, -81.09347
TIMEZONE = zi.ZoneInfo("US/Eastern")


def hour_float_to_datetime(year: int, month: int, day: int, hour: float) -> datetime:
    """Converts a float hour to a datetime object, e.g., 12.5 -> 12:30 PM."""
    hour_int = int(hour)
    minute_int = int((hour - hour_int) * 60)
    return datetime(year, month, day, hour_int, minute_int, tzinfo=TIMEZONE)


def get_soloar_parameters(time: datetime) -> tuple:
    """Get solar parameters for a given time.

    The solar parameters are:
    - Local solar time (hours)
    - Hour angle (degrees)
    - Declination (degrees)
    - Zenith angle (degrees)
    - Altitude angle (degrees)
    - Azimuth angle (degrees)
    - Sunrise (datetime)
    - Sunset (datetime)
    """
    utc_offset = time.utcoffset().total_seconds() / 3600
    days_since_boy = (time - datetime(time.year, 1, 1, tzinfo=TIMEZONE)).days

    # Ref: https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time
    # zenith angle is the angle between the sun and the vertical direction
    # altitude angle is the angle between the sun and the horizontal direction
    # azimuth angle is the angle between the sun and the north direction
    locat_std_time_meridian = 15 * utc_offset
    B = np.deg2rad(360/365 * (days_since_boy - 81))
    eq_of_time = 9.87*np.sin(2*B) - 7.53*np.cos(B) - 1.5*np.sin(B)
    time_correction_factor = 4*(LONG - locat_std_time_meridian) + eq_of_time
    local_solar_time_hrs = time.hour + (time.minute + time_correction_factor) / 60
    hour_angle = 15*(local_solar_time_hrs - 12)
    declination_deg = -23.45*np.cos(np.deg2rad(360/365*(days_since_boy+10)))

    declination_rad = np.deg2rad(declination_deg)
    lat_rad = np.deg2rad(LAT)
    hra_rad = np.deg2rad(hour_angle)

    cos_zenith_angle = np.sin(lat_rad)*np.sin(declination_rad) + np.cos(np.deg2rad(LAT))*np.cos(np.deg2rad(declination_deg))*np.cos(hra_rad)
    zenith_angle_deg = np.rad2deg(np.arccos(cos_zenith_angle))
    altitude_angle_deg = 90 - zenith_angle_deg
    azimuth_angle_deg = np.rad2deg(np.arccos((np.sin(declination_rad)*np.cos(lat_rad) - np.cos(declination_rad)*np.sin(lat_rad)*np.cos(hra_rad)) / np.cos(np.deg2rad(altitude_angle_deg))))
    azimuth_angle_deg = 360 - azimuth_angle_deg if hour_angle > 0 else azimuth_angle_deg

    sunrise = hour_float_to_datetime(
        time.year, time.month, time.day,
        12 - 1/15*np.rad2deg(np.arccos(-np.tan(lat_rad)*np.tan(declination_rad))) - time_correction_factor/60
    )
    sunset = hour_float_to_datetime(
        time.year, time.month, time.day,
        12 + 1/15*np.rad2deg(np.arccos(-np.tan(lat_rad)*np.tan(declination_rad))) - time_correction_factor/60
    )

    return (
        local_solar_time_hrs,
        hour_angle,
        declination_deg,
        zenith_angle_deg,
        altitude_angle_deg,
        azimuth_angle_deg,
        sunrise,
        sunset
    )


def get_sun_path(today: datetime) -> list:
    """Get the sun path for a given day.

    The sun path is a list of tuples, each containing:
    - Time (datetime)
    - Altitude angle (degrees)
    - Azimuth angle (degrees)
    """
    noon_today = datetime(today.year, today.month, today.day, 12, 0, tzinfo=TIMEZONE)
    (
        _, _, _, _, _, _,
        sunrise,
        sunset
    ) = get_soloar_parameters(noon_today)

    day_length = sunset - sunrise
    day_length_hrs = day_length.total_seconds() / 3600
    time_range = [sunrise + timedelta(hours=i) for i in np.linspace(0, day_length_hrs, 24)]
    solar_params_today = []
    for ti in time_range:
        (
            _, _, _, _,
            altitude_angle_deg,
            azimuth_angle_deg, _, _
        ) = get_soloar_parameters(ti)
        solar_params_today.append((ti, altitude_angle_deg, azimuth_angle_deg))

    return solar_params_today


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