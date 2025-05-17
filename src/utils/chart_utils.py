# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
import os
from io import TextIOWrapper
from typing import Iterator

from src import *
from src import constants, swe
from src.models.angles import (
    ForegroundAngles,
    MinorAngles,
    NonForegroundAngles,
)
from src.models.options import AngularityModel, NodeTypes, Options
from src.user_interfaces.widgets import *
from src.utils.format_utils import to360

SIGNS_SHORT = [
    'Ar',
    'Ta',
    'Ge',
    'Cn',
    'Le',
    'Vi',
    'Li',
    'Sc',
    'Sg',
    'Cp',
    'Aq',
    'Pi',
]
PLANET_NAMES = [
    'Moon',
    'Sun',
    'Mercury',
    'Venus',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Pluto',
    'Eris',
    'Sedna',
    'Mean Node',
    'True Node',
    'Eastpoint',
    'Vertex',
]
PLANET_NAMES_SHORT = [
    'Mo',
    'Su',
    'Me',
    'Ve',
    'Ma',
    'Ju',
    'Sa',
    'Ur',
    'Ne',
    'Pl',
    'Er',
    'Se',
    'No',
    'No',
    'Ep',
    'Vx',
]


def convert_long_name_to_short(name: str) -> str:
    return constants.PLANETS[name]['short_name']


def convert_short_name_to_long(name: str) -> str:
    for planet in constants.PLANETS:
        if constants.PLANETS[planet]['short_name'] == name:
            return planet


DEFAULT_ECLIPTICAL_ORBS = {
    '0': [3.0, 7.0, 10.0],
    '180': [3.0, 7.0, 10.0],
    '90': [3.0, 6.0, 7.5],
    '45': [1.0, 2.0, 0],
    '120': [3.0, 6.0, 7.5],
    '60': [3.0, 6.0, 7.5],
    '30': [0, 0, 0],
}
DEFAULT_MUNDANE_ORBS = {
    '0': [3.0, 0, 0],
    '180': [3.0, 0, 0],
    '90': [3.0, 0, 0],
    '45': [0, 0, 0],
}

RULERSHIPS = {
    'Ar': ['Su', 'Pl'],
    'Ta': ['Mo', 'Ve'],
    'Ge': ['Me'],
    'Cn': ['Mo', 'Ju'],
    'Le': ['Su'],
    'Vi': ['Me'],
    'Li': ['Ve', 'Sa'],
    'Sc': ['Ma'],
    'Sg': ['Ju'],
    'Cp': ['Ma', 'Sa'],
    'Aq': ['Ur'],
    'Pi': ['Ve', 'Ne'],
}

POS_SIGN = {
    'Mo': ['Cn', 'Ta'],
    'Su': ['Le', 'Ar'],
    'Me': ['Ge', 'Vi'],
    'Ve': ['Ta', 'Li', 'Pi'],
    'Ma': ['Sc', 'Cp'],
    'Ju': ['Sg', 'Cn'],
    'Sa': ['Cp', 'Li'],
    'Ur': ['Aq'],
    'Ne': ['Pi'],
    'Pl': ['Ar'],
    'Er': [],
    'Se': [],
    'No': [],
    'MN': [],
    'TN': [],
    'Ch': [],
    'Ce': [],
    'Pa': [],
    'Jn': [],
    'Vs': [],
    'Or': [],
    'Ha': [],
    'Mk': [],
    'Go': [],
    'Qu': [],
    'Sl': [],
}

NEG_SIGN = {
    'Mo': ['Cp', 'Sc'],
    'Su': ['Aq', 'Li'],
    'Me': ['Sg', 'Pi'],
    'Ve': ['Sc', 'Ar', 'Vi'],
    'Ma': ['Ta', 'Cn'],
    'Ju': ['Ge', 'Cp'],
    'Sa': ['Cn', 'Ar'],
    'Ur': ['Le'],
    'Ne': ['Vi'],
    'Pl': ['Li'],
    'Er': [],
    'Se': [],
    'No': [],
    'MN': [],
    'TN': [],
    'Ch': [],
    'Ce': [],
    'Pa': [],
    'Jn': [],
    'Vs': [],
    'Or': [],
    'Ha': [],
    'Mk': [],
    'Go': [],
    'Qu': [],
    'Sl': [],
}

DS = '\N{DEGREE SIGN}'

DQ = '"'
SQ = "'"


def major_angularity_curve_cadent_background(orb: float):
    if orb <= 10:
        orb *= 6
    elif orb > 10 and orb <= 40:
        orb = 2 * orb + 40
    elif orb > 40 and orb <= 60:
        orb *= 3
    else:
        orb = 6 * orb - 180

    return _major_angle_angularity_strength_percent(orb)


def major_angularity_curve_midquadrant_background(orb: float):
    if orb > 45:
        orb = 90 - orb
    if orb <= 10:
        orb *= 6
    elif orb > 10 and orb <= 35:
        orb = 2.4 * orb + 36
    else:
        orb = 6 * orb - 90

    return _major_angle_angularity_strength_percent(orb)


def _major_angle_angularity_strength_percent(orb: float) -> float:
    # Normalize the -1 to +1 range to a percentage
    raw = math.cos(math.radians(orb))

    # Convert from -1 to +1 to 0 to +2
    raw = raw + 1

    # Reduce to 0 to +1
    raw /= 2

    # Convert to percentage
    return raw * 100


def major_angularity_curve_eureka_formula(orb: float):
    initial_angularity = math.cos(math.radians(orb * 4))
    # Reduce the weight - this essentially is a square of the calculated score
    faded_angularity = initial_angularity * ((initial_angularity + 1) / 2)
    # Same curve as angularity, but shifted 60 degrees
    cadency_strength = -1 * math.cos(math.radians(4 * (orb - 60)))
    # Reduce the weight of this term as before
    faded_cadency_strength = cadency_strength * (
        1 - ((cadency_strength + 1) / 2)
    )

    # This is a curve that moves between -1.125 and +1.125
    penultimate_score = faded_angularity + faded_cadency_strength
    # Convert to -1 to +1
    penultimate_score /= 1.125

    # Convert to 0 to +1
    raw_decimal = (penultimate_score + 1) / 2
    return raw_decimal * 100


def minor_angularity_curve(orb_degrees: float, options: Options):
    max_orb = calc_class_3_orb(options.angularity.minor_angles)
    curve_multiplier = 360.0 / (max_orb * 4)

    # Regular cosine curve
    raw = math.cos(math.radians(orb_degrees * curve_multiplier))

    # Convert from -1 to +1 to 0 to +2
    raw += 1
    # Spread this curve across 50 percentage points
    raw *= 25
    # Finally, add 50 get a percentage
    raw += 50

    return raw


def calc_class_3_orb(orbs: list[float]) -> float:
    if orbs[2] is not None and orbs[2] > 0:
        return float(orbs[2])

    if orbs[1] is not None and orbs[1] > 0:
        return float(orbs[1]) * 1.5

    return float(orbs[0]) * 2.5


def inrange(
    value: float,
    center: float,
    orb: float,
    use_rem: bool = False,
    circle_division: float | None = None,
) -> bool:
    if not use_rem:
        return value >= center - orb and value <= center + orb

    if circle_division is not None:
        center = 360 / circle_division

    remainder_value = value % center
    return remainder_value <= orb or remainder_value >= center - orb


def in_harmonic_range(
    value: float, orb: float, harmonic: float
) -> tuple[bool, float]:
    harmonic_degree_width = 360 / harmonic

    remainder_value = value % harmonic_degree_width

    offset_from_exact = min(
        remainder_value, harmonic_degree_width - remainder_value
    )

    return (offset_from_exact <= orb, offset_from_exact)


def zod_min(value):
    value %= 360
    deg = int(value)
    minute = round((value - deg) * 60)
    d = 0
    s = 0
    if minute == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        minute = 0
        deg += 1
    return f'{(deg % 30) or d:2d}{SIGNS_SHORT[(deg // 30) + s]}{minute:2d}'


def zod_sec(value):
    value %= 360
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    d = 0
    s = 0
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        minute = 0
        deg += 1
    return f'{(deg % 30) or d:2d}{SIGNS_SHORT[deg // 30 + s]}{minute:2d}\'{sec:2d}"'


def center_align(value, width=33):
    if len(value) > width:
        value = value[0:width]
    left = (width - len(value)) // 2
    left = ' ' * left
    right = (width + 1 - len(value)) // 2
    right = ' ' * right
    return left + value + right


def left_align(value, width):
    if len(value) > width:
        value = value[0:width]
    return value + ' ' * (width - len(value))


def right_align(value, width):
    if len(value) > width:
        value = value[0:width]
    return ' ' * (width - len(value)) + value


def fmt_hms(time):
    day = 0
    if time >= 24:
        day = 1
        time -= 24
    elif time < 0:
        day = -1
        time += 24
    hour = int(time)
    time = (time - hour) * 60
    minute = int(time)
    time = (time - minute) * 60
    sec = round(time)
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        minute = 0
        hour += 1
    if hour == 24:
        hour = 0
        day += 1
    if day == 0:
        day = ''
    elif day == 2:
        day = ' +2 days'
    else:
        day = f' {day:+d} day'
    return f'{hour:2d}:{minute:02d}:{sec:02d}{day}'


def fmt_lat(value, nosec=False):
    sym = 'N'
    if value < 0:
        sym = 'S'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    if nosec:
        minute = round(value)
        sec = 0
    else:
        minute = int(value)
        value = (value - minute) * 60
        sec = round(value)
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        deg += 1
        minute = 0
    if nosec:
        return f'{deg:2d}{sym}{minute:2d}'
    return f'{deg:2d}{sym}{minute:2d}\'{sec:2d}"'


def fmt_long(value):
    sym = 'E'
    if value < 0:
        sym = 'W'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        deg += 1
        minute = 0
    return f'{deg:3d}{sym}{minute:2d}\'{sec:2d}"'


def fmt_dms(value):
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        minute = 0
        deg += 1
    return f'{deg:2d}{DS}{minute:2}\'{sec:2}"'


def fmt_minutes(value):
    return int(value) * 60 + (value - int(value)) * 60


def fmt_dm(value, noz=False, degree_digits=2):
    deg = int(value)
    value = (value - deg) * 60
    minute = round(value)
    if minute == 60:
        minute = 0
        deg += 1
    if noz:
        if degree_digits == 2:
            return f"{deg:2d}{DS}{minute:2}'"
        if degree_digits == 3:
            return f"{deg:>3d}{DS}{minute:>2}'"
    if degree_digits == 2:
        return f"{deg:>02d}{DS}{minute:>02}'"
    if degree_digits == 3:
        return f"{deg:>03d}{DS}{minute:>02}'"


def signed_degree_minute(value):
    if value < 0:
        return f'-{fmt_dm(-value, True)}'
    elif value > 0:
        return f'+{fmt_dm(value, True)}'
    else:
        return f' {fmt_dm(0)}'


def signed_minute_second(value):
    if value < 0:
        s = '-'
    elif value > 0:
        s = '+'
    else:
        s = ' '
    value = abs(value) * 60
    min = int(value)
    value = (value - min) * 60
    sec = round(value)
    if sec == 60:
        sec = 0
        min += 1
    return f'{s}{min:2}\'{sec:2}"'


def angularity_activates_ingress(orb: float, angle: str) -> bool:
    if orb < 0:
        return False

    if angle.strip() in ['A', 'D', 'M', 'I']:
        return orb <= 3.0
    return orb <= 2.0


def make_chart_path(chart, temporary, is_ingress=False):
    if isinstance(chart, dict):
        ingress = (
            True
            if chart['type'][0:3] in ['Ari', 'Can', 'Lib', 'Cap']
            or not chart['name']
            else False
        )
    else:
        ingress = is_ingress
    if isinstance(chart, dict):
        if ingress:
            first = f"{chart['year']}-{chart['month']}-{chart['day']}"
            second = chart['location']
            third = chart['type']
        else:
            first = chart['name']
            index = first.find(';')
            if index > -1:
                first = first[0:index]
            second = f"{chart['year']}-{chart['month']:02d}-{chart['day']:02d}"
            third = chart['type']
    else:
        if ingress:
            first = f'{chart.year}-{chart.month}-{chart.day}'
            second = chart.location
            third = chart.type.value
        else:
            first = chart.name
            index = first.find(';')
            if index > -1:
                first = first[0:index]
            second = f'{chart.year}-{chart.month:02d}-{chart.day:02d}'
            third = chart.type.value
    filename = f'{first}~{second}~{third}.dat'
    if ingress:
        filepath = os.path.join(
            f"{chart['year'] if isinstance(chart, dict) else chart.year}",
            filename,
        )
    else:
        filepath = os.path.join(first[0], first, filename)
    path = TEMP_CHARTS if temporary else CHART_PATH
    return os.path.abspath(os.path.join(path, filepath))


def calc_aspect_strength_percent(
    max_orb: int, raw_orb: float, as_float=False
) -> str:

    curve_multiplier = 90 / max_orb
    strength_percent = math.cos(math.radians(raw_orb * curve_multiplier))

    strength_percent = round(strength_percent * 100)

    return f'{strength_percent:3d}' if not as_float else strength_percent


def convert_house_to_pvl(house: float) -> float:
    zero_index_house = house - 1
    return (int(zero_index_house) * 30) + (
        ((zero_index_house) - int(zero_index_house)) * 30
    )


def greatest_nonzero_class_orb(orbs: list[float]) -> float:
    for i in range(len(orbs) - 1, -1, -1):
        if orbs[i] > 0:
            return orbs[i]
    return 0


def decimal_longitude_to_sign(longitude: float) -> str:
    sign = SIGNS_SHORT[int(longitude // 30)]
    sign_degrees = int(longitude % 30)

    raw_degrees = int(longitude)
    mins = int((longitude - raw_degrees) * 60)

    seconds = int((((longitude - raw_degrees) * 60) - mins) * 60)

    return f'{sign_degrees: >2}{sign}{mins: >2}\'{seconds: >2}"'


def declination_from_zodiacal(longitude: float, obliquity: float) -> float:
    sin_dec = math.sin(math.radians(longitude)) * math.sin(
        math.radians(obliquity)
    )
    return math.degrees(math.asin(sin_dec))


def right_ascension_from_zodiacal(longitude: float, obliquity: float) -> float:
    tan_ra = math.tan(math.radians(longitude)) * math.cos(
        math.radians(obliquity)
    )
    return to360(math.degrees(math.atan(tan_ra)))


def precess_mc(
    longitude: float, ayanamsa: float, obliquity: float
) -> tuple[float, float]:
    (right_ascension, declination) = swe.cotrans(
        [longitude + ayanamsa, 0, 0],
        obliquity,
    )
    return (right_ascension, declination)


def write_triple_columns_to_file(
    classes: list[list], chartfile: TextIOWrapper
):
    for aspect_index in range(
        max(
            len(classes[0]),
            len(classes[1]),
            len(classes[2]),
        )
    ):
        if aspect_index < len(classes[0]):
            text = (
                str(classes[0][aspect_index])
                if classes[0][aspect_index]
                else ' ' * 26
            )

            chartfile.write(
                left_align(
                    text,
                    width=26,
                )
            )
        else:
            chartfile.write(' ' * 26)
        if aspect_index < len(classes[1]):
            chartfile.write(
                center_align(
                    str(classes[1][aspect_index]),
                    width=26,
                )
            )
        else:
            chartfile.write(' ' * 26)
        if aspect_index < len(classes[2]):
            chartfile.write(
                right_align(
                    str(classes[2][aspect_index]),
                    width=26,
                )
            )
        else:
            chartfile.write(' ' * 26)
        chartfile.write('\n')


def truncate(number, digits) -> float:
    # Improve accuracy with floating point operations, to avoid truncate(16.4, 2) = 16.39 or truncate(-1.13, 2) = -1.12
    nbDecimals = len(str(number).split('.')[1])
    if nbDecimals <= digits:
        return number
    stepper = 10.0**digits
    return math.trunc(stepper * number) / stepper


def includes_any(collection: list[any], elements: list[any]):
    return len(list(set(collection) & set(elements))) > 0
