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

from src.models.options import ProgramOptions
from src.swe import *


from src.user_interfaces.widgets import *
from src.utils.format_utils import display_name, toDMS
from src.utils.gui_utils import ShowHelp


CHART_OPTIONS_FULL = [
    '--- Major Charts --- ',
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
    '--- Secondary Charts ---',
    'Novienic Solar Return (NSR)',
    '- 10-Day Solar (Quarti-NSR)',
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    'Sidereal Anlunar Return (SAR)',
    '- Quarti-SAR #1',
    '- Demi-SAR',
    '- Quarti-SAR #2',
    'Kinetic Anlunar Return (KAR)',
    '- Quarti-KAR #1',
    '- Demi-KAR',
    '- Quarti-KAR #2',
    '--- Other Charts ---',
    'Sidereal Yoga Return (SYR)',
    '- Quarti-SYR #1',
    '- Demi-SYR',
    '- Quarti-SYR #2',
    'Lunar Synodic Return (LSR)',
    '- Quarti-LSR #1',
    '- Demi-LSR',
    '- Quarti-LSR #2',
    'SoliLunar (SoLu)',
    '- Quarto-SoLu #1',
    '- Demi-SoLu',
    '- Quarti-SoLu #2',
    'LuniSolar (LuSo)',
    '- Quarti-LuSo #1',
    '- Demi-LuSo',
    '- Quarti-LuSo #2',
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
    '--- Secondary Charts ---',
    'Novienic Solar Return (NSR)',
    '- 10-Day Solar (Quarti-NSR)',
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    'Sidereal Anlunar Return (SAR)',
    '- Demi-SAR',
    'Kinetic Anlunar Return (KAR)',
    '- Demi-KAR',
    '--- Other Charts ---',
    'Sidereal Yoga Return (SYR)',
    '- Demi-SYR',
    'Lunar Synodic Return (LSR)',
    '- Demi-LSR',
    'SoliLunar (SoLu)',
    '- Demi-SoLu',
    'LuniSolar (LuSo)',
    '- Demi-LuSo',
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
    'Sidereal Anlunar Return (SAR)',
    '- Demi-SAR',
]

EXPERIMENTAL = [
    'Novienic Lunar Return (NLR)',
    '- 18-Hour Lunar (Quarti-NLR)',
    'Kinetic Anlunar Return (KAR)',
    '- Quarti-KAR #1',
    '- Demi-KAR',
    '- Quarti-KAR #2',
    'Sidereal Yoga Return (SYR)',
    '- Quarti-SYR #1',
    '- Demi-SYR',
    '- Quarti-SYR #2',
    'Lunar Synodic Return (LSR)',
    '- Quarti-LSR #1',
    '- Demi-LSR',
    '- Quarti-LSR #2',
    'SoliLunar (SoLu)',
    '- Quarto-SoLu #1',
    '- Demi-SoLu',
    '- Quarti-SoLu #2',
    'LuniSolar (LuSo)',
    '- Quarti-LuSo #1',
    '- Demi-LuSo',
    '- Quarti-LuSo #2',
]


class SolunarsAllInOne(Frame):
    def __init__(self, base, filename, program_options: ProgramOptions):
        super().__init__()
        now = dt.utcnow()

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

        Label(self, 'Date ' + DATE_FMT, 0.1, 0.1, 0.15, anchor=tk.W)
        Label(self, 'Time UT H M S ', 0.1, 0.15, 0.15, anchor=tk.W)
        Label(self, 'Location', 0.1, 0.2, 0.15, anchor=tk.W)
        Label(self, 'Lat D M S', 0.1, 0.25, 0.15, anchor=tk.W)
        Label(self, 'Long D M S', 0.1, 0.3, 0.15, anchor=tk.W)
        Label(self, 'Options', 0.1, 0.4, 0.15, anchor=tk.W)

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
        Radiobutton(self, self.search, 0, 'Active Charts', 0.6, 0.6, 0.3).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 0)
        )
        Radiobutton(self, self.search, 1, 'Forwards', 0.6, 0.65, 0.3).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 1)
        )
        Radiobutton(self, self.search, 2, 'Backwards', 0.6, 0.7, 0.3).bind(
            '<Button-1>', lambda _: delay(self.toggle_year, 2)
        )

        self.search.value = 0
        self.search.focus()

        self.oneyear = Checkbutton(
            self, 'All Selected For Months:', 0.6, 0.8, 0.3
        )

        self.all_for_months = Entry(self, '6', 0.8, 0.8, 0.025)

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

        Button(self, 'Clear', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        backbtn = Button(self, 'Back', 0.8, 0.95, 0.20)
        backbtn.bind('<Button-1>', lambda _: delay(self.back))
        self.status = Label(self, '', 0, 0.9, 1)

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
            # We must be unselecting the only selection
            widget.delete(0, tk.END)

            for (insertion_conter, item) in enumerate(self._options):
                widget.insert(tk.END, item)
                if item.startswith('---'):
                    widget.itemconfig(insertion_conter, fg='gray')

            self._in_callback = False
            return

        selected_items = []

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

        for (insertion_conter, item) in enumerate(
            selected_items + originals_minus_starred
        ):
            widget.insert(tk.END, item)
            if item.startswith('---'):
                widget.itemconfig(insertion_conter, fg='gray')

        # Reselect all newly added/promoted starred items
        widget.select_clear(0, tk.END)
        for i, item in enumerate(widget.get(0, tk.END)):
            if item in selected_items:
                widget.select_set(i)

        self._in_callback = False

    def enable_find(self):
        self.findbtn.disabled = False

    def toggle_year(self, value):
        pass

    def back(self):
        self.destroy()

    def select_all_of_type(self, preset):
        self._in_callback = True
        # already_selected = self.listbox.selections
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

        already_selected.reverse()

        for (insertion_conter, item) in enumerate(
            already_selected + originals_minus_starred
        ):
            self.listbox.insert(tk.END, item)
            if item.startswith('---'):
                self.listbox.itemconfig(insertion_conter, fg='gray')

        # Reselect all originally selected items
        self.listbox.select_clear(0, tk.END)
        for i, item in enumerate(self.listbox.get(0, tk.END)):
            if item in already_selected:
                self.listbox.select_set(i)

        self._in_callback = False

    def clear_selections(self):
        self._in_callback = True

        # Rebuild final listbox
        self.listbox.delete(0, tk.END)

        for (insertion_conter, item) in enumerate(self._options):
            self.listbox.insert(tk.END, item)
            if item.startswith('---'):
                self.listbox.itemconfig(insertion_conter, fg='gray')

        # Reselect all newly added/promoted starred items
        self.listbox.select_clear(0, tk.END)

        self._in_callback = False

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
