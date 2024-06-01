# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
from init import *
from widgets import *


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
}

DS = '\N{DEGREE SIGN}'

DS = '\N{DEGREE SIGN}'
DQ = '"'
SQ = "'"


def main_angularity_curve(a):
    if a <= 10:
        a *= 6
    elif a > 10 and a <= 40:
        a = 2 * a + 40
    elif a > 40 and a <= 60:
        a *= 3
    else:
        a = 6 * a - 180
    return math.cos(math.radians(a))


def main_angularity_curve_2(a):
    if a > 45:
        a = 90 - a
    if a <= 10:
        a *= 6
    elif a > 10 and a <= 35:
        a = 2.4 * a + 36
    else:
        a = 6 * a - 90
    return math.cos(math.radians(a))


def minor_angularity_curve(orb_degrees: float):
    return math.cos(math.radians(orb_degrees * 30))


def inrange(value: float, center: float, orb: float) -> bool:
    return value >= center - orb and value <= center + orb


def zod_min(value):
    value %= 360
    deg = int(value)
    min = round((value - deg) * 60)
    d = 0
    s = 0
    if min == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        min = 0
        deg += 1
    return f'{(deg % 30) or d:2d}{SIGNS_SHORT[(deg // 30) + s]}{min:2d}'


def zod_sec(value):
    value %= 360
    deg = int(value)
    value = (value - deg) * 60
    min = int(value)
    value = (value - min) * 60
    sec = round(value)
    d = 0
    s = 0
    if sec == 60:
        sec = 0
        min += 1
    if min == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        min = 0
        deg += 1
    return (
        f'{(deg % 30) or d:2d}{SIGNS_SHORT[deg // 30 + s]}{min:2d}\'{sec:2d}"'
    )


def center(value, width=33):
    if len(value) > width:
        value = value[0:width]
    left = (width - len(value)) // 2
    left = ' ' * left
    right = (width + 1 - len(value)) // 2
    right = ' ' * right
    return left + value + right


def left(value, width):
    if len(value) > width:
        value = value[0:width]
    return value + ' ' * (width - len(value))


def right(value, width):
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
    min = int(time)
    time = (time - min) * 60
    sec = round(time)
    if sec == 60:
        sec = 0
        min += 1
    if min == 60:
        min = 0
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
    return f'{hour:2d}:{min:02d}:{sec:02d}{day}'


def fmt_lat(value, nosec=False):
    sym = 'N'
    if value < 0:
        sym = 'S'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    if nosec:
        min = round(value)
        sec = 0
    else:
        min = int(value)
        value = (value - min) * 60
        sec = round(value)
    if sec == 60:
        min += 1
        sec = 0
    if min == 60:
        deg += 1
        min = 0
    if nosec:
        return f'{deg:2d}{sym}{min:2d}'
    return f"{deg:2d}{sym}{min:2d}'{sec:2d}{DQ}"


def fmt_long(value):
    sym = 'E'
    if value < 0:
        sym = 'W'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    min = int(value)
    value = (value - min) * 60
    sec = round(value)
    if sec == 60:
        min += 1
        sec = 0
    if min == 60:
        deg += 1
        min = 0
    return f"{deg:3d}{sym}{min:2d}'{sec:2d}{DQ}"


def fmt_dms(value):
    deg = int(value)
    value = (value - deg) * 60
    min = int(value)
    value = (value - min) * 60
    sec = round(value)
    if sec == 60:
        sec = 0
        min += 1
    if min == 60:
        min = 0
        deg += 1
    return f"{deg:2d}{DS}{min:2}'{sec:2}{DQ}"


def fmt_dm(value, noz=False):
    deg = int(value)
    value = (value - deg) * 60
    min = round(value)
    if min == 60:
        min = 0
        deg += 1
    if noz:
        return f"{deg:2d}{DS}{min:2}'"
    return f"{deg:02d}{DS}{min:02}'"


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
