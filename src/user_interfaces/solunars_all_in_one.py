# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import os
from datetime import datetime as dt


from src import *

from src.swe import *


from src.user_interfaces.widgets import *
from src.utils.format_utils import display_name, toDMS
from src.utils.gui_utils import ShowHelp


CHART_OPTIONS = [
    '--- Major Charts --- ',
    'Sidereal Solar Return',
    'Demi Sidereal Solar Return',
    '1st Quarti Sidereal Solar Return',
    '3rd Quarti Sidereal Solar Return',
    'SLR',
    'DSLR',
    'QSLR1',
    'QSLR3',
    '--- Minor Charts ---',
    'NSR',
    '10-Dy SR',
    'NLR',
    '18-Hr LR',
    'SAR',
    'DSAR',
    'QSAR1',
    'QSAR3',
    '--- Kinetics ---',
    'KSR',
    'KDSR',
    'KQSR1',
    'KQSR3',
    'KLR',
    'KDLR',
    'KQLR1',
    'KQLR3',
    'KSAR',
    'KDSAR',
    'KQSAR1',
    'KQSAR3',
    '--- Supplemental ---',
    'SoLu',
    'DSoLu',
    'QSoLu1',
    'QSoLu3',
    'LuSo',
    'DLuSo',
    'QLuSo1',
    'QLuSo3',
    'SYR',
    'DSYR',
    'QSYR1',
    'QSYR3',
    'LSR',
    'DLSR',
    'QLSR1',
    'QLSR3',
]


class SolunarsAllInOne(Frame):
    def __init__(self, base, filename):
        super().__init__()
        now = dt.utcnow()
        chart = {}

        self.more_charts = {}

        self.base = base
        self.filename = filename
        self.filename_label = Label(self, display_name(filename), 0, 0, 1)
        Label(self, 'Search Direction', 0.1, 0.5, 0.15, anchor=tk.W)

        self.init = True
        self.search = Radiogroup(self)
        Radiobutton(
            self, self.search, 0, 'Active Charts', 0.1, 0.55, 0.15
        ).bind('<Button-1>', lambda _: delay(self.toggle_year, 0))
        Radiobutton(self, self.search, 1, 'Forwards', 0.1, 0.6, 0.15).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 1)
        )
        Radiobutton(self, self.search, 2, 'Backwards', 0.1, 0.65, 0.15).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 2)
        )

        self.search.value = 0
        self.search.focus()
        self.init = False
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
        self.notes = PlaceholderEntry(
            self, '', 0.3, 0.35, 0.3, placeholder='Notes'
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

        Label(self, 'Date ' + DATE_FMT, 0.15, 0.1, 0.15, anchor=tk.W)
        Label(self, 'Time UT H M S ', 0.15, 0.15, 0.15, anchor=tk.W)
        Label(self, 'Location', 0.15, 0.2, 0.15, anchor=tk.W)
        Label(self, 'Lat D M S', 0.15, 0.25, 0.15, anchor=tk.W)
        Label(self, 'Long D M S', 0.15, 0.3, 0.15, anchor=tk.W)
        Label(self, 'Options', 0.15, 0.4, 0.15, anchor=tk.W)

        self.chart_select_frame = tk.Frame(
            self, width=0.5, height=0.5, background=BG_COLOR
        )
        self.chart_select_frame.place(
            relx=0.45, rely=0.5, relwidth=0.3, relheight=0.3, anchor=tk.N
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
            x=0.9,
            y=0.9,
            width=0.95,
            height=0.95,
            selectmode=tk.MULTIPLE,
        )
        self.listbox.set_options(CHART_OPTIONS)
        self.listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.listbox.bind('<Button-1>', self.on_click)

        self.scrollbar = Scrollbar(self.chart_select_frame)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        Button(self, 'All Major', 0.3, 0.8, 0.15).bind(
            '<Button-1>', lambda _: delay(self.all_charts, True)
        )
        Button(self, 'Clear', 0.45, 0.8, 0.15).bind(
            '<Button-1>', lambda _: delay(self.all_charts, False)
        )
        self.oneyear = Checkbutton(
            self, 'All Selected Solunars For One Year', 0.3, 0.85, 0.4
        )
        self.oneyear.config(state=tk.DISABLED)
        self.istemp = Radiogroup(self)
        Radiobutton(self, self.istemp, 0, 'Permanent Charts', 0.3, 0.9, 0.25)
        Radiobutton(self, self.istemp, 1, 'Temporary Charts', 0.5, 0.9, 0.25)
        self.istemp.value = 1

        Button(self, 'Calculate', 0.85, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.calculate)
        )
        Button(self, 'Help', 0.2, 0.95, 0.2).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, os.path.join(HELP_PATH, 'solunars.txt')),
        )

        Button(self, 'Clear', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        backbtn = Button(self, 'Back', 0.8, 0.95, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.85, 1)

    def is_header(self, item):
        return item.startswith('---')

    def on_click(self, event):
        # Get the listbox widget from the event
        self.listbox = event.widget
        # Determine the index of the clicked item using the y coordinate of the click event
        idx = self.listbox.nearest(event.y)
        # Retrieve the text of that item
        item = self.listbox.get(idx)
        # If it's a header, stop the event processing so it doesn't get selected.
        if self.is_header(item):
            return 'break'  # Cancels the default handling

    def enable_find(self):
        self.findbtn.disabled = False

    def toggle_year(self, value):
        pass

    def back(self):
        self.destroy()

    def all_charts(self, value):
        pass

    def more_finish(self, selected):
        pass

    def more_files(self):
        pass

    def make_event(self):
        pass

    def check_style(self):
        try:
            y = int(self.datey.text)
        except Exception:
            return
        self.old.checked = True if y < 1583 else False

    def loc_finish(self, selected):
        pass

    def recent_loc(self):
        pass

    def find(self):
        pass

    def select_options(self):
        pass

    def temp_options(self):
        from src.user_interfaces.chart_options import ChartOptions

        ChartOptions(self.options.text, True, self.options)

    def clear(self):
        self.destroy()

    def calculate(self):
        pass

    def forward_search(self, chart, solunars):
        pass

    def backward_search(self, chart, solunars):
        pass

    def burst(self, chart, solunars):
        pass

    def active_search(self, chart, solunars):
        pass

    def make_chart(self, chart, date, chtype, cclass, show=True):
        pass

    def save_location(self, chart):
        pass
