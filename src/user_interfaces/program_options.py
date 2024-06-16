# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import random
import sys
import tkinter.colorchooser as tkcolorchooser

import anglicize
import us
from geopy import Nominatim

from src import (BG_COLOR, BTN_COLOR, COLOR_FILE, DATA_ENTRY_FILE, DATE_FMT,
                 ERR_COLOR, HELP_PATH, HOME_LOC, HOME_LOC_FILE, LOCATIONS_FILE,
                 STUDENT_FILE, TIME_FMT, TXT_COLOR)
from src.constants import DQ, DS, VERSION
from src.user_interfaces.locations import Locations
from src.user_interfaces.widgets import (Button, Entry, Frame, Label,
                                         Radiobutton, Radiogroup, check_num,
                                         delay, tk)
from src.utils.format_utils import normalize_text
from src.utils.gui_utils import ShowHelp


class ProgramOptions(Frame):
    def __init__(self):
        super().__init__()
        Label(self, 'Color Options', 0, 0, 1)
        Label(self, 'Background', 0.2, 0.05, 0.15, anchor=tk.W)
        self.bgsample = Label(self, '', 0.35, 0.05, 0.05, anchor=tk.W)
        self.bgcolor = Entry(self, '', 0.4, 0.05, 0.2)
        self.bgcolor.focus()
        Button(self, 'Choose', 0.6, 0.05, 0.1).bind(
            '<Button-1>', lambda _: delay(self.choose_color, 'background')
        )
        Label(self, 'Button', 0.2, 0.1, 0.15, anchor=tk.W)
        self.btnsample = Label(self, '', 0.35, 0.1, 0.05)
        self.btncolor = Entry(self, '', 0.4, 0.1, 0.2)
        Button(self, 'Choose', 0.6, 0.1, 0.1).bind(
            '<Button-1>', lambda _: delay(self.choose_color, 'button')
        )
        Label(self, 'Text', 0.2, 0.15, 0.15, anchor=tk.W)
        self.txtsample = Label(self, '', 0.35, 0.15, 0.05)
        self.txtcolor = Entry(self, '', 0.4, 0.15, 0.2)
        Button(self, 'Choose', 0.6, 0.15, 0.1).bind(
            '<Button-1>', lambda _: delay(self.choose_color, 'text')
        )
        Label(self, 'Error', 0.2, 0.2, 0.15, anchor=tk.W)
        self.errsample = Label(self, '', 0.35, 0.2, 0.05)
        self.errcolor = Entry(self, '', 0.4, 0.2, 0.2)
        Button(self, 'Choose', 0.6, 0.2, 0.1).bind(
            '<Button-1>', lambda _: delay(self.choose_color, 'error')
        )
        Label(self, 'Data Entry Options', 0, 0.25, 1)
        Label(self, 'Date Format', 0.2, 0.3, 0.2, anchor=tk.W)
        self.dtfmt = Radiogroup(self)
        Radiobutton(self, self.dtfmt, 0, 'M D Y', 0.4, 0.3, 0.1)
        Radiobutton(self, self.dtfmt, 1, 'D M Y', 0.5, 0.3, 0.15)
        Label(self, 'Time Format', 0.2, 0.35, 0.2, anchor=tk.W)
        self.tmfmt = Radiogroup(self)
        Radiobutton(self, self.tmfmt, 0, 'AM/PM', 0.4, 0.35, 0.1)
        Radiobutton(self, self.tmfmt, 1, '24 Hour', 0.5, 0.35, 0.1)
        Label(self, 'Student Options', 0.2, 0.45, 0.2, anchor=tk.W)
        self.isstudent = Radiogroup(self)
        Radiobutton(self, self.isstudent, 1, 'Yes', 0.4, 0.45, 0.1)
        Radiobutton(self, self.isstudent, 0, 'No', 0.5, 0.45, 0.1)
        if os.path.exists(STUDENT_FILE):
            self.isstudent.value = 1
        Label(self, 'Home Location', 0.15, 0.55, 0.15, anchor=tk.W)
        self.loc = Entry(self, '', 0.3, 0.55, 0.3)
        self.loc.bind('<KeyRelease>', lambda _: self.enable_find)
        Button(self, 'Recent', 0.6, 0.55, 0.1).bind(
            '<Button-1>', lambda _: delay(self.recent_loc)
        )
        self.findbtn = Button(self, 'Find', 0.7, 0.55, 0.1)
        self.findbtn.bind('<Button-1>', lambda _: delay(self.find))
        Label(self, 'Lat D M S', 0.15, 0.6, 0.15, anchor=tk.W)
        self.latd = Entry(self, '', 0.3, 0.6, 0.1)
        self.latd.bind('<KeyRelease>', lambda _: delay(check_num, self.latd))
        self.latm = Entry(self, '', 0.4, 0.6, 0.1)
        self.latm.bind('<KeyRelease>', lambda _: delay(check_num, self.latm))
        self.lats = Entry(self, '0', 0.5, 0.6, 0.1)
        self.lats.bind('<KeyRelease>', lambda _: delay(check_num, self.lats))
        self.latdir = Radiogroup(self)
        Radiobutton(self, self.latdir, 0, 'North', 0.6, 0.6, 0.1)
        Radiobutton(self, self.latdir, 1, 'South', 0.7, 0.6, 0.1)
        Label(self, 'Long D M S', 0.15, 0.65, 0.15, anchor=tk.W)
        self.longd = Entry(self, '', 0.3, 0.65, 0.1)
        self.longd.bind('<KeyRelease>', lambda _: delay(check_num, self.longd))
        self.longm = Entry(self, '', 0.4, 0.65, 0.1)
        self.longm.bind('<KeyRelease>', lambda _: delay(check_num, self.longm))
        self.longs = Entry(self, '0', 0.5, 0.65, 0.1)
        self.longs.bind('<KeyRelease>', lambda _: delay(check_num, self.longs))
        self.longdir = Radiogroup(self)
        Radiobutton(self, self.longdir, 0, 'East ', 0.6, 0.65, 0.1)
        Radiobutton(self, self.longdir, 1, 'West ', 0.7, 0.65, 0.1)
        self.longdir.value = '1'
        Button(self, 'Save', 0.2, 0.75, 0.15).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Restart', 0.35, 0.75, 0.15).bind(
            '<Button-1>', lambda _: delay(self.restart)
        )
        Button(self, 'Help', 0.5, 0.75, 0.15).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, HELP_PATH + r'\program_options.txt'),
        )
        Button(self, 'Back', 0.65, 0.75, 0.15).bind(
            '<Button-1>', lambda _: delay(self.destroy)
        )
        self.status = Label(self, '', 0, 0.8, 1)
        self.load()

    def load(self):
        self.bgsample.bg = BG_COLOR
        self.bgcolor.text = BG_COLOR
        self.btnsample.bg = BTN_COLOR
        self.btncolor.text = BTN_COLOR
        self.txtsample.bg = TXT_COLOR
        self.txtcolor.text = TXT_COLOR
        self.errsample.bg = ERR_COLOR
        self.errcolor.text = ERR_COLOR
        self.dtfmt.value = 1 if DATE_FMT == 'D M Y' else 0
        self.tmfmt.value = 1 if TIME_FMT == '24 Hour' else 0
        self.isstudent.value = 1 if os.path.exists(STUDENT_FILE) else 0
        if HOME_LOC:
            self.loc.text = HOME_LOC[0]
            direc = 'N'
            value = HOME_LOC[1]
            if value < 0:
                value = -value
                direc = 'S'
            latd = int(value)
            value = (value - latd) * 60
            latm = int(value)
            value = (value - latm) * 60
            lats = round(value)
            if lats == 60:
                lats == 0
                latm += 1
            if latm == 60:
                latm = 0
                latd += 1
            self.latd.text = latd
            self.latm.text = latm
            self.lats.text = lats
            self.latdir.value = 0 if direc == 'N' else 1
            direc = 'E'
            value = HOME_LOC[2]
            if value < 0:
                value = -value
                direc = 'W'
            longd = int(value)
            value = (value - longd) * 60
            longm = int(value)
            value = (value - longm) * 60
            longs = round(value)
            if longs == 60:
                longs == 0
                longm += 1
            if longm == 60:
                longm = 0
                longd += 1
            self.longd.text = longd
            self.longm.text = longm
            self.longs.text = longs

    def save_colors(self):
        colors = {}
        colors['bg_color'] = self.bgcolor.text
        colors['button_color'] = self.btncolor.text
        colors['text_color'] = self.txtcolor.text
        colors['error_color'] = self.errcolor.text
        if not os.path.exists(COLOR_FILE):
            os.makedirs(os.path.dirname(COLOR_FILE), exist_ok=True)
        try:
            with open(COLOR_FILE, 'w') as datafile:
                json.dump(colors, datafile, indent=4)
            return True
        except Exception as e:
            self.status.error('Unable to save color options.')
            return False

    def choose_color(self, colortype):
        temp = tkcolorchooser.askcolor()
        if not temp[0]:
            return
        color = temp[1]
        if colortype == 'background':
            self.bgsample.bg = color
            self.bgcolor.text = color
        elif colortype == 'button':
            self.btnsample.bg = color
            self.btncolor.text = color
        elif colortype == 'text':
            self.txtsample.bg = color
            self.txtcolor.text = color
        elif colortype == 'error':
            self.errsample.bg = color
            self.errcolor.text = color

    def save_fmt(self):
        fmt = {}
        fmt['date_fmt'] = 'D M Y' if self.dtfmt.value else 'M D Y'
        fmt['time_fmt'] = '24 Hour' if self.tmfmt.value else 'AM/PM'
        if not os.path.exists(DATA_ENTRY_FILE):
            os.makedirs(os.path.dirname(DATA_ENTRY_FILE), exist_ok=True)
        try:
            with open(DATA_ENTRY_FILE, 'w') as datafile:
                json.dump(fmt, datafile, indent=4)
            return True
        except Exception as e:
            self.status.error('Unable to save data entry options.')
            return False

    def save_student(self):
        if self.isstudent.value:
            if not os.path.exists(STUDENT_FILE):
                try:
                    with open(STUDENT_FILE, 'w') as datafile:
                        pass
                    return True
                except Exception:
                    self.status.error('Unable to save student options.')
                    return False
            else:
                return True
        else:
            if os.path.exists(STUDENT_FILE):
                try:
                    os.remove(STUDENT_FILE)
                except Exception:
                    self.status.error('Unable to save student options.')
                    return False
            else:
                return True

    def enable_find(self):
        self.findbtn.disabled = False

    def find(self):
        if self.findbtn.disabled:
            return
        self.status.text = ''
        if not self.loc.text:
            return self.status.error('Location required.', self.loc)
        geolocator = Nominatim(
            user_agent=f'Time Matters {VERSION} {random.randrange(0, 100000):05d}'
        )
        self.loc.text = normalize_text(self.loc.text)
        try:
            location = geolocator.geocode(self.loc.text)
        except Exception:
            return self.status.error(
                f'Unable to connect to location database.', self.latd
            )
        if not location:
            return self.status.error(
                f"'{self.loc.text}' not in database.", self.latd
            )
        loc = str(location).split(',')
        locx = []
        ok = True
        for i in range(len(loc)):
            temp = anglicize.anglicize(loc[i])
            ok = all(ord(c) <= 256 for c in loc[i])
            if not ok:
                break
            locx.append(temp)
        if ok:
            loc = locx
            city = loc[0].strip()
            country = loc[-1].strip()
            if country == 'United States':
                state = None
                for i in range(1, len(loc) - 1):
                    state = us.states.lookup(loc[i])
                    if state:
                        break
                if state:
                    country = f'{state.abbr} USA'
                else:
                    country = 'USA'
            if country == 'France' and len(loc) == 5:
                if 'France' not in loc[-2]:
                    country = loc[-3].strip()
            self.loc.text = f'{city}, {country}'
        direc = 'N'
        value = location.latitude
        if value < 0:
            value = -value
            direc = 'S'
        latd = int(value)
        value = (value - latd) * 60
        latm = int(value)
        value = (value - latm) * 60
        lats = round(value)
        if lats == 60:
            lats == 0
            latm += 1
        if latm == 60:
            latm = 0
            latd += 1
        self.latd.text = latd
        self.latm.text = latm
        self.lats.text = lats
        self.latdir.value = 0 if direc == 'N' else 1
        direc = 'E'
        value = location.longitude
        if value < 0:
            value = -value
            direc = 'W'
        longd = int(value)
        value = (value - longd) * 60
        longm = int(value)
        value = (value - longm) * 60
        longs = round(value)
        if longs == 60:
            longs == 0
            longm += 1
        if longm == 60:
            longm = 0
            longd += 1
        self.longd.text = longd
        self.longm.text = longm
        self.longs.text = longs
        self.longdir.value = 0 if direc == 'E' else 1

    def loc_finish(self, selected):
        if selected is None:
            return
        self.findbtn.disabled = True
        self.loc.text = selected[0]
        direc = 'N'
        value = selected[1]
        if value < 0:
            value = -value
            direc = 'S'
        latd = int(value)
        value = (value - latd) * 60
        latm = int(value)
        value = (value - latm) * 60
        lats = round(value)
        if lats == 60:
            lats == 0
            latm += 1
        if latm == 60:
            latm = 0
            latd += 1
        self.latd.text = latd
        self.latm.text = latm
        self.lats.text = lats
        self.latdir.value = 0 if direc == 'N' else 1
        direc = 'E'
        value = selected[2]
        if value < 0:
            value = -value
            direc = 'W'
        longd = int(value)
        value = (value - longd) * 60
        longm = int(value)
        value = (value - longm) * 60
        longs = round(value)
        if longs == 60:
            longs == 0
            longm += 1
        if longm == 60:
            longm = 0
            longd += 1
        self.longd.text = longd
        self.longm.text = longm
        self.longs.text = longs

    def recent_loc(self):
        try:
            with open(LOCATIONS_FILE, 'r') as datafile:
                recs = json.load(datafile)
            delay(Locations, recs, self.loc_finish)
            if len(recs) == 0:
                self.status.error('No saved locations.')
        except Exception:
            self.status.error(f"Can't open 'locations.json'.")

    def save_home(self):
        try:
            lat = (
                int(self.latd.text)
                + int(self.latm.text) / 60
                + int(self.lats.text or '0') / 3600
            )
        except Exception:
            return self.status.error('Latitude must be numeric.', self.latd)
        if lat < 0 or lat > 89.99:
            return self.status.error(
                f"Latitude must be between 0{DS} and 89{DS}59'59{DQ}.",
                self.latd,
            )
        if self.latdir.value == 1:
            lat = -lat
        try:
            long = (
                int(self.longd.text)
                + int(self.longm.text) / 60
                + int(self.longs.text or '0') / 3600
            )
        except Exception:
            return self.status.error('Longitude must be numeric.', self.longd)
        if long < 0 or long > 180:
            return self.status.error(
                f'Longitude must be between 0{DS} and 180{DS}.'
            )
        if self.longdir.value == 1:
            long = -long
        loc = [normalize_text(self.loc.text, True), lat, long]
        try:
            with open(HOME_LOC_FILE, 'w') as datafile:
                json.dump(loc, datafile, indent=4)
            return True
        except Exception:
            self.status.error('Unable to save home location.')
            return False

    def save(self):
        if not self.save_colors():
            return False
        if not self.save_fmt():
            return False
        if not self.save_student():
            return False
        if not self.save_home():
            return False
        self.status.text = 'Program options saved.'
        return True

    def restart(self):
        self.status.text = 'Restarting Time Matters.'
        if self.save():
            os.execl(sys.executable, sys.executable, *sys.argv)
            main.destroy()
