# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk

from src import *
from src.user_interfaces.widgets import *


class BetaFeatures(Frame):
    def __init__(self):
        super().__init__()

        Label(self, 'Current Unfinished Features', 0, 0, 1, font=font_24)
        Label(
            self,
            'Features listed below will be enabled if Enable Beta Features is set.',
            0,
            0.05,
            1,
        )
        Label(
            self,
            '· Toggle non-traditional bodies via separate page off of Chart Options.',
            0,
            0.2,
            1,
        )
        Label(
            self,
            '· New asteroids: Chiron, Ceres, Pallas, Juno, Vesta.',
            0,
            0.25,
            1,
        )
        Label(
            self, '· New TNOs: Haumea, Makemake, Gonggong, Quaoar.', 0, 0.3, 1
        )

        Button(self, 'Back', 0.45, 0.75, 0.1).bind(
            '<Button-1>', lambda _: delay(self.destroy)
        )
