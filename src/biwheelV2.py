# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.


import math
from copy import deepcopy
from datetime import datetime

from chart_utils import *
from utils import open_file


def write_to_file(chart, planet, prefix, pa_only=False):
    pd = chart[planet]
    index = PLANET_NAMES.index(planet)
    pa = PLANET_NAMES_SHORT[index]
    if pa_only:
        return prefix + pa
    d = prefix + pa + ' ' + zod_min(pd[0])
    if index < 14:
        d += ' ' + fmt_dm(pd[-1] % 30)
        d = d[0:-1]
    else:
        d = center_align(d, 16)
    return d


class BiwheelV2:
    def __init__(self, chart, temporary, options):
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]
        filename = make_chart_path(chart, temporary)
        filename = filename[0:-3] + 'txt'
        try:
            chartfile = open(filename, 'w')
        except Exception as e:
            tkmessagebox.showerror(f'Unable to open file:', f'{e}')
            return
        with chartfile:
            self.cclass = chart.get('class', None)
            if not self.cclass:
                self.cclass = get_return_class(chart['type'])
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
            cusps = [zod_min(c) for c in chart['cusps']]
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
            if (
                'solar' not in chart['type'].lower()
                and 'lunar' not in chart['type'].lower()
            ):
                chart_grid[20][18:51] = center_align(chart['name'])
            elif 'return' in chart['type'].lower():
                parts = chart['name'].split(';')
                chart_grid[20][18:51] = center_align(parts[0])
            chart_grid[21][18:51] = center_align(chart['type'])
            line = (
                str(chart['day']) + ' ' + month_abrev[chart['month'] - 1] + ' '
            )
            line += (
                f"{chart['year']} "
                if chart['year'] > 0
                else f"{-chart['year'] + 1} BCE "
            )
            if not chart['style']:
                line += 'OS '
            line += fmt_hms(chart['time']) + ' ' + chart['zone']
            chart_grid[22][18:51] = center_align(line)
            chart_grid[23][18:51] = center_align(chart['location'])
            chart_grid[24][18:51] = center_align(
                fmt_lat(chart['latitude']) + ' ' + fmt_long(chart['longitude'])
            )
            chart_grid[25][18:51] = center_align(
                'UT ' + fmt_hms(chart['time'] + chart['correction'])
            )
            chart_grid[26][18:51] = center_align(
                'RAMC ' + fmt_dms(chart['ramc'])
            )
            chart_grid[27][18:51] = center_align('OE ' + fmt_dms(chart['oe']))
            chart_grid[28][18:51] = center_align(
                'SVP ' + zod_sec(360 - chart['ayan'])
            )
            chart_grid[29][18:51] = center_align('Sidereal Zodiac')
            chart_grid[30][18:51] = center_align('Campanus Houses')
            chart_grid[31][18:51] = center_align(chart['notes'] or '')
            radix = chart['base_chart']
            chart_grid[33][18:51] = center_align('Radical (r) Chart')
            if chart['type'] not in INGRESSES:
                if (
                    'solar' not in radix['type'].lower()
                    and 'lunar' not in radix['type'].lower()
                ):
                    chart_grid[34][18:51] = center_align(radix['name'])
                elif 'return' in radix['type'].lower():
                    parts = radix['name'].split(';')
                    chart_grid[34][18:51] = center_align(parts[0])
            chtype = radix['type']
            if chtype.endswith(' Single Wheel'):
                chtype = chtype.replace(' Single Wheel', '')
            chart_grid[35][18:51] = center_align(chtype)
            line = (
                str(radix['day']) + ' ' + month_abrev[radix['month'] - 1] + ' '
            )
            line += (
                f"{radix['year']} "
                if radix['year'] > 0
                else f"{-radix['year'] + 1} BCE "
            )
            if not radix['style']:
                line += 'OS '
            line += fmt_hms(radix['time']) + ' ' + radix['zone']
            chart_grid[36][18:51] = center_align(line)
            chart_grid[37][18:51] = center_align(radix['location'])
            chart_grid[38][18:51] = center_align(
                fmt_lat(radix['latitude']) + ' ' + fmt_long(radix['longitude'])
            )
            chart_grid[39][18:51] = center_align(
                'UT ' + fmt_hms(radix['time'] + radix['correction'])
            )
            chart_grid[40][18:51] = center_align(
                'RAMC ' + fmt_dms(radix['ramc'])
            )
            chart_grid[41][18:51] = center_align('OE ' + fmt_dms(radix['oe']))
            chart_grid[42][18:51] = center_align(
                'SVP ' + zod_sec(360 - radix['ayan'])
            )
            chart_grid[43][18:51] = center_align('Sidereal Zodiac')
            chart_grid[44][18:51] = center_align('Campanus Houses')
            chart_grid[45][18:51] = center_align(radix['notes'] or '')

            x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
            y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
            houses = [[] for i in range(12)]
            extras = []
            for column_index in range(12):
                houses[column_index] = self.sort_house(
                    chart, column_index, options
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
                                ] = write_to_file(chart, planet, 't')
                            else:
                                chart_grid[y[column_index] + sub_index][
                                    x[column_index] : x[column_index] + 16
                                ] = write_to_file(
                                    chart['base_chart'], planet, 'r'
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
                    center_align(
                        f'Planet{s} not shown above, details below:', 81
                    )
                    + '\n'
                )
                ex = ''
                for planet_name in len(extras):
                    if planet_name[-1] == 't':
                        ex += (
                            write_to_file(chart, planet_name[0], 't', True)
                            + ' '
                        )
                    else:
                        ex += (
                            write_to_file(
                                chart['base_chart'], planet_name[0], 'r', True
                            )
                            + ' '
                        )
                chartfile.write(center_align(ex[0:-1], 81) + '\n')

            chartfile.write('\n\n' + '-' * 81 + '\n')
            chartfile.write(
                'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
            )
            chartfile.write(center_align('Transiting Planets', 81) + '\n')
            angularity_options = options.get('angularity', {})
            major_limit = angularity_options.get(
                'major_angles', [3.0, 7.0, 10.0]
            )
            minor_limit = angularity_options.get(
                'minor_angles', [1.0, 2.0, 3.0]
            )

            planets_foreground = []
            planet_foreground_angles = {}

            for column_index in range(3):
                if major_limit[column_index] == 0:
                    major_limit[column_index] = -3
                if minor_limit[column_index] == 0:
                    minor_limit[column_index] = -3
            for planet_name in PLANET_NAMES:
                if planet_name == 'Eastpoint':
                    break
                if planet_name == 'Eris' and not options.get('use_Eris', 1):
                    continue
                if planet_name == 'Sedna' and not options.get('use_Sedna', 0):
                    continue
                if planet_name == 'True Node' and options.get('Node', 0) != 1:
                    continue
                if planet_name == 'Mean Node' and options.get('Node', 0) != 2:
                    continue
                planet_data = chart[planet_name]
                planet_index = PLANET_NAMES.index(planet_name)
                chartfile.write(
                    left_align(PLANET_NAMES_SHORT[planet_index], 3)
                )
                chartfile.write(zod_sec(planet_data[0]) + ' ')
                chartfile.write(fmt_lat(planet_data[1], True) + ' ')
                if abs(planet_data[2]) >= 1:
                    chartfile.write(s_dm(planet_data[2]) + ' ')
                else:
                    chartfile.write(s_ms(planet_data[2]) + ' ')
                chartfile.write(
                    right_align(fmt_dm(planet_data[3], True), 7) + ' '
                )
                chartfile.write(fmt_lat(planet_data[4], True) + ' ')

                # Azimuth
                chartfile.write(
                    right_align(fmt_dm(planet_data[5], True), 7) + ' '
                )

                # Altitude
                chartfile.write(s_dm(planet_data[6]) + ' ')

                # Meridian Longitude
                chartfile.write(
                    fmt_dm(planet_data[7], degree_digits=3, noz=True) + ' '
                )

                # House position
                chartfile.write(
                    right_align(fmt_dm(planet_data[8], True), 7) + ' '
                )

                # Angularity
                (
                    angularity,
                    strength_percent,
                    _,
                    is_mundanely_background,
                ) = self.calc_angle_and_strength(
                    planet_data,
                    chart,
                    angularity_options,
                )

                planet_foreground_angles[
                    't' + PLANET_NAMES_SHORT[planet_index]
                ] = angularity

                angularity_is_empty = angularity.strip() == ''
                angularity_is_background = angularity.strip().lower() == 'b'

                if (
                    not angularity_is_empty and not angularity_is_background
                ) or (planet_name == 'Moon' and 'I' in self.cclass):
                    planets_foreground.append('t' + planet_name)

                if angularity_is_background or is_mundanely_background:
                    planet_foreground_angles[
                        't' + PLANET_NAMES_SHORT[planet_index]
                    ] = 'B'

                # Conjunctions to Vertex/Antivertex
                minor_limit = angularity_options.get(
                    'minor_angles', [1.0, 2.0, 3.0]
                )

                if angularity_is_empty or is_mundanely_background:
                    if inrange(planet_data[5], 270, minor_limit[2]):
                        angularity = 'Vx'
                    elif inrange(planet_data[5], 90, minor_limit[2]):
                        angularity = 'Av'

                chartfile.write(f'{strength_percent:3d}% {angularity}')
                chartfile.write('\n')

            chartfile.write('-' * 81 + '\n')
            chartfile.write(center_align('Radical Planets', 81) + '\n')
            for planet_name in PLANET_NAMES:
                if planet_name == 'Eastpoint':
                    break
                if planet_name == 'Eris' and not options.get('use_Eris', 1):
                    continue
                if planet_name == 'Sedna' and not options.get('use_Sedna', 0):
                    continue
                if planet_name == 'True Node' and options.get('Node', 0) != 1:
                    continue
                if planet_name == 'Mean Node' and options.get('Node', 0) != 2:
                    continue
                planet_data = chart['base_chart'][planet_name]
                planet_index = PLANET_NAMES.index(planet_name)
                chartfile.write(
                    left_align(PLANET_NAMES_SHORT[planet_index], 3)
                )
                chartfile.write(zod_sec(planet_data[0]) + ' ')
                chartfile.write(fmt_lat(planet_data[1], True) + ' ')
                if abs(planet_data[2]) >= 1:
                    chartfile.write(s_dm(planet_data[2]) + ' ')
                else:
                    chartfile.write(s_ms(planet_data[2]) + ' ')
                chartfile.write(
                    right_align(fmt_dm(planet_data[3], True), 7) + ' '
                )
                chartfile.write(fmt_lat(planet_data[4], True) + ' ')
                chartfile.write(
                    right_align(fmt_dm(planet_data[5], True), 7) + ' '
                )
                chartfile.write(s_dm(planet_data[6]) + ' ')

                # Meridian Longitude
                chartfile.write(
                    fmt_dm(planet_data[7], degree_digits=3, noz=True) + ' '
                )

                # House position
                chartfile.write(
                    right_align(fmt_dm(planet_data[8], True), 7) + ' '
                )

                # Angularity
                (
                    angularity,
                    strength_percent,
                    _,
                    is_mundanely_background,
                ) = self.calc_angle_and_strength(
                    planet_data,
                    chart,
                    angularity_options,
                )

                planet_foreground_angles[
                    'r' + PLANET_NAMES_SHORT[planet_index]
                ] = angularity

                angularity_is_empty = angularity.strip() == ''
                angularity_is_background = angularity.strip().lower() == 'b'

                if (
                    not angularity_is_empty and not angularity_is_background
                ) or (planet_name == 'Moon' and 'I' in self.cclass):
                    planets_foreground.append('r' + planet_name)

                if angularity_is_empty and is_mundanely_background:
                    planet_foreground_angles[
                        'r' + PLANET_NAMES_SHORT[planet_index]
                    ] = 'B'

                # Conjunctions to Vertex/Antivertex
                minor_limit = angularity_options.get(
                    'minor_angles', [1.0, 2.0, 3.0]
                )

                if angularity_is_empty or is_mundanely_background:
                    if inrange(planet_data[5], 270, minor_limit[2]):
                        angularity = 'Vx'
                    elif inrange(planet_data[5], 90, minor_limit[2]):
                        angularity = 'Av'

                chartfile.write(f'{strength_percent:3d}% {angularity}')
                chartfile.write('\n')

            chartfile.write('-' * 81 + '\n')
            ecliptic_aspects = options.get(
                'ecliptic_aspects', DEFAULT_ECLIPTICAL_ORBS
            )
            mundane_aspects = options.get(
                'mundane_aspects', DEFAULT_MUNDANE_ORBS
            )
            aspect_classes = [[], [], [], []]
            aspect_headers = ['Class 1', 'Class 2', 'Class 3', 'Other Partile']

            # Transit to transit
            for column_index in range(13):
                for sub_index in range(column_index + 1, 14):
                    (
                        ecliptic_aspect,
                        ecliptic_class,
                        ecliptic_orb,
                    ) = self.find_easpect(
                        chart,
                        column_index,
                        sub_index,
                        ecliptic_aspects,
                        options,
                        planets_foreground,
                        0,
                    )
                    (
                        mundane_aspect,
                        mundane_class,
                        mundane_orb,
                    ) = self.find_maspect(
                        chart,
                        column_index,
                        sub_index,
                        mundane_aspects,
                        options,
                        planets_foreground,
                        0,
                    )

                    if ecliptic_aspect and mundane_aspect:
                        if mundane_orb < ecliptic_orb:
                            ecliptic_aspect = ''
                        else:
                            mundane_aspect = ''
                    if ecliptic_aspect:
                        aspect_classes[ecliptic_class - 1].append(
                            ecliptic_aspect
                        )
                    if mundane_aspect:
                        aspect_classes[mundane_class - 1].append(
                            mundane_aspect
                        )

            # Transits to natal
            for column_index in range(14):
                for sub_index in range(14):
                    # Skip showing solunar return aspects to itself
                    if (
                        column_index == 0
                        and sub_index == 0
                        and self.cclass == 'LR'
                    ):
                        continue
                    if (
                        column_index == 1
                        and sub_index == 1
                        and self.cclass == 'SR'
                    ):
                        continue

                    (
                        ecliptic_aspect,
                        ecliptic_class,
                        ecliptic_orb,
                    ) = self.find_easpect(
                        chart,
                        column_index,
                        sub_index,
                        ecliptic_aspects,
                        options,
                        planets_foreground,
                        1,
                    )
                    (
                        mundane_aspect,
                        mundane_class,
                        mundane_orb,
                    ) = self.find_maspect(
                        chart,
                        column_index,
                        sub_index,
                        mundane_aspects,
                        options,
                        planets_foreground,
                        1,
                    )

                    if ecliptic_aspect and mundane_aspect:
                        if mundane_orb < ecliptic_orb:
                            ecliptic_aspect = ''
                        else:
                            mundane_aspect = ''
                    if ecliptic_aspect:
                        aspect_classes[ecliptic_class - 1].append(
                            ecliptic_aspect
                        )
                    if mundane_aspect:
                        aspect_classes[mundane_class - 1].append(
                            mundane_aspect
                        )

            # Natal to natal
            for column_index in range(13):
                for sub_index in range(column_index + 1, 14):
                    (
                        ecliptic_aspect,
                        ecliptic_class,
                        ecliptic_orb,
                    ) = self.find_easpect(
                        chart,
                        column_index,
                        sub_index,
                        ecliptic_aspects,
                        options,
                        planets_foreground,
                        2,
                    )
                    (
                        mundane_aspect,
                        mundane_class,
                        mundane_orb,
                    ) = self.find_maspect(
                        chart,
                        column_index,
                        sub_index,
                        mundane_aspects,
                        options,
                        planets_foreground,
                        2,
                    )

                    if ecliptic_aspect and mundane_aspect:
                        if mundane_orb < ecliptic_orb:
                            ecliptic_aspect = ''
                        else:
                            mundane_aspect = ''
                    if ecliptic_aspect:
                        aspect_classes[ecliptic_class - 1].append(
                            ecliptic_aspect
                        )
                    if mundane_aspect:
                        aspect_classes[mundane_class - 1].append(
                            mundane_aspect
                        )

            for aspect_class in range(4):
                inserts = []
                for aspect_index in range(len(aspect_classes[aspect_class])):
                    if aspect_index == 0:
                        save = (
                            aspect_classes[aspect_class][aspect_index][0]
                            + aspect_classes[aspect_class][aspect_index][7]
                        )
                    a = (
                        aspect_classes[aspect_class][aspect_index][0]
                        + aspect_classes[aspect_class][aspect_index][7]
                    )
                    if a != save:
                        inserts.append(aspect_index)
                        save = a
                for k in range(len(inserts) - 1, -1, -1):
                    aspect_classes[aspect_class].insert(inserts[k], '-' * 22)

            for column_index in range(2, -1, -1):
                if len(aspect_classes[column_index]) == 0:
                    del aspect_classes[column_index]
                    del aspect_headers[column_index]
                    aspect_classes.append([])
                    aspect_headers.append('')
            if any(aspect_headers):
                for column_index in range(0, 3):
                    chartfile.write(
                        center_align(
                            f'{aspect_headers[column_index]} Aspects'
                            if aspect_headers[column_index]
                            else '',
                            24,
                        )
                    )
                chartfile.write('\n')
            for column_index in range(
                max(
                    len(aspect_classes[0]),
                    len(aspect_classes[1]),
                    len(aspect_classes[2]),
                )
            ):
                if column_index < len(aspect_classes[0]):
                    chartfile.write(
                        left_align(aspect_classes[0][column_index], 24)
                    )
                else:
                    chartfile.write(' ' * 24)
                if column_index < len(aspect_classes[1]):
                    chartfile.write(
                        center_align(aspect_classes[1][column_index], 24)
                    )
                else:
                    chartfile.write(' ' * 24)
                if column_index < len(aspect_classes[2]):
                    chartfile.write(
                        right_align(aspect_classes[2][column_index], 24)
                    )
                else:
                    chartfile.write(' ' * 24)
                chartfile.write('\n')
            chartfile.write('-' * 81 + '\n')
            if aspect_classes[3]:
                chartfile.write(
                    center_align(f'{aspect_headers[3]} Aspects', 76) + '\n'
                )
                for a in aspect_classes[3]:
                    chartfile.write(center_align(a, 81) + '\n')
                chartfile.write('-' * 81 + '\n')
            chartfile.write(center_align('Cosmic State', 81) + '\n')
            chartfile.write(center_align('Transiting Planets', 81) + '\n')
            cclass = chart['class']
            for column_index in range(14):
                if column_index == 10 and not options.get('use_Eris', 1):
                    continue
                if column_index == 11 and not options.get('use_Sedna', 0):
                    continue
                if column_index == 12 and options.get('Node', 0) != 1:
                    continue
                if column_index == 13 and options.get('Node', 0) != 2:
                    continue
                pn = PLANET_NAMES[column_index]
                xpn = 't' + pn
                pa = PLANET_NAMES_SHORT[column_index]
                xpa = 't' + pa
                planet_data = chart[pn]
                if pa != 'Mo':
                    chartfile.write('\n')
                chartfile.write(pa + ' ')
                sign = SIGNS_SHORT[int(planet_data[0] // 30)]
                if sign in POS_SIGN[pa]:
                    x = '+'
                elif sign in NEG_SIGN[pa]:
                    x = '-'
                else:
                    x = ' '
                chartfile.write(f'{sign}{x} ')
                chartfile.write(planet_foreground_angles.get(pa, '') + ' |')
                asplist = []
                for sub_index in range(3):
                    for entry in aspect_classes[sub_index]:
                        if xpa in entry:
                            pct = str(200 - int(entry[17:20]))
                            entry = entry[0:17] + entry[22:]
                            if entry[0:3] == xpa:
                                entry = entry[4:]
                            else:
                                entry = (
                                    f'{entry[4:6]} {entry[0:3]}{entry[10:]}'
                                )
                            asplist.append([entry, pct])
                asplist.sort(key=lambda p: p[1] + p[0][8:13])
                if asplist:
                    chartfile.write(' ')
                for sub_index, a in enumerate(asplist):
                    chartfile.write(a[0] + '   ')
                    if sub_index % 4 == 3 and sub_index != len(asplist) - 1:
                        chartfile.write('\n' + (' ' * 8) + '| ')
            chartfile.write('\n' + '-' * 81 + '\n')
            chartfile.write(center_align('Radical Planets', 81) + '\n')
            cclass = chart['class']
            for column_index in range(14):
                if column_index == 10 and not options.get('use_Eris', 1):
                    continue
                if column_index == 11 and not options.get('use_Sedna', 0):
                    continue
                if column_index == 12 and options.get('Node', 0) != 1:
                    continue
                if column_index == 13 and options.get('Node', 0) != 2:
                    continue
                pn = PLANET_NAMES[column_index]
                xpn = 'r' + pn
                pa = PLANET_NAMES_SHORT[column_index]
                xpa = 'r' + pa
                planet_data = chart['base_chart'][pn]
                if pa != 'Mo':
                    chartfile.write('\n')
                chartfile.write(pa + ' ')
                sign = SIGNS_SHORT[int(planet_data[0] // 30)]
                if sign in POS_SIGN[pa]:
                    x = '+'
                elif sign in NEG_SIGN[pa]:
                    x = '-'
                else:
                    x = ' '
                chartfile.write(f'{sign}{x} ')
                chartfile.write(planet_foreground_angles.get(pa, '') + ' |')
                asplist = []
                for sub_index in range(3):
                    for entry in aspect_classes[sub_index]:
                        if xpa in entry:
                            pct = str(200 - int(entry[17:20]))
                            entry = entry[0:17] + entry[22:]
                            if entry[0:3] == xpa:
                                entry = entry[4:]
                            else:
                                entry = (
                                    f'{entry[4:6]} {entry[0:3]}{entry[10:]}'
                                )
                            asplist.append([entry, pct])
                asplist.sort(key=lambda p: p[1] + p[0][8:13])
                if asplist:
                    chartfile.write(' ')
                for sub_index, a in enumerate(asplist):
                    chartfile.write(a[0] + '   ')
                    if sub_index % 4 == 3 and sub_index != len(asplist) - 1:
                        chartfile.write('\n' + (' ' * 8) + '| ')
            self.filename = filename
            chartfile.write('\n' + '-' * 81 + '\n')
            chartfile.write(
                f"Created by Time Matters {VERSION} ({datetime.now().strftime('%d %b %Y')})"
            )
        return

    def sort_house(self, chart, h, options):
        house = []
        for pl in PLANET_NAMES:
            if pl == 'Eris' and not options.get('use_Eris', 1):
                continue
            if pl == 'Sedna' and not options.get('use_Sedna', 0):
                continue
            if pl == 'Vertex' and not options.get('use_Vertex', 0):
                continue
            if pl == 'True Node' and options.get('Node', 0) != 1:
                continue
            if pl == 'Mean Node' and options.get('Node', 0) != 2:
                continue
            pd = chart[pl]
            if pd[-1] // 30 == h:
                pos = (pd[-1] % 30) / 2
                house.append([pl, pd[-1], pos, 't'])
        for pl in PLANET_NAMES:
            if pl == 'Eris' and not options.get('use_Eris', 1):
                continue
            if pl == 'Sedna' and not options.get('use_Sedna', 0):
                continue
            if pl == 'Eastpoint':
                continue
            if pl == 'Vertex':
                continue
            if pl == 'True Node' and options.get('Node', 0) != 1:
                continue
            if pl == 'Mean Node' and options.get('Node', 0) != 2:
                continue
            pd = chart['base_chart'][pl]
            if pd[-1] // 30 == h:
                pos = (pd[-1] % 30) / 2
                house.append([pl, pd[-1], pos, 'r'])
        house.sort(key=lambda h: h[1])
        return self.spread(house)

    def spread(self, old, start=0):
        new = [[] for i in range(15)]
        placed = 0
        for i in range(len(old)):
            x = int(old[i][-2]) + start
            limit = 15 - len(old) + placed
            if x > limit:
                x = limit
            while True:
                if len(new[x]):
                    x += 1
                else:
                    break
            new[x] = old[i]
            placed += 1
        return new

    def find_easpect(self, chart, i, j, ea, options, plfg, atype):
        pn1 = PLANET_NAMES[i]
        pn2 = PLANET_NAMES[j]
        if self.cclass == 'SR' and pn1 == 'Sun' and pn2 == 'Sun':
            return ('', 0, 0)
        if self.cclass == 'LR' and pn1 == 'Moon' and pn2 == 'Moon':
            return ('', 0, 0)
        if (pn1 == 'Eris' or pn2 == 'Eris') and not options.get('use_Eris', 1):
            return ('', 0, 0)
        if (pn1 == 'Sedna' or pn2 == 'Sedna') and not options.get(
            'use_Sedna', 0
        ):
            return ('', 0, 0)
        if (pn1 == 'True Node' or pn2 == 'True Node') and options.get(
            'Node', 0
        ) != 1:
            return ('', 0, 0)
        if (pn1 == 'Mean Node' or pn2 == 'Mean Node') and options.get(
            'Node', 0
        ) != 2:
            return ('', 0, 0)
        if atype < 2:
            pd1 = chart[PLANET_NAMES[i]]
            pre1 = 't'
        else:
            pd1 = chart['base_chart'][PLANET_NAMES[i]]
            pre1 = 'r'
        if atype == 0:
            pd2 = chart[PLANET_NAMES[j]]
            pre2 = 't'
        else:
            pd2 = chart['base_chart'][PLANET_NAMES[j]]
            pre2 = 'r'
        pa1 = PLANET_NAMES_SHORT[i]
        pa2 = PLANET_NAMES_SHORT[j]
        astr = ['0', '180', '90', '45', '45', '120', '60', '30', '30']
        anum = [0, 180, 90, 45, 135, 120, 60, 30, 150]
        aname = ['co', 'op', 'sq', 'oc', 'oc', 'tr', 'sx', 'in', 'in']
        d = abs(pd1[0] - pd2[0]) % 360
        if d > 180:
            d = 360 - d
        for i in range(9):
            aspd = ea[astr[i]]
            if aspd[2]:
                maxorb = aspd[2]
            elif aspd[1]:
                maxorb = aspd[1] * 1.25
            elif aspd[0]:
                maxorb = aspd[0] * 2.5
            else:
                maxorb = -1
            if d >= anum[i] - maxorb and d <= anum[i] + maxorb:
                asp = aname[i]
                if maxorb <= 0:
                    return ('', 0, 0)
                m = 60 / maxorb
                d = abs(d - anum[i])
                if d <= aspd[0]:
                    acl = 1
                elif d <= aspd[1]:
                    acl = 2
                elif d <= aspd[2]:
                    acl = 3
                else:
                    return ('', 0, 0)
                if self.cclass == 'SR' and pre1 + pn1 == 'tMoon':
                    break
                if options.get('show_aspects', 0) == 1:
                    if pre1 + pn1 not in plfg and pre2 + pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if pre1 + pn1 not in plfg or pre2 + pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)
        p = math.cos(math.radians(d * m))
        p = round((p - 0.5) * 200)
        p = f'{p:3d}'
        return (
            f'{pre1}{pa1} {asp} {pre2}{pa2} {fmt_dm(abs(d), True)}{p}%  ',
            acl,
            d,
        )

    def find_maspect(self, chart, i, j, ma, options, plfg, atype):
        pn1 = PLANET_NAMES[i]
        pn2 = PLANET_NAMES[j]
        if self.cclass == 'SR' and pn1 == 'Sun' and pn2 == 'Sun':
            return ('', 0, 0)
        if self.cclass == 'LR' and pn1 == 'Moon' and pn2 == 'Moon':
            return ('', 0, 0)
        if (pn1 == 'Eris' or pn2 == 'Eris') and not options.get('use_Eris', 1):
            return ('', 0, 0)
        if (pn1 == 'Sedna' or pn2 == 'Sedna') and not options.get(
            'use_Sedna', 0
        ):
            return ('', 0, 0)
        if (pn1 == 'True Node' or pn2 == 'True Node') and options.get(
            'Node', 0
        ) != 1:
            return ('', 0, 0)
        if (pn1 == 'Mean Node' or pn2 == 'Mean Node') and options.get(
            'Node', 0
        ) != 2:
            return ('', 0, 0)
        if atype < 2:
            pd1 = chart[PLANET_NAMES[i]]
            pre1 = 't'
        else:
            pd1 = chart['base_chart'][PLANET_NAMES[i]]
            pre1 = 'r'
        if atype == 0:
            pd2 = chart[PLANET_NAMES[j]]
            pre2 = 't'
        else:
            pd2 = chart['base_chart'][PLANET_NAMES[j]]
            pre2 = 'r'
        pa1 = PLANET_NAMES_SHORT[i]
        pa2 = PLANET_NAMES_SHORT[j]
        d = abs(pd1[8] - pd2[8]) % 360
        if d > 180:
            d = 360 - d
        astr = ['0', '180', '90', '45', '45']
        anum = [0, 180, 90, 45, 135]
        aname = ['co', 'op', 'sq', 'oc', 'oc']
        for i in range(5):
            aspd = ma[astr[i]]
            if aspd[2]:
                maxorb = aspd[2]
            elif aspd[1]:
                maxorb = aspd[1] * 1.25
            elif aspd[0]:
                maxorb = aspd[0] * 2.5
            else:
                maxorb = -1
            if d >= anum[i] - maxorb and d <= anum[i] + maxorb:
                asp = aname[i]
                if maxorb <= 0:
                    return ('', 0, 0)
                m = 60 / maxorb
                d = abs(d - anum[i])
                if d <= aspd[0]:
                    acl = 1
                elif d <= aspd[1]:
                    acl = 2
                elif d <= aspd[2]:
                    acl = 3
                else:
                    return ('', 0, 0)
                if self.cclass == 'SR' and pre1 + pn1 == 'tMoon':
                    break
                if options.get('show_aspects', 0) == 1:
                    if pre1 + pn1 not in plfg and pre2 + pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if pre1 + pn1 not in plfg or pre2 + pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)
        p = math.cos(math.radians(d * m))
        p = round((p - 0.5) * 200)
        p = f'{p:3d}'
        return (
            f'{pre1}{pa1} {asp} {pre2}{pa2} {fmt_dm(abs(d), True)}{p}% M',
            acl,
            d,
        )

    def calc_angle_and_strength(
        self,
        planet_data: list,
        chart: dict,
        angularity_options: dict,
    ) -> tuple[str, float, bool, bool]:
        # I should be able to rewrite this mostly using self. variables

        major_angle_orbs = angularity_options.get(
            'major_angles', [3.0, 7.0, 10.0]
        )
        minor_angle_orbs = angularity_options.get(
            'minor_angles', [1.0, 2.0, 3.0]
        )

        for orb_class in range(3):
            if major_angle_orbs[orb_class] == 0:
                major_angle_orbs[orb_class] = -3
            if minor_angle_orbs[orb_class] == 0:
                minor_angle_orbs[orb_class] = -3

        house_quadrant_position = planet_data[8] % 90
        if angularity_options['model'] == 1:
            mundane_angularity_strength = (
                major_angularity_curve_midquadrant_background(
                    house_quadrant_position
                )
            )
        elif angularity_options['model'] == 0:
            mundane_angularity_strength = (
                major_angularity_curve_cadent_background(
                    house_quadrant_position
                )
            )
        else:   # model == 2
            mundane_angularity_strength = (
                major_angularity_curve_eureka_formula(house_quadrant_position)
            )

        aspect_to_asc = abs(chart['cusps'][1] - planet_data[0])
        if aspect_to_asc > 180:
            aspect_to_asc = 360 - aspect_to_asc
        if inrange(aspect_to_asc, 90, 3):
            square_asc_strength = minor_angularity_curve(
                abs(aspect_to_asc - 90)
            )
        else:
            square_asc_strength = -2
        aspect_to_mc = abs(chart['cusps'][10] - planet_data[0])
        if aspect_to_mc > 180:
            aspect_to_mc = 360 - aspect_to_mc
        if inrange(aspect_to_mc, 90, 3):
            square_mc_strength = minor_angularity_curve(abs(aspect_to_mc - 90))
        else:
            square_mc_strength = -2
        ramc_aspect = abs(chart['ramc'] - planet_data[3])
        if ramc_aspect > 180:
            ramc_aspect = 360 - ramc_aspect
        if inrange(ramc_aspect, 90, 3):
            ramc_square_strength = minor_angularity_curve(
                abs(ramc_aspect - 90)
            )
        else:
            ramc_square_strength = -2

        angularity_strength = max(
            mundane_angularity_strength,
            square_asc_strength,
            square_mc_strength,
            ramc_square_strength,
        )

        angularity = ' '
        is_mundanely_background = False

        mundane_angularity_orb = (
            90 - house_quadrant_position
            if house_quadrant_position > 45
            else house_quadrant_position
        )

        if mundane_angularity_orb <= major_angle_orbs[0]:
            angularity = 'F'
        elif mundane_angularity_orb <= major_angle_orbs[1]:
            angularity = 'F'
        elif mundane_angularity_orb <= major_angle_orbs[2]:
            angularity = 'F'

        else:
            if mundane_angularity_strength <= 25:
                is_mundanely_background = True
                angularity = 'B'
                if angularity_options.get('no_bg', False):
                    angularity = ' '

        zenith_nadir_orb = abs(aspect_to_asc - 90)
        if zenith_nadir_orb <= minor_angle_orbs[0]:
            angularity = 'F'
        elif zenith_nadir_orb <= minor_angle_orbs[1]:
            angularity = 'F'
        elif zenith_nadir_orb <= minor_angle_orbs[2]:
            angularity = 'F'

        ep_wp_eclipto_orb = abs(aspect_to_mc - 90)
        if ep_wp_eclipto_orb <= minor_angle_orbs[0]:
            angularity = 'F'
        elif ep_wp_eclipto_orb <= minor_angle_orbs[1]:
            angularity = 'F'
        elif ep_wp_eclipto_orb <= minor_angle_orbs[2]:
            angularity = 'F'

        ep_wp_ascension_orb = abs(ramc_aspect - 90)
        if ep_wp_ascension_orb <= minor_angle_orbs[0]:
            angularity = 'F'
        elif ep_wp_ascension_orb <= minor_angle_orbs[1]:
            angularity = 'F'
        elif ep_wp_ascension_orb <= minor_angle_orbs[2]:
            angularity = 'F'

        angularity_orb = -1

        # if foreground, get specific angle - we can probably do this all at once
        if angularity == 'F':
            # Foreground in prime vertical longitude
            if angularity_strength == mundane_angularity_strength:
                if planet_data[8] >= 345:
                    angularity_orb = 360 - planet_data[8]
                    angularity = 'A '
                elif planet_data[8] <= 15:
                    angularity_orb = planet_data[8]
                    angularity = 'A '
                elif inrange(planet_data[8], 90, 15):
                    angularity_orb = abs(planet_data[8] - 90)
                    angularity = 'I '
                elif inrange(planet_data[8], 180, 15):
                    angularity_orb = abs(planet_data[8] - 180)
                    angularity = 'D '
                elif inrange(planet_data[8], 270, 15):
                    angularity_orb = abs(planet_data[8] - 270)
                    angularity = 'M '

            # Foreground on Zenith/Nadir
            if angularity_strength == square_asc_strength:
                zenith_nadir_orb = chart['cusps'][1] - planet_data[0]
                if zenith_nadir_orb < 0:
                    zenith_nadir_orb += 360
                if inrange(zenith_nadir_orb, 90, 5):
                    angularity_orb = abs(zenith_nadir_orb - 90)
                    angularity = 'Z '
                if inrange(zenith_nadir_orb, 270, 5):
                    angularity_orb = abs(zenith_nadir_orb - 270)
                    angularity = 'N '

            # Foreground on Eastpoint/Westpoint
            if angularity_strength == square_mc_strength:
                ep_wp_eclipto_orb = chart['cusps'][10] - planet_data[0]
                if ep_wp_eclipto_orb < 0:
                    ep_wp_eclipto_orb += 360
                if inrange(ep_wp_eclipto_orb, 90, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 90)
                    angularity = 'W '
                if inrange(ep_wp_eclipto_orb, 270, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 270)
                    angularity = 'E '

            if angularity_strength == ramc_square_strength:
                ep_wp_ascension_orb = chart['ramc'] - planet_data[3]
                if ep_wp_ascension_orb < 0:
                    ep_wp_ascension_orb += 360
                if inrange(ep_wp_ascension_orb, 90, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 90)
                    angularity = 'Wa'
                if inrange(ep_wp_ascension_orb, 270, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 270)
                    angularity = 'Ea'

        if angularity == 'B':
            angularity = ' b'
        elif angularity == ' ':
            angularity = '  '

        if 'I' not in self.cclass:
            # It's not an ingress; dormancy is always negated
            planet_negates_dormancy = True
        else:
            planet_negates_dormancy = angularity_activates_ingress(
                angularity_orb, angularity
            )

        return (
            angularity,
            angularity_strength,
            planet_negates_dormancy,
            is_mundanely_background,
        )

    def find_midpoint(self, planet, plist, i, j, options):
        mpx = options.get('midpoints', {})
        if planet[0] == 'Ep':
            return self.mmp_eastpoint(planet, mmp, plist, i, j)
        if planet[0] == 'Ze':
            return self.mmp_zenith(planet, mmp, plist, i, j)
        p = planet[1]
        m = (plist[i][1] + plist[j][1]) / 2
        d = (p - m) % 360
        if d > 180:
            d = 360 - d
        mp0 = mpx.get('0', 0) / 60
        if mp0:
            if d <= mp0 or d > 180 - mp0:
                if d < 90:
                    z = d
                else:
                    z = 180 - d
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'d"
        mp90 = mpx.get('90', 0) / 60
        if mp90:
            if d >= 90 - mp90 and d <= 90 + mp90:
                z = abs(d - 90)
                di = mpx.get('is90', 'd')
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'{di}"
        mp45 = mpx.get('45', 0) / 60
        if mp45:
            if d >= 45 - mp45 and d <= 45 + mp45:
                z = abs(d - 45)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'i"
            if d >= 135 - mp45 and d <= 135 + mp45:
                z = abs(d - 135)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'i"
        return ''

    def mmp_major(self, plist, i, j, mmp):
        m = (plist[i][3] + plist[j][3]) / 2
        m %= 90
        if m > mmp and m < 90 - mmp:
            return ''
        z = 90 - m if m > 45 else m
        return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'MA"

    def mmp_eastpoint(self, planet, plist, i, j, mmp):
        m = (plist[i][1] + plist[j][1]) / 2
        p = planet[1]
        d = (p - m) % 360
        if d > 180:
            d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:
                z1 = d
            else:
                z1 = 180 - d
        else:
            z1 = 1000
        m = (plist[i][2] + plist[j][2]) / 2
        p = planet[2]
        d = (p - m) % 360
        if d > 180:
            d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:
                z2 = d
            else:
                z2 = 180 - d
        else:
            z2 = 1000
        z = min(z1, z2)
        xl1 = (plist[i][1] - planet[1]) % 360
        xa1 = (plist[i][2] - planet[2]) % 360
        if xl1 > 180:
            xl1 = 360 - xl1
        if xa1 > 180:
            xa1 = 360 - xa1
        xl2 = (plist[j][1] - planet[1]) % 360
        xa2 = (plist[j][2] - planet[2]) % 360
        if xl2 > 180:
            xl2 = 360 - xl2
        if xa2 > 180:
            xa2 = 360 - xa2
        if not any(
            [
                xl1 <= 3,
                xl1 >= 177,
                xa1 <= 3,
                xa1 >= 177,
                xl2 <= 3,
                xl2 >= 177,
                xa2 <= 3,
                xa2 >= 177,
            ]
        ):
            return ''
        if z < 1000:
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'ME"
        return ''

    def mmp_zenith(self, planet, plist, i, j, mmp):
        p = planet[1]
        x = (plist[i][1] - p) % 360
        if x > 180:
            x = 360 - x
        if x > 3 and x < 177:
            return ''
        x = plist[i][2] - p % 360
        if x > 180:
            x = 360 - x
        if x > 3 and x < 177:
            return ''
        m = (plist[i][1] + plist[j][1]) / 2
        d = (p - m) % 360
        if d > 180:
            d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:
                z = d
            else:
                z = 180 - d
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):02}'MZ"
        return ''

    def mmp_all(self, ep, ze, plist, i, j, options):
        mmp = options.get('midpoints', {}).get('M', 0) / 60
        if not mmp:
            return ''
        a = self.mmp_major(plist, i, j, mmp)
        e = self.mmp_eastpoint(ep, plist, i, j, mmp)
        z = self.mmp_zenith(ze, plist, i, j, mmp)
        ai = a[6:8] if a else '99'
        ei = e[6:8] if e else '99'
        zi = e[6:8] if z else '99'
        if ai <= ei:
            x = a
            xi = ai
        else:
            x = e
            xi = ei
        x = x if xi <= zi else z
        return x

    def show(self):
        open_file(self.filename)
