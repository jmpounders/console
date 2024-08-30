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