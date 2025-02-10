# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src import *
from src.user_interfaces.widgets import *


class ExtraPlanetOptions(Frame):
    def __init__(self, name, extra_bodies, completion_function):
        super().__init__()
        self.completion_function = completion_function
        self.extra_bodies = extra_bodies

        self.status = Label(self, '', 0, 0.5, 1)

        Label(self, f'Extra Planets For {name}', 0, 0, 1)

        Label(self, 'Asteroids', 0.1, 0.1, 0.3, anchor='w')
        self.vesta = Checkbutton(self, 'Vesta (Vs)', 0.1, 0.15, 0.3)
        self.vesta.checked = 'Vs' in extra_bodies

        self.juno = Checkbutton(self, 'Juno (Jn)', 0.1, 0.20, 0.3)
        self.juno.checked = 'Jn' in extra_bodies

        self.ceres = Checkbutton(self, 'Ceres (Ce)', 0.1, 0.25, 0.3)
        self.ceres.checked = 'Ce' in extra_bodies

        self.pallas = Checkbutton(self, 'Pallas (Pa)', 0.1, 0.3, 0.3)
        self.pallas.checked = 'Pa' in extra_bodies

        self.chiron = Checkbutton(self, 'Chiron (Ch)', 0.1, 0.35, 0.3)
        self.chiron.checked = 'Ch' in extra_bodies

        Label(self, 'Trans-Neptunian Objects', 0.4, 0.1, 0.3, anchor='w')

        self.orcus = Checkbutton(self, 'Orcus (Or)', 0.4, 0.15, 0.3)
        self.orcus.checked = 'Or' in extra_bodies

        self.haumea = Checkbutton(self, 'Haumea (Ha)', 0.4, 0.2, 0.3)
        self.haumea.checked = 'Ha' in extra_bodies

        self.quaoar = Checkbutton(self, 'Quaoar (Qu)', 0.4, 0.25, 0.3)
        self.quaoar.checked = 'Qu' in extra_bodies

        self.makemake = Checkbutton(self, 'Makemake (Mk)', 0.4, 0.30, 0.3)
        self.makemake.checked = 'Mk' in extra_bodies

        self.gonggong = Checkbutton(self, 'Gonggong (Go)', 0.4, 0.35, 0.3)
        self.gonggong.checked = 'Go' in extra_bodies

        self.eris = Checkbutton(self, 'Eris (Er)', 0.4, 0.40, 0.3)
        self.eris.checked = 'Er' in extra_bodies

        self.sedna = Checkbutton(self, 'Sedna (Se)', 0.4, 0.45, 0.3)
        self.sedna.checked = 'Se' in extra_bodies

        Button(self, 'Save', 0.1, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.save_extra_planets)
        )

        Button(self, 'Back', 0.3, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.back)
        )

    def save_extra_planets(self):
        self.status.text = ''
        try:
            extra_bodies = []
            if self.chiron.checked:
                extra_bodies.append('Ch')
            if self.ceres.checked:
                extra_bodies.append('Ce')
            if self.juno.checked:
                extra_bodies.append('Jn')
            if self.pallas.checked:
                extra_bodies.append('Pa')
            if self.vesta.checked:
                extra_bodies.append('Vs')
            if self.eris.checked:
                extra_bodies.append('Er')
            if self.haumea.checked:
                extra_bodies.append('Ha')
            if self.makemake.checked:
                extra_bodies.append('Mk')
            if self.gonggong.checked:
                extra_bodies.append('Go')
            if self.quaoar.checked:
                extra_bodies.append('Qu')
            if self.orcus.checked:
                extra_bodies.append('Or')
            if self.sedna.checked:
                extra_bodies.append('Se')

            self.extra_bodies = extra_bodies

            self.destroy()
            self.completion_function(self.extra_bodies)
        except Exception as e:
            self.status.error('Error saving extra planet options: ' + str(e))

    def back(self):
        self.destroy()
        self.completion_function(self.extra_bodies)
