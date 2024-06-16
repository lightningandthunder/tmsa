# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src.program_launch import *
from src.user_interfaces.widgets import *
from src.utils.format_utils import display_name


class MoreCharts(Frame):
    def __init__(self, listing, callback, offset):
        super().__init__()
        self.listing = listing
        self.callback = callback
        self.offset = offset
        self.lbls = []
        self.names = {}
        Label(self, 'Select Chart', 0, 0, 1)
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
        for i in range(min(17, len(self.listing) - offset)):
            self.lbls[i].text = display_name(self.listing[i + offset])
            self.names[self.lbls[i].text] = self.listing[i + offset]
        Label(
            self, 'Right click a chart to remove it from history.', 0, 0.9, 1
        )
        Button(self, 'Not Found', 0.4, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.not_found)
        )

    def set_result(self, value):
        if value == '':
            return
        self.destroy()
        self.callback(self.names.get(value, None))

    def not_found(self):
        self.destroy()
        self.callback(None)

    def remove(self, value):
        file = self.names.get(value, None)
        if not file:
            return
        index = self.listing.index(file) if file in self.listing else -1
        if index == -1:
            return
        self.listing.pop(index)
        for i in range(17):
            self.lbls[i].text = ''
        for i in range(min(17, len(self.listing) - self.offset)):
            self.lbls[i].text = display_name(self.listing[i + self.offset])
