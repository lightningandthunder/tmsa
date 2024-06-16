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
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from copy import deepcopy
from datetime import datetime as dt

import anglicize
import us
from geopy import Nominatim

from chart import Chart
from constants import DQ, DS, VERSION
from gui_utils import ShowHelp
from init import *
from locations import Locations
from more_charts import MoreCharts
from swe import *
from utils import display_name, open_file, toDMS
from widgets import *


class Solunars(Frame):
    def __init__(self, base, filename):
        super().__init__()
        now = dt.utcnow()
        chart = {}
        self.base = base
        self.filename = filename
        self.fnlbl = Label(self, display_name(filename), 0, 0, 1)
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
        self.loc = Entry(self, base['location'], 0.3, 0.2, 0.3)
        self.loc.bind('<KeyRelease>', lambda _: delay(self.enable_find))
        Button(self, 'Recent', 0.6, 0.2, 0.1).bind(
            '<Button-1>', lambda _: delay(self.recent_loc)
        )
        self.findbtn = Button(self, 'Find', 0.7, 0.2, 0.1)
        self.findbtn.bind('<Button-1>', lambda _: delay(self.find))
        Label(self, 'Lat D M S', 0.15, 0.25, 0.15, anchor=tk.W)
        (d, m, s, si) = toDMS(base['latitude'])
        self.latd = Entry(self, d, 0.3, 0.25, 0.1)
        self.latd.bind('<KeyRelease>', lambda _: delay(check_num, self.latd))
        self.latm = Entry(self, m, 0.4, 0.25, 0.1)
        self.latm.bind('<KeyRelease>', lambda _: delay(check_num, self.latm))
        self.lats = Entry(self, s, 0.5, 0.25, 0.1)
        self.lats.bind('<KeyRelease>', lambda _: delay(check_num, self.lats))
        self.latdir = Radiogroup(self)
        Radiobutton(self, self.latdir, 0, 'North', 0.6, 0.25, 0.1)
        Radiobutton(self, self.latdir, 1, 'South', 0.7, 0.25, 0.1)
        self.latdir.value = 1 if si == -1 else 0
        Label(self, 'Long D M S', 0.15, 0.3, 0.15, anchor=tk.W)
        (d, m, s, si) = toDMS(base['longitude'])
        self.longd = Entry(self, d, 0.3, 0.3, 0.1)
        self.longd.bind('<KeyRelease>', lambda _: delay(check_num, self.longd))
        self.longm = Entry(self, m, 0.4, 0.3, 0.1)
        self.longm.bind('<KeyRelease>', lambda _: delay(check_num, self.longm))
        self.longs = Entry(self, s, 0.5, 0.3, 0.1)
        self.longs.bind('<KeyRelease>', lambda _: delay(check_num, self.longs))
        self.longdir = Radiogroup(self)
        Radiobutton(self, self.longdir, 0, 'East ', 0.6, 0.3, 0.1)
        Radiobutton(self, self.longdir, 1, 'West ', 0.7, 0.3, 0.1)
        self.longdir.value = 1 if si == -1 else 0
        Label(self, 'Notes', 0.15, 0.35, 0.15, anchor=tk.W)
        self.notes = Entry(self, '', 0.3, 0.35, 0.3)
        Label(self, 'Options', 0.15, 0.4, 0.15, anchor=tk.W)
        self.options = Entry(self, 'Default Return', 0.3, 0.4, 0.3)
        Button(self, 'Select', 0.6, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.select_options)
        )
        Button(self, 'Temporary', 0.7, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.temp_options)
        )
        Label(self, 'Optional Event', 0.15, 0.45, 0.15)
        Button(self, 'New Chart', 0.3, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.make_event)
        )
        Button(self, 'Find Chart', 0.45, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.more_files)
        )
        self.event = None
        Label(self, 'Solar Returns', 0.15, 0.5, 0.3, anchor=tk.W)
        self.mainsolar = Checkbutton(self, 'SSR', 0.3, 0.5, 0.1)
        self.demisolar = Checkbutton(self, 'DSSR', 0.4, 0.5, 0.1)
        self.fqsolar = Checkbutton(self, 'QSSR1', 0.5, 0.5, 0.1)
        self.lqsolar = Checkbutton(self, 'QSSR3', 0.6, 0.5, 0.1)
        Label(self, 'Lunar Returns', 0.15, 0.55, 0.3, anchor=tk.W)
        self.mainlunar = Checkbutton(self, 'SLR', 0.3, 0.55, 0.1)
        self.demilunar = Checkbutton(self, 'DSLR', 0.4, 0.55, 0.1)
        self.fqlunar = Checkbutton(self, 'QSLR1', 0.5, 0.55, 0.1)
        self.lqlunar = Checkbutton(self, 'QSLR3', 0.6, 0.55, 0.1)
        Button(self, 'Select All', 0.3, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_charts, True)
        )
        Button(self, 'Clear Selections', 0.5, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_charts, False)
        )
        self.oneyear = Checkbutton(
            self, 'All Selected Solunars For One Year', 0.3, 0.65, 0.4
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
            lambda _: delay(ShowHelp, os.path.join(HELP_PATH, 'solunars.txt')),
        )
        backbtn = Button(self, 'Back', 0.7, 0.8, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.9, 1)

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

    def back(self):
        self.destroy()
        from user_interfaces.select_chart import SelectChart

        SelectChart()

    def all_charts(self, value):
        self.mainsolar.checked = value
        self.demisolar.checked = value
        self.fqsolar.checked = value
        self.lqsolar.checked = value
        self.mainlunar.checked = value
        self.demilunar.checked = value
        self.fqlunar.checked = value
        self.lqlunar.checked = value

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
            filename = filename.replace('/', '\\')
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
            sec = 0
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
        self.notes.focus()

    def select_options(self):
        name = tkfiledialog.askopenfilename(
            initialdir=OPTION_PATH, filetypes=[['Option Files', '.opt']]
        )
        if not name:
            return
        name = name.replace('/', '\\')
        if not name.startswith(OPTION_PATH):
            return
        text = name.replace(OPTION_PATH, '').replace('_', ' ')
        self.options.text = text[1:-4]

    def temp_options(self):
        from user_interfaces.chart_options import ChartOptions

        ChartOptions(self.options.text, True, self.options)

    def clear(self):
        self.destroy()
        Solunars(self.base, self.filename)

    def calculate(self):
        self.status.text = ''
        self.findbtn.disabled = False
        chart = {}
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
        chart['style'] = 0 if self.old.checked else 1
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
        chart['location'] = normalize_text(self.loc.text)
        if not chart['location']:
            return self.status.error('Location must be specified.', self.loc)
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
        chart['notes'] = normalize_text(self.notes.text, True)
        chart['options'] = self.options.text.strip()
        chart['base_chart'] = self.base
        solunars = []
        if self.mainsolar.checked:
            solunars.append('Solar Return')
        if self.demisolar.checked:
            solunars.append('Demi-Solar Return')
        if self.fqsolar.checked:
            solunars.append('First Quarti-Solar Return')
        if self.lqsolar.checked:
            solunars.append('Last Quarti-Solar Return')
        if self.mainlunar.checked:
            solunars.append('Lunar Return')
        if self.demilunar.checked:
            solunars.append('Demi-Lunar Return')
        if self.fqlunar.checked:
            solunars.append('First Quarti-Lunar Return')
        if self.lqlunar.checked:
            solunars.append('Last Quarti-Lunar Return')
        if not solunars:
            self.status.error('No solunars selected.')
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
                self.make_chart(cchart, date, 'Event', 'N')
            else:
                filename = self.event[0:-3] + 'txt'
                if os.path.exists(filename):
                    open_file(filename)
        self.save_location(chart)
        if self.oneyear.checked:
            self.burst(chart, solunars)
        elif self.search.value == 0:
            self.asearch(chart, solunars)
        elif self.search.value == 1:
            self.fsearch(chart, solunars)
        elif self.search.value == 2:
            self.bsearch(chart, solunars)
        else:
            self.status.error('No search direction selected.')

    def fsearch(self, chart, solunars):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = chart['base_chart']['Sun'][0]
        moon = chart['base_chart']['Moon'][0]
        for sol in solunars:
            cchart = deepcopy(chart)
            sl = sol.lower()
            if 'solar' in sl:
                cclass = 'SR'
                if 'demi' in sl:
                    target = (sun + 180) % 360
                elif 'first' in sl:
                    target = (sun + 90) % 360
                elif 'last' in sl:
                    target = (sun + 270) % 360
                else:
                    target = sun
                date = calc_sun_crossing(target, start)
            elif 'lunar' in sl:
                cclass = 'LR'
                if 'demi' in sl:
                    target = (moon + 180) % 360
                elif 'first' in sl:
                    target = (moon + 90) % 360
                elif 'last' in sl:
                    target = (moon + 270) % 360
                else:
                    target = moon
                date = calc_moon_crossing(target, start)
            self.make_chart(chart, date, sol, cclass)

    def bsearch(self, chart, solunars):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = chart['base_chart']['Sun'][0]
        moon = chart['base_chart']['Moon'][0]
        for sol in solunars:
            sl = sol.lower()
            if 'solar' in sl:
                cclass = 'SR'
                if 'demi' in sl:
                    target = (sun + 180) % 360
                elif 'first' in sl:
                    target = (sun + 90) % 360
                elif 'last' in sl:
                    target = (sun + 270) % 360
                else:
                    target = sun
                date = calc_sun_crossing(target, start - 184)
                if date > start:
                    date = calc_sun_crossing(target, start - 367)
            elif 'lunar' in sl:
                cclass = 'LR'
                if 'demi' in sl:
                    target = (moon + 180) % 360
                elif 'first' in sl:
                    target = (moon + 90) % 360
                elif 'last' in sl:
                    target = (moon + 270) % 360
                else:
                    target = moon
                date = calc_moon_crossing(target, start - 15)
                if date > start:
                    date = calc_moon_crossing(target, start - 29)
            self.make_chart(chart, date, sol, cclass)

    def burst(self, chart, solunars):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = chart['base_chart']['Sun'][0]
        moon = chart['base_chart']['Moon'][0]
        if self.search.value == 2:
            start -= 366
        for sol in solunars:
            cchart = deepcopy(chart)
            sl = sol.lower()
            if 'solar' in sl:
                cclass = 'SR'
                if 'demi' in sl:
                    target = (sun + 180) % 360
                elif 'first' in sl:
                    target = (sun + 90) % 360
                elif 'last' in sl:
                    target = (sun + 270) % 360
                else:
                    target = sun
                date = calc_sun_crossing(target, start)
            elif 'lunar' in sl:
                cclass = 'LR'
                if 'demi' in sl:
                    target = (moon + 180) % 360
                elif 'first' in sl:
                    target = (moon + 90) % 360
                elif 'last' in sl:
                    target = (moon + 270) % 360
                else:
                    target = moon
                date = calc_moon_crossing(target, start)
            self.make_chart(chart, date, sol, cclass, False)
        for i in range(0, 366, 26):
            for sol in solunars:
                sl = sol.lower()
                if 'solar' in sl:
                    cclass = 'SR'
                    if 'demi' in sl:
                        target = (sun + 180) % 360
                    elif 'first' in sl:
                        target = (sun + 90) % 360
                    elif 'last' in sl:
                        target = (sun + 270) % 360
                    else:
                        target = sun
                    date = calc_sun_crossing(target, start)
                elif 'lunar' in sl:
                    cclass = 'LR'
                    if 'demi' in sl:
                        target = (moon + 180) % 360
                    elif 'first' in sl:
                        target = (moon + 90) % 360
                    elif 'last' in sl:
                        target = (moon + 270) % 360
                    else:
                        target = moon
                    date = calc_moon_crossing(target, start + i)
                    if date > start + 366:
                        continue
            self.make_chart(chart, date, sol, cclass, False)
        self.status.text = 'Charts complete.'

    def asearch(self, chart, solunars):
        found = False
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = chart['base_chart']['Sun'][0]
        moon = chart['base_chart']['Moon'][0]
        srs = []
        lrs = []
        for sol in solunars:
            sl = sol.lower()
            if 'solar' in sl:
                srs.append(sol)
            if 'lunar' in sl:
                lrs.append(sol)
        cclass = 'SR'
        if srs:
            cclass = 'SR'
            date = calc_sun_crossing(sun, start - 184)
            if date > start:
                if date - start <= 15 and srs[0] == 'Solar Return':
                    self.make_chart(chart, date, srs[0], cclass)
                date = calc_sun_crossing(sun, start - 367)
            if srs[0] == 'Solar Return':
                self.make_chart(chart, date, srs[0], cclass)
                found = True
                srs = srs[1:]
            dstart = date
        if srs:
            target = (sun + 180) % 360
            date = calc_sun_crossing(target, dstart)
            if date > start:
                if date - start <= 15 and srs[0] == 'Demi-Solar Return':
                    self.make_chart(chart, date, srs[0], cclass)
                    found = True
                qstart = dstart
            else:
                if srs[0] == 'Demi-Solar Return':
                    self.make_chart(chart, date, srs[0], cclass)
                    found = True
                qstart = date
            if srs[0] == 'Demi-Solar Return':
                srs = srs[1:]
        if srs:
            if qstart == dstart:
                target = (sun + 90) % 360
                chtype = 'First Quarti-Solar Return'
            else:
                target = (sun + 270) % 360
                chtype = 'Last Quarti-Solar Return'
            date = calc_sun_crossing(target, qstart)
            if date - start <= 15:
                self.make_chart(chart, date, chtype, cclass)
        if lrs:
            cclass = 'LR'
            date = calc_moon_crossing(moon, start - 15)
            if date > start:
                if date - start <= 1.25 and lrs[0] == 'Lunar Return':
                    self.make_chart(chart, date, lrs[0], cclass)
                date = calc_moon_crossing(moon, start - 29)
            if lrs[0] == 'Lunar Return':
                self.make_chart(chart, date, lrs[0], cclass)
                found = True
                lrs = lrs[1:]
            dstart = date
        if lrs:
            target = (moon + 180) % 360
            date = calc_moon_crossing(target, dstart)
            if date > start:
                if date - start <= 1.25 and lrs[0] == 'Demi-Lunar Return':
                    self.make_chart(chart, date, lrs[0], cclass)
                    found = True
                qstart = dstart
            else:
                if lrs[0] == 'Demi-Lunar Return':
                    self.make_chart(chart, date, lrs[0], cclass)
                    found = True
                qstart = date
            if lrs[0] == 'Demi-Lunar Return':
                lrs = lrs[1:]
        if lrs:
            if qstart == dstart:
                target = (moon + 90) % 360
                chtype = 'First Quarti-Lunar Return'
            else:
                target = (moon + 270) % 360
                chtype = 'Last Quarti-Lunar Return'
            date = calc_moon_crossing(target, qstart)
            if date - start <= 1.25:
                self.make_chart(chart, date, chtype, cclass)
                found = True
        if not found:
            self.status.error('No charts found.')

    def make_chart(self, chart, date, chtype, cclass, show=True):
        cchart = deepcopy(chart)
        (y, m, d, t) = revjul(date, cchart['style'])
        cchart['year'] = y
        cchart['month'] = m
        cchart['day'] = d
        cchart['time'] = t
        cchart['name'] = (
            f"{cchart['base_chart']['name']}"
            if chart.get('base_chart', None)
            else ''
        )
        cchart['type'] = chtype
        cchart['class'] = cclass
        cchart['correction'] = 0
        cchart['zone'] = 'UT'
        if show:
            Chart(cchart, self.istemp.value).report.show()
        else:
            Chart(cchart, self.istemp.value).report

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
