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
from src.constants import DQ, DS, MONTHS, VERSION
from src.models.charts import (
    ANLUNAR_FAMILY,
    KAR_FAMILY,
    KLR_FAMILY,
    KSR_FAMILY,
    LSR_FAMILY,
    LUNAR_RETURN_FAMILY,
    LUNAR_RETURNS,
    LUNISOLAR_FAMILY,
    NLR_FAMILY,
    NSR_FAMILY,
    SOLAR_RETURN_FAMILY,
    SOLAR_RETURNS,
    SOLILUNAR_FAMILY,
    SOLUNAR_FAMILIES,
    ChartObject,
    ChartType,
    ChartWheelRole,
)
from src.models.options import ProgramOptions
from src.swe import *
from src.user_interfaces.chart_assembler import assemble_charts
from src.user_interfaces.locations import Locations
from src.user_interfaces.more_charts import MoreCharts
from src.user_interfaces.widgets import *
from src.utils.chart_utils import includes_any
from src.utils.format_utils import display_name, normalize_text, to360, toDMS
from src.utils.gui_utils import ShowHelp
from src.utils.os_utils import open_file
from src.utils.solunars import (
    append_applicable_returns,
    find_julian_days_for_aspect_to_progressed_body,
    find_novienic_crossings_until_date,
    find_progressed_anlunar_crossings_until_date,
    find_progressed_crossings_until_date,
    find_solunar_crossings_until_date,
    set_up_progressed_params,
)


class SolunarsAllInOne(Frame):
    def __init__(self, base, filename, program_options: ProgramOptions):
        super().__init__()
        now = dt.utcnow()

        self.bind_all('<Button-1>', self.on_global_click, add='+')

        self._options = (
            CHART_OPTIONS_FULL
            if program_options.quarti_returns_enabled
            else CHART_OPTIONS_NO_QUARTIS
        )
        self._in_callback = False

        self._previous_selections = []

        self.program_options = program_options
        self.more_charts = {}

        self.base = base
        self.filename = filename
        self.filename_label = Label(self, display_name(filename), 0, 0, 1)

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
        h = '%I' if TIME_FMT == 'AM/PM' else '%H'
        self.timeh = Entry(self, now.strftime(h), 0.3, 0.15, 0.1)

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
        self.loc = Entry(self, base['location'], 0.3, 0.2, 0.3)
        self.loc.bind('<KeyRelease>', lambda _: delay(self.enable_find))
        Button(self, 'Recent', 0.6, 0.2, 0.1).bind(
            '<Button-1>', lambda _: delay(self.recent_loc)
        )
        self.findbtn = Button(self, 'Find', 0.7, 0.2, 0.1)
        self.findbtn.bind('<Button-1>', lambda _: delay(self.find))
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

        self.notes = Entry(
            self,
            '',
            0.3,
            0.35,
            0.3,
        )
        self.options = Entry(self, 'Return Default', 0.3, 0.4, 0.3)
        Button(self, 'Select', 0.6, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.select_options)
        )
        Button(self, 'Temporary', 0.7, 0.4, 0.1).bind(
            '<Button-1>', lambda _: delay(self.temp_options)
        )
        Button(self, 'New Chart', 0.3, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.make_event)
        )
        Button(self, 'Find Chart', 0.45, 0.45, 0.15).bind(
            '<Button-1>', lambda _: delay(self.more_files)
        )
        self.event = None

        Label(self, 'Date ' + DATE_FMT, 0.1, 0.1, 0.15, anchor=tk.W)
        Label(self, 'Time UT H M S ', 0.1, 0.15, 0.15, anchor=tk.W)
        Label(self, 'Location', 0.1, 0.2, 0.15, anchor=tk.W)
        Label(self, 'Lat D M S', 0.1, 0.25, 0.15, anchor=tk.W)
        Label(self, 'Long D M S', 0.1, 0.3, 0.15, anchor=tk.W)
        Label(self, 'Notes', 0.1, 0.35, 0.15, anchor=tk.W)
        Label(self, 'Options', 0.1, 0.4, 0.15, anchor=tk.W)
        Label(self, 'Opt. Event', 0.1, 0.45, 0.15, anchor=tk.W)

        self.chart_select_frame = tk.Frame(
            self, width=0.5, height=0.5, background=BG_COLOR
        )
        self.chart_select_frame.place(
            relx=0.45, rely=0.55, relwidth=0.3, relheight=0.3, anchor=tk.N
        )

        Label(
            self.chart_select_frame,
            'Select Chart Types',
            x=0,
            y=0,
            anchor=tk.N,
        ).pack(side=tk.TOP, pady=10)

        self.listbox = Listbox(
            self.chart_select_frame,
            x=0,
            y=0,
            width=0,
            height=0,
            selectmode=tk.MULTIPLE,
        )

        self.listbox.set_options(self._options)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        self.scrollbar = Scrollbar(self.chart_select_frame)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(
            yscrollcommand=self.scrollbar.set,
            activestyle='dotbox',
            selectbackground=BG_COLOR,
            selectforeground=TXT_COLOR,
        )

        # The Listbox randomly triggers with no selected entries;
        # this is needed to gate the "clear" function
        self.selected_solunars = []
        self.clicked_clear = False

        self.last_click_widget = None
        self.last_click_coords = (0, 0)

        Label(self, 'Quick Select', 0.1, 0.55, 0.2, anchor=tk.W)

        Button(self, 'SSR + LRs', 0.1, 0.6, 0.15).bind(
            '<Button-1>',
            lambda _: delay(self.select_all_of_type, SSR_AND_LUNARS),
        )
        Button(self, 'All Major', 0.1, 0.65, 0.15).bind(
            '<Button-1>', lambda _: delay(self.select_all_of_type, ALL_MAJOR)
        )
        Button(self, 'Maj + Minor', 0.1, 0.7, 0.15, font=font_16).bind(
            '<Button-1>',
            lambda _: delay(self.select_all_of_type, MAJOR_AND_MINOR),
        )
        Button(self, 'Experimental', 0.1, 0.75, 0.15, font=font_16).bind(
            '<Button-1>',
            lambda _: delay(self.select_all_of_type, EXPERIMENTAL),
        )
        Button(self, 'Clear', 0.1, 0.8, 0.15).bind(
            '<Button-1>', lambda _: delay(self.clear_selections)
        )

        Label(self, 'Search Direction', 0.6, 0.55, 0.2, anchor=tk.CENTER)
        self.search = Radiogroup(self)
        Radiobutton(self, self.search, 0, 'Active', 0.6, 0.6, 0.3).bind(
            '<Button-1>', lambda _: delay(self.update_search_direction, 0)
        )
        Radiobutton(self, self.search, 1, 'Nearest', 0.6, 0.65, 0.3).bind(
            '<Button-1>', lambda _: delay(self.update_search_direction, 2)
        )
        Radiobutton(self, self.search, 2, 'Next', 0.6, 0.7, 0.3).bind(
            '<Button-1>', lambda _: delay(self.update_search_direction, 1)
        )

        self.init = True

        self.search.value = 0
        self.search.focus()

        Label(self, '# of Months:', 0.6, 0.75, 0.3, anchor=tk.W)

        self.burst_month_duration = Entry(self, '', 0.6, 0.8, 0.05)

        self.istemp = Radiogroup(self)
        Radiobutton(self, self.istemp, 0, 'Permanent Charts', 0.3, 0.5, 0.25)
        Radiobutton(self, self.istemp, 1, 'Temporary Charts', 0.5, 0.5, 0.25)
        self.istemp.value = 1

        Button(self, 'Calculate', 0, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.calculate)
        )
        Button(self, 'Help', 0.2, 0.95, 0.2).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, os.path.join(HELP_PATH, 'solunars.txt')),
        )

        Button(self, 'Reset', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )

        backbtn = Button(self, 'Back', 0.8, 0.95, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.9, 1)

    def on_global_click(self, event):
        self.last_click_widget = event.widget
        self.last_click_coords = (event.x_root, event.y_root)

    def was_last_click_inside_listbox(self):
        if not hasattr(self, 'last_click_coords'):
            return False

        x, y = self.last_click_coords
        x1 = self.listbox.winfo_rootx()
        y1 = self.listbox.winfo_rooty()
        x2 = x1 + self.listbox.winfo_width()
        y2 = y1 + self.listbox.winfo_height()

        return x1 <= x <= x2 and y1 <= y <= y2

    def on_select(self, event):
        if self._in_callback:
            return

        self._in_callback = True

        widget = event.widget

        selected_indices = list(widget.curselection())

        # Unselect and remove headers from selection
        for i in selected_indices:
            if widget.get(i).startswith('---'):
                widget.select_clear(i)

        selected_indices = [
            i for i in selected_indices if not widget.get(i).startswith('---')
        ]

        if not selected_indices:
            # It must've triggered accidentally
            if not self.clicked_clear and len(self.selected_solunars) > 1:
                self._in_callback = False
                return

            if (
                len(self.selected_solunars) == 1
                and not self.was_last_click_inside_listbox()
            ):
                self._in_callback = False
                return

            # We must be unselecting the only selection
            widget.delete(0, tk.END)

            for (insertion_counter, item) in enumerate(self._options):
                widget.insert(tk.END, item)
                if item.startswith('---'):
                    widget.itemconfig(insertion_counter, fg='gray')

            self._in_callback = False
            self.clicked_clear = False
            return

        selected_items = []
        scroll_position = widget.yview()

        for i in selected_indices:
            item = widget.get(i)
            if item.startswith('* '):
                selected_items.append(item)
            elif item.startswith('- '):
                selected_items.append(item.replace('- ', '* '))
            else:
                selected_items.append(f'* {item}')

        originals_minus_starred = [
            item
            for item in self._options
            if f'* {item}' not in selected_items
            and item.replace('- ', '* ') not in selected_items
        ]

        # Rebuild final listbox
        widget.delete(0, tk.END)
        if selected_items:
            widget.insert(tk.END, SELECTED_HEADER)
            widget.itemconfig(0, fg=BTN_COLOR)

        for (insertion_counter, item) in enumerate(
            selected_items + originals_minus_starred
        ):
            widget.insert(tk.END, item)
            if item.startswith('---'):
                index = insertion_counter
                if selected_items:
                    # There's a "selected" header at index 0
                    index += 1

                widget.itemconfig(index, fg='gray')

        # Reselect all newly added/promoted starred items
        widget.select_clear(0, tk.END)
        for i, item in enumerate(widget.get(0, tk.END)):
            if item in selected_items:
                widget.select_set(i)

        widget.yview_moveto(scroll_position[0])

        self.selected_solunars = selected_items

        self._in_callback = False
        self.clicked_clear = False
        self.last_click_widget = None

    def enable_find(self):
        self.findbtn.disabled = False

    def update_search_direction(self, value):
        if self.init:
            return
        self.init = True
        self.search.value = value
        self.init = False

    def back(self):
        from src.user_interfaces.select_chart import SelectChart

        self.destroy()
        SelectChart()

    def select_all_of_type(self, preset):
        self._in_callback = True
        already_selected = []

        for chart in preset:
            # Skip over quartis if they're disabled
            if chart not in self._options:
                continue

            item = chart.replace('- ', '* ')
            if not item.startswith('* '):
                item = f'* {item}'

            if item not in already_selected:
                already_selected.insert(0, item)

        originals_minus_starred = [
            item
            for item in self._options
            if f'* {item}' not in already_selected
            and item.replace('- ', '* ') not in already_selected
        ]

        # Rebuild final listbox
        self.listbox.delete(0, tk.END)

        self.listbox.insert(tk.END, SELECTED_HEADER)
        self.listbox.itemconfig(0, fg=BTN_COLOR)

        already_selected.reverse()

        for (insertion_conter, item) in enumerate(
            already_selected + originals_minus_starred
        ):
            self.listbox.insert(tk.END, item)
            if item.startswith('---'):
                # We add 1 to the counter because there's a "selected" header
                # at index 0
                self.listbox.itemconfig(insertion_conter + 1, fg='gray')

        # Reselect all originally selected items
        self.listbox.select_clear(0, tk.END)
        for i, item in enumerate(self.listbox.get(0, tk.END)):
            if item in already_selected:
                self.listbox.select_set(i)

        self.selected_solunars = already_selected
        self._in_callback = False

    def clear_selections(self):
        self._in_callback = True
        self.clicked_clear = True

        # Rebuild final listbox
        self.listbox.delete(0, tk.END)

        for (insertion_conter, item) in enumerate(self._options):
            self.listbox.insert(tk.END, item)
            if item.startswith('---'):
                self.listbox.itemconfig(insertion_conter, fg='gray')

        # Reselect all newly added/promoted starred items
        self.listbox.select_clear(0, tk.END)

        self._in_callback = False
        self.clicked_clear = False
        self.selected_solunars = []

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
        SolunarsAllInOne(self.base, self.filename, self.program_options)

    def calculate(self):
        solars = []
        lunars = []

        for entry in self.selected_solunars:
            entry = entry.replace('*', '-')
            if entry not in CHART_OPTIONS_FULL:
                entry = entry.strip('-').strip()
            solunar_type = LABELS_TO_RETURNS[entry]
            if solunar_type in SOLAR_RETURNS:
                solars.append(solunar_type)
            elif solunar_type in LUNAR_RETURNS:
                lunars.append(solunar_type)

        if not solars and not lunars:
            self.status.error('No solunars selected.')
            return

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
        params['radix'] = ChartObject(self.base).with_role(
            ChartWheelRole.RADIX
        )

        if self.event:
            if self.event == '<':
                cchart = deepcopy(params)
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
        self.save_location(params)

        dates_and_chart_params = []
        input_date = julday(
            params['year'],
            params['month'],
            params['day'],
            params['time'],
            params['style'],
        )

        duration = None
        if len(self.burst_month_duration.text.strip()) != 0:
            duration = int(self.burst_month_duration.text.strip())
            if duration == 0:
                duration = None

        if self.search.value == 0:
            dates_and_chart_params = self.search_solunars(
                params, solars, lunars, active=True
            )
            if duration:
                burst_chart_params = self.search_solunars(
                    params, solars, lunars, burst_months=duration
                )
                dates_and_chart_params += burst_chart_params
        elif self.search.value == 1:
            active_chart_params = self.search_solunars(
                params, solars, lunars, active=True
            )
            forward_chart_params = self.search_solunars(params, solars, lunars)

            for chart_type in solars + lunars:
                active_chart_info = pydash.find(
                    active_chart_params, lambda p: p[2] == chart_type
                ) or ({}, 999999999, None, None)
                future_chart_info = pydash.find(
                    forward_chart_params, lambda p: p[2] == chart_type
                )

                active_difference = math.fabs(
                    active_chart_info[1] - input_date
                )
                future_difference = math.fabs(
                    future_chart_info[1] - input_date
                )

                if active_difference < future_difference:
                    dates_and_chart_params.append(active_chart_info)
                else:
                    dates_and_chart_params.append(future_chart_info)

            if duration:
                burst_chart_params = self.search_solunars(
                    params, solars, lunars, burst_months=duration
                )
                dates_and_chart_params += burst_chart_params

        elif self.search.value == 2:
            dates_and_chart_params = self.search_solunars(
                params, solars, lunars, burst_months=duration
            )
        else:
            self.status.error('No search direction selected.')

        if len(dates_and_chart_params) == 0:
            self.status.error('No charts found.')
            return

        charts_created = 0

        # Skip duplicates
        already_created_charts = {}

        active_charts_found = []

        dates_and_chart_params = sorted(
            dates_and_chart_params, key=lambda x: -1 * x[1]
        )

        # for x in dates_and_chart_params:
        #     print(x[1], x[2])

        searching_active_charts = self.search.value in [0, 1]

        for index in range(len(dates_and_chart_params)):
            (
                chart_params,
                date,
                solunar_type,
                chart_class,
            ) = dates_and_chart_params[index]

            family = pydash.find(SOLUNAR_FAMILIES, lambda f: solunar_type in f)
            assert family is not None

            family_has_demi = len(family) > 2

            is_demi = 'Demi' in solunar_type
            is_quarti = (
                'Quarti' in solunar_type
                or 'Eighteen' in solunar_type  # "quarti" NSR
                or 'Ten' in solunar_type  # "quarti" NLR
            )

            chart_is_active = date < input_date

            if searching_active_charts and chart_is_active:
                full_chart_found = family[0] in active_charts_found

                if (is_demi or is_quarti) and full_chart_found:
                    continue

                if is_quarti and family_has_demi:
                    demi_found = family[1] in active_charts_found

                    if demi_found:
                        continue

            truncated_date = int(date)
            if truncated_date in already_created_charts:
                if solunar_type in already_created_charts[truncated_date]:
                    continue
                else:
                    already_created_charts[truncated_date].append(solunar_type)
            else:
                already_created_charts[truncated_date] = [solunar_type]

            self.make_chart(
                chart_params,
                date,
                solunar_type,
                chart_class,
            )

            if chart_is_active:
                active_charts_found.append(solunar_type)

            charts_created += 1

        s = '' if charts_created == 1 else 's'
        self.status.text = f'{charts_created} chart{s} created.'

    def search_solunars(
        self,
        params: dict,
        solars: list[str],
        lunars: list[str],
        burst_months=None,
        active=False,
    ):
        dates_and_chart_params: list[tuple[any]] = []

        def _append_returns(
            returns, chart_type, chart_class, override_params=None
        ):
            append_applicable_returns(
                returns=returns,
                return_args_list=dates_and_chart_params,
                args=(
                    override_params or params,
                    None,
                    chart_type,
                    chart_class,
                ),
                burst=burst_months is not None and burst_months > 0,
                active=active,
            )

        def append_lunars(returns, chart_type, override_params=None):
            _append_returns(
                returns, chart_type, 'LR', override_params=override_params
            )

        def append_solars(returns, chart_type, override_params=None):
            _append_returns(
                returns, chart_type, 'SR', override_params=override_params
            )

        radix = params['radix']

        base_start = julday(
            params['year'],
            params['month'],
            params['day'],
            params['time'],
            params['style'],
        )

        continue_until_date = None

        if burst_months:
            continue_until_date = base_start + (30 * burst_months)

        sun_radix_longitude = radix.planets['Sun'].longitude
        moon_radix_longitude = radix.planets['Moon'].longitude

        for solar_return_type in solars:
            cycle_length = 366

            continue_until_date_solar = continue_until_date or (
                base_start if active else base_start + 365
            )

            # Traditional Solar Returns
            if solar_return_type in SOLAR_RETURN_FAMILY:
                starting_date = base_start - 365 if active else base_start

                returns = find_solunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_solar,
                    target_body='Sun',
                    target_longitude=sun_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=solar_return_type,
                    grace_period=10,
                )

                append_solars(returns, solar_return_type)
                continue

            elif solar_return_type in NSR_FAMILY:
                if solar_return_type == ChartType.NOVIENIC_SOLAR_RETURN.value:
                    starting_date = base_start - 41 if active else base_start
                else:
                    starting_date = base_start - 11 if active else base_start

                returns = find_novienic_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_solar,
                    target_body='Sun',
                    target_longitude=sun_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=solar_return_type,
                    grace_period=1,
                )

                append_solars(returns, solar_return_type)
                continue

            elif solar_return_type in SOLILUNAR_FAMILY:
                starting_date = base_start - 365 if active else base_start

                returns = find_solunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_solar,
                    target_body='Sun',
                    target_longitude=moon_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=solar_return_type,
                    grace_period=10,
                )

                append_solars(returns, solar_return_type)
                continue

            elif solar_return_type in KSR_FAMILY:
                starting_date = base_start - 365 if active else base_start

                returns = find_progressed_crossings_until_date(
                    base_start=starting_date,
                    radix_julian_day_utc=radix.julian_day_utc,
                    continue_until_date=continue_until_date_solar,
                    target_body='Sun',
                    radix_sun_longitude=sun_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=solar_return_type,
                    grace_period=10,
                )

                append_solars(returns, solar_return_type)
                continue

        for lunar_return_type in lunars:
            cycle_length = 29

            continue_until_date_lunar = continue_until_date or (
                base_start if active else base_start + 29
            )

            if lunar_return_type in LUNAR_RETURN_FAMILY:
                starting_date = base_start - 29 if active else base_start

                returns = find_solunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_lunar,
                    target_body='Moon',
                    target_longitude=moon_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=lunar_return_type,
                    grace_period=1,
                )

                append_lunars(returns, lunar_return_type)
                continue

            elif lunar_return_type in NLR_FAMILY:
                starting_date = base_start - 3.5 if active else base_start

                returns = find_novienic_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_lunar,
                    target_body='Moon',
                    target_longitude=moon_radix_longitude,
                    cycle_length=3.5,
                    solunar_type=lunar_return_type,
                    grace_period=0.5,
                )

                append_lunars(returns, lunar_return_type)
                continue

            elif lunar_return_type in LUNISOLAR_FAMILY:
                starting_date = base_start - 29 if active else base_start

                returns = find_solunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_lunar,
                    target_body='Moon',
                    target_longitude=sun_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=lunar_return_type,
                    grace_period=1,
                )

                append_lunars(returns, lunar_return_type)
                continue

            elif lunar_return_type in ANLUNAR_FAMILY:
                # Get previous solar return
                # TODO - when this crosses over into the next year, it won't use the next SSR

                solar_return_date = calc_sun_crossing(
                    sun_radix_longitude, base_start - 366
                )
                (year, month, day, time) = revjul(
                    solar_return_date, params['style']
                )

                ssr_params = {**params}
                ssr_params.update(
                    {
                        'name': radix.name + ' Solar Return',
                        'type': ChartType.SOLAR_RETURN.value,
                        'year': year,
                        'month': month,
                        'day': day,
                        'time': time,
                    }
                )

                ssr_chart = ChartObject(ssr_params)

                solar_moon = ssr_chart.planets['Moon'].longitude

                starting_date = base_start - 29 if active else base_start

                returns = find_solunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_lunar,
                    target_body='Moon',
                    target_longitude=solar_moon,
                    cycle_length=cycle_length,
                    solunar_type=lunar_return_type,
                    grace_period=1,
                )

                append_lunars(
                    returns,
                    lunar_return_type,
                    override_params={**params, 'ssr_chart': ssr_chart},
                )
                continue

            elif lunar_return_type in LSR_FAMILY:
                precision = 5

                natal_elongation = get_signed_orb_to_reference(
                    moon_radix_longitude, sun_radix_longitude
                )
                natal_elongation = round(natal_elongation, precision)

                start = base_start - 30 if active else base_start

                while start <= continue_until_date_lunar:
                    target_elongation = natal_elongation
                    next_increment = 30

                    if (
                        lunar_return_type
                        == ChartType.DEMI_LUNAR_SYNODIC_RETURN.value
                    ):
                        if natal_elongation > 0:
                            target_elongation = natal_elongation - 180
                        else:
                            target_elongation = natal_elongation + 180

                        next_increment = 15
                    elif (
                        lunar_return_type
                        == ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value
                    ):
                        if natal_elongation > 0:
                            target_elongation = natal_elongation + 90
                        else:
                            target_elongation = natal_elongation - 90
                        next_increment = 7.5
                    elif (
                        lunar_return_type
                        == ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value
                    ):
                        if natal_elongation > 0:
                            target_elongation = natal_elongation - 90
                        else:
                            target_elongation = natal_elongation + 90
                        next_increment = 7.5

                    if target_elongation > 180:
                        diff = target_elongation - 180
                        target_elongation = -1 * (180 - diff)

                    elif target_elongation < -180:
                        diff = target_elongation + 180
                        target_elongation = -1 * (-180 - diff)

                    lower_bound = start
                    higher_bound = start + 30

                    date = find_jd_utc_of_elongation(
                        target_elongation, lower_bound, higher_bound
                    )
                    if date:
                        dates_and_chart_params.append(
                            (params, date, lunar_return_type, 'LR')
                        )
                    start += next_increment

                continue

            elif lunar_return_type in KAR_FAMILY:
                # Get previous solar return
                # TODO - when this crosses over into the next year, it won't use the next SSR

                solar_return_date = calc_sun_crossing(
                    sun_radix_longitude, base_start - 366
                )
                (year, month, day, time) = revjul(
                    solar_return_date, params['style']
                )

                ssr_params = {**params}
                ssr_params.update(
                    {
                        'name': radix.name + ' Solar Return',
                        'type': ChartType.SOLAR_RETURN.value,
                        'year': year,
                        'month': month,
                        'day': day,
                        'time': time,
                    }
                )

                ssr_chart = ChartObject(ssr_params)

                starting_date = base_start - 29 if active else base_start

                returns = find_progressed_anlunar_crossings_until_date(
                    base_start=starting_date,
                    continue_until_date=continue_until_date_lunar,
                    radix_sun_longitude=sun_radix_longitude,
                    solunar_type=lunar_return_type,
                    grace_period=1,
                )

                append_lunars(
                    returns,
                    lunar_return_type,
                    override_params={**params, 'ssr_chart': ssr_chart},
                )
                continue

            elif lunar_return_type in KLR_FAMILY:
                starting_date = base_start - 29 if active else base_start

                returns = find_progressed_crossings_until_date(
                    base_start=starting_date,
                    radix_julian_day_utc=radix.julian_day_utc,
                    continue_until_date=continue_until_date_lunar,
                    target_body='Moon',
                    radix_sun_longitude=sun_radix_longitude,
                    cycle_length=cycle_length,
                    solunar_type=lunar_return_type,
                    grace_period=1,
                )

                append_lunars(returns, lunar_return_type)
                continue

        return dates_and_chart_params

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

    def save_location(self, params):
        try:
            with open(LOCATIONS_FILE, 'r') as datafile:
                locs = json.load(datafile)
            newloc = [
                params['location'],
                params['latitude'],
                params['longitude'],
            ]
            if newloc in locs:
                locs.remove(newloc)
            locs.insert(0, newloc)
            if len(locs) > 50:
                locs = locs[0:50]
            with open(LOCATIONS_FILE, 'w') as datafile:
                locs = json.dump(locs, datafile, indent=4)
        except Exception:
            pass


LABELS_TO_RETURNS = {
    '--- Major Charts ---': '',
    'Sidereal Solar Return (SSR)': ChartType.SOLAR_RETURN.value,
    '- Quarti-SSR #1': ChartType.FIRST_QUARTI_SOLAR_RETURN.value,
    '- Demi-SSR': ChartType.DEMI_SOLAR_RETURN.value,
    '- Quarti-SSR #2': ChartType.LAST_QUARTI_SOLAR_RETURN.value,
    'Sidereal Lunar Return (SLR)': ChartType.LUNAR_RETURN.value,
    '- Quarti-SLR #1': ChartType.FIRST_QUARTI_LUNAR_RETURN.value,
    '- Demi-SLR': ChartType.DEMI_LUNAR_RETURN.value,
    '- Quarti-SLR #2': ChartType.LAST_QUARTI_LUNAR_RETURN.value,
    '--- Kinetics ---': '',
    'Kinetic Solar Return (KSR)': ChartType.KINETIC_SOLAR_RETURN.value,
    '- Quarti-KSR #1': ChartType.FIRST_QUARTI_KINETIC_SOLAR_RETURN.value,
    '- Demi-KSR': ChartType.DEMI_KINETIC_SOLAR_RETURN.value,
    '- Quarti-KSR #2': ChartType.LAST_QUARTI_KINETIC_SOLAR_RETURN.value,
    'Kinetic Lunar Return (KLR)': ChartType.KINETIC_LUNAR_RETURN.value,
    '- Quarti-KLR #1': ChartType.FIRST_QUARTI_KINETIC_LUNAR_RETURN.value,
    '- Demi-KLR': ChartType.DEMI_KINETIC_LUNAR_RETURN.value,
    '- Quarti-KLR #2': ChartType.LAST_QUARTI_KINETIC_LUNAR_RETURN.value,
    '--- Secondary Charts ---': '',
    'Novienic Solar Return (NSR)': ChartType.NOVIENIC_SOLAR_RETURN.value,
    '- 10-Day Solar (Quarti-NSR)': ChartType.TEN_DAY_SOLAR_RETURN.value,
    'Novienic Lunar Return (NLR)': ChartType.NOVIENIC_LUNAR_RETURN.value,
    '- 18-Hour Lunar (Quarti-NLR)': ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value,
    'Sidereal Anlunar Return (SAR)': ChartType.ANLUNAR_RETURN.value,
    '- Quarti-SAR #1': ChartType.FIRST_QUARTI_ANLUNAR_RETURN.value,
    '- Demi-SAR': ChartType.DEMI_ANLUNAR_RETURN.value,
    '- Quarti-SAR #2': ChartType.LAST_QUARTI_ANLUNAR_RETURN.value,
    'Kinetic Anlunar Return (KAR)': ChartType.KINETIC_ANLUNAR_RETURN.value,
    '- Quarti-KAR #1': ChartType.FIRST_QUARTI_KINETIC_ANLUNAR_RETURN.value,
    '- Demi-KAR': ChartType.KINETIC_DEMI_ANLUNAR_RETURN.value,
    '- Quarti-KAR #2': ChartType.LAST_QUARTI_KINETIC_ANLUNAR_RETURN.value,
    '--- Other Charts ---': '',
    'Sidereal Yoga Return (SYR)': ChartType.YOGA_RETURN.value,
    'Lunar Synodic Return (LSR)': ChartType.LUNAR_SYNODIC_RETURN.value,
    '- Quarti-LSR #1': ChartType.FIRST_QUARTI_LUNAR_SYNODIC_RETURN.value,
    '- Demi-LSR': ChartType.DEMI_LUNAR_SYNODIC_RETURN.value,
    '- Quarti-LSR #2': ChartType.LAST_QUARTI_LUNAR_SYNODIC_RETURN.value,
    'SoliLunar (SoLu)': ChartType.SOLILUNAR_RETURN.value,
    '- Quarti-SoLu #1': ChartType.FIRST_QUARTI_SOLILUNAR_RETURN.value,
    '- Demi-SoLu': ChartType.DEMI_SOLILUNAR_RETURN.value,
    '- Quarti-SoLu #2': ChartType.LAST_QUARTI_SOLILUNAR_RETURN.value,
    'LuniSolar (LuSo)': ChartType.LUNISOLAR_RETURN.value,
    '- Quarti-LuSo #1': ChartType.FIRST_QUARTI_LUNISOLAR_RETURN.value,
    '- Demi-LuSo': ChartType.DEMI_LUNISOLAR_RETURN.value,
    '- Quarti-LuSo #2': ChartType.LAST_QUARTI_LUNISOLAR_RETURN.value,
}

CHART_OPTIONS_FULL = [
    '--- Major Charts ---',
    'Sidereal Solar Return (SSR)',
    '- Quarti-SSR #1',
    '- Demi-SSR',
    '- Quarti-SSR #2',
    'Sidereal Lunar Return (SLR)',
    '- Quarti-SLR #1',
    '- Demi-SLR',
    '- Quarti-SLR #2',
    '--- Kinetics ---',
    'Kinetic Solar Return (KSR)',
    '- Quarti-KSR #1',
    '- Demi-KSR',
    '- Quarti-KSR #2',
    'Kinetic Lunar Return (KLR)',
    '- Quarti-KLR #1',
    '- Demi-KLR',
    '- Quarti-KLR #2',
    'Kinetic Anlunar Return (KAR)',
    '- Quarti-KAR #1',
    '- Demi-KAR',
    '- Quarti-KAR #2',
    '--- Secondary Charts ---',
    'Lunar Synodic Return (LSR)',
    '- Quarti-LSR #1',
    '- Demi-LSR',
    '- Quarti-LSR #2',
    'Novienic Solar Return (NSR)',
    '- 10-Day Solar (Quarti-NSR)',
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    '--- Other Charts ---',
    # 'Sidereal Yoga Return (SYR)',
    'SoliLunar (SoLu)',
    '- Quarti-SoLu #1',
    '- Demi-SoLu',
    '- Quarti-SoLu #2',
    'LuniSolar (LuSo)',
    '- Quarti-LuSo #1',
    '- Demi-LuSo',
    '- Quarti-LuSo #2',
    'Sidereal Anlunar Return (SAR)',
    '- Quarti-SAR #1',
    '- Demi-SAR',
    '- Quarti-SAR #2',
]

CHART_OPTIONS_NO_QUARTIS = [
    '--- Major Charts --- ',
    'Sidereal Solar Return (SSR)',
    '- Demi-SSR',
    'Sidereal Lunar Return (SLR)',
    '- Demi-SLR',
    '--- Kinetics ---',
    'Kinetic Solar Return (KSR)',
    '- Demi-KSR',
    'Kinetic Lunar Return (KLR)',
    '- Demi-KLR',
    'Kinetic Anlunar Return (KAR)',
    '- Demi-KAR',
    '--- Secondary Charts ---',
    'Lunar Synodic Return (LSR)',
    '- Demi-LSR',
    'Novienic Solar Return (NSR)',
    '- 10-Day Solar (Quarti-NSR)',
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    '--- Other Charts ---',
    # 'Sidereal Yoga Return (SYR)',
    'SoliLunar (SoLu)',
    '- Demi-SoLu',
    'LuniSolar (LuSo)',
    '- Demi-LuSo',
    'Sidereal Anlunar Return (SAR)',
    '- Demi-SAR',
]

SSR_AND_LUNARS = [
    'Sidereal Solar Return (SSR)',
    'Sidereal Lunar Return (SLR)',
    '- Quarti-SLR #1',
    '- Demi-SLR',
    '- Quarti-SLR #2',
]

ALL_MAJOR = [
    'Sidereal Solar Return (SSR)',
    '- Quarti-SSR #1',
    '- Demi-SSR',
    '- Quarti-SSR #2',
    'Sidereal Lunar Return (SLR)',
    '- Quarti-SLR #1',
    '- Demi-SLR',
    '- Quarti-SLR #2',
]

MAJOR_AND_MINOR = [
    'Sidereal Solar Return (SSR)',
    '- Quarti-SSR #1',
    '- Demi-SSR',
    '- Quarti-SSR #2',
    'Sidereal Lunar Return (SLR)',
    '- Quarti-SLR #1',
    '- Demi-SLR',
    '- Quarti-SLR #2',
    'Kinetic Lunar Return (KLR)',
    '- Demi-KLR',
    'Novienic Solar Return (NSR)',
    '- 10-Day Solar (Quarti-NSR)',
    'Kinetic Anlunar Return (KAR)',
    '- Demi-KAR',
]

EXPERIMENTAL = [
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    'Kinetic Anlunar Return (KAR)',
    '- Quarti-KAR #1',
    '- Demi-KAR',
    '- Quarti-KAR #2',
    # 'Sidereal Yoga Return (SYR)',
    'Lunar Synodic Return (LSR)',
    '- Quarti-LSR #1',
    '- Demi-LSR',
    '- Quarti-LSR #2',
    'SoliLunar (SoLu)',
    '- Quarti-SoLu #1',
    '- Demi-SoLu',
    '- Quarti-SoLu #2',
    'LuniSolar (LuSo)',
    '- Quarti-LuSo #1',
    '- Demi-LuSo',
    '- Quarti-LuSo #2',
]

SELECTED_HEADER = '--- Selected Charts ---'
