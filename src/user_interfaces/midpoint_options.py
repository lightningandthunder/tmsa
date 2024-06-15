# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src.gui_utils import ShowHelp
from src.init import *
from src.user_interfaces.widgets import *


class MidpointOptions(Frame):
    def __init__(self, name, retdict, func):
        super().__init__()
        self.retdict = retdict
        self.func = func
        Label(self, f'Midpoint Options For {name}', 0, 0, 1)
        Label(self, 'Orb in minutes, to omit leave blank.', 0, 0.05, 1)
        Label(self, 'Ecliptical', 0, 0.1, 1)
        Label(self, '0/180', 0.4, 0.15, 0.1)
        self.mp0 = Entry(self, '', 0.5, 0.15, 0.05)
        self.mp0.bind('<KeyRelease>', lambda _: delay(check_num, self.mp0))
        Label(self, '90', 0.4, 0.2, 0.1)
        self.mp90 = Entry(self, '', 0.5, 0.2, 0.05)
        self.mp90.bind('<KeyRelease>', lambda _: delay(check_num, self.mp90))
        Label(self, 'Is 90?', 0.4, 0.25, 0.1)
        self.is90 = Radiogroup(self)
        Radiobutton(self, self.is90, 0, 'Direct', 0.5, 0.25, 0.1)
        Radiobutton(self, self.is90, 1, 'Indirect', 0.6, 0.25, 0.1)
        Label(self, '45', 0.4, 0.3, 0.1)
        self.mp45 = Entry(self, '', 0.5, 0.3, 0.05)
        self.mp45.bind('<KeyRelease>', lambda _: delay(check_num, self.mp45))
        Label(self, 'Mundane', 0, 0.35, 1)
        self.mpm = Entry(self, '', 0.475, 0.4, 0.05)
        self.mpm.bind('<KeyRelease>', lambda _: delay(check_num, self.mpm))
        Button(self, 'Save', 0.1, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Clear', 0.3, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        Button(self, 'Help', 0.5, 0.55, 0.2).bind(
            '<Button-1>',
            lambda _: delay(ShowHelp, HELP_PATH + r'\midpoint_options.txt'),
        )
        Button(self, 'Back', 0.7, 0.55, 0.2).bind(
            '<Button-1>', lambda _: delay(self.back)
        )
        self.status = Label(self, '', 0, 0.5, 1)
        mp0 = retdict.get('0')
        if mp0:
            self.mp0.text = mp0
        mp90 = retdict.get('90')
        if mp90:
            self.mp90.text = mp90
        mp45 = retdict.get('45')
        if mp45:
            self.mp45.text = mp45
        mpm = retdict.get('M')
        if mpm:
            self.mpm.text = mpm
        mis90 = retdict.get('is90', 'd')
        self.is90.value = 0 if mis90 == 'd' else 1

    def clear(self):
        self.mp0.text = ''
        self.mp90.text = ''
        self.mp45.text = ''
        self.mpm.text = ''
        self.is90.value = 0

    def save(self):
        self.status.text = ''
        try:
            m = self.mp0.text.strip()
            m = int(m) if m else 0
            if m > 90:
                return self.status.error(
                    'Orb for midpoint must be less than or equal to 90.',
                    self.mp0,
                )
            self.retdict['0'] = m
            m = self.mp90.text.strip()
            m = int(m) if m else 0
            if m > 90:
                return self.status.error(
                    'Orb for midpoint must be less than or equal to 90.',
                    self.mp90,
                )
            self.retdict['90'] = m
            m = self.mp45.text.strip()
            m = int(m) if m else 0
            if m > 90:
                return self.status.error(
                    'Orb for midpoint must be less than or equal to 90.',
                    self.mp45,
                )
            self.retdict['45'] = m
            m = self.mpm.text.strip()
            m = int(m) if m else 0
            if m > 90:
                return self.status.error(
                    'Orb for midpoint must be less than or equal to 90.',
                    self.mpm,
                )
            self.retdict['M'] = m
            self.retdict['is90'] = 'i' if self.is90.value else 'd'
            self.destroy()
            self.func()
        except Exception:
            self.status.error('Orb for midpoints must be numeric or blank.')

    def back(self):
        self.retdict = {}
        self.destroy()
        self.func()
