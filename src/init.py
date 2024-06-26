# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import shutil
import sys

from constants import PLATFORM
from libs import *

startup = True

if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))


def app_path(path=None):
    if not path:
        return APP_PATH
    return os.path.abspath(os.path.join(APP_PATH, path))


def copy_file_if_not_exists(expected: str, src: str):
    if not os.path.exists(expected):
        shutil.copyfile(src, expected)


month_abrev = [
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

EPHE_PATH = app_path('ephe')
HELP_PATH = app_path('help')

if PLATFORM == 'Win32GUI':
    d1 = os.path.expanduser(r'~\Documents')
elif PLATFORM == 'linux':
    d1 = os.path.join('/var', 'lib', 'tmsa')

# Originally...
# DLL_PATH = app_path(r"..\dll\swedll32.dll")

if PLATFORM == 'Win32GUI':
    DLL_PATH = app_path(os.path.join('dll', 'swedll32.dll'))
if PLATFORM == 'linux':
    DLL_PATH = app_path(os.path.join('dll', 'libswe.so'))

if os.path.exists(d1):
    d1 = os.path.expandvars(d1)
else:
    d1 = None

if PLATFORM == 'Win32GUI':
    import winreg

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders',
    )
    for i in range(1000):
        try:
            r = winreg.EnumValue(key, i)
            if r[0] == 'Personal':
                d2 = r[1]
                break
        except:
            d2 = None
    key.Close()
    if d2:
        d2 = os.path.expandvars(d2)
        if os.path.exists(d2):
            docpath = d2
        else:
            d2 = None
    elif d1:
        docpath = d1
    else:
        docpath = 'c:\\'
    CHART_PATH = os.path.join(docpath, 'tmsa', 'charts')
    os.makedirs(CHART_PATH, exist_ok=True)

    TEMP_CHARTS = os.path.join(CHART_PATH, 'temporary')

    ERROR_FILE = os.path.join(docpath, 'tmsa_errors', 'error.txt')
    os.makedirs(os.path.dirname(ERROR_FILE), exist_ok=True)

    OPTION_PATH = os.path.join(docpath, 'tmsa', 'options')
    os.makedirs(OPTION_PATH, exist_ok=True)

elif PLATFORM == 'linux':
    import shutil

    CHART_PATH = os.path.join('/var', 'lib', 'tmsa', 'charts')
    os.makedirs(CHART_PATH, exist_ok=True)
    TEMP_CHARTS = os.path.join(CHART_PATH, 'temporary')

    ERROR_FILE = os.path.join('/var', 'log', 'tmsa', 'error.txt')
    os.makedirs(os.path.dirname(ERROR_FILE), exist_ok=True)

    OPTION_PATH = os.path.join(
        os.path.expanduser('~'), '.config', 'tmsa', 'options'
    )
    os.makedirs(OPTION_PATH, exist_ok=True)

    copy_file_if_not_exists(
        os.path.join(OPTION_PATH, 'Default_Natal.opt'),
        app_path(os.path.join('assets', 'Default_Natal.opt')),
    )
    copy_file_if_not_exists(
        os.path.join(OPTION_PATH, 'Cosmobiology.opt'),
        app_path(os.path.join('assets', 'Cosmobiology.opt')),
    )
    copy_file_if_not_exists(
        os.path.join(OPTION_PATH, 'Default_Ingress.opt'),
        app_path(os.path.join('assets', 'Default_Ingress.opt')),
    )
    copy_file_if_not_exists(
        os.path.join(OPTION_PATH, 'Default_Return.opt'),
        app_path(os.path.join('assets', 'Default_Return.opt')),
    )
    copy_file_if_not_exists(
        os.path.join(OPTION_PATH, 'Student_Natal.opt'),
        app_path(os.path.join('assets', 'Student_Natal.opt')),
    )

STUDENT_FILE = os.path.join(OPTION_PATH, 'student.json')

LOCATIONS_FILE = os.path.join(OPTION_PATH, 'locations.json')

if not os.path.exists(LOCATIONS_FILE):
    try:
        with open(LOCATIONS_FILE, 'w') as datafile:
            json.dump([], datafile, indent=4)
    except Exception:
        pass

RECENT_FILE = os.path.join(OPTION_PATH, 'recent.json')

COLOR_FILE = os.path.join(OPTION_PATH, 'colors.json')

if not os.path.exists(RECENT_FILE):
    try:
        with open(COLOR_FILE, 'w') as datafile:
            json.dump([], datafile, indent=4)
    except Exception:
        pass

default_colors = {
    'bg_color': 'black',
    'button_color': 'blue',
    'text_color': 'yellow',
    'error_color': 'red',
}
colors = None

default = True
if os.path.exists(COLOR_FILE):
    try:
        with open(COLOR_FILE) as datafile:
            colors = json.load(datafile)
        default = False
    except Exception:
        pass

if default:
    try:
        with open(COLOR_FILE, 'w') as datafile:
            json.dump(
                colors if colors is not None else default_colors,
                datafile,
                indent=4,
            )
    except Exception:
        pass

if colors is None or colors == [] or colors == {}:
    colors = default_colors

BG_COLOR = colors['bg_color']
BTN_COLOR = colors['button_color']
TXT_COLOR = colors['text_color']
ERR_COLOR = colors['error_color']

DATA_ENTRY_FILE = os.path.join(OPTION_PATH, 'data_entry.json')

data_entry = {'date_fmt': 'M D Y', 'time_fmt': 'AM/PM'}
default = True
if os.path.exists(DATA_ENTRY_FILE):
    try:
        with open(DATA_ENTRY_FILE) as datafile:
            data_entry = json.load(datafile)
        default = False
    except Exception:
        pass
if default:
    try:
        with open(DATA_ENTRY_FILE, 'w') as datafile:
            json.dump(data_entry, datafile, indent=4)
    except Exception:
        pass

DATE_FMT = data_entry['date_fmt']
TIME_FMT = data_entry['time_fmt']

HOME_LOC_FILE = os.path.join(OPTION_PATH, 'home.json')

if os.path.exists(HOME_LOC_FILE):
    try:
        with open(HOME_LOC_FILE, 'r') as datafile:
            HOME_LOC = json.load(datafile)
    except Exception:
        HOME_LOC = None
else:
    HOME_LOC = None


def normalize(text, nocap=False, maxlen=33):
    text = text.strip()
    cap = True
    spok = True
    result = ''
    for ch in text:
        if ch.isalpha():
            if cap and not nocap:
                result += ch.upper()
                cap = False
            else:
                result += ch
            spok = True
        elif ch.isspace() and spok:
            result += ' '
            spok = False
            cap = True
        elif ch not in ':\\?*"/<>|~;':
            result += ch
            cap = True
            spok = True
    if len(result) > maxlen:
        result = result[0 : len(result) - maxlen]
    return result


def make_chart_path(chart, temporary):
    ingress = (
        True
        if chart['type'][0:3] in ['Ari', 'Can', 'Lib', 'Cap']
        or not chart['name']
        else False
    )
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
    filename = f'{first}~{second}~{third}.dat'
    if ingress:
        filepath = f"{chart['year']}\\{filename}"
    else:
        filepath = f'{first[0]}\\{first}\\{filename}'
    path = TEMP_CHARTS if temporary else CHART_PATH
    return os.path.abspath(os.path.join(path, filepath))
