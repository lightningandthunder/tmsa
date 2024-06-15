# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
import tkinter as tk
import tkinter.colorchooser as tkcolorchooser
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
import traceback
import webbrowser
from copy import *
from ctypes import *
from datetime import datetime, timedelta
from tkinter.font import Font as tkFont

import anglicize
import pytz
import us
from geopy import *
from geopy.geocoders import *
from timezonefinder import TimezoneFinder
