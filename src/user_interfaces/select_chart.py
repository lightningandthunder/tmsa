# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import shutil
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from src import *
from src.constants import DEV_MODE
from src.models.charts import INGRESSES
from src.user_interfaces.more_charts import MoreCharts
from src.user_interfaces.new_chart import NewChart
from src.user_interfaces.solunars import Solunars
from src.user_interfaces.solunarsV2 import SolunarsV2
from src.user_interfaces.widgets import *
from src.utils.chart_utils import make_chart_path
from src.utils.format_utils import display_name, parse_version_from_txt_file
from src.utils.gui_utils import (
    ShowHelp,
    newline_if_past_breakpoint,
    show_not_implemented,
)
from src.utils.os_utils import open_file
from src.user_interfaces.widgets import main


class SelectChart(Frame):
    def __init__(self):
        super().__init__()
        main.bind('<Configure>', self.resize)

        self.fnlbl = Label(self, '', 0, 0, 1)
        self.filename = ''
        self.first = Button(self, 'Find Chart', 0.3, 0.05, 0.2)
        self.first.bind('<Button-1>', lambda _: delay(self.find_file))
        self.first.focus()
        Button(self, 'Show Chart', 0.5, 0.05, 0.2).bind(
            '<Button-1>', lambda _: delay(self.show_file)
        )
        Button(self, 'Export Chart', 0.3, 0.1, 0.2).bind(
            '<Button-1>', lambda _: delay(self.export_file)
        )
        self.recalculate_button = Button(
            self, 'Recalculate Chart', 0.5, 0.1, 0.2
        )
        self.recalculate_button.bind(
            '<Button-1>', lambda _: delay(self.recalculate)
        )

        Button(self, 'Delete Chart', 0.3, 0.15, 0.2).bind(
            '<Button-1>', lambda _: delay(self.delete_file)
        )
        Button(self, 'Solunars', 0.5, 0.15, 0.2).bind(
            '<Button-1>', lambda _: delay(self.solunars)
        )
        Button(self, 'Clear History', 0.3, 0.2, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear_history)
        )
        self.predictive_methods_button = Button(
            self,
            'Predictive Methods',
            0.5,
            0.2,
            0.2,
            button_color=DISABLED_BUTTON_COLOR,
        )
        self.predictive_methods_button.bind(
            '<Button-1>', lambda _: delay(show_not_implemented)
        )
        Button(self, 'Help', 0.3, 0.25, 0.2).bind(
            '<Button-1>',
            lambda _: delay(
                ShowHelp, os.path.join(HELP_PATH, 'selectchart.txt')
            ),
        )
        self.last = Button(self, 'Back', 0.5, 0.25, 0.2)
        self.last.bind('<Button-1>', lambda _: delay(self.destroy))
        self.last.bind('<Tab>', lambda _: delay(self.first.focus))
        self.status = Label(self, '', 0, 0.3, 1)
        self.reclbls = []
        self.recnames = []
        for i in range(11):
            self.reclbls.append(
                Label(self, '', 0, 0.35 + 0.05 * i, 1, font=ulfont)
            )
            self.reclbls[i].bind(
                '<Button-1>', lambda e: delay(self.set_file, e.widget.text)
            )
            self.reclbls[i].bind(
                '<Button-3>', lambda e: delay(self.unset_file, e.widget.text)
            )
        Label(
            self, 'Right click a chart to remove it from history.', 0, 0.9, 1
        )
        self.morebtn = Button(self, 'More Charts', 0.4, 0.95, 0.2)
        self.morebtn.bind('<Button-1>', lambda _: delay(self.more_files))
        self.morebtn.disabled = True
        self.load_files()

    def resize_recalculate(self):
        width = main.winfo_width()

        text = newline_if_past_breakpoint(
            self.recalculate_button.text, 1350, width
        )
        self.recalculate_button.configure(
            text=text, font=font_16 if width < 1350 else base_font
        )

    def resize_predictive_methods(self):
        width = main.winfo_width()

        text = newline_if_past_breakpoint(
            self.predictive_methods_button.text, 1350, width
        )
        self.predictive_methods_button.configure(
            text=text, font=font_16 if width < 1350 else base_font
        )

    def resize(self, event):
        if self.recalculate_button.winfo_exists():
            self.resize_recalculate()
        if self.predictive_methods_button.winfo_exists():
            self.resize_predictive_methods()

    def load_files(self):
        try:
            with open(RECENT_FILE, 'r') as datafile:
                self.recs = json.load(datafile)
        except Exception:
            self.recs = []
        if len(self.recs) > 100:
            self.recs = self.recs[0:100]
        self.morebtn.disabled = True if len(self.recs) <= 11 else False
        for i in range(11):
            self.reclbls[i].text = ''
        for i in range(len(self.recs)):
            text = display_name(os.path.basename(self.recs[i]))
            self.recnames.append(text)
            if i < 11:
                self.reclbls[i].text = self.recnames[i]
        if len(self.recnames) > 0:
            self.fnlbl.text = self.recnames[0]
            self.filename = self.recs[0]
        else:
            self.find_file()

    def more_finish(self, selected):
        if selected:
            self.filename = selected
            self.fnlbl.text = display_name(selected)
            self.sort_recent()
        else:
            self.status.error('No chart chosen.')
            self.find_file()
            self.morebtn.disabled = True if len(self.recs) <= 11 else False

    def more_files(self):
        if self.morebtn.disabled:
            return
        MoreCharts(self.recs, self.more_finish, 11)

    def save_files(self):
        try:
            with open(RECENT_FILE, 'w') as datafile:
                json.dump(self.recs, datafile, indent=4)
        except Exception:
            pass

    def set_file(self, text):
        if len(self.recnames) > 0:
            i = self.recnames.index(text) if text in self.recnames else -1
            if i == -1 or i >= 11:
                return
            self.fnlbl.text = self.recnames[i]
            self.filename = self.recs[i]
            self.sort_recent()

    def unset_file(self, text):
        if len(self.recnames) > 0:
            i = self.recnames.index(text) if text in self.recnames else -1
            if i == -1 or i >= 11:
                return
            self.recs.pop(i)
            self.recnames.pop(i)
            self.sort_recent(False)

    def sort_recent(self, save=True):
        i = (
            self.recs.index(self.filename)
            if self.filename in self.recs
            else -1
        )
        if i > -1:
            self.recs.pop(i)
            self.recnames.pop(i)
        if save:
            self.recs.insert(0, self.filename)
            self.recnames.insert(0, self.fnlbl.text)
            if len(self.recs) > 50:
                self.recs = self.recs[0:50]
                self.recnames = self.recnames[0:50]
        for i in range(11):
            self.reclbls[i].text = ''
        for i in range(min(len(self.recnames), 11)):
            self.reclbls[i].text = self.recnames[i]
        self.morebtn.disabled = True if len(self.recs) <= 11 else False
        self.save_files()

    def clear_history(self):
        if os.path.exists(RECENT_FILE):
            try:
                os.remove(RECENT_FILE)
                self.recs = []
                self.recnames = []
                self.fnlbl.text = ''
                self.filename = ''
                for i in range(11):
                    self.reclbls[i].text = ''
            except Exception as e:
                self.status.error(f'Unable to clear history.')

    def find_file(self):
        self.status.text = ''
        self.filename = ''
        self.fnlbl.text = ''
        name = tkfiledialog.askopenfilename(
            initialdir=CHART_PATH, filetypes=[('Chart Files', '*.dat')]
        )
        if name:
            name = name.replace('/', os.path.sep)
            self.filename = name
            self.fnlbl.text = display_name(name)
            self.sort_recent()
        else:
            self.status.error('No chart chosen.')

    def show_file(self):
        if self.filename == '':
            return
        self.sort_recent()
        filename = self.migrate(self.filename)
        if filename == '':
            return
        filename = filename[0:-3] + 'txt'
        if os.path.exists(filename):
            open_file(filename)
        else:
            self.recalculate()

    def recalculate(self):
        if self.filename == '':
            return
        self.sort_recent()
        try:
            with open(self.filename) as file:
                chart = json.load(file)
                if chart.get('class') == 'I':
                    return self.status.error('Cannot recalculate ingresses.')
                if chart.get('base_chart', False):
                    chart['base_chart'] = None
                    chart['type'] += ' Single Wheel'
                NewChart(chart)
        except Exception as e:
            self.status.error(
                f"Unable to open file '{os.path.basename(self.filename)}'."
            )

    def export_file(self):
        if self.filename == '':
            return
        name = tkfiledialog.asksaveasfilename(
            initialfile=os.path.basename(self.filename),
            initialdir=CHART_PATH + os.path.join('..', '..'),
        )
        if not name:
            self.status.error('No export location chosen.')
            return
        name = name.replace('/', os.path.sep)
        try:
            shutil.copyfile(self.filename, name)
            self.status.text = f'{self.fnlbl.text} exported.'
            self.sort_recent()
        except Exception as e:
            self.status.error(
                f"Unable to export file: '{os.path.basename(self.filename)}'"
            )

    def delete_file(self):
        if self.filename == '':
            return
        if tkmessagebox.askyesno(
            'Are you sure?', f"Delete chart '{self.fnlbl.text}'?"
        ):
            try:
                os.remove(self.filename)
                filename = self.filename[0:-3] + 'txt'
                if os.path.exists(filename):
                    os.remove(filename)
                self.status.text = f'{self.fnlbl.text} deleted.'
                self.sort_recent(False)
            except Exception as e:
                self.status.error(
                    f"Unable to delete file: '{os.path.basepath(filename)}'."
                )

    def solunars(self):
        if self.filename == '':
            return
        try:
            with open(self.filename) as file:
                chart = json.load(file)
            if 'version' not in chart:
                datafile_name = self.filename[0:-3] + 'txt'
                chart['version'] = parse_version_from_txt_file(datafile_name)

            self.sort_recent()
            if chart.get('base_chart', None):
                chart['basechart'] = None
            main.after(0, self.destroy())
            if DEV_MODE:
                SolunarsV2(chart, self.filename)
            else:
                Solunars(chart, self.filename)
        except Exception as e:
            self.status.error(
                f"Unable to open file: '{os.path.basename(self.filename)}' : {e}."
            )
            return

    def migrate(self, filename):
        if filename.count('~') > 1:
            return filename
        path = os.path.join(CHART_PATH, filename[0], filename)
        try:
            with open(filename) as datafile:
                chart = json.load(datafile)
            newpath = make_chart_path(
                chart,
                False,
                is_ingress=True
                if chart.type in INGRESSES or not chart.name
                else False,
            )
            if not os.path.exists(newpath):
                os.makedirs(os.path.dirname(newpath), exist_ok=True)
            shutil.move(path, newpath)
            tpath = path[0:-3] + 'txt'
            tnewpath = newpath[0:-3] + 'txt'
            shutil.move(tpath, tnewpath)
            self.recs[0] = newpath
            self.recnames[0] = display_name(newpath)
            self.save_files()
            self.load_files()
            return newpath
        except Exception as e:
            self.status.error(
                f"Unable to convert '{os.path.basename(filename)}' to new format ."
            )
            tkmessagebox.showinfo('?', str(e))
            return ''
