# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src import *
from src.user_interfaces.widgets import *
from src.utils.gui_utils import ShowHelp


class PVPOptions(Frame):
    def __init__(self, name, pvp_opts, func):
        super().__init__()
        self.pvp_opts = pvp_opts
        self.func = func

        self.enable_pvp = Checkbutton(self, 'Enable', 0.4, 0.35, 0.215)
        self.enable_pvp.checked = pvp_opts.get('enabled', False)

        Label(self, f'Prime Vertical Paran Options For {name}', 0, 0, 1)
        Label(self, 'Orb in degrees, to omit leave blank.', 0, 0.05, 1)
        Label(self, 'C1', 0.4, 0.1, 0.05)
        Label(self, 'C2', 0.5, 0.1, 0.05)
        Label(self, 'C3', 0.6, 0.1, 0.05)

        Label(self, '0', 0.3, 0.15, 0.1)
        self.conjunction_1 = Entry(self, '', 0.4, 0.15, 0.05)
        self.conjunction_1.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.conjunction_1)
        )
        self.conjunction_2 = Entry(self, '', 0.5, 0.15, 0.05)
        self.conjunction_2.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.conjunction_2)
        )
        self.conjunction_3 = Entry(self, '', 0.6, 0.15, 0.05)
        self.conjunction_3.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.conjunction_3)
        )

        Label(self, '180', 0.3, 0.2, 0.1)
        self.opposition_1 = Entry(self, '', 0.4, 0.2, 0.05)
        self.opposition_1.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.opposition_1)
        )
        self.opposition_2 = Entry(self, '', 0.5, 0.2, 0.05)
        self.opposition_2.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.opposition_2)
        )
        self.opposition_3 = Entry(self, '', 0.6, 0.2, 0.05)
        self.opposition_3.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.opposition_3)
        )

        Label(self, '90', 0.3, 0.25, 0.1)
        self.square_1 = Entry(self, '', 0.4, 0.25, 0.05)
        self.square_1.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.square_1)
        )
        self.square_2 = Entry(self, '', 0.5, 0.25, 0.05)
        self.square_2.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.square_2)
        )
        self.square_3 = Entry(self, '', 0.6, 0.25, 0.05)
        self.square_3.bind(
            '<KeyRelease>', lambda _: delay(check_dec, self.square_3)
        )

        Button(self, 'Save', 0.1, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Clear', 0.3, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        Button(self, 'Help', 0.5, 0.55, 0.2).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, HELP_PATH + r'\pvp_options.txt'),
        )
        Button(self, 'Back', 0.7, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.back)
        )
        self.status = Label(self, '', 0, 0.5, 1)

        conjunction_class_1 = pvp_opts.get('0')[0]
        if conjunction_class_1:
            self.conjunction_1.text = conjunction_class_1

        conjunction_class_2 = pvp_opts.get('0')[1]
        if conjunction_class_2:
            self.conjunction_2.text = conjunction_class_2

        conjunction_class_3 = pvp_opts.get('0')[2]
        if conjunction_class_3:
            self.conjunction_3.text = conjunction_class_3

        opposition_class_1 = pvp_opts.get('180')[0]
        if opposition_class_1:
            self.opposition_1.text = opposition_class_1

        opposition_class_2 = pvp_opts.get('180')[1]
        if opposition_class_2:
            self.opposition_2.text = opposition_class_2

        opposition_class_3 = pvp_opts.get('180')[2]
        if opposition_class_3:
            self.opposition_3.text = opposition_class_3

        square_class_1 = pvp_opts.get('90')[0]
        if square_class_1:
            self.square_1.text = square_class_1

        square_class_2 = pvp_opts.get('90')[1]
        if square_class_2:
            self.square_2.text = square_class_2

        square_class_3 = pvp_opts.get('90')[2]
        if square_class_3:
            self.square_3.text = square_class_3

    def clear(self):
        self.conjunction_1.text = ''
        self.conjunction_2.text = ''
        self.conjunction_3.text = ''
        self.opposition_1.text = ''
        self.opposition_2.text = ''
        self.opposition_3.text = ''
        self.square_1.text = ''
        self.square_2.text = ''
        self.square_3.text = ''

    def save(self):
        self.status.text = ''
        try:
            co_1 = self.conjunction_1.text.strip()
            co_1 = float(co_1) if co_1 else 0
            co_2 = self.conjunction_2.text.strip()
            co_2 = float(co_2) if co_2 else 0
            co_3 = self.conjunction_3.text.strip()
            co_3 = float(co_3) if co_3 else 0
            self.pvp_opts['0'] = [co_1, co_2, co_3]

            op_1 = self.opposition_1.text.strip()
            op_1 = float(op_1) if op_1 else 0
            op_2 = self.opposition_2.text.strip()
            op_2 = float(op_2) if op_2 else 0
            op_3 = self.opposition_3.text.strip()
            op_3 = float(op_3) if op_3 else 0
            self.pvp_opts['180'] = [op_1, op_2, op_3]

            sq_1 = self.square_1.text.strip()
            sq_1 = float(sq_1) if sq_1 else 0
            sq_2 = self.square_2.text.strip()
            sq_2 = float(sq_2) if sq_2 else 0
            sq_3 = self.square_3.text.strip()
            sq_3 = float(sq_3) if sq_3 else 0
            self.pvp_opts['90'] = [sq_1, sq_2, sq_3]

            self.pvp_opts['enabled'] = self.enable_pvp.checked

            self.destroy()
            self.func()
        except Exception as e:
            self.status.error('Error saving PVP options: ' + str(e))

    def back(self):
        self.pvp_opts = {}
        self.destroy()
        self.func()
