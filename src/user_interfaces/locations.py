# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json

from src.program_launch import *
from src.user_interfaces.widgets import *
from src.utils.chart_utils import *


class Locations(Frame):
    def __init__(self, listing, callback):
        super().__init__()
        self.callback = callback
        self.listing = listing
        self.names = [
            f'{item[0]} {fmt_lat(item[1])} {fmt_long(item[2])}'
            for item in listing
        ]
        self.locdict = {}
        for i in range(len(self.names)):
            self.locdict[self.names[i]] = self.listing[i]
        self.lbls = []
        Label(self, 'Select Location', 0, 0, 1)
        for i in range(17):
            self.lbls.append(
                Label(self, '', 0, i * 0.05 + 0.05, 1, font=ulfont)
            )
            self.lbls[i].bind(
                '<Button-1>', lambda e: delay(self.set_result, e.widget.text)
            )
            self.lbls[i].bind(
                '<Button-3>', lambda e: delay(self.remove, e.widget.text)
            )
        for i in range(min(17, len(self.listing))):
            self.lbls[i].text = self.names[i]
        Label(
            self,
            'Right click a location to remove it from history.',
            0,
            0.9,
            1,
        )
        Button(self, 'Not Found', 0.4, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.not_found)
        )

    def set_result(self, value):
        if value == '':
            return
        self.destroy()
        self.callback(self.locdict.get(value, None))

    def not_found(self):
        self.destroy()
        self.callback(None)

    def remove(self, value):
        file = self.locdict.get(value, None)
        if not file:
            return
        index = self.listing.index(file) if file in self.listing else -1
        if index == -1:
            return
        self.listing.pop(index)
        self.names.pop(index)
        for i in range(17):
            self.lbls[i].text = ''
        for i in range(min(17, len(self.listing))):
            self.lbls[i].text = self.names[i]
        try:
            with open(LOCATIONS_FILE, 'w') as datafile:
                json.dump(self.listing, datafile, indent=4)
        except Exception:
            pass
