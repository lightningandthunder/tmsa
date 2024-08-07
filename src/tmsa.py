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
import shutil
import webbrowser

from chart_options import ChartOptions
from constants import VERSION
from gui_utils import ShowHelp, newline_if_past_breakpoint, show_not_implemented
from ingresses import Ingresses
from init import *
from new_chart import NewChart
from program_options import ProgramOptions
from select_chart import SelectChart
from widgets import *

TITLE = f'Time Matters {VERSION}'
INTRO = f"""A freeware program for calculating geometrically
accurate astrological charts in the Sidereal Zodiac,
as rediscovered by Cyril Fagan and Donald Bradley."""
COPYRIGHT = f"""\u00a9 2021-2024 James A. Eshelman.
Created by Mike Nelson (mikestar13)
and developed further by Mike Verducci.
Released under the GNU Affero General Public License"""
LICENSE = 'www.gnu.org/licenses/agpl-3.0.en.html'
DEDICATION = 'Dedicated to our colleagues and collaborators at'
SOLUNARS = 'www.solunars.com'
FOR_MORE_INFO = 'For more information about Sidereal Astrology, see:'
POINTS = 'www.solunars.com/viewtopic.php?f=8&t=2259'
SOURCE_CODE = 'Source code may be found at'
GITHUB = 'https://github.com/lightningandthunder/tmsa'

X_COORD = 0
WIDTH = 1
HEIGHT_UNIT = 0.022


class StartPage(Frame):
    def __init__(self):
        super().__init__()
        global startup

        self.parent = main
        self.parent.bind('<Configure>', self.resize)

        self.title = Label(self, TITLE, X_COORD, 0.025, WIDTH, font=title_font)
        self.intro = Label(
            self, INTRO, X_COORD, 0.125, WIDTH, HEIGHT_UNIT * 3, font=base_font
        )
        self.dedication = Label(
            self, DEDICATION, X_COORD, 0.225, WIDTH, HEIGHT_UNIT
        )
        self.solunars = Label(
            self, SOLUNARS, X_COORD, 0.25, WIDTH, HEIGHT_UNIT, font=ulfont
        )
        self.solunars.bind(
            '<Button-1>', lambda _: webbrowser.open_new(SOLUNARS)
        )

        self.for_more_info = Label(
            self, FOR_MORE_INFO, X_COORD, 0.325, WIDTH, HEIGHT_UNIT
        )
        self.points = Label(
            self, POINTS, X_COORD, 0.35, WIDTH, HEIGHT_UNIT, font=ulfont
        )
        self.points.bind('<Button-1>', lambda _: webbrowser.open_new(POINTS))

        self.copyright = Label(
            self, COPYRIGHT, X_COORD, 0.65, WIDTH, HEIGHT_UNIT * 4
        )

        self.license = Label(
            self, LICENSE, X_COORD, 0.74, WIDTH, HEIGHT_UNIT, font=ulfont
        )
        self.license.bind('<Button-1>', lambda _: webbrowser.open_new(LICENSE))

        self.source_code = Label(
            self, SOURCE_CODE, X_COORD, 0.825, WIDTH, HEIGHT_UNIT
        )
        Label(self, GITHUB, X_COORD, 0.85, WIDTH, HEIGHT_UNIT, font=ulfont)
        self.source_code.bind(
            '<Button-1>', lambda _: webbrowser.open_new(GITHUB)
        )

        self.chart_for_now = Button(self, 'Chart for Now', 0.2, 0.4, 0.2)
        self.chart_for_now.bind('<Button-1>', lambda _: delay(NewChart, False))
        self.chart_for_now.focus()

        Button(self, 'New Chart', 0.4, 0.4, 0.2).bind(
            '<Button-1>', lambda _: delay(NewChart)
        )
        Button(self, 'Select Chart', 0.6, 0.4, 0.2).bind(
            '<Button-1>', lambda _: delay(SelectChart)
        )
        Button(self, 'Ingresses', 0.2, 0.45, 0.2).bind(
            '<Button-1>', lambda _: delay(Ingresses)
        )
        default = (
            'Student Natal'
            if os.path.exists(STUDENT_FILE)
            else 'Default Natal'
        )

        self.chart_options = Button(self, 'Chart Options', 0.4, 0.45, 0.2)
        self.chart_options.bind(
            '<Button-1>', lambda _: delay(ChartOptions, default)
        )

        self.predictive_options = Button(
            self, 'Predictive Options', 0.6, 0.45, 0.2, font=base_font
        )
        self.predictive_options.bind(
            '<Button-1>', lambda _: delay(show_not_implemented)
        )

        Button(self, 'Help', 0.2, 0.5, 0.2).bind(
            '<Button-1>', lambda _: delay(ShowHelp, HELP_PATH + r'\main.txt')
        )
        self.program_options = Button(
            self, 'Program Options', 0.4, 0.5, 0.2, font=font_16
        )
        self.program_options.bind(
            '<Button-1>', lambda _: delay(ProgramOptions)
        )

        Button(self, 'Exit Program', 0.6, 0.5, 0.2).bind(
            '<Button-1>', lambda _: delay(main.destroy)
        )

        if not startup:
            return
        startup = False

        try:
            if os.path.exists(TEMP_CHARTS):
                shutil.rmtree(TEMP_CHARTS)
            os.mkdir(TEMP_CHARTS)
        except:
            return

        try:
            with open(RECENT_FILE, 'r') as datafile:
                recs = json.load(datafile)
        except:
            return

        recs = [rec for rec in recs if '\\temporary\\' not in rec]
        if len(recs) > 100:
            recs = recs[0:100]
        try:
            with open(RECENT_FILE, 'w') as datafile:
                recs = json.dump(recs, datafile, indent=4)
        except:
            pass

    def resize(self, event):
        self.resize_predictive_options()
        self.resize_program_options()
        self.resize_chart_options()
        self.resize_chart_for_now()
        self.resize_intro()

    def resize_intro(self):
        height = self.parent.winfo_height()

        scale_factor = height / 1070 if height < 1070 else 1
        self.intro.configure(height=math.floor(scale_factor * HEIGHT_UNIT * 3))
        if height < 800:
            self.intro.configure(font=font_10)
        elif height < 1070:
            self.intro.configure(font=font_12)
        else:
            self.intro.configure(font=base_font)

    def resize_predictive_options(self):
        width = self.parent.winfo_width()

        text = newline_if_past_breakpoint(
            self.predictive_options.text, 1350, width
        )
        self.predictive_options.configure(
            text=text, font=font_16 if width < 1350 else base_font
        )
        # font = utils.get_scaled_font(width, 1350)
        # self.predictive_options.configure(font=font)

    def resize_program_options(self):
        width = self.parent.winfo_width()

        text = newline_if_past_breakpoint(
            self.program_options.text, 1125, width
        )
        self.program_options.configure(
            text=text, font=font_16 if width < 1125 else base_font
        )
        # font = utils.get_scaled_font(width, 1125)
        # self.program_options.configure(font=font)

    def resize_chart_options(self):
        width = self.parent.winfo_width()

        text = newline_if_past_breakpoint(self.chart_options.text, 975, width)
        self.chart_options.configure(
            text=text, font=font_16 if width < 975 else base_font
        )
        # font = utils.get_scaled_font(width, 975)
        # self.chart_options.configure(font=font)

    def resize_chart_for_now(self):
        width = self.parent.winfo_width()

        text = newline_if_past_breakpoint(self.chart_for_now.text, 975, width)
        self.chart_for_now.configure(
            text=text, font=font_16 if width < 975 else base_font
        )
        # font = utils.get_scaled_font(width, 975)
        # self.chart_for_now.configure(font=font)


StartPage()
main.mainloop()
