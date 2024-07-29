# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from io import TextIOWrapper
import tkinter.messagebox as tkmessagebox
from datetime import datetime

import src.models.charts as chart_models
import src.models.options as option_models
import src.constants as constants
from src.user_interfaces.core_chart import CoreChart
import src.utils.chart_utils as chart_utils
import src.models.angles as angles_models


class Uniwheel(CoreChart):
    table_width = 81

    def __init__(
        self,
        charts: list[chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        super().__init__(charts, temporary, options)
        self.core_chart = charts[0]
        filename = chart_utils.make_chart_path(charts[0], temporary)
        filename = filename[0:-3] + 'txt'
        try:
            chartfile = open(filename, 'w')
        except Exception as e:
            tkmessagebox.showerror(f'Unable to open file:', f'{e}')
            return

        with chartfile:
            self.draw_chart(chartfile)
            self.write_info_table(chartfile)

            chartfile.write('\n' + '-' * self.table_width + '\n')
            chartfile.write(
                f"Created by Time Matters {constants.VERSION}  ({datetime.now().strftime('%d %b %Y')})"
            )

    def draw_chart(
        self,
        chartfile: TextIOWrapper,
    ):
        chart_grid = self.make_chart_grid(rows=65, cols=69)

        chart = self.charts[0]

        chartfile.write('\n')

        if chart.type not in chart_utils.INGRESSES:
            name = chart.name
            if ';' in name:
                name = name.split(';')[0]
            chart_grid[21][18:51] = chart_utils.center_align(name)
        chtype = str(chart.type.value)
        if chtype.endswith(' Single Wheel'):
            chtype = chtype.replace(' Single Wheel', '')
        chart_grid[23][18:51] = chart_utils.center_align(chtype)
        line = str(chart.day) + ' ' + constants.MONTHS[chart.month - 1] + ' '
        line += (
            f'{chart.year} ' if chart.year > 0 else f'{-chart.year + 1} BCE '
        )
        if not chart.style:
            line += 'OS '
        line += chart_utils.fmt_hms(chart.time) + ' ' + chart.zone
        chart_grid[25][18:51] = chart_utils.center_align(line)
        chart_grid[27][18:51] = chart_utils.center_align(chart.location)
        chart_grid[29][18:51] = chart_utils.center_align(
            chart_utils.fmt_lat(chart.geo_latitude)
            + ' '
            + chart_utils.fmt_long(chart.geo_longitude)
        )
        chart_grid[31][18:51] = chart_utils.center_align(
            'UT ' + chart_utils.fmt_hms(chart.time + chart.correction)
        )
        chart_grid[33][18:51] = chart_utils.center_align(
            'RAMC ' + chart_utils.fmt_dms(chart.ramc)
        )
        chart_grid[35][18:51] = chart_utils.center_align(
            'OE ' + chart_utils.fmt_dms(chart.obliquity)
        )
        chart_grid[37][18:51] = chart_utils.center_align(
            'SVP ' + chart_utils.zod_sec(360 - chart.ayanamsa)
        )
        chart_grid[39][18:51] = chart_utils.center_align('Sidereal Zodiac')
        chart_grid[41][18:51] = chart_utils.center_align('Campanus Houses')
        chart_grid[43][18:51] = chart_utils.center_align(
            chart.notes or '* * * * *'
        )

        x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
        y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
        houses = [[] for _ in range(12)]
        for index in range(12):
            houses[index] = super().sort_house(self.charts, index)
            if index > 3 and index < 9:
                houses[index].reverse()
            for sub_index in range(15):
                if houses[index][sub_index]:
                    temp = houses[index][sub_index]
                    if len(temp) > 2:
                        planet = houses[index][sub_index][0]
                        chart_grid[y[index] + sub_index][
                            x[index] : x[index] + 16
                        ] = self.insert_planet_into_line(chart, planet)

        for row in chart_grid:
            chartfile.write(' ')
            for col in row:
                chartfile.write(col)
            chartfile.write('\n')

        chartfile.write('\n\n' + '-' * self.table_width + '\n')
