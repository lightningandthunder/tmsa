# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import os
import sys

VERSION = '0.6.0a0'

DS = '\N{DEGREE SIGN}'
DQ = '"'
SQ = "'"

PLANETS = {
    'Moon': {
        'long_name': 'Moon',
        'short_name': 'Mo',
        'number': 0,
    },
    'Sun': {
        'long_name': 'Sun',
        'short_name': 'Su',
        'number': 1,
    },
    'Mercury': {
        'long_name': 'Mercury',
        'short_name': 'Me',
        'number': 2,
    },
    'Venus': {
        'long_name': 'Venus',
        'short_name': 'Ve',
        'number': 3,
    },
    'Mars': {
        'long_name': 'Mars',
        'short_name': 'Ma',
        'number': 4,
    },
    'Jupiter': {
        'long_name': 'Jupiter',
        'short_name': 'Ju',
        'number': 5,
    },
    'Saturn': {
        'long_name': 'Saturn',
        'short_name': 'Sa',
        'number': 6,
    },
    'Uranus': {
        'long_name': 'Uranus',
        'short_name': 'Ur',
        'number': 7,
    },
    'Neptune': {
        'long_name': 'Neptune',
        'short_name': 'Ne',
        'number': 8,
    },
    'Pluto': {
        'long_name': 'Pluto',
        'short_name': 'Pl',
        'number': 9,
    },
    'Eris': {
        'long_name': 'Eris',
        'short_name': 'Er',
        'number': 146199,
    },
    'Sedna': {
        'long_name': 'Sedna',
        'short_name': 'Se',
        'number': 100377,
    },
    'Mean Node': {
        'long_name': 'Mean Node',
        'short_name': 'No',
        'number': 10,
    },
    'True Node': {
        'long_name': 'True Node',
        'short_name': 'No',
        'number': 11,
    },
    'Quaoar': {
        'short_name': 'Qu',
        'short_name': 'Qu',
        'number': 60000,
    },
    'Orcus': {
        'short_name': 'Or',
        'short_name': 'Or',
        'number': 100482,
    },
    'Haumea': {
        'long_name': 'Haumea',
        'short_name': 'Ha',
        'number': 146108,
    },
    'Makemake': {
        'long_name': 'Makemake',
        'short_name': 'Mk',
        'number': 146472,
    },
    'Gonggong': {
        'long_name': 'Gonggong',
        'short_name': 'Go',
        'number': 235088,
    },
    'Chiron': {
        'long_name': 'Chiron',
        'short_name': 'Ch',
        'number': 15,
    },
    'Ceres': {
        'long_name': 'Ceres',
        'short_name': 'Ce',
        'number': 17,
    },
    'Pallas': {
        'long_name': 'Pallas',
        'short_name': 'Pa',
        'number': 18,
    },
    'Juno': {
        'long_name': 'Juno',
        'short_name': 'Jn',
        'number': 19,
    },
    'Vesta': {
        'long_name': 'Vesta',
        'short_name': 'Vs',
        'number': 20,
    },
    'Salacia': {
        'long_name': 'Salacia',
        'short_name': 'Sl',
        'number': 130347,
    },
}

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


PLATFORM = None

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
