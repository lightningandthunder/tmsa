# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import os
import sys
from typing import TypedDict

VERSION = '0.7.0a9'
OLDEST_SUPPORTED_VERSION = '0.6.0'

DS = '\u00B0'
DQ = '"'
SQ = "'"

PLATFORM = None

PROGRESSION_Q1 = 0.00273032809
PROGRESSION_Q2 = 0.00273780311

DEV_MODE = False

match sys.platform:
    case 'win32':
        PLATFORM = 'Win32GUI'
    case 'linux':
        PLATFORM = 'linux'
    case 'darwin':
        PLATFORM = 'darwin'
    case _:
        raise RuntimeError(f'Unsupported architecture {sys.platform}')

if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))


LABEL_X_COORD = 0
LABEL_WIDTH = 1
LABEL_HEIGHT_UNIT = 0.022

ANGLE_ABBREVIATIONS = [
    'As',
    'Mc',
]

MONTHS = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
]

HOUR_FRACTION_OF_A_DAY = 1 / 24


class PlanetInfo(TypedDict):
    short_name: str
    long_name: str
    number: int
    stationary_period_hours: float


class AngleInfo(TypedDict):
    short_name: str
    long_name: str


ANGLES: dict[str, AngleInfo] = {
    'Ascendant': {
        'short_name': 'As',
        'long_name': 'Ascendant',
    },
    'Midheaven': {
        'short_name': 'Mc',
        'long_name': 'Midheaven',
    },
    'Eastpoint': {
        'short_name': 'Ep',
        'long_name': 'Eastpoint',
    },
    'Vertex': {
        'short_name': 'Ve',
        'long_name': 'Vertex',
    },
    'AntiVertex': {
        'short_name': 'Av',
        'long_name': 'AntiVertex',
    },
}

PLANETS: dict[str, PlanetInfo] = {
    'Moon': {
        'short_name': 'Mo',
        'long_name': 'Moon',
        'number': 1,
        'stationary_period_hours': -1.0,
        'traditional': True,
    },
    'Mean Node': {
        'short_name': 'MN',
        'long_name': 'Mean Node',
        'number': 10,
        'stationary_period_hours': -1,
        'traditional': True,
    },
    'True Node': {
        'short_name': 'TN',
        'long_name': 'True Node',
        'number': 11,
        'stationary_period_hours': -1,
        'traditional': True,
    },
    'Sun': {
        'short_name': 'Su',
        'long_name': 'Sun',
        'number': 0,
        'stationary_period_hours': -1.0,
        'traditional': True,
    },
    'Mercury': {
        'short_name': 'Me',
        'long_name': 'Mercury',
        'number': 2,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Venus': {
        'short_name': 'Ve',
        'long_name': 'Venus',
        'number': 3,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Mars': {
        'short_name': 'Ma',
        'long_name': 'Mars',
        'number': 4,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Vesta': {
        'short_name': 'Vs',
        'long_name': 'Vesta',
        'number': 20,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Juno': {
        'short_name': 'Jn',
        'long_name': 'Juno',
        'number': 19,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Ceres': {
        'short_name': 'Ce',
        'long_name': 'Ceres',
        'number': 17,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Pallas': {
        'short_name': 'Pa',
        'long_name': 'Pallas',
        'number': 18,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Jupiter': {
        'short_name': 'Ju',
        'long_name': 'Jupiter',
        'number': 5,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Saturn': {
        'short_name': 'Sa',
        'long_name': 'Saturn',
        'number': 6,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Chiron': {
        'short_name': 'Ch',
        'long_name': 'Chiron',
        'number': 15,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Uranus': {
        'short_name': 'Ur',
        'long_name': 'Uranus',
        'number': 7,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Neptune': {
        'short_name': 'Ne',
        'long_name': 'Neptune',
        'number': 8,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Orcus': {
        'short_name': 'Or',
        'long_name': 'Orcus',
        'number': 100482,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Pluto': {
        'short_name': 'Pl',
        'long_name': 'Pluto',
        'number': 9,
        'stationary_period_hours': 72,
        'traditional': True,
    },
    'Haumea': {
        'short_name': 'Ha',
        'long_name': 'Haumea',
        'number': 146108,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Quaoar': {
        'short_name': 'Qu',
        'long_name': 'Quaoar',
        'number': 60000,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Makemake': {
        'short_name': 'Mk',
        'long_name': 'Makemake',
        'number': 146472,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Gonggong': {
        'short_name': 'Go',
        'long_name': 'Gonggong',
        'number': 235088,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Eris': {
        'short_name': 'Er',
        'long_name': 'Eris',
        'number': 146199,
        'stationary_period_hours': 72,
        'traditional': False,
    },
    'Sedna': {
        'short_name': 'Se',
        'long_name': 'Sedna',
        'number': 100377,
        'stationary_period_hours': 72,
        'traditional': False,
    },
}
