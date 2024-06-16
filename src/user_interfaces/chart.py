# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import tkinter.messagebox as tkmessagebox

from src import OPTION_PATH, RECENT_FILE
from src.swe import (calc_ayan, calc_azimuth, calc_cusps, calc_house_pos,
                     calc_lat_to_lmt, calc_meridian_longitude, calc_obliquity,
                     calc_planet, cotrans, julday)
from src.user_interfaces.biwheelV2 import BiwheelV2
from src.user_interfaces.uniwheelV2 import UniwheelV2
from src.utils.chart_utils import make_chart_path
from src.utils.format_utils import to360

planet_names = [
    'Moon',
    'Sun',
    'Mercury',
    'Venus',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Pluto',
    'Eris',
    'Sedna',
    'Mean Node',
    'True Node',
]
planet_indices = [1, 0] + [i for i in range(2, 10)] + [146199, 100377, 10, 11]


class Chart:
    def __init__(self, chart, temporary, burst=False):
        self.jd = julday(
            chart['year'],
            chart['month'],
            chart['day'],
            chart['time'] + chart['correction'],
            chart['style'],
        )
        self.long = chart['longitude']
        if chart['zone'] == 'LAT':
            self.jd = calc_lat_to_lmt(self.jd, self.long)
        self.ayan = calc_ayan(self.jd)
        chart['ayan'] = self.ayan
        self.oe = calc_obliquity(self.jd)
        chart['oe'] = self.oe
        self.lat = chart['latitude']
        (cusps, angles) = calc_cusps(self.jd, self.lat, self.long)
        self.ramc = angles[0]
        chart['cusps'] = cusps
        chart['ramc'] = self.ramc
        chart['Vertex'] = [
            angles[1],
            calc_house_pos(
                self.ramc, self.lat, self.oe, to360(angles[1] + self.ayan), 0
            ),
        ]
        chart['Eastpoint'] = [
            angles[2],
            calc_house_pos(
                self.ramc, self.lat, self.oe, to360(angles[2] + self.ayan), 0
            ),
        ]
        for i in range(len(planet_indices)):
            planet_index = planet_indices[i]
            planet_name = planet_names[i]

            [
                longitude,
                latitude,
                speed,
                right_ascension,
                declination,
            ] = calc_planet(self.jd, planet_index)
            [azimuth, altitude] = calc_azimuth(
                self.jd,
                self.long,
                self.lat,
                to360(longitude + self.ayan),
                latitude,
            )
            house_position = calc_house_pos(
                self.ramc,
                self.lat,
                self.oe,
                to360(longitude + self.ayan),
                latitude,
            )
            meridian_longitude = calc_meridian_longitude(azimuth, altitude)

            data = [
                longitude,
                latitude,
                speed,
                right_ascension,
                declination,
                azimuth,
                altitude,
                meridian_longitude,
                house_position,
            ]

            chart[planet_name] = data

        self.save_and_print(chart, temporary, burst)

    def save_and_print(self, chart, temporary, burst):
        try:
            optfile = chart['options'].replace(' ', '_') + '.opt'
            with open(os.path.join(OPTION_PATH, optfile)) as datafile:
                options = json.load(datafile)
        except Exception:
            tkmessagebox.showerror(
                'File Error', f"Unable to open '{optfile}'."
            )
            return
        filename = make_chart_path(chart, temporary)
        if not burst:
            try:
                with open(RECENT_FILE, 'r') as datafile:
                    recent = json.load(datafile)
            except Exception:
                recent = []
        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        try:
            with open(filename, 'w') as datafile:
                json.dump(chart, datafile, indent=4)
        except Exception as e:
            tkmessagebox.showerror('Unable to save file', f'{e}')
            return
        if not burst:
            if filename in recent:
                recent.remove(filename)
            recent.insert(0, filename)
            try:
                with open(RECENT_FILE, 'w') as datafile:
                    json.dump(recent, datafile, indent=4)
            except Exception:
                pass
        if chart.get('base_chart', None):
            self.precess(chart['base_chart'])
            self.report = BiwheelV2(chart, temporary, options)
        else:
            self.report = UniwheelV2(chart, temporary, options)

    def precess(self, chart):
        for planet_name in planet_names:
            planet_data = chart[planet_name]
            planet_data[3:5] = cotrans(
                [planet_data[0] + self.ayan, planet_data[1], planet_data[2]],
                self.oe,
            )
            planet_data[5:7] = calc_azimuth(
                self.jd,
                self.long,
                self.lat,
                to360(planet_data[0] + self.ayan),
                planet_data[1],
            )
            planet_data[7] = calc_meridian_longitude(
                planet_data[5], planet_data[6]
            )

            planet_data[8] = calc_house_pos(
                self.ramc,
                self.lat,
                self.oe,
                to360(planet_data[0] + self.ayan),
                planet_data[1],
            )
            chart[planet_name] = planet_data
