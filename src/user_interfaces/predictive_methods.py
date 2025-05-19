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
from src.utils.chart_utils import ut_time_correction
from src.utils.format_utils import (
    display_name,
    normalize_text,
    to360,
    toDMS,
)
from src.utils.gui_utils import ShowHelp
from src.utils.os_utils import open_file
from src.utils.transits.progressions import (
    ProgressionTypes,
    get_progressed_jd_utc,
)


class PredictiveMethods(Frame):
    def __init__(self, base, filename):
        super().__init__()
        now = dt.utcnow()
        chart = {}

        self.program_options = ProgramOptions.from_file(PROGRAM_OPTION_PATH)

        self.base = base
        self.filename = filename
        self.fnlbl = Label(self, display_name(filename), 0, 0, 1)

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

        self.options = Entry(self, 'Progressed Default', 0.3, 0.4, 0.3)

        Button(self, 'Select', 0.6, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.select_options)
        )
        Button(self, 'Temporary', 0.7, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.temp_options)
        )

        self.event = None
        Label(self, 'Transits', 0.15, 0.5, 0.3, anchor=tk.W)
        self.transits_to_natal = Checkbutton(self, 'Natal', 0.3, 0.5, 0.1)
        self.transits_to_ssr = Checkbutton(self, 'SSR', 0.4, 0.5, 0.1)

        self.transits_to_progressed_natal = Checkbutton(
            self, 'p Natal', 0.5, 0.5, 0.1
        )
        self.transits_to_solar_quotidian = Checkbutton(
            self, 'SQ', 0.6, 0.5, 0.1
        )

        Label(self, 'Progressions', 0.15, 0.55, 0.3, anchor=tk.W)
        self.sidereal_natal_quotidian = Checkbutton(
            self, 'SNQ', 0.3, 0.55, 0.1
        )
        self.solar_quotidian = Checkbutton(self, 'SQ', 0.4, 0.55, 0.1)

        self.pssr = Checkbutton(self, 'PSSR', 0.5, 0.55, 0.1)
        self.progressed_qssr = Checkbutton(self, 'p QSSR', 0.6, 0.55, 0.1)

        Button(self, 'Select All', 0.3, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_selections, True)
        )
        Button(self, 'Clear Selections', 0.5, 0.6, 0.2).bind(
            '<Button-1>', lambda _: delay(self.all_selections, False)
        )

        Label(self, 'Progression Rate', 0.15, 0.65, 0.15, anchor=tk.W)
        self.mean_or_apparent = Radiogroup(self)
        Radiobutton(self, self.mean_or_apparent, 0, 'Mean', 0.3, 0.65, 0.1)
        Radiobutton(self, self.mean_or_apparent, 1, 'Apparent', 0.4, 0.65, 0.1)
        self.mean_or_apparent.value = 0

        self.istemp = Radiogroup(self)
        Radiobutton(self, self.istemp, 0, 'Permanent Charts', 0.3, 0.7, 0.25)
        Radiobutton(self, self.istemp, 1, 'Temporary Charts', 0.5, 0.7, 0.25)
        self.istemp.value = 1

        Button(self, 'Calculate', 0, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.calculate)
        )

        Button(self, 'Help', 0.2, 0.95, 0.2).bind(
            '<Button-1>',
            lambda _: delay(
                ShowHelp, os.path.join(HELP_PATH, 'predictive.txt')
            ),
        )

        Button(self, 'Clear', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )

        backbtn = Button(self, 'Back', 0.8, 0.95, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.85, 1)

    def enable_find(self):
        self.findbtn.disabled = False

    def back(self):
        self.destroy()

        # This needs to be here to avoid a circular import
        from src.user_interfaces.select_chart import SelectChart

        SelectChart()

    def all_selections(self, value):
        self.transits_to_natal.checked = value
        self.transits_to_ssr.checked = value
        self.transits_to_progressed_natal.checked = value
        self.transits_to_solar_quotidian.checked = value

        self.sidereal_natal_quotidian.checked = value
        self.solar_quotidian.checked = value
        self.pssr.checked = value
        self.progressed_qssr.checked = value

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
        PredictiveMethods(self.base, self.filename)

    def calculate(self):
        self.status.text = ''
        self.findbtn.disabled = False
        params = {}
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
        if self.bce.checked:
            y = -y + 1
        params['year'] = y
        if m < 1 or m > 12:
            return self.status.error(
                'Month must be between 1 and 12.', self.datem
            )
        params['month'] = m
        if d < 1 or d > 31:
            return self.status.error(
                'Day must be between 1 and 31.', self.dated
            )
        params['day'] = d
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
        params['style'] = 0 if self.old.checked else 1
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
        params['time'] = time
        params['location'] = normalize_text(self.loc.text)
        if not params['location']:
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
        params['latitude'] = lat
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

        params['longitude'] = long
        params['notes'] = normalize_text(self.notes.text, True)
        params['options'] = self.options.text.strip()
        params['base_chart'] = self.base

        params['chart_type'] = 'snq'
        params['type'] = ChartType.SIDEREAL_NATAL_QUOTIDIAN.value
        params['use_transit'] = False

        radix = ChartObject(params['base_chart']).with_role(
            ChartWheelRole.RADIX
        )

        target_julian_day = swe.julday(
            params['year'],
            params['month'],
            params['day'],
            params['time'],
            params['style'],
        )

        progressed_jd = get_progressed_jd_utc(
            base_jd=radix.julian_day_utc,
            target_jd=target_julian_day,
            radix_sun_longitude=radix.planets['Sun'].longitude,
            progression_type=ProgressionTypes.Q2.value,
        )

        (p_year, p_month, p_day, p_time) = swe.revjul(
            progressed_jd, params['style']
        )

        p_hour = int(p_time)
        p_min = int((p_time - (int(p_time))) * 60)
        p_sec = int(
            (
                ((p_time - (int(p_time))) * 60)
                - int((p_time - (int(p_time))) * 60)
            )
            * 60
        )

        print(
            f'Derived progression date: {p_hour}:{p_min}:{p_sec} - {p_month} {p_day} {p_year}'
        )

        params['name'] = params['base_chart']['name']

        params['progressed_chart'] = {
            'year': p_year,
            'month': p_month,
            'day': p_day,
            'time': p_time,
            'zone': 'UT',
            'correction': 0,
            'type': ChartType.SIDEREAL_NATAL_QUOTIDIAN.value,
            'location': params['location'],
            'longitude': params['longitude'],
            'latitude': params['latitude'],
            'name': params['base_chart']['name'],
        }

        self.make_chart(
            params, progressed_jd, ChartType.SIDEREAL_NATAL_QUOTIDIAN, 'Q'
        )

    def make_chart(self, params, date, chtype, cclass, show=True):
        cchart = deepcopy(params)
        (y, m, d, t) = revjul(date, cchart['style'])
        cchart['year'] = y
        cchart['month'] = m
        cchart['day'] = d
        cchart['time'] = t
        cchart['name'] = (
            f"{cchart['base_chart']['name']}"
            if params.get('base_chart', None)
            else ''
        )
        cchart['type'] = chtype
        cchart['class'] = cclass
        cchart['correction'] = 0
        cchart['zone'] = 'UT'

        chart_class = assemble_charts(params, self.istemp)

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
