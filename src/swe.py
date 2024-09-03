# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
from ctypes import (
    CDLL,
    POINTER,
    byref,
    c_char,
    c_char_p,
    c_double,
    c_int,
    c_void_p,
    create_string_buffer,
)

from src import *
from src.constants import HOUR_FRACTION_OF_A_DAY, PLANETS, PLATFORM
from src.utils.format_utils import (
    add_360_if_negative,
    arccotangent,
    cotangent,
    north_azimuth,
    southern_azimuth,
)

dll = CDLL(DLL_PATH)


if PLATFORM == 'Win32GUI':
    swe_set_ephe = getattr(dll, '_swe_set_ephe_path@4')
elif PLATFORM == 'linux':
    swe_set_ephe = getattr(dll, 'swe_set_ephe_path')
elif PLATFORM == 'darwin':
    swe_set_ephe = getattr(dll, 'swe_set_ephe_path')
swe_set_ephe.argtypes = [c_char_p]
swe_set_ephe.restype = c_void_p
swe_set_ephe(EPHE_PATH.encode())


def _get_handle_for_platform(dll: CDLL, windows_string: str):
    if PLATFORM == 'Win32GUI':
        handle = windows_string
    elif PLATFORM == 'linux':
        [handle, _] = windows_string.split('@')
        handle = handle.strip('_')
    elif PLATFORM == 'darwin':
        [handle, _] = windows_string.split('@')
        handle = handle.strip('_')

    return getattr(dll, handle)


swe_julday = _get_handle_for_platform(dll, '_swe_julday@24')
swe_julday.argtypes = [c_int, c_int, c_int, c_double, c_int]
swe_julday.restype = c_double

swe_revjul = _get_handle_for_platform(dll, '_swe_revjul@28')
swe_revjul.argtypes = [
    c_double,
    c_int,
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_double),
]
swe_revjul.restype = c_void_p

swe_calc_ut = _get_handle_for_platform(dll, '_swe_calc_ut@24')
swe_calc_ut.argtypes = [
    c_double,
    c_int,
    c_int,
    POINTER(c_double * 6),
    POINTER(c_char * 256),
]

swe_get_ayanamsa_ex_ut = _get_handle_for_platform(
    dll, '_swe_get_ayanamsa_ex_ut@20'
)
swe_get_ayanamsa_ex_ut.argtypes = [
    c_double,
    c_int,
    POINTER(c_double),
    POINTER(c_char * 256),
]

swe_houses_ex = _get_handle_for_platform(dll, '_swe_houses_ex@40')
swe_houses_ex.argtypes = [
    c_double,
    c_int,
    c_double,
    c_double,
    c_int,
    POINTER(c_double * 13),
    POINTER(c_double * 10),
]

swe_house_pos = _get_handle_for_platform(dll, '_swe_house_pos@36')
swe_house_pos.argtypes = [
    c_double,
    c_double,
    c_double,
    c_int,
    POINTER(c_double * 2),
    POINTER(c_char * 256),
]
swe_house_pos.restype = c_double

swe_azalt = _get_handle_for_platform(dll, '_swe_azalt@40')
swe_azalt.argtypes = [
    c_double,
    c_int,
    POINTER(c_double * 3),
    c_double,
    c_double,
    POINTER(c_double * 3),
    POINTER(c_double * 3),
]

swe_lat_to_lmt = _get_handle_for_platform(dll, '_swe_lat_to_lmt@24')
swe_lat_to_lmt.argtypes = [
    c_double,
    c_double,
    POINTER(c_double),
    POINTER(c_char * 256),
]

swe_solcross_ut = _get_handle_for_platform(dll, '_swe_solcross_ut@24')
swe_solcross_ut.argtypes = [c_double, c_double, c_int, POINTER(c_char * 256)]
swe_solcross_ut.restype = c_double

swe_mooncross_ut = _get_handle_for_platform(dll, '_swe_mooncross_ut@24')
swe_mooncross_ut.argtypes = [c_double, c_double, c_int, POINTER(c_char * 256)]
swe_mooncross_ut.restype = c_double.restype = c_double

swe_cotrans = _get_handle_for_platform(dll, '_swe_cotrans@16')
swe_cotrans.argtypes = [POINTER(c_double * 3), POINTER(c_double * 3), c_double]


def julday(year, month, day, hour, isgreg) -> float:
    return swe_julday(year, month, day, hour, isgreg)


def calc_planet(universal_time: float, planet: int):
    """Calculates the position of a given planet.

    Returns:
        List[float]: [longitude, latitude, speed, right ascension, declination]"""
    err = create_string_buffer(256)
    result_array = (c_double * 6)()
    sidereal_positions_and_speed = 64 * 1024 + 256
    swe_calc_ut(
        universal_time,
        planet,
        sidereal_positions_and_speed,
        byref(result_array),
        byref(err),
    )
    result = []
    for i in range(len(result_array)):
        if i in [0, 1, 3]:
            result.append(result_array[i])

    # The flag here indicates equatorial positions, and speed
    equatorial_positions_and_speed = 2048 + 256
    swe_calc_ut(
        universal_time,
        planet,
        equatorial_positions_and_speed,
        byref(result_array),
        byref(err),
    )
    for i in range(len(result_array)):
        if i in [0, 1]:
            result.append(result_array[i])

    return result


def calc_obliquity(ut):
    err = create_string_buffer(256)
    pos = (c_double * 6)()
    swe_calc_ut(ut, -1, 0, byref(pos), byref(err))
    result = []
    for p in pos:
        result.append(p)
    return result[0]


def calc_ayan(ut):
    err = create_string_buffer(256)
    pos = c_double()
    swe_get_ayanamsa_ex_ut(ut, 0, byref(pos), byref(err))
    return pos.value


def calc_cusps(ut, lat, long):
    cusps_return_array = (c_double * 13)()
    angles_return_array = (c_double * 10)()
    swe_houses_ex(
        ut,
        64 * 1024,
        lat,
        long,
        ord('C'),
        byref(cusps_return_array),
        byref(angles_return_array),
    )
    # The angles kept are RAMC, Vertex, Equatorial Ascendant
    return [cusps_return_array[:], angles_return_array[2:5]]


def calc_house_pos(ramc, geo_latitude, obliquity, tlong, elat):
    """Calculates the Campanus house position.

    Returns:
        float: Campanus house position 1-12"""
    err = create_string_buffer(256)
    planet_ecliptic_pos = (c_double * 2)(tlong, elat)
    campanus_house = ord('C')
    return (
        swe_house_pos(
            ramc,
            geo_latitude,
            obliquity,
            campanus_house,
            planet_ecliptic_pos,
            err,
        )
        * 30
        - 30
    )


def calc_azimuth(
    universal_time: float,
    geo_longitude: float,
    geo_latitude: float,
    tlong,
    elat,
):
    """Calculates the azimuth and altitude of a given planet.

    Returns:
        List[float]: [azimuth, true altitude]"""
    geo = (c_double * 3)(geo_longitude, geo_latitude, 0)
    pl = (c_double * 3)(tlong, elat, 0)
    az = (c_double * 3)()
    swe_azalt(universal_time, 0, byref(geo), 0, 0, byref(pl), byref(az))
    aa = []
    for i in range(len(az)):
        if i in [0, 1]:
            aa.append(az[i])
    aa[0] = (aa[0] + 180) % 360
    return aa


def calc_lat_to_lmt(lat, long):
    err = create_string_buffer(256)
    lat = c_double(lat)
    long = c_double(long)
    lmt = c_double()
    swe_lat_to_lmt(lat, long, byref(lmt), byref(err))
    return lmt.value


def revjul(ut, isgreg):
    year = c_int()
    month = c_int()
    day = c_int()
    time = c_double()
    swe_revjul(ut, isgreg, byref(year), byref(month), byref(day), byref(time))
    return (year.value, month.value, day.value, time.value)


def calc_sun_crossing(pos, ut):
    err = create_string_buffer(256)
    cross = swe_solcross_ut(pos, ut, 64 * 1024, byref(err))
    s = calc_planet(cross, 0)
    sun = s[0]
    if sun > pos + 180:
        sun -= 360
    if sun < pos:
        # interpolation given the speed of the sun
        cross += (pos - sun + 0.5 / 86400) / s[2]
    return cross


def calc_moon_crossing(pos, ut):
    err = create_string_buffer(256)
    cross = swe_mooncross_ut(pos, ut, 64 * 1024, byref(err))
    m = calc_planet(cross, 1)
    moon = m[0]
    if moon > pos + 180:
        moon -= 360
    if moon < pos:
        # interpolation given the speed of the moon
        cross += (pos - moon + 0.5 / 86400) / m[2]
    return cross


def cotrans(ecliptic, oe):
    ec = (c_double * 3)(*ecliptic)
    eq = (c_double * 3)()
    swe_cotrans(ec, byref(eq), -oe)
    equator = []
    for i in range(2):
        equator.append(eq[i])
    return equator


def calc_meridian_longitude(azimuth: float, altitude: float):
    ratio = cotangent(math.radians(altitude)) / math.cos(math.radians(azimuth))
    meridian_longitude = math.degrees(arccotangent(ratio))
    meridian_longitude = add_360_if_negative(meridian_longitude)

    # We have a few cases here: nothern/southern ML, above/below horizon.
    # ML 0-90 should mean south-above
    # ML 90-180 should mean north-above
    # ML 180-270 should mean north-below
    # ML 270-360 should mean south-below

    # This is separate from northern/southern AZIMUTH though:
    # Southern azimuth is 90-270; Northern azimuth is 270-90.

    # Correct above/below errors
    if altitude >= 0 and meridian_longitude > 270:
        meridian_longitude = add_360_if_negative(180 - meridian_longitude)
    elif altitude < 0 and meridian_longitude < 90:
        meridian_longitude = add_360_if_negative(180 - meridian_longitude)

    # Correct northern/southern errors
    elif (
        meridian_longitude > 270 or meridian_longitude < 90
    ) and north_azimuth(azimuth):
        meridian_longitude = add_360_if_negative(180 - meridian_longitude)
    elif (90 < meridian_longitude < 270) and southern_azimuth(azimuth):
        meridian_longitude = add_360_if_negative(180 - meridian_longitude)

    # Re-check above/below errors, with pure 180° correction, not a flip
    if altitude >= 0 and meridian_longitude > 180:
        meridian_longitude = meridian_longitude - 180
    elif altitude < 0 and meridian_longitude < 180:
        meridian_longitude = add_360_if_negative(meridian_longitude - 180)

    return meridian_longitude


def is_planet_stationary(long_name: str, julian_day: float) -> bool:
    stats = PLANETS[long_name]

    # Planet cannot be stationary
    if stats['stationary_period_hours'] < 0:
        return False

    maximum_time_difference = (
        stats['stationary_period_hours'] * HOUR_FRACTION_OF_A_DAY
    ) / 2

    base_direction = calc_planet(julian_day, stats['number'])[2] > 0

    beginning_time = julian_day - maximum_time_difference
    beginning_period_direction = (
        calc_planet(beginning_time, stats['number'])[2] > 0
    )

    # There was a station at some point
    if base_direction != beginning_period_direction:
        return True

    ending_time = julian_day + maximum_time_difference
    ending_period_direction = calc_planet(ending_time, stats['number'])[2] > 0

    return base_direction != ending_period_direction
