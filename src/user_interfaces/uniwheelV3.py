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

    def write_cosmic_state(
        self,
        chartfile: TextIOWrapper,
        planet_foreground_angles: dict[str, str],
        aspects_by_class: list[list[str]],
        planets_foreground: list[str],
    ):
        chart = self.charts[0]
        chartfile.write(
            chart_utils.center_align('Cosmic State', self.table_width) + '\n'
        )
        moon_sign = constants.SIGNS_SHORT[
            int(chart.planets['Moon'].longitude // 30)
        ]
        sun_sign = constants.SIGNS_SHORT[
            int(chart.planets['Sun'].longitude // 30)
        ]

        for index, (planet_name, planet_info) in enumerate(
            chart_utils.iterate_allowed_planets()
        ):
            planet_short_name = planet_info['short_name']
            planet_data = chart.planets[planet_name]

            if index != 0:
                chartfile.write('\n')

            chartfile.write(planet_short_name + ' ')

            sign = constants.SIGNS_SHORT[int(planet_data.longitude // 30)]

            if sign in constants.POS_SIGN[planet_short_name]:
                plus_minus = '+'
            elif sign in constants.NEG_SIGN[planet_short_name]:
                plus_minus = '-'
            else:
                plus_minus = ' '
            chartfile.write(f'{sign}{plus_minus} ')

            # TODO - I think this is right but I'm not positive
            angle = planet_foreground_angles.get(
                planet_short_name, angles_models.NonForegroundAngles.BLANK
            )
            if angle.strip() == '':
                angle = ' '
            elif angle.strip() in [
                a.value.strip().upper() for a in angles_models.ForegroundAngles
            ]:
                angle = 'F'
            else:
                angle = 'B'
            chartfile.write(angle + ' |')

            need_another_row = False

            if self.chart.type not in chart_utils.INGRESSES:
                if planet_short_name != 'Mo':
                    if moon_sign in constants.POS_SIGN[planet_short_name]:
                        chartfile.write(f' Mo {moon_sign}+')
                        need_another_row = True
                    elif moon_sign in constants.NEG_SIGN[planet_short_name]:
                        chartfile.write(f' Mo {moon_sign}-')
                        need_another_row = True
                if planet_short_name != 'Su':
                    if sun_sign in constants.POS_SIGN[planet_short_name]:
                        chartfile.write(f' Su {sun_sign}+')
                        need_another_row = True
                    elif sun_sign in constants.NEG_SIGN[planet_short_name]:
                        chartfile.write(f' Su {sun_sign}-')
                        need_another_row = True

            aspect_list = []

            for class_index in range(3):
                for entry in aspects_by_class[class_index]:
                    if planet_short_name in entry:
                        percent = str(200 - int(entry[15:18]))
                        entry = entry[0:15] + entry[20:]
                        if entry[0:2] == planet_short_name:
                            entry = entry[3:]
                        else:
                            entry = f'{entry[3:5]} {entry[0:2]}{entry[8:]}'
                        aspect_list.append([entry, percent])

            aspect_list.sort(key=lambda p: p[1] + p[0][6:11])
            if aspect_list:
                if need_another_row:
                    chartfile.write('\n' + (' ' * 9) + '| ')
                    need_another_row = False
                else:
                    chartfile.write(' ')

            for aspect_index, aspect in enumerate(aspect_list):
                chartfile.write(aspect[0] + '   ')
                if (
                    aspect_index % 4 == 3
                    and aspect_index != len(aspect_list) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '| ')

            points_to_show_midpoint_aspects_to = []
            for index, (planet_name, planet_info) in enumerate(
                chart_utils.iterate_allowed_planets(self.options)
            ):
                planet_longitude = chart.planets[planet_name].longitude
                planet_short_name = planet_info['short_name']
                if (
                    (self.options.show_aspects or option_models.ShowAspect.ALL)
                    == option_models.ShowAspect.ALL
                    or planet_short_name in planets_foreground
                ):
                    points_to_show_midpoint_aspects_to.append(
                        [planet_short_name, planet_longitude]
                    )

            points_to_show_midpoint_aspects_to.append(['As', chart.cusps[1]])
            points_to_show_midpoint_aspects_to.append(['Mc', chart.cusps[10]])
            if len(points_to_show_midpoint_aspects_to) > 1 and (
                (self.options.show_aspects or option_models.ShowAspect.ALL)
                == option_models.ShowAspect.ALL
                or planet_name in planets_foreground
            ):
                # ecliptic midpoints?
                emp = []
                for remaining_planet in range(
                    len(points_to_show_midpoint_aspects_to) - 1
                ):
                    for k in range(
                        remaining_planet + 1,
                        len(points_to_show_midpoint_aspects_to),
                    ):
                        mp = self.find_midpoint(
                            [planet_short_name, planet_data.longitude],
                            points_to_show_midpoint_aspects_to,
                            remaining_planet,
                            k,
                            self.options,
                        )
                        if mp:
                            emp.append(mp)
                if emp:
                    emp.sort(key=lambda p: p[6:8])
                    if need_another_row or aspect_list:
                        chartfile.write('\n' + (' ' * 9) + '| ')
                    else:
                        chartfile.write(' ')
                    for remaining_planet, a in enumerate(emp):
                        chartfile.write('   ' + a + '   ')
                        if (
                            remaining_planet % 4 == 3
                            and remaining_planet != len(emp) - 1
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')

        sign = constants.SIGNS_SHORT[int(chart.cusps[1] // 30)]
        points_to_show_midpoint_aspects_to = []
        for planet_index in range(14):
            if planet_index == 10 and not self.options.get('use_Eris', 1):
                continue
            if planet_index == 11 and not self.options.get('use_Sedna', 0):
                continue
            if planet_index == 12 and self.options.get('Node', 0) != 1:
                continue
            if planet_index == 13 and self.options.get('Node', 0) != 2:
                continue
            plna = constants.PLANET_NAMES[planet_index]
            planet_longitude = chart[plna][0]
            plra = chart[plna].right_ascension
            plpvl = chart[plna].house
            planet_short_name = constants.PLANET_NAMES_SHORT[planet_index]
            if (
                self.options.get('show_aspects', 0) == 0
                or plna in planets_foreground
            ):
                points_to_show_midpoint_aspects_to.append(
                    [planet_short_name, planet_longitude, plra, plpvl]
                )
        points_to_show_midpoint_aspects_to.append(['Mc', chart.cusps[10]])
        if len(points_to_show_midpoint_aspects_to) > 1:
            emp = []
            for remaining_planet in range(
                len(points_to_show_midpoint_aspects_to) - 1
            ):
                for k in range(
                    remaining_planet + 1,
                    len(points_to_show_midpoint_aspects_to),
                ):
                    mp = self.find_midpoint(
                        ['As', chart.cusps[1]],
                        points_to_show_midpoint_aspects_to,
                        remaining_planet,
                        k,
                        self.options,
                    )
                    if mp:
                        emp.append(mp)
            if emp:
                emp.sort(key=lambda p: p[6:8])
                chartfile.write(f'\nAs {sign}    | ')
                for remaining_planet, a in enumerate(emp):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(emp) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')
        sign = constants.SIGNS_SHORT[int(chart.cusps[10] // 30)]
        points_to_show_midpoint_aspects_to[-1] = ['As', chart.cusps[1]]
        if len(points_to_show_midpoint_aspects_to) > 1:
            emp = []
            for remaining_planet in range(
                len(points_to_show_midpoint_aspects_to) - 1
            ):
                for k in range(
                    remaining_planet + 1,
                    len(points_to_show_midpoint_aspects_to),
                ):
                    mp = self.find_midpoint(
                        ['Mc', chart.cusps[10]],
                        points_to_show_midpoint_aspects_to,
                        remaining_planet,
                        k,
                        self.options,
                    )
                    if mp:
                        emp.append(mp)
            if emp:
                emp.sort(key=lambda p: p[6:8])
                chartfile.write(f'\nMc {sign}    | ')
                for remaining_planet, a in enumerate(emp):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(emp) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')
        del points_to_show_midpoint_aspects_to[-1]
        if len(points_to_show_midpoint_aspects_to) > 1:
            emp = []
            ep = [
                'Ep',
                (chart.cusps[10] + 90) % 360,
                (chart.ramc + 90) % 360,
            ]
            ze = ['Ze', (chart.cusps[1] - 90) % 360]
            for remaining_planet in range(
                len(points_to_show_midpoint_aspects_to) - 1
            ):
                for k in range(
                    remaining_planet + 1,
                    len(points_to_show_midpoint_aspects_to),
                ):
                    mp = self.mmp_all(
                        ep,
                        ze,
                        points_to_show_midpoint_aspects_to,
                        remaining_planet,
                        k,
                        self.options,
                    )
                    if mp:
                        emp.append(mp)
            if emp:
                empa = []
                empe = []
                empz = []
                for x in emp:
                    if x[-1] == 'A':
                        empa.append(x[:-1])
                    elif x[-1] == 'E':
                        empe.append(x[:-1])
                    else:
                        empz.append(x[:-1])
                empa.sort(key=lambda p: p[6:8])
                empe.sort(key=lambda p: p[6:8])
                empz.sort(key=lambda p: p[6:8])
                if empa:
                    chartfile.write(f'\nAngle    | ')
                    for remaining_planet, a in enumerate(empa):
                        chartfile.write('   ' + a + '   ')
                        if (
                            remaining_planet % 4 == 3
                            and remaining_planet != len(empa) - 1
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')
                if empe:
                    chartfile.write(f'\nEp       | ')
                    for remaining_planet, a in enumerate(empe):
                        chartfile.write('   ' + a + '   ')
                        if (
                            remaining_planet % 4 == 3
                            and remaining_planet != len(empe) - 1
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')
                if empz:
                    chartfile.write(f'\nZe       | ')
                    for remaining_planet, a in enumerate(empz):
                        chartfile.write('   ' + a + '   ')
                        if (
                            remaining_planet % 4 == 3
                            and remaining_planet != len(empz) - 1
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')
