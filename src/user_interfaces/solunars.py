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
import pydash
import us
from geopy import Nominatim

from src import *
from src import swe
from src.constants import DQ, DS, MONTHS, VERSION
from src.models.charts import ChartObject, ChartType, ChartWheelRole
from src.models.options import ProgramOptions
from src.swe import *
from src.user_interfaces.chart_assembler import assemble_charts
from src.user_interfaces.locations import Locations
from src.user_interfaces.more_charts import MoreCharts
from src.user_interfaces.more_solunars import MoreSolunars
from src.user_interfaces.widgets import *
from src.utils.format_utils import (
    display_name,
    normalize_text,
    to360,
    toDMS,
)
from src.utils.gui_utils import ShowHelp
from src.utils.os_utils import open_file


class Solunars(Frame):
    def __init__(self, base, filename):
        super().__init__()
        now = dt.utcnow()
        chart = {}

        self.program_options = ProgramOptions.from_file(PROGRAM_OPTION_PATH)

        self.more_charts = {}

        self.base = base
        self.filename = filename
        self.fnlbl = Label(self, display_name(filename), 0, 0, 1)
        Label(self, 'Search', 0.15, 0.05, 0.15, anchor=tk.W)
        self.init = True
        self.search = Radiogroup(self)
        Radiobutton(self, self.search, 0, 'Active', 0.3, 0.05, 0.2).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 0)
        )
        Radiobutton(self, self.search, 1, 'Forward', 0.5, 0.05, 0.15).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 1)
        )
        Radiobutton(self, self.search, 2, 'Backward', 0.65, 0.05, 0.15).bind(
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
        self.options = Entry(self, 'Return Default', 0.3, 0.4, 0.3)
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
        Label(self, 'Solar Returns', 0.15, 0.5, 0.3, anchor=tk.W)
        self.mainsolar = Checkbutton(self, 'SSR', 0.3, 0.5, 0.1)
        self.demisolar = Checkbutton(self, 'DSSR', 0.4, 0.5, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.fqsolar = Checkbutton(self, 'QSSR1', 0.5, 0.5, 0.1)
            self.lqsolar = Checkbutton(self, 'QSSR3', 0.6, 0.5, 0.1)

        Label(self, 'Lunar Returns', 0.15, 0.55, 0.3, anchor=tk.W)
        self.mainlunar = Checkbutton(self, 'SLR', 0.3, 0.55, 0.1)
        self.demilunar = Checkbutton(self, 'DSLR', 0.4, 0.55, 0.1)

        if self.program_options.quarti_returns_enabled:
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

        Button(self, 'Calculate', 0, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.calculate)
        )
        Button(self, 'Help', 0.2, 0.95, 0.2).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, os.path.join(HELP_PATH, 'solunars.txt')),
        )
        Button(self, 'More Charts', 0.4, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.show_more_solunars)
        )
        Button(self, 'Clear', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        backbtn = Button(self, 'Back', 0.8, 0.95, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.85, 1)

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

        # This needs to be here to avoid a circular import
        from src.user_interfaces.select_chart import SelectChart

        SelectChart()

    def all_charts(self, value):
        self.mainsolar.checked = value
        self.demisolar.checked = value
        self.mainlunar.checked = value
        self.demilunar.checked = value

        if self.program_options.quarti_returns_enabled:
            self.fqsolar.checked = value
            self.lqsolar.checked = value
            self.fqlunar.checked = value
            self.lqlunar.checked = value

        if not value:
            self.more_charts = {}

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

    def show_more_solunars(self):
        MoreSolunars(
            self.more_charts, self.program_options, self.more_solunars_finish
        )

    def more_solunars_finish(self, selected):
        self.more_charts = selected

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
        solars = []
        lunars = []

        if self.mainsolar.checked:
            solunars.append('Solar Return')
            solars.append('Solar Return')
        if self.demisolar.checked:
            solunars.append('Demi-Solar Return')
            solars.append('Demi-Solar Return')
        if pydash.get(self, 'fqsolar.checked'):
            solunars.append('First Quarti-Solar Return')
            solars.append('First Quarti-Solar Return')
        if pydash.get(self, 'lqsolar.checked'):
            solunars.append('Last Quarti-Solar Return')
            solars.append('Last Quarti-Solar Return')

        if self.mainlunar.checked:
            solunars.append('Lunar Return')
            lunars.append('Lunar Return')
        if self.demilunar.checked:
            solunars.append('Demi-Lunar Return')
            lunars.append('Demi-Lunar Return')
        if pydash.get(self, 'fqlunar.checked'):
            solunars.append('First Quarti-Lunar Return')
            lunars.append('First Quarti-Lunar Return')
        if pydash.get(self, 'lqlunar.checked'):
            solunars.append('Last Quarti-Lunar Return')
            lunars.append('Last Quarti-Lunar Return')

        if self.more_charts.get('nsr'):
            solunars.append(ChartType.NOVIENIC_SOLAR_RETURN.value)
            solars.append(ChartType.NOVIENIC_SOLAR_RETURN.value)
        if self.more_charts.get('10-day'):
            solunars.append(ChartType.TEN_DAY_SOLAR_RETURN.value)
            solars.append(ChartType.TEN_DAY_SOLAR_RETURN.value)
        if self.more_charts.get('nlr'):
            solunars.append(ChartType.NOVIENIC_LUNAR_RETURN.value)
            lunars.append(ChartType.NOVIENIC_LUNAR_RETURN.value)
        if self.more_charts.get('18-hour'):
            solunars.append(ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value)
            lunars.append(ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value)

        if self.more_charts.get('solu'):
            solunars.append(ChartType.SOLILUNAR_RETURN.value)
            solars.append(ChartType.SOLILUNAR_RETURN.value)
        if self.more_charts.get('demi-solu'):
            solunars.append(ChartType.DEMI_SOLILUNAR_RETURN.value)
            solars.append(ChartType.DEMI_SOLILUNAR_RETURN.value)
        if self.more_charts.get('quarti-solu-1'):
            solunars.append(ChartType.FIRST_QUARTI_SOLILUNAR_RETURN.value)
            solars.append(ChartType.FIRST_QUARTI_SOLILUNAR_RETURN.value)
        if self.more_charts.get('quarti-solu-3'):
            solunars.append(ChartType.LAST_QUARTI_SOLILUNAR_RETURN.value)
            solars.append(ChartType.LAST_QUARTI_SOLILUNAR_RETURN.value)

        if self.more_charts.get('luso'):
            solunars.append(ChartType.LUNISOLAR_RETURN.value)
            lunars.append(ChartType.LUNISOLAR_RETURN.value)
        if self.more_charts.get('demi-luso'):
            solunars.append(ChartType.DEMI_LUNISOLAR_RETURN.value)
            lunars.append(ChartType.DEMI_LUNISOLAR_RETURN.value)
        if self.more_charts.get('quarti-luso-1'):
            solunars.append(ChartType.FIRST_QUARTI_LUNISOLAR_RETURN.value)
            lunars.append(ChartType.FIRST_QUARTI_LUNISOLAR_RETURN.value)
        if self.more_charts.get('quarti-luso-3'):
            solunars.append(ChartType.LAST_QUARTI_LUNISOLAR_RETURN.value)
            lunars.append(ChartType.LAST_QUARTI_LUNISOLAR_RETURN.value)

        if self.more_charts.get('sar'):
            solunars.append(ChartType.ANLUNAR_RETURN.value)
            lunars.append(ChartType.ANLUNAR_RETURN.value)
        if self.more_charts.get('demi-sar'):
            solunars.append(ChartType.DEMI_ANLUNAR_RETURN.value)
            lunars.append(ChartType.DEMI_ANLUNAR_RETURN.value)
        if self.more_charts.get('quarti-sar-1'):
            solunars.append(ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value)
            lunars.append(ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value)
        if self.more_charts.get('quarti-sar-3'):
            solunars.append(ChartType.LAST_QUARTI_ANLUNAR_RETURN.value)
            lunars.append(ChartType.LAST_QUARTI_ANLUNAR_RETURN.value)

        if self.more_charts.get('lsr'):
            solunars.append(ChartType.LUNAR_SYNODIC_RETURN.value)
            lunars.append(ChartType.LUNAR_SYNODIC_RETURN.value)
        if self.more_charts.get('demi-lsr'):
            solunars.append(ChartType.DEMI_LUNAR_SYNODIC_RETURN.value)
            lunars.append(ChartType.DEMI_LUNAR_SYNODIC_RETURN.value)
        if self.more_charts.get('quarti-lsr-1'):
            solunars.append(ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value)
            lunars.append(ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value)
        if self.more_charts.get('quarti-lsr-3'):
            solunars.append(ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value)
            lunars.append(ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value)

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

        chart['radix'] = ChartObject(self.base).with_role(ChartWheelRole.RADIX)
        chart['base_chart']['Sun'] = [chart['radix'].planets['Sun'].longitude]
        chart['base_chart']['Moon'] = [
            chart['radix'].planets['Moon'].longitude
        ]

        if self.oneyear.checked:
            self.burst(chart, solunars)
        elif self.search.value == 0:
            self.active_search(chart, solunars)
        elif self.search.value == 1:
            self.forward_search(chart, solunars)
        elif self.search.value == 2:
            self.backward_search(chart, solunars)
        else:
            self.status.error('No search direction selected.')

    def forward_search(self, chart, solunars):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = pydash.get(
            chart,
            'base_chart.Sun.[0]',
            pydash.get(chart, 'base_chart.planets.Sun.[0]'),
        )
        moon = pydash.get(
            chart,
            'base_chart.Moon.[0]',
            pydash.get(chart, 'base_chart.planets.Moon.[0]'),
        )

        for sol in solunars:
            target = sun
            sl = sol.lower()
            if (
                'solar' in sl
                and not 'solilunar' in sl
                and not 'lunisolar' in sl
            ):
                cclass = 'SR'
                if 'demi' in sl:
                    target = (sun + 180) % 360
                elif 'first' in sl:
                    target = (sun + 90) % 360
                elif 'last' in sl:
                    target = (sun + 270) % 360
                elif 'novienic' in sl:
                    increment = 40
                    while True:
                        target = to360(sun + increment)
                        test_date = calc_sun_crossing(target, start)
                        if test_date - start >= 41:
                            increment -= 40
                            continue

                        break
                elif '10-day' in sl:
                    increment = 10
                    while True:
                        target = to360(sun + increment)
                        test_date = calc_sun_crossing(target, start)
                        if test_date - start >= 11:
                            increment -= 10
                            continue
                        break

                date = calc_sun_crossing(target, start)

            elif (
                'lunar' in sl
                and not 'lunisolar' in sl
                and not 'solilunar' in sl
                and not 'anlunar' in sl
                and not 'synodic' in sl
            ):
                target = moon
                cclass = 'LR'
                if 'demi' in sl:
                    target = (moon + 180) % 360
                elif 'first' in sl:
                    target = (moon + 90) % 360
                elif 'last' in sl:
                    target = (moon + 270) % 360
                elif 'novienic' in sl:
                    increment = 40
                    while True:
                        target = to360(moon + increment)
                        test_date = calc_moon_crossing(target, start)
                        if test_date - start >= 3.45:
                            increment -= 40
                            continue
                        break
                elif '18-hour' in sl:
                    increment = 10
                    while True:
                        target = to360(moon + increment)
                        test_date = calc_moon_crossing(target, start)
                        if test_date - start >= 0.86:
                            increment += 10
                            continue
                        break

                date = calc_moon_crossing(target, start)

            elif 'solilunar' in sl:
                target = moon
                sl = sol.lower()
                cclass = 'SR'

                if 'demi' in sl:
                    target = (moon + 180) % 360
                elif 'first' in sl:
                    target = (moon + 90) % 360
                elif 'last' in sl:
                    target = (moon + 270) % 360

                date = calc_sun_crossing(target, start)

            elif 'lunisolar' in sl:
                target = sun
                sl = sol.lower()
                cclass = 'LR'

                if 'demi' in sl:
                    target = (sun + 180) % 360
                elif 'first' in sl:
                    target = (sun + 90) % 360
                elif 'last' in sl:
                    target = (sun + 270) % 360

                date = calc_moon_crossing(target, start)

            elif 'anlunar' in sl:
                cclass = 'LR'
                # Get previous solar return
                solar_return_date = calc_sun_crossing(sun, start - 366)
                (year, month, day, time) = revjul(
                    solar_return_date, chart['style']
                )

                ssr_params = {**chart}
                ssr_params.update(
                    {
                        'name': chart['base_chart']['name'] + ' Solar Return',
                        'julian_day_utc': solar_return_date,
                        'type': ChartType.SOLAR_RETURN.value,
                        'year': year,
                        'month': month,
                        'day': day,
                        'time': time,
                    }
                )

                ssr_chart = ChartObject(ssr_params)

                solar_moon = ssr_chart.planets['Moon'].longitude

                if 'demi' in sl:
                    target = (solar_moon + 180) % 360
                elif 'first' in sl:
                    target = (solar_moon + 90) % 360
                elif 'last' in sl:
                    target = (solar_moon + 270) % 360
                else:
                    target = solar_moon

                chart['ssr_chart'] = ssr_chart

                date = calc_moon_crossing(target, start)

            elif 'synodic' in sl:
                cclass = 'LR'

                precision = 5

                natal_elongation = get_signed_orb_to_reference(moon, sun)
                natal_elongation = round(natal_elongation, precision)

                target_elongation = natal_elongation

                if 'demi' in sl:
                    target_elongation = to360(natal_elongation + 180)
                elif 'first' in sl:
                    target_elongation = to360(natal_elongation + 90)
                elif 'last' in sl:
                    target_elongation = to360(natal_elongation + 270)

                if target_elongation > 180:
                    target_elongation -= 180
                    target_elongation *= -1

                lower_bound = start
                higher_bound = start + 29.5

                while True:
                    date = (lower_bound + higher_bound) / 2
                    test_elongation = swe.calc_signed_moon_elongation(date)
                    test_elongation = round(test_elongation, precision)

                    if (
                        target_elongation == test_elongation
                        or higher_bound <= lower_bound
                    ):
                        break

                    elif test_elongation > target_elongation:
                        higher_bound = date
                    else:
                        lower_bound = date

            self.make_chart(chart, date, sol, cclass)

    def backward_search(self, chart, solunars):
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )
        sun = pydash.get(
            chart,
            'base_chart.Sun.[0]',
            pydash.get(chart, 'base_chart.planets.Sun.[0]'),
        )
        moon = pydash.get(
            chart,
            'base_chart.Moon.[0]',
            pydash.get(chart, 'base_chart.planets.Moon.[0]'),
        )

        past_date_already_found = False

        for sol in solunars:
            normalized_name = sol.lower()
            if 'solar' in normalized_name:
                cclass = 'SR'
                if 'demi' in normalized_name:
                    target = (sun + 180) % 360
                elif 'first' in normalized_name:
                    target = (sun + 90) % 360
                elif 'last' in normalized_name:
                    target = (sun + 270) % 360
                elif 'novienic' in normalized_name:
                    past_date_already_found = True
                    increment = 40

                    base_date = start - 82

                    while True:
                        target = to360(sun + increment)
                        date = calc_sun_crossing(target, base_date)
                        if date > start - 40:
                            increment -= 40
                            if increment == 0:
                                increment -= 40

                            continue

                        if start - date >= 40:
                            increment -= 40
                            if increment == 0:
                                increment -= 40

                            continue

                        break

                elif '10-day' in normalized_name:
                    past_date_already_found = True
                    date_to_use = start - 20
                    increment = 10
                    while True:
                        target = to360(sun + increment)
                        date = calc_sun_crossing(target, date_to_use)
                        if date - start >= 21:
                            increment -= 10
                            if increment == 0:
                                increment -= 10
                            continue

                        break
                else:
                    target = sun

                if not past_date_already_found:
                    date = calc_sun_crossing(target, start - 184)

                    if date > start:
                        date = calc_sun_crossing(target, start - 367)

            elif 'lunar' in normalized_name:
                cclass = 'LR'
                if 'demi' in normalized_name:
                    target = (moon + 180) % 360
                elif 'first' in normalized_name:
                    target = (moon + 90) % 360
                elif 'last' in normalized_name:
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
        sun = pydash.get(
            chart,
            'base_chart.Sun.[0]',
            pydash.get(chart, 'base_chart.planets.Sun.[0]'),
        )
        moon = pydash.get(
            chart,
            'base_chart.Moon.[0]',
            pydash.get(chart, 'base_chart.planets.Moon.[0]'),
        )
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

    def active_search(self, chart, solunars):
        found = False
        start = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'],
            chart['style'],
        )

        sun = pydash.get(
            chart,
            'base_chart.Sun.[0]',
            pydash.get(chart, 'base_chart.planets.Sun.[0]'),
        )
        moon = pydash.get(
            chart,
            'base_chart.Moon.[0]',
            pydash.get(chart, 'base_chart.planets.Moon.[0]'),
        )

        solar_returns = []
        lunar_returns = []
        for sol in solunars:
            sl = sol.lower()
            if 'solilunar' in sl or ('solar' in sl and not 'lunisolar' in sl):
                solar_returns.append(sol)
            if 'lunisolar' in sl or ('lunar' in sl and not 'solilunar' in sl):
                lunar_returns.append(sol)
        chart_class = 'SR'
        if solar_returns:
            chart_class = 'SR'
            date = calc_sun_crossing(sun, start - 184)
            if date > start:
                if date - start <= 15 and solar_returns[0] == 'Solar Return':
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                date = calc_sun_crossing(sun, start - 367)
            if solar_returns[0] == 'Solar Return':
                self.make_chart(chart, date, solar_returns[0], chart_class)
                found = True
                solar_returns = solar_returns[1:]
            demi_start = date
        if solar_returns:
            target = (sun + 180) % 360
            date = calc_sun_crossing(target, demi_start)
            if date > start:
                if (
                    date - start <= 15
                    and solar_returns[0] == 'Demi-Solar Return'
                ):
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                    found = True
                quarti_start = demi_start
            else:
                if solar_returns[0] == 'Demi-Solar Return':
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                    found = True
                quarti_start = date
            if solar_returns[0] == 'Demi-Solar Return':
                solar_returns = solar_returns[1:]
        if solar_returns and solar_returns[0] in [
            'First Quarti-Solar Return',
            'Last Quarti-Solar Return',
        ]:
            if quarti_start == demi_start:
                target = (sun + 90) % 360
                chtype = 'First Quarti-Solar Return'
            else:
                target = (sun + 270) % 360
                chtype = 'Last Quarti-Solar Return'
            date = calc_sun_crossing(target, quarti_start)
            if date - start <= 15:
                self.make_chart(chart, date, chtype, chart_class)

        # NSR and 10-Day Solars
        if solar_returns and solar_returns[0] == 'Novienic Solar Return':
            increment = 40

            base_date = start - 42
            date_to_use = None

            while True:
                target = to360(sun + increment)
                test_date = calc_sun_crossing(target, base_date)
                if test_date > start:
                    increment -= 40
                    continue

                if start - test_date >= 40:
                    increment -= 40
                    continue

                date_to_use = test_date
                break

            self.make_chart(chart, date_to_use, solar_returns[0], chart_class)
            solar_returns = solar_returns[1:]
            found = True

        if solar_returns and solar_returns[0] == '10-Day Solar Return':
            increment = 10

            base_date = start - 12
            date_to_use = None

            while True:
                target = to360(sun + increment)
                test_date = calc_sun_crossing(target, base_date)
                if test_date > start:
                    increment -= 10
                    continue

                if start - test_date >= 10:
                    increment += 10
                    continue

                date_to_use = test_date
                break

            self.make_chart(chart, date_to_use, solar_returns[0], chart_class)
            solar_returns = solar_returns[1:]
            found = True

        # Solilunar variants
        if solar_returns:
            chart_class = 'SR'
            date = calc_sun_crossing(moon, start - 184)
            if date > start:
                if (
                    date - start <= 15
                    and solar_returns[0] == ChartType.SOLILUNAR_RETURN.value
                ):
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                date = calc_sun_crossing(moon, start - 367)
            if solar_returns[0] == ChartType.SOLILUNAR_RETURN.value:
                self.make_chart(chart, date, solar_returns[0], chart_class)
                found = True
                solar_returns = solar_returns[1:]
            demi_start = date
        if solar_returns:
            target = (moon + 180) % 360
            date = calc_sun_crossing(target, demi_start)
            if date > start:
                if (
                    date - start <= 15
                    and solar_returns[0]
                    == ChartType.DEMI_SOLILUNAR_RETURN.value
                ):
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                    found = True
                quarti_start = demi_start
            else:
                if solar_returns[0] == ChartType.DEMI_SOLILUNAR_RETURN.value:
                    self.make_chart(chart, date, solar_returns[0], chart_class)
                    found = True
                quarti_start = date
            if solar_returns[0] == ChartType.DEMI_SOLILUNAR_RETURN.value:
                solar_returns = solar_returns[1:]
        if solar_returns and solar_returns[0] in [
            ChartType.FIRST_QUARTI_SOLILUNAR_RETURN.value,
            ChartType.LAST_QUARTI_SOLILUNAR_RETURN.value,
        ]:
            if quarti_start == demi_start:
                target = (moon + 90) % 360
                chtype = ChartType.FIRST_QUARTI_SOLILUNAR_RETURN.value
            else:
                target = (moon + 270) % 360
                chtype = ChartType.LAST_QUARTI_SOLILUNAR_RETURN.value
            date = calc_sun_crossing(target, quarti_start)
            if date - start <= 15:
                self.make_chart(chart, date, chtype, chart_class)

        if lunar_returns:
            chart_class = 'LR'
            date = calc_moon_crossing(moon, start - 15)
            if date > start:
                if date - start <= 1.25 and lunar_returns[0] == 'Lunar Return':
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                date = calc_moon_crossing(moon, start - 29)
            if lunar_returns[0] == 'Lunar Return':
                self.make_chart(chart, date, lunar_returns[0], chart_class)
                found = True
                lunar_returns = lunar_returns[1:]
            demi_start = date
        if lunar_returns:
            target = (moon + 180) % 360
            date = calc_moon_crossing(target, demi_start)
            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0] == 'Demi-Lunar Return'
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = demi_start
            else:
                if lunar_returns[0] == 'Demi-Lunar Return':
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = date
            if lunar_returns[0] == 'Demi-Lunar Return':
                lunar_returns = lunar_returns[1:]
        if lunar_returns and lunar_returns[0] in [
            'First Quarti-Lunar Return',
            'Last Quarti-Lunar Return',
        ]:
            if quarti_start == demi_start:
                target = (moon + 90) % 360
                chtype = 'First Quarti-Lunar Return'
            else:
                target = (moon + 270) % 360
                chtype = 'Last Quarti-Lunar Return'
            date = calc_moon_crossing(target, quarti_start)
            if date - start <= 1.25:
                self.make_chart(chart, date, chtype, chart_class)
                found = True

        # NLR and 18-Hour Lunars
        if (
            lunar_returns
            and lunar_returns[0] == ChartType.NOVIENIC_LUNAR_RETURN.value
        ):
            increment = 40

            base_date = start - 4
            date_to_use = None

            while True:
                target = to360(moon + increment)
                test_date = calc_moon_crossing(target, base_date)
                if test_date > start:
                    increment -= 40
                    continue

                if start - test_date >= 3.45:
                    increment += 40
                    continue

                date_to_use = test_date
                break

            self.make_chart(chart, date_to_use, lunar_returns[0], chart_class)
            lunar_returns = lunar_returns[1:]
            found = True

        if (
            lunar_returns
            and lunar_returns[0] == ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value
        ):
            increment = 10

            base_date = start - 1
            date_to_use = None

            while True:
                target = to360(moon + increment)
                test_date = calc_moon_crossing(target, base_date)
                if test_date > start:
                    increment -= 10
                    continue

                if start - test_date >= 0.86:
                    increment += 10
                    continue

                date_to_use = test_date
                break

            self.make_chart(chart, date_to_use, lunar_returns[0], chart_class)
            lunar_returns = lunar_returns[1:]
            found = True

        # Lunisolar variants
        if lunar_returns and lunar_returns[0] in [
            ChartType.LUNISOLAR_RETURN.value,
            ChartType.DEMI_LUNISOLAR_RETURN.value,
            ChartType.FIRST_QUARTI_LUNISOLAR_RETURN.value,
            ChartType.LAST_QUARTI_LUNISOLAR_RETURN.value,
        ]:
            date = calc_moon_crossing(sun, start - 15)
            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0] == ChartType.LUNISOLAR_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                date = calc_moon_crossing(sun, start - 29)
            if lunar_returns[0] == ChartType.LUNISOLAR_RETURN.value:
                self.make_chart(chart, date, lunar_returns[0], chart_class)
                found = True
                lunar_returns = lunar_returns[1:]
            demi_start = date

        if lunar_returns:
            target = (sun + 180) % 360
            date = calc_moon_crossing(target, demi_start)
            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0]
                    == ChartType.DEMI_LUNISOLAR_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = demi_start
            else:
                if lunar_returns[0] == ChartType.DEMI_LUNISOLAR_RETURN.value:
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = date
            if lunar_returns[0] == ChartType.DEMI_LUNISOLAR_RETURN.value:
                lunar_returns = lunar_returns[1:]

        if lunar_returns:
            if quarti_start == demi_start:
                target = (sun + 90) % 360
                chtype = ChartType.FIRST_QUARTI_LUNISOLAR_RETURN.value
            else:
                target = (sun + 270) % 360
                chtype = ChartType.LAST_QUARTI_LUNISOLAR_RETURN.value
            date = calc_moon_crossing(target, quarti_start)
            if date - start <= 1.25:
                self.make_chart(chart, date, chtype, chart_class)
                found = True

        # Anlunars
        if lunar_returns and lunar_returns[0] in [
            ChartType.ANLUNAR_RETURN.value,
            ChartType.DEMI_ANLUNAR_RETURN.value,
            ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value,
            ChartType.LAST_QUARTI_ANLUNAR_RETURN.value,
        ]:
            chart_class = 'LR'
            # Get past SSR
            ssr_date = calc_sun_crossing(sun, start - 366)
            (year, month, day, time) = revjul(ssr_date, chart['style'])

            ssr_params = {**chart}
            ssr_params.update(
                {
                    'name': chart['base_chart']['name'] + ' Solar Return',
                    'julian_day_utc': ssr_date,
                    'type': ChartType.SOLAR_RETURN.value,
                    'year': year,
                    'month': month,
                    'day': day,
                    'time': time,
                }
            )

            ssr_chart = ChartObject(ssr_params)
            chart['ssr_chart'] = ssr_chart

            solar_moon = ssr_chart.planets['Moon'].longitude

            date = calc_moon_crossing(solar_moon, start - 15)
            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0] == ChartType.ANLUNAR_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                date = calc_moon_crossing(solar_moon, start - 29)
            if lunar_returns[0] == ChartType.ANLUNAR_RETURN.value:
                self.make_chart(chart, date, lunar_returns[0], chart_class)
                found = True
                lunar_returns = lunar_returns[1:]
            demi_start = date

            if lunar_returns:
                target = (solar_moon + 180) % 360
                date = calc_moon_crossing(target, demi_start)
                if date > start:
                    if (
                        date - start <= 1.25
                        and lunar_returns[0]
                        == ChartType.DEMI_ANLUNAR_RETURN.value
                    ):
                        self.make_chart(
                            chart, date, lunar_returns[0], chart_class
                        )
                        found = True
                    quarti_start = demi_start
                else:
                    if lunar_returns[0] == ChartType.DEMI_ANLUNAR_RETURN.value:
                        self.make_chart(
                            chart, date, lunar_returns[0], chart_class
                        )
                        found = True
                    quarti_start = date
                if lunar_returns[0] == ChartType.DEMI_ANLUNAR_RETURN.value:
                    lunar_returns = lunar_returns[1:]
            if lunar_returns and lunar_returns[0] in [
                ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value,
                ChartType.LAST_QUARTI_ANLUNAR_RETURN.value,
            ]:
                if quarti_start == demi_start:
                    target = (solar_moon + 90) % 360
                    chtype = ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value
                else:
                    target = (solar_moon + 270) % 360
                    chtype = ChartType.LAST_QUARTI_ANLUNAR_RETURN.value
                date = calc_moon_crossing(target, quarti_start)
                if date - start <= 1.25:
                    self.make_chart(chart, date, chtype, chart_class)
                    found = True

        if lunar_returns and 'Synodic' in lunar_returns[0]:
            chart_class = 'LR'

            natal_elongation = get_signed_orb_to_reference(moon, sun)

            full_lsr_elongation = natal_elongation
            if full_lsr_elongation > 180:
                full_lsr_elongation -= 180
                full_lsr_elongation *= -1

            date = find_jd_utc_of_elongation(
                full_lsr_elongation,
                start - 15,
                start + 14.5,
            )

            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0]
                    == ChartType.LUNAR_SYNODIC_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                date = find_jd_utc_of_elongation(
                    full_lsr_elongation,
                    start - 29.5,
                    start,
                )
            if lunar_returns[0] == ChartType.LUNAR_SYNODIC_RETURN.value:
                self.make_chart(chart, date, lunar_returns[0], chart_class)
                found = True
                lunar_returns = lunar_returns[1:]
            demi_start = date

        if lunar_returns:
            demi_elongation = to360(natal_elongation + 180)
            if demi_elongation > 180:
                demi_elongation -= 180
                demi_elongation *= -1

            date = find_jd_utc_of_elongation(
                demi_elongation,
                demi_start,
                demi_start + 29.5,
            )

            if date > start:
                if (
                    date - start <= 1.25
                    and lunar_returns[0]
                    == ChartType.DEMI_LUNAR_SYNODIC_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = demi_start
            else:
                if (
                    lunar_returns[0]
                    == ChartType.DEMI_LUNAR_SYNODIC_RETURN.value
                ):
                    self.make_chart(chart, date, lunar_returns[0], chart_class)
                    found = True
                quarti_start = date
            if lunar_returns[0] == ChartType.DEMI_LUNAR_SYNODIC_RETURN.value:
                lunar_returns = lunar_returns[1:]

        if lunar_returns and lunar_returns[0] in [
            ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value,
            ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value,
        ]:
            first_quarti_elongation = to360(natal_elongation + 90)
            if first_quarti_elongation > 180:
                first_quarti_elongation -= 180
                first_quarti_elongation *= -1

            last_quarti_elongation = -1 * first_quarti_elongation
            if last_quarti_elongation > 180:
                last_quarti_elongation -= 180
                last_quarti_elongation *= -1

            if quarti_start == demi_start:
                target = first_quarti_elongation
                chtype = ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value
            else:
                target = last_quarti_elongation
                chtype = ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value

            date = find_jd_utc_of_elongation(
                target,
                quarti_start,
                quarti_start + 29.5,
            )
            if date - start <= 1.25:
                self.make_chart(chart, date, chtype, chart_class)
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

        chart_class = assemble_charts(cchart, self.istemp.value)
        if show:
            chart_class.show()

        return chart_class

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
