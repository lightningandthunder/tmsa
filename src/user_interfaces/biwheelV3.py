# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from io import TextIOWrapper

import src.models.charts as chart_models
import src.models.options as option_models
import src.constants as constants
from src.user_interfaces.core_chart import CoreChart
import src.utils.chart_utils as chart_utils
import src.utils.calculation_utils as calc_utils
from src.utils.chart_utils import (
    zod_sec,
    center_align,
    fmt_dms,
    fmt_hms,
    fmt_lat,
    fmt_long,
)


class BiwheelV3(CoreChart):
    table_width = 81
    rows = 65
    columns = 69

    def __init__(
        self,
        charts: list[chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        super().__init__(charts, temporary, options)

    def draw_chart(
        self,
        chartfile: TextIOWrapper,
    ):
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

        return_chart = calc_utils.find_outermost_chart(self.charts)
        self.cclass = self.get_return_class(return_chart)

        chartfile.write('\n')
        for column_index in range(cols):
            chart_grid[0][column_index] = '-'
            chart_grid[16][column_index] = '-'
            if column_index <= 17 or column_index >= 51:
                chart_grid[32][column_index] = '-'
            chart_grid[48][column_index] = '-'
            chart_grid[64][column_index] = '-'
        for row_index in range(rows):
            chart_grid[row_index][0] = '|'
            chart_grid[row_index][17] = '|'
            if row_index <= 16 or row_index >= 48:
                chart_grid[row_index][34] = '|'
            chart_grid[row_index][51] = '|'
            chart_grid[row_index][68] = '|'
        for index in range(0, rows, 16):
            for sub_index in range(0, cols, 17):
                if index == 32 and sub_index == 34:
                    continue
                chart_grid[index][sub_index] = '+'
        cusps = [chart_utils.zod_min(c) for c in return_chart.cusps]
        chart_grid[0][14:20] = cusps[11]
        chart_grid[0][31:37] = cusps[10]
        chart_grid[0][48:54] = cusps[9]
        chart_grid[16][0:6] = cusps[12]
        chart_grid[16][63:69] = cusps[8]
        chart_grid[32][0:6] = cusps[1]
        chart_grid[32][63:69] = cusps[7]
        chart_grid[48][0:6] = cusps[2]
        chart_grid[48][63:69] = cusps[6]
        chart_grid[64][14:20] = cusps[3]
        chart_grid[64][31:37] = cusps[4]
        chart_grid[64][48:54] = cusps[5]

        chart_grid[19][18:51] = center_align('Transiting (t) Chart')

        return_chart_type = return_chart.type.value.lower()

        if (
            'solar' not in return_chart_type
            and 'lunar' not in return_chart_type
        ):
            chart_grid[20][18:51] = center_align(return_chart.name)
        elif 'return' in return_chart_type:
            parts = return_chart.name.split(';')
            chart_grid[20][18:51] = center_align(parts[0])
        chart_grid[21][18:51] = center_align(return_chart.type.value)
        line = (
            str(return_chart.day)
            + ' '
            + constants.MONTHS[return_chart.month - 1]
            + ' '
        )
        line += (
            f'{return_chart.year} '
            if return_chart.year > 0
            else f'{-(return_chart.year) + 1} BCE '
        )
        if not return_chart.style:
            line += 'OS '
        line += fmt_hms(return_chart.time) + ' ' + return_chart.zone

        chart_grid[22][18:51] = center_align(line)
        chart_grid[23][18:51] = center_align(return_chart.location)
        chart_grid[24][18:51] = center_align(
            fmt_lat(return_chart.geo_latitude)
            + ' '
            + fmt_long(return_chart.geo_longitude)
        )
        chart_grid[25][18:51] = center_align(
            'UT ' + fmt_hms(return_chart.time + return_chart.correction)
        )
        chart_grid[26][18:51] = center_align(
            'RAMC ' + fmt_dms(return_chart.ramc)
        )
        chart_grid[27][18:51] = center_align(
            'OE ' + fmt_dms(return_chart.obliquity)
        )
        chart_grid[28][18:51] = center_align(
            'SVP ' + zod_sec(360 - return_chart.ayanamsa)
        )
        chart_grid[29][18:51] = center_align('Sidereal Zodiac')
        chart_grid[30][18:51] = center_align('Campanus Houses')
        chart_grid[31][18:51] = center_align(return_chart.notes or '')

        radix = self.find_innermost_chart()
        chart_grid[33][18:51] = center_align('Radical (r) Chart')
        if radix.type not in chart_models.INGRESSES:
            radix_type = radix.type.value.lower()
            if 'solar' not in radix_type and 'lunar' not in radix_type:
                chart_grid[34][18:51] = center_align(radix.name)
            elif 'return' in radix.name.lower():
                parts = radix.name.split(';')
                chart_grid[34][18:51] = center_align(parts[0])
        chtype = radix.type.value
        if chtype.endswith(' Single Wheel'):
            chtype = chtype.replace(' Single Wheel', '')
        chart_grid[35][18:51] = center_align(chtype)
        line = str(radix.day) + ' ' + constants.MONTHS[radix.month - 1] + ' '
        line += (
            f'{radix.year} ' if radix.year > 0 else f'{-(radix.year) + 1} BCE '
        )
        if not radix.style:
            line += 'OS '
        line += fmt_hms(radix.time) + ' ' + radix.zone
        chart_grid[36][18:51] = center_align(line)
        chart_grid[37][18:51] = center_align(radix.location)
        chart_grid[38][18:51] = center_align(
            fmt_lat(radix.geo_latitude) + ' ' + fmt_long(radix.geo_longitude)
        )
        chart_grid[39][18:51] = center_align(
            'UT ' + fmt_hms(radix.time + radix.correction)
        )
        chart_grid[40][18:51] = center_align('RAMC ' + fmt_dms(radix.ramc))
        chart_grid[41][18:51] = center_align('OE ' + fmt_dms(radix.obliquity))
        chart_grid[42][18:51] = center_align(
            'SVP ' + zod_sec(360 - radix.ayanamsa)
        )
        chart_grid[43][18:51] = center_align('Sidereal Zodiac')
        chart_grid[44][18:51] = center_align('Campanus Houses')
        chart_grid[45][18:51] = center_align(radix.notes or '')

        x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
        y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
        houses = [[] for i in range(12)]
        extras = []
        for column_index in range(12):
            houses[column_index] = self.sort_house(
                self.charts,
                column_index,
            )
            excess = len(houses[column_index]) - 15
            if excess > 0:
                extras.extend(houses[column_index][7 : 7 + excess])
                del houses[column_index][7 : 7 + excess]
            if column_index > 3 and column_index < 9:
                houses[column_index].reverse()
            for sub_index in range(15):
                if houses[column_index][sub_index]:
                    temp = houses[column_index][sub_index]
                    if len(temp) > 2:
                        planet = houses[column_index][sub_index][0]
                        if houses[column_index][sub_index][-1] == 't':
                            chart_grid[y[column_index] + sub_index][
                                x[column_index] : x[column_index] + 16
                            ] = self.insert_planet_into_line(
                                return_chart, planet, 't', width=16
                            )
                        else:
                            chart_grid[y[column_index] + sub_index][
                                x[column_index] : x[column_index] + 16
                            ] = self.insert_planet_into_line(
                                radix, planet, 'r', width=16
                            )
        for row in chart_grid:
            chartfile.write(' ')
            for col in row:
                chartfile.write(col)
            chartfile.write('\n')

        if extras:
            chartfile.write('\n\n' + '-' * 81 + '\n')
            s = 's' if len(extras) > 1 else ''
            chartfile.write(
                center_align(f'Planet{s} not shown above, details below:', 81)
                + '\n'
            )
            ex = ''
            for planet_name in len(extras):
                if planet_name[-1] == 't':
                    ex += (
                        self.insert_planet_into_line(
                            return_chart, planet_name[0], 't', True, width=16
                        )
                        + ' '
                    )
                else:
                    ex += (
                        self.insert_planet_into_line(
                            radix, planet_name[0], 'r', True, width=16
                        )
                        + ' '
                    )
            chartfile.write(center_align(ex[0:-1], 81) + '\n')
