# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
import os
from typing import Iterator
from itertools import chain

from src import *
from src import constants
from src.models.options import NodeTypes, Options
from src.user_interfaces.widgets import *

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

INGRESSES = [
    'Capsolar',
    'Cansolar',
    'Arisolar',
    'Libsolar',
    'Caplunar',
    'Canlunar',
    'Arilunar',
    'Liblunar',
]

SOLUNAR_RETURNS = [
    'Lunar Return',
    'Kinetic Lunar Return',
    'Novienic Lunar Return',
    '18-Hour Lunar Return',
    'Solar Return',
    'Kinetic Solar Return',
    'Novienic Solar Return',
    '10-Day Solar Return',
    'Anlunar Return',
    'Kinetic Anlunar Return',
    'Solilunar Return',
    'Lunisolar Return',
]

RETURNS_WHERE_MOON_ALWAYS_FOREGROUND = [
    'Novienic Lunar Return',
    '18-Hour Lunar Return',
    'Solar Return',
    'Kinetic Solar Return',
    'Novienic Solar Return',
    '10-Day Solar Return',
    'Solilunar Return',
]

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


def major_angularity_curve_cadent_background(orb):
    if orb <= 10:
        orb *= 6
    elif orb > 10 and orb <= 40:
        orb = 2 * orb + 40
    elif orb > 40 and orb <= 60:
        orb *= 3
    else:
        orb = 6 * orb - 180

    return _major_angle_angularity_strength_percent(orb)


def major_angularity_curve_midquadrant_background(orb):
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
    return round(raw * 100)


def major_angularity_curve_eureka_formula(orb):
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
    return round(raw_decimal * 100)


def calculate_angularity_curve(orb_degrees: float):
    return math.cos(math.radians(orb_degrees * 4))


def minor_angularity_curve(orb_degrees: float):
    # Cosine curve
    raw = math.cos(math.radians(orb_degrees * 30))
    # Convert from -1 to +1 to 0 to +2
    raw += 1
    # Spread this curve across 50 percentage points
    raw *= 25
    # Finally, add 50 get a percentage
    raw += 50

    return round(raw)


def inrange(value: float, center: float, orb: float) -> bool:
    return value >= center - orb and value <= center + orb


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


def s_dm(value):
    if value < 0:
        return f'-{fmt_dm(-value, True)}'
    elif value > 0:
        return f'+{fmt_dm(value, True)}'
    else:
        return f' {fmt_dm(0)}'


def s_ms(value):
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


def make_chart_path(chart, temporary):
    if isinstance(chart, dict):
        ingress = (
            True
            if chart['type'][0:3] in ['Ari', 'Can', 'Lib', 'Cap']
            or not chart['name']
            else False
        )
    else:
        ingress = True if chart.type in INGRESSES or not chart.name else False
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


def iterate_allowed_planets(
    options: Options,
) -> Iterator[tuple[str, dict[str, any]]]:
    for planet_name, data in constants.PLANETS.items():
        if (
            data['number'] > 11
            and data['short_name'] not in options.extra_bodies
        ):
            continue
        elif (
            planet_name == 'True Node'
            and options.node_type.value != NodeTypes.TRUE_NODE.value
        ):
            continue
        elif (
            planet_name == 'Mean Node'
            and options.node_type.value != NodeTypes.MEAN_NODE.value
        ):
            continue

        else:
            yield planet_name, data


def calc_aspect_strength_percent(max_orb: int, raw_orb: float) -> str:
    strength = 60 / max_orb
    strength_percent = math.cos(math.radians(raw_orb * strength))
    strength_percent = round((strength_percent - 0.5) * 200)
    return f'{strength_percent:3d}'


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
