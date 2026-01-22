# Copyright 2026 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src import *
from src.user_interfaces.widgets import *
from src.utils.format_utils import display_name


class MoreCharts(Frame):
    def __init__(self, listing, callback, offset):
        super().__init__()
        self.listing = listing
        self.callback = callback
        self.offset = offset
        self.file_labels = []
        self.names = {}
        Label(self, 'Select Chart', 0, 0, 1)
        for i in range(17):
            self.file_labels.append(
                Label(self, '', 0, i * 0.05 + 0.05, 1, font=ulfont)
            )
            self.file_labels[i].bind(
                '<Button-1>', lambda e: delay(self.set_result, e.widget.text)
            )
            self.file_labels[i].bind(
                '<Button-3>', lambda e: delay(self.remove, e.widget.text)
            )
        for i in range(min(17, len(self.listing) - self.offset)):
            self.file_labels[i].text = display_name(
                self.listing[i + self.offset]
            )
            self.names[self.file_labels[i].text] = self.listing[
                i + self.offset
            ]
        Label(
            self, 'Right click a chart to remove it from history.', 0, 0.9, 1
        )

        if len(self.listing) - self.offset >= 17:
            Button(self, 'Previous', 0.3, 0.95, 0.2).bind(
                '<Button-1>', lambda _: self.destroy()
            )
            Button(self, 'Next', 0.5, 0.95, 0.2).bind(
                '<Button-1>', lambda _: delay(self.next_page())
            )
        else:
            Button(self, 'Previous', 0.4, 0.95, 0.2).bind(
                '<Button-1>', lambda _: self.destroy()
            )

        Button(self, 'Search Files', 0.8, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.not_found)
        )

    def set_result(self, value):
        if value == '':
            return
        self.destroy()
        self.callback(self.names.get(value, None))

    def next_page(self):
        MoreCharts(self.listing, self.callback, self.offset + 17)

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
            self.file_labels[i].text = ''
        for i in range(min(17, len(self.listing) - self.offset)):
            self.file_labels[i].text = display_name(
                self.listing[i + self.offset]
            )
