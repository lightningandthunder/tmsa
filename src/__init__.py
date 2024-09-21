# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os

from src.constants import PLATFORM
from src.defaults.option_defaults import (
    COSMOBIOLOGY,
    INGRESS_DEFAULT,
    NATAL_DEFAULT,
    RETURN_DEFAULT,
    STUDENT_NATAL,
)
from src.utils.os_utils import (
    app_path,
    create_directory,
    migrate_from_file,
    write_to_path,
)

STILL_STARTING_UP = True


def log_error(error: str):
    print(error)
    write_to_path(ERROR_FILE, error)


EPHE_PATH = app_path('ephe')
HELP_PATH = app_path('help')

# Set base directories and paths
if PLATFORM == 'Win32GUI':
    primary_directory = os.path.expanduser(r'~\Documents')
    DLL_PATH = app_path(os.path.join('dll', 'swedll32.dll'))
elif PLATFORM == 'linux':
    primary_directory = os.path.join(os.path.expanduser('~'), '.tmsa')
    if not os.path.exists(primary_directory):
        create_directory(primary_directory)
    DLL_PATH = app_path(os.path.join('dll', 'libswe.so'))
elif PLATFORM == 'darwin':
    primary_directory = os.path.join(
        os.path.expanduser('~'), 'Documents', 'tmsa'
    )
    if not os.path.exists(primary_directory):
        create_directory(primary_directory)
    DLL_PATH = app_path(os.path.join('dll', 'libswe.dylib'))

if os.path.exists(primary_directory):
    primary_directory = os.path.expandvars(primary_directory)
else:
    primary_directory = None

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
                secondary_directory = r[1]
                break
        except:
            secondary_directory = None
    key.Close()
    if secondary_directory:
        secondary_directory = os.path.expandvars(secondary_directory)
        if os.path.exists(secondary_directory):
            docpath = secondary_directory
        else:
            secondary_directory = None
    elif primary_directory:
        docpath = primary_directory
    else:
        docpath = 'c:\\'
    CHART_PATH = os.path.join(docpath, 'tmsa', 'charts')
    os.makedirs(CHART_PATH, exist_ok=True)

    TEMP_CHARTS = os.path.join(CHART_PATH, 'temporary')

    ERROR_FILE = os.path.join(docpath, 'tmsa_errors', 'error.txt')
    os.makedirs(os.path.dirname(ERROR_FILE), exist_ok=True)

    OPTION_PATH = os.path.join(docpath, 'tmsa', 'options')
    os.makedirs(OPTION_PATH, exist_ok=True)


elif PLATFORM in ['linux', 'darwin']:
    CHART_PATH = os.path.join(primary_directory, 'charts')
    create_directory(CHART_PATH)
    TEMP_CHARTS = os.path.join(CHART_PATH, 'temporary')

    log_directory = os.path.join(primary_directory, 'logs')
    create_directory(log_directory)
    ERROR_FILE = os.path.join(log_directory, 'error.txt')

    # Make empty error file if it doesn't exist
    if not os.path.exists(ERROR_FILE):
        open(ERROR_FILE, 'w').close()

    OPTION_PATH = os.path.join(primary_directory, 'options')
    create_directory(OPTION_PATH)

# Ensure all option file defaults exist.
# This is the same for every OS.

migrate_from_file(
    old_path=os.path.join(OPTION_PATH, 'Default_Natal.opt'),
    new_path=os.path.join(OPTION_PATH, 'Natal_Default.opt'),
    fallback=json.dumps(NATAL_DEFAULT),
)

migrate_from_file(
    old_path=os.path.join(OPTION_PATH, 'Default_Ingress.opt'),
    new_path=os.path.join(OPTION_PATH, 'Ingress_Default.opt'),
    fallback=json.dumps(INGRESS_DEFAULT),
)

migrate_from_file(
    old_path=os.path.join(OPTION_PATH, 'Default_Return.opt'),
    new_path=os.path.join(OPTION_PATH, 'Return_Default.opt'),
    fallback=json.dumps(RETURN_DEFAULT),
)

migrate_from_file(
    old_path=os.path.join(OPTION_PATH, 'Cosmobiology.opt'),
    new_path=os.path.join(OPTION_PATH, 'Cosmobiology.opt'),
    fallback=json.dumps(COSMOBIOLOGY),
)

migrate_from_file(
    os.path.join(OPTION_PATH, 'Student_Natal.opt'),
    os.path.join(OPTION_PATH, 'Student_Natal.opt'),
    fallback=json.dumps(STUDENT_NATAL),
)

STUDENT_FILE = os.path.join(OPTION_PATH, 'student.json')

LOCATIONS_FILE = os.path.join(OPTION_PATH, 'locations.json')

if not os.path.exists(LOCATIONS_FILE):
    try:
        with open(LOCATIONS_FILE, 'w') as datafile:
            json.dump([], datafile, indent=4)
    except Exception as e:
        log_error(e)

RECENT_FILE = os.path.join(OPTION_PATH, 'recent.json')

COLOR_FILE = os.path.join(OPTION_PATH, 'colors.json')

if not os.path.exists(RECENT_FILE):
    try:
        with open(COLOR_FILE, 'w') as datafile:
            json.dump([], datafile, indent=4)
    except Exception as e:
        log_error(e)

default_colors = {
    'bg_color': 'black',
    'button_color': 'blue',
    'disabled_button': 'gray25',
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
    except Exception as e:
        log_error(e)

if default:
    try:
        with open(COLOR_FILE, 'w') as datafile:
            json.dump(
                colors if colors is not None else default_colors,
                datafile,
                indent=4,
            )
    except Exception as e:
        log_error(e)

if colors is None or colors == [] or colors == {}:
    colors = default_colors

BG_COLOR = colors.get('bg_color', default_colors['bg_color'])
BTN_COLOR = colors.get('button_color', default_colors['button_color'])
DISABLED_BUTTON_COLOR = colors.get(
    'disabled_button', default_colors['disabled_button']
)
TXT_COLOR = colors.get('text_color', default_colors['text_color'])
ERR_COLOR = colors.get('error_color', default_colors['error_color'])

DATA_ENTRY_FILE = os.path.join(OPTION_PATH, 'data_entry.json')

data_entry = {'date_fmt': 'M D Y', 'time_fmt': 'AM/PM'}
default = True
if os.path.exists(DATA_ENTRY_FILE):
    try:
        with open(DATA_ENTRY_FILE) as datafile:
            data_entry = json.load(datafile)
        default = False
    except Exception as e:
        log_error(e)

if default:
    try:
        with open(DATA_ENTRY_FILE, 'w') as datafile:
            json.dump(data_entry, datafile, indent=4)
    except Exception as e:
        log_error(e)

DATE_FMT = data_entry['date_fmt']
TIME_FMT = data_entry['time_fmt']

HOME_LOC_FILE = os.path.join(OPTION_PATH, 'home.json')

if os.path.exists(HOME_LOC_FILE):
    try:
        with open(HOME_LOC_FILE, 'r') as datafile:
            HOME_LOC = json.load(datafile)
    except Exception as e:
        HOME_LOC = None
        log_error(e)
else:
    HOME_LOC = None
