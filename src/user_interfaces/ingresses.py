# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import random
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from copy import deepcopy
from datetime import datetime as dt

import anglicize
import us
from geopy import Nominatim

from src import *
from src.constants import DQ, DS, MONTHS, VERSION
from src.swe import *
from src.user_interfaces.chart_assembler import assemble_charts
from src.user_interfaces.locations import Locations
from src.user_interfaces.more_charts import MoreCharts
from src.user_interfaces.widgets import *
from src.utils.format_utils import display_name, normalize_text
from src.utils.gui_utils import ShowHelp, open_file


class Ingresses(Frame):
    def __init__(self):
        super().__init__()
        now = dt.utcnow()
        chart = {}
        Label(self, 'Search', 0.15, 0.05, 0.15, anchor=tk.W)
        self.init = True
        self.search = Radiogroup(self)
        Radiobutton(
            self, self.search, 0, 'Active Charts', 0.3, 0.05, 0.2
        ).bind('<Button-1>', lambda _: delay(self.toggle_year, 0))
        Radiobutton(self, self.search, 1, 'Forwards', 0.5, 0.05, 0.15).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 1)
        )
        Radiobutton(self, self.search, 2, 'Backwards', 0.65, 0.05, 0.15).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 2)
        )
        self.search.value = 0
        self.search.focus()
        self.init = False
        Label(self, 'Date ' + DATE_FMT, 0.15, 0.1, 0.15, anchor=tk.W)
        if DATE_FMT == 'D M Y':
            self.dated = Entry(self, now.strftime('%d'), 0.3, 0.1, 0.1)
            self.datem = Entry(self, now.strftime('%m'), 0.4, 0.1, 0.1)
        else:
            self.datem = Entry(self, now.strftime('%m'), 0.3, 0.1, 0.1)
            self.dated = Entry(self, now.strftime('%d'), 0.4, 0.1, 0.1)
        self.datey = Entry(self, now.strftime('%Y'), 0.5, 0.1, 0.1)
        self.datey.bind('<FocusOut>', lambda _: delay(self.check_style))
        self.datem.bind('<KeyRelease>', lambda _: delay(check_num, self.datem))
        self.dated.bind('<KeyRelease>', lambda _: delay(check_num, self.dated))
        self.datey.bind(
            '<KeyRelease>',
            lambda _: delay(check_snum, self.datem),
        )
        self.bce = Checkbutton(self, 'BC/BCE', 0.6, 0.1, 0.1, focus=False)
        self.old = Checkbutton(self, 'OS', 0.7, 0.1, 0.1, focus=False)
        Label(self, 'Time UT H M S ', 0.15, 0.15, 0.15, anchor=tk.W)
        h = '%I' if TIME_FMT == 'AM/PM' else '%H'
        self.timeh = Entry(self, now.strftime(h), 0.3, 0.15, 0.1)
        maxh = 12 if TIME_FMT == 'AM/PM' else 23
        self.timeh.bind('<KeyRelease>', lambda _: delay(check_num, self.timeh))
        self.timem = Entry(self, now.strftime('%M'), 0.4, 0.15, 0.1)
        self.timem.bind('<KeyRelease>', lambda _: delay(check_num, self.timem))
        self.times = Entry(self, now.strftime('%S'), 0.5, 0.15, 0.1)
        self.times.bind('<KeyRelease>', lambda _: delay(check_num, self.times))
        self.tmfmt = Radiogroup(self)
        if TIME_FMT == '24 Hour':
            Radiobutton(self, self.tmfmt, 2, '24 Hour Clock', 0.6, 0.15, 0.2)
            self.tmfmt.value = 2
        else:
            Radiobutton(self, self.tmfmt, 0, 'AM', 0.6, 0.15, 0.1)
            Radiobutton(self, self.tmfmt, 1, 'PM', 0.7, 0.15, 0.1)
            if now.strftime('%p') == 'PM':
                self.tmfmt.value = 1
        Label(self, 'Location', 0.15, 0.2, 0.15, anchor=tk.W)
        self.loc = Entry(self, '', 0.3, 0.2, 0.3)
        self.loc.bind('<KeyRelease>', lambda _: delay(self.enable_find))
        Button(self, 'Recent', 0.6, 0.2, 0.1).bind(
            '<Button-1>', lambda _: delay(self.recent_loc)
        )
        self.findbtn = Button(self, 'Find', 0.7, 0.2, 0.1)
        self.findbtn.bind('<Button-1>', lambda _: delay(self.find))
        Label(self, 'Lat D M S', 0.15, 0.25, 0.15, anchor=tk.W)
        self.latd = Entry(self, '', 0.3, 0.25, 0.1)
        self.latd.bind('<KeyRelease>', lambda _: delay(check_num, self.latd))
        self.latm = Entry(self, '', 0.4, 0.25, 0.1)
        self.latm.bind('<KeyRelease>', lambda _: delay(check_num, self.latm))
        self.lats = Entry(self, '0', 0.5, 0.25, 0.1)
        self.lats.bind('<KeyRelease>', lambda _: delay(check_num, self.lats))
        self.latdir = Radiogroup(self)
        Radiobutton(self, self.latdir, 0, 'North', 0.6, 0.25, 0.1)
        Radiobutton(self, self.latdir, 1, 'South', 0.7, 0.25, 0.1)
        Label(self, 'Long D M S', 0.15, 0.3, 0.15, anchor=tk.W)
        self.longd = Entry(self, '', 0.3, 0.3, 0.1)
        self.longd.bind('<KeyRelease>', lambda _: delay(check_num, self.longd))
        self.longm = Entry(self, '', 0.4, 0.3, 0.1)
        self.longm.bind('<KeyRelease>', lambda _: delay(check_num, self.longm))
        self.longs = Entry(self, '0', 0.5, 0.3, 0.1)
        self.longs.bind('<KeyRelease>', lambda _: delay(check_num, self.longs))
        self.longdir = Radiogroup(self)
        Radiobutton(self, self.longdir, 0, 'East ', 0.6, 0.3, 0.1)
        Radiobutton(self, self.longdir, 1, 'West ', 0.7, 0.3, 0.1)
        self.longdir.value = 1
        Label(self, 'Notes', 0.15, 0.35, 0.15, anchor=tk.W)
        self.notes = Entry(self, '', 0.3, 0.35, 0.3)
        Label(self, 'Options', 0.15, 0.4, 0.15, anchor=tk.W)
        self.options = Entry(self, 'Ingress Default', 0.3, 0.4, 0.3)
        Button(self, 'Select', 0.6, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.select_options)
        )
        Button(self, 'Temporary', 0.7, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.temp_options)
        )
        Label(self, 'Opt. Event', 0.15, 0.45, 0.15)
        Button(self, 'New Chart', 0.3, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.make_event)
        )
        Button(self, 'Find Chart', 0.45, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.more_files)
        )
        self.event = None
        Label(self, 'Solar Ingress', 0.15, 0.5, 0.3, anchor=tk.W)
        self.capsolar = Checkbutton(self, 'Capricorn', 0.3, 0.5, 0.13)
        self.cansolar = Checkbutton(self, 'Cancer', 0.43, 0.5, 0.09)
        self.arisolar = Checkbutton(self, 'Aries', 0.52, 0.5, 0.09)
        self.libsolar = Checkbutton(self, 'Libra', 0.61, 0.5, 0.09)
        Label(self, 'Lunar Ingress', 0.15, 0.55, 0.3, anchor=tk.W)
        self.caplunar = Checkbutton(self, 'Capricorn', 0.3, 0.55, 0.13)
        self.canlunar = Checkbutton(self, 'Cancer', 0.43, 0.55, 0.09)
        self.arilunar = Checkbutton(self, 'Aries', 0.52, 0.55, 0.09)
        self.liblunar = Checkbutton(self, 'Libra', 0.61, 0.55, 0.09)
        Button(self, 'Select All', 0.3, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_charts, True)
        )
        Button(self, 'Clear Selections', 0.5, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_charts, False)
        )
        self.oneyear = Checkbutton(
            self, 'All Selected Ingresses For One Year', 0.3, 0.65, 0.4
        )
        self.oneyear.config(state=tk.DISABLED)
        self.istemp = Radiogroup(self)
        Radiobutton(self, self.istemp, 0, 'Permanent Charts', 0.3, 0.7, 0.25)
        Radiobutton(self, self.istemp, 1, 'Temporary Charts', 0.5, 0.7, 0.25)
        self.istemp.value = 1
        Button(self, 'Calculate', 0.1, 0.8, 0.2).bind(
            '<Button-1>', lambda _: delay(self.calculate)
        )
        Button(self, 'Clear', 0.3, 0.8, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        Button(self, 'Help', 0.5, 0.8, 0.2).bind(
            '<Button-1>',
            lambda _: delay(
                ShowHelp, os.path.join(HELP_PATH, 'ingresses.txt')
            ),
        )
        Button(self, 'Back', 0.7, 0.8, 0.20).bind(
            '<Button-1>', lambda _: delay(self.destroy)
        )
        self.status = Label(self, '', 0, 0.9, 1)
        if HOME_LOC:
            self.loc.text = HOME_LOC[0]
            value = HOME_LOC[1]
            if value < 0:
                value = -value
                self.latdir.value = 1
            else:
                self.latdir.value = 0
            degree = int(value)
            value = (value - degree) * 60
            minute = int(value)
            value = (value - minute) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                minute += 1
            if minute == 60:
                minute = 0
                degree += 1
            self.latd.text = degree
            self.latm.text = minute
            self.lats.text = sec
            value = HOME_LOC[2]
            if value < 0:
                value = -value
                self.longdir.value = 1
            else:
                self.longdir.value = 0
            degree = int(value)
            value = (value - degree) * 60
            minute = int(value)
            value = (value - minute) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                minute += 1
            if minute == 60:
                minute = 0
                degree += 1
            self.longd.text = degree
            self.longm.text = minute
            self.longs.text = sec

    def enable_find(self):
        self.findbtn.disabled = False

    def toggle_year(self, value):
        if self.init:
            return
        if value == 0:
            self.oneyear.checked = False
            self.oneyear.config(state=tk.DISABLED)
        else:
            self.oneyear.config(state=tk.NORMAL)
        self.init = True
        self.search.value = value
        self.init = False

    def all_charts(self, value):
        self.capsolar.checked = value
        self.cansolar.checked = value
        self.arisolar.checked = value
        self.libsolar.checked = value
        self.caplunar.checked = value
        self.canlunar.checked = value
        self.arilunar.checked = value
        self.liblunar.checked = value

    def more_finish(self, selected):
        if selected:
            filename = selected
        else:
            self.status.error('No event chart chosen.')
            filename = tkfiledialog.askopenfilename(
                initialdir=CHART_PATH, filetypes=[('Chart Files', '*.dat')]
            )
            if not filename:
                return
            filename = filename.replace('/', os.path.sep)
        self.status.text = f' Event Chart: {display_name(filename)}'
        self.event = filename
        try:
            with open(self.event) as datafile:
                echart = json.load(datafile)
        except Exception:
            return self.status.error(
                f"Unable to open file '{os.path.basename(self.event)}'."
            )
        y = echart['year']
        m = echart['month']
        d = echart['day']
        t = echart['time'] + echart['correction']
        g = echart['style']
        (y, m, d, t) = revjul(julday(y, m, d, t, g), g)
        if y < 1:
            y = -y + 1
            self.bce.checked = True
        else:
            self.bce.checked = False
        self.datey.text = y
        self.datem.text = m
        self.dated.text = d
        self.old.checked = not g
        hr = int(t)
        t = 60 * (t - hr)
        mi = int(t)
        t = 60 * (t - mi)
        se = round(t)
        if se == 60:
            se = 0
            mi += 1
        if mi == 60:
            mi = 0
            hr += 1
        if hr == 24:
            hr = 0
            (y, m, d, t) = revjul(julday(y, m, d + 1, 0, g), g)
        self.datey.text = y
        self.datem.text = m
        self.dated.text = d
        self.timeh.text = hr
        self.timem.text = mi
        self.times.text = se
        if TIME_FMT == 'AM/PM':
            self.tmfmt.value == 1 if hr >= 12 else 0
            if hr > 12:
                self.timeh.text = hr - 12
            if hr == 0:
                self.timeh.text = 12
        self.loc.text = echart['location']
        lat = echart['latitude']
        self.latdir.value = 1 if lat < 0 else 0
        lat = abs(lat)
        d = int(lat)
        lat = 60 * (lat - d)
        m = int(lat)
        lat = 60 * (lat - m)
        s = round(lat)
        self.latd.text = d
        self.latm.text = m
        self.lats.text = s
        long = echart['longitude']
        self.longdir.value = 1 if long < 0 else 0
        long = abs(long)
        d = int(long)
        long = 60 * (long - d)
        m = int(long)
        lat = 60 * (long - m)
        s = round(long)
        self.longd.text = d
        self.longm.text = m
        self.longs.text = s
        filename = filename[0:-3] + 'txt'

    def more_files(self):
        self.event = None
        try:
            with open(RECENT_FILE, 'r') as datafile:
                recs = json.load(datafile)
        except Exception:
            self.status.error("Can't open 'recent.json' file.")
        delay(MoreCharts, recs, self.more_finish, 0)

    def make_event(self):
        self.event = '<'
        save = self.options.text
        self.select_options()
        self.eopt = self.options.text
        self.options.text = save
        self.status.text = (
            f"Event chart will be calculated using options '{self.eopt}'"
        )

    def check_style(self):
        try:
            y = int(self.datey.text)
        except Exception:
            return
        self.old.checked = True if y < 1583 else False

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
        self.longdir.value = 0 if direc == 'E' else 1

    def recent_loc(self):
        try:
            with open(LOCATIONS_FILE, 'r') as datafile:
                recs = json.load(datafile)
            if len(recs) == 0:
                return self.status.error('No saved locations.')
            delay(Locations, recs, self.loc_finish)
        except Exception as e:
            self.status.error("Can't open 'locations.json'.")

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
        except Exception as e:
            return self.status.error(
                f'Unable to connect to location database.', self.loc
            )
        if not location:
            return self.status.error(
                f"'{self.loc.text}' not in database.", self.loc
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

    def select_options(self):
        name = tkfiledialog.askopenfilename(
            initialdir=OPTION_PATH, filetypes=[['Option Files', '.opt']]
        )
        if not name:
            return
        name = name.replace('/', os.path.sep)
        if not name.startswith(OPTION_PATH):
            return
        text = name.replace(OPTION_PATH, '').replace('_', ' ')
        self.options.text = text[1:-4]

    def temp_options(self):
        from src.user_interfaces.chart_options import ChartOptions

        ChartOptions(self.options.text, True, self.options)

    def clear(self):
        self.destroy()
        Ingresses()

    def calculate(self):
        self.status.text = ''
        self.findbtn.disabled = True
        chart = {}
        self.status.text = ''
        chart['location'] = normalize_text(self.loc.text) or 'Undisclosed'
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
        chart['latitude'] = lat
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
                f'Longitude must be between 0{DS} and 180{DS}.', self.longd
            )
        if self.longdir.value == 1:
            long = -long
        chart['longitude'] = long
        try:
            y = int(self.datey.text)
            m = int(self.datem.text)
            d = int(self.dated.text)
        except Exception:
            return self.status.error('Date must be numeric.')
        if not self.bce.checked and y < 1:
            y = -y + 1
            self.datey.text = y
            self.bce.checked = True
        if y < 1 or y > 3000:
            return self.status.error(
                'Year must be between 1 and 3000.', self.datey
            )
        if self.bce.checked:
            y = -y + 1
        chart['year'] = y
        if m < 1 or m > 12:
            return self.status.error(
                'Month must be between 1 and 12.', self.datem
            )
        chart['month'] = m
        if d < 1 or d > 31:
            return self.status.error(
                'Day must be between 1 and 31.', self.dated
            )
            return
        chart['day'] = d
        z = str(y) if y > 0 else str(-y + 1) + ' BCE'
        if self.old.checked and y > 1582:
            if not tkmessagebox.askyesno(
                'Are you sure?',
                f'Is {d} {MONTHS[m -1]} {z} old style (Julian)?',
            ):
                return
        elif not self.old.checked and y <= 1582:
            if not tkmessagebox.askyesno(
                'Are you sure?',
                f'Is {d} {MONTHS[m -1]} {z} new style (Gregorian)?',
            ):
                return
        try:
            time = (
                int(self.timeh.text)
                + int(self.timem.text) / 60
                + int(self.times.text or '0') / 3600
            )
        except Exception:
            return self.status.error('Time must be numeric.', self.timeh)
        if TIME_FMT == '24 Hour':
            if time < 0 or time >= 24:
                return self.status.error(
                    'Time must be between 0:0:0 and 23:59:59', self.timeh
                )
        else:
            if time == 12:
                if self.tmfmt.value:
                    message = 'The chosen time 12:00:00 PM means noon.\n'
                    message += (
                        'For midnight at the beginning of the day, chose AM.\n'
                    )
                    message += 'For midnight at the end of the day, choose AM and add a day to the date.'
                else:
                    message = 'The chosen time 12:00:00 AM means midnight at the beginning of the day.\n'
                    message += 'For noon, chose PM\n'
                    message += 'For midnight at the end of the day, choose AM and add a day to the date.'
                if not tkmessagebox.askyesno('Is this correct?', message):
                    return
            if time < 0 or time >= 13:
                return self.status.error(
                    'Time must be between 0:0:0 and 12:59:59', self.timeh
                )
            if time >= 12:
                time -= 12
            if self.tmfmt.value == 1:
                time += 12
        chart['time'] = time
        chart['style'] = 0 if self.old.checked else 1
        chart['notes'] = normalize_text(self.notes.text, True)
        chart['options'] = self.options.text.strip()

        ingresses = []
        if self.capsolar.checked:
            ingresses.append('Capsolar')
        if self.cansolar.checked:
            ingresses.append('Cansolar')
        if self.arisolar.checked:
            ingresses.append('Arisolar')
        if self.libsolar.checked:
            ingresses.append('Libsolar')
        if self.caplunar.checked:
            ingresses.append('Caplunar')
        if self.canlunar.checked:
            ingresses.append('Canlunar')
        if self.arilunar.checked:
            ingresses.append('Arilunar')
        if self.liblunar.checked:
            ingresses.append('Liblunar')
        if not ingresses:
            self.status.error('No ingresses selected.')
            return
        if self.event:
            if self.event == '<':
                cchart = deepcopy(chart)
                date = julday(
                    cchart['year'],
                    cchart['month'],
                    cchart['day'],
                    cchart['time'],
                    cchart['style'],
                )
                cchart['options'] = self.eopt
                cchart['base_chart'] = None
                self.make_chart(cchart, date, 'Event')
            else:
                filename = self.event[0:-3] + 'txt'
                if os.path.exists(filename):
                    open_file(filename)
        self.save_location(chart)
        if self.oneyear.checked:
            self.burst(chart, ingresses)
        elif self.search.value == 0:
            self.asearch(chart, ingresses)
        elif self.search.value == 1:
            self.fsearch(chart, ingresses)
        elif self.search.value == 2:
            self.bsearch(chart, ingresses)
        else:
            self.status.error('No search direction selected.')

    def fsearch(self, chart, ingresses):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        for ing in ingresses:
            if 'Ari' in ing:
                target = 0
            if 'Can' in ing:
                target = 90
            if 'Lib' in ing:
                target = 180
            if 'Cap' in ing:
                target = 270
            if 'solar' in ing:
                date = calc_sun_crossing(target, start)
            if 'lunar' in ing:
                date = calc_moon_crossing(target, start)
            self.make_chart(chart, date, ing)

    def bsearch(self, chart, ingresses):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        for ing in ingresses:
            if 'Ari' in ing:
                target = 0
            if 'Can' in ing:
                target = 90
            if 'Lib' in ing:
                target = 180
            if 'Cap' in ing:
                target = 270
            if 'solar' in ing:
                date = calc_sun_crossing(target, start - 184)
                if date > start:
                    date = calc_sun_crossing(target, start - 367)
            if 'lunar' in ing:
                date = calc_moon_crossing(target, start - 15)
                if date > start:
                    date = calc_moon_crossing(target, start - 29)
            self.make_chart(chart, date, ing)

    def burst(self, chart, ingresses):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        if self.search.value == 2:
            start -= 366
        for ing in ingresses:
            if 'solar' in ing:
                if 'Ari' in ing:
                    target = 0
                if 'Can' in ing:
                    target = 90
                if 'Lib' in ing:
                    target = 180
                if 'Cap' in ing:
                    target = 270
                date = calc_sun_crossing(target, start)
                self.make_chart(chart, date, ing, False)
        for i in range(0, 366, 26):
            for ing in ingresses:
                if 'lunar' in ing:
                    if 'Ari' in ing:
                        target = 0
                    if 'Can' in ing:
                        target = 90
                    if 'Lib' in ing:
                        target = 180
                    if 'Cap' in ing:
                        target = 270
                    date = calc_moon_crossing(target, start + i)
                    self.make_chart(chart, date, ing, False)
                    if date > start + 366:
                        continue
        self.status.text = 'Charts complete.'

    def asearch(self, chart, ingresses):
        found = False
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        for ing in ingresses:
            cchart = deepcopy(chart)
            if 'Ari' in ing:
                target = 0
            if 'Can' in ing:
                target = 90
            if 'Lib' in ing:
                target = 180
            if 'Cap' in ing:
                target = 270
            if 'solar' in ing:
                date = calc_sun_crossing(target, start - 184)
                if date > start:
                    date = calc_sun_crossing(target, start - 367)
                found = True
                self.make_chart(chart, date, ing)
            if 'lunar' in ing:
                date = calc_moon_crossing(target, start - 15)
                if date > start:
                    date = calc_moon_crossing(target, start - 29)
                found = True
                self.make_chart(chart, date, ing)
        if not found:
            self.status.error('No charts found.')

    def make_chart(self, chart, date, chtype, show=True):
        cchart = deepcopy(chart)
        (y, m, d, t) = revjul(date, cchart['style'])
        cchart['year'] = y
        cchart['month'] = m
        cchart['day'] = d
        cchart['time'] = t
        cchart['name'] = ''
        cchart['type'] = chtype
        cchart['class'] = 'I'
        cchart['correction'] = 0
        cchart['zone'] = 'UT'
        if show:
            assemble_charts(cchart, self.istemp.value).show()
        else:
            assemble_charts(cchart, self.istemp.value)

    def save_location(self, chart):
        try:
            with open(LOCATIONS_FILE, 'r') as datafile:
                locs = json.load(datafile)
            newloc = [chart['location'], chart['latitude'], chart['longitude']]
            if newloc in locs:
                locs.remove(newloc)
            locs.insert(0, newloc)
            if len(locs) > 50:
                locs = locs[0:50]
            with open(LOCATIONS_FILE, 'w') as datafile:
                locs = json.dump(locs, datafile, indent=4)
        except Exception:
            pass
