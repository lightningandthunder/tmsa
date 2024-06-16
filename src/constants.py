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
