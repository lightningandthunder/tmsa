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


class Biwheel(CoreChart):
    table_width = 81

    def __init__(
        self,
        charts: list[chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        super().__init__(charts, temporary, options)
        self.core_chart = charts[0]
        for chart in charts:
            if chart.type == chart_models.ChartWheelRole.RADIX:
                self.core_chart = chart
                break

        self.outer_chart = charts[1]
        for chart in charts:
            if chart.type == chart_models.ChartWheelRole.TRANSIT:
                self.outer_chart = chart
                break

        filename = chart_utils.make_chart_path(self.outer_chart, temporary)
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
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

        chart = self.charts[0]

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
        cusps = [chart_utils.zod_min(c) for c in chart.cusps]
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

    def write_info_table(
        self,
        chartfile: TextIOWrapper,
    ):
        chart = self.charts[0]

        chartfile.write(
            'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
        )
        angularity_options = self.options.angularity
        planets_foreground = []
        planet_foreground_angles = {}

        # Default to true if this is an ingress chart
        whole_chart_is_dormant = (
            True if chart.type in chart_utils.INGRESSES else False
        )

        for planet_name, _ in chart_utils.iterate_allowed_planets(
            self.options
        ):
            planet_data = chart.planets[planet_name]

            chartfile.write(chart_utils.left_align(planet_data.short_name, 3))

            # Write planet data to info table
            chartfile.write(chart_utils.zod_sec(planet_data.longitude) + ' ')
            chartfile.write(
                chart_utils.fmt_lat(planet_data.latitude, True) + ' '
            )
            if abs(planet_data.speed) >= 1:
                chartfile.write(chart_utils.s_dm(planet_data.speed) + ' ')
            else:
                chartfile.write(chart_utils.s_ms(planet_data.speed) + ' ')
            chartfile.write(
                chart_utils.right_align(
                    chart_utils.fmt_dm(planet_data.right_ascension, True), 7
                )
                + ' '
            )
            chartfile.write(
                chart_utils.fmt_lat(planet_data.declination, True) + ' '
            )

            # Azimuth
            chartfile.write(
                chart_utils.right_align(
                    chart_utils.fmt_dm(planet_data.azimuth, True), 7
                )
                + ' '
            )

            # Altitude
            chartfile.write(
                chart_utils.right_align(
                    chart_utils.s_dm(planet_data.altitude), 7
                )
                + ' '
            )

            # Meridian Longitude
            chartfile.write(
                chart_utils.fmt_dm(
                    planet_data.meridian_longitude, degree_digits=3, noz=True
                )
                + ' '
            )

            # House position
            chartfile.write(
                chart_utils.right_align(
                    chart_utils.fmt_dm(planet_data.house, True), 7
                )
                + ' '
            )

            # Angularity
            (
                angularity,
                strength_percent,
                planet_negates_dormancy,
                is_mundanely_background,
            ) = self.calc_angle_and_strength(
                planet_data,
                chart,
            )

            if planet_negates_dormancy:
                whole_chart_is_dormant = False

            planet_foreground_angles[planet_data.short_name] = angularity

            if (
                not angularity == angles_models.NonForegroundAngles.BLANK
                and not angularity
                == angles_models.NonForegroundAngles.BACKGROUND
            ):
                planets_foreground.append(planet_name)

            # Special case for Moon - always treat it as foreground
            elif planet_name == 'Moon' and (
                chart.type in chart_utils.INGRESSES
                or chart.type in chart_utils.SOLUNAR_RETURNS
            ):
                planet_data.treat_as_foreground = True

            if is_mundanely_background:
                planet_foreground_angles[
                    planet_data.short_name
                ] = angles_models.NonForegroundAngles.BACKGROUND

            # Conjunctions to Vertex/Antivertex
            minor_limit = angularity_options.minor_angles or [1.0, 2.0, 3.0]

            if (
                angularity == angles_models.NonForegroundAngles.BLANK
                or is_mundanely_background
            ):
                if chart_utils.inrange(
                    planet_data.azimuth, 270, minor_limit[2]
                ):
                    angularity = angles_models.NonForegroundAngles.VERTEX
                elif chart_utils.inrange(
                    planet_data.azimuth, 90, minor_limit[2]
                ):
                    angularity = angles_models.NonForegroundAngles.ANTIVERTEX

            chartfile.write(f'{strength_percent:3d}% {angularity}')
            chartfile.write('\n')

        if whole_chart_is_dormant:
            chartfile.write('-' * self.table_width + '\n')
            chartfile.write(
                chart_utils.center_align('Dormant Ingress', self.table_width)
                + '\n'
            )

        # Aspects
        ecliptical_orbs = (
            self.options.ecliptic_aspects
            or chart_utils.DEFAULT_ECLIPTICAL_ORBS
        )

        mundane_orbs = (
            self.options.mundane_aspects or chart_utils.DEFAULT_MUNDANE_ORBS
        )

        aspects_by_class = [[], [], [], []]
        aspect_class_headers = [
            'Class 1',
            'Class 2',
            'Class 3',
            'Other Partile',
        ]

        for (
            primary_index,
            (primary_planet_long_name, _),
        ) in enumerate(chart_utils.iterate_allowed_planets(self.options)):
            for (
                secondary_index,
                (secondary_planet_long_name, _),
            ) in enumerate(chart_utils.iterate_allowed_planets(self.options)):
                if secondary_index <= primary_index:
                    continue

                # If options say to skip one or both planets' aspects outside the foreground,
                # just skip calculating anything
                show_aspects = (
                    self.options.show_aspects or option_models.ShowAspect.ALL
                )

                if (
                    show_aspects
                    == option_models.ShowAspect.ONE_PLUS_FOREGROUND
                ):
                    if (
                        primary_planet_long_name not in planets_foreground
                        and secondary_planet_long_name
                        not in planets_foreground
                    ):
                        if not self.options.partile_nf:
                            continue

                if show_aspects == option_models.ShowAspect.BOTH_FOREGROUND:
                    if (
                        primary_planet_long_name not in planets_foreground
                        or secondary_planet_long_name not in planets_foreground
                    ):
                        if not self.options.partile_nf:
                            continue

                primary_planet_data = chart.planets[primary_planet_long_name]
                secondary_planet_data = chart.planets[
                    secondary_planet_long_name
                ]

                ecliptical_aspect = super().find_ecliptical_aspect(
                    primary_planet_data,
                    None,
                    secondary_planet_data,
                    None,
                    planets_foreground,
                    whole_chart_is_dormant,
                )
                mundane_aspect = super().find_mundane_aspect(
                    primary_planet_data,
                    None,
                    secondary_planet_data,
                    None,
                    planets_foreground,
                    whole_chart_is_dormant,
                )

                # TODO - the code below forces roles, when there doesn't need to be any.
                pvp_aspect = None
                # TODO - this is a temporary change to allow PVP aspects to be shown
                if self.options.allow_pvp_aspects or False:
                    pvp_aspect = super().find_pvp_aspect(
                        primary_planet_data,
                        self.core_chart.role,
                        secondary_planet_data,
                        self.core_chart.role,
                    )

                # This will get overwritten if there are any other aspects,
                # i.e. if there are any other aspects, the PVP aspect will not be used
                tightest_aspect = pvp_aspect

                if ecliptical_aspect or mundane_aspect:
                    tightest_aspect = min(
                        ecliptical_aspect,
                        mundane_aspect,
                        key=lambda x: x.orb if x else 1000,
                    )

                if tightest_aspect:
                    aspects_by_class[tightest_aspect.aspect_class - 1].append(
                        tightest_aspect
                    )

        # Remove empty aspect classes
        if len(aspects_by_class[3]) == 0 or whole_chart_is_dormant:
            del aspects_by_class[3]
            del aspect_class_headers[3]
            aspects_by_class.append([])
            aspect_class_headers.append('')
        for class_index in range(2, -1, -1):
            if len(aspects_by_class[class_index]) == 0:
                del aspects_by_class[class_index]
                del aspect_class_headers[class_index]
                aspects_by_class.append([])
                aspect_class_headers.append('')

        if any(aspect_class_headers):
            chartfile.write('-' * self.table_width + '\n')
            for class_index in range(0, 3):
                chartfile.write(
                    chart_utils.center_align(
                        f'{aspect_class_headers[class_index]} Aspects'
                        if aspect_class_headers[class_index]
                        else '',
                        24,
                    )
                )
            chartfile.write('\n')

        # Write aspects from all classes to file
        for aspect_index in range(
            max(
                len(aspects_by_class[0]),
                len(aspects_by_class[1]),
                len(aspects_by_class[2]),
            )
        ):
            if aspect_index < len(aspects_by_class[0]):
                chartfile.write(
                    chart_utils.left_align(
                        str(aspects_by_class[0][aspect_index]), width=24
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class[1]):
                chartfile.write(
                    chart_utils.center_align(
                        str(aspects_by_class[1][aspect_index]), width=24
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class[2]):
                chartfile.write(
                    chart_utils.right_align(
                        str(aspects_by_class[2][aspect_index]), width=24
                    )
                )
            else:
                chartfile.write(' ' * 24)
            chartfile.write('\n')

        chartfile.write('-' * self.table_width + '\n')
        if aspects_by_class[3]:
            chartfile.write(
                chart_utils.center_align(
                    f'{aspect_class_headers[3]} Aspects',
                    width=self.table_width,
                )
                + '\n'
            )
            for aspect in aspects_by_class[3]:
                chartfile.write(
                    chart_utils.center_align(str(aspect), self.table_width)
                    + '\n'
                )
            chartfile.write('-' * self.table_width + '\n')

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
            chart_utils.iterate_allowed_planets(self.options)
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
