# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
import os
from datetime import datetime

from chart_utils import *
from constants import VERSION
from utils import open_file


def write_to_file(chart, planet):
    pd = chart[planet]
    index = PLANET_NAMES.index(planet)
    pa = PLANET_NAMES_SHORT[index]

    d = pa + ' ' + zod_min(pd[0])
    if index < 14:
        d += ' ' + fmt_dm(pd[-1] % 30)
    else:
        d = center_align(d, 16)
    return d


def get_return_class(value):
    value = value.lower()
    if value[0:3] in ['cap', 'can', 'ari', 'lib']:
        return 'SI' if 'solar' in value else 'LI'
    if 'return' in value:
        return 'SR' if 'solar' in value else 'LR'
    return 'N'


class Uniwheel:
    def __init__(self, chart, temporary, options):
        rows = 65
        cols = 69
        chart_grid = [[' ' for i in range(cols)] for j in range(rows)]
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
            for planet_index in range(cols):
                chart_grid[0][planet_index] = '-'
                chart_grid[16][planet_index] = '-'
                if planet_index <= 17 or planet_index >= 51:
                    chart_grid[32][planet_index] = '-'
                chart_grid[48][planet_index] = '-'
                chart_grid[64][planet_index] = '-'
            for planet_index in range(rows):
                chart_grid[planet_index][0] = '|'
                chart_grid[planet_index][17] = '|'
                if planet_index <= 16 or planet_index >= 48:
                    chart_grid[planet_index][34] = '|'
                chart_grid[planet_index][51] = '|'
                chart_grid[planet_index][68] = '|'
            for planet_index in range(0, rows, 16):
                for j in range(0, cols, 17):
                    if planet_index == 32 and j == 34:
                        continue
                    chart_grid[planet_index][j] = '+'
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

            if chart['type'] not in INGRESSES:
                name = chart['name']
                if ';' in name:
                    name = name.split(';')
                    name = name[0]
                chart_grid[21][18:51] = center_align(name)
            chtype = chart['type']
            if chtype.endswith(' Single Wheel'):
                chtype = chtype.replace(' Single Wheel', '')
            chart_grid[23][18:51] = center_align(chtype)
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
            chart_grid[25][18:51] = center_align(line)
            chart_grid[27][18:51] = center_align(chart['location'])
            chart_grid[29][18:51] = center_align(
                fmt_lat(chart['latitude']) + ' ' + fmt_long(chart['longitude'])
            )
            chart_grid[31][18:51] = center_align(
                'UT ' + fmt_hms(chart['time'] + chart['correction'])
            )
            chart_grid[33][18:51] = center_align(
                'RAMC ' + fmt_dms(chart['ramc'])
            )
            chart_grid[35][18:51] = center_align('OE ' + fmt_dms(chart['oe']))
            chart_grid[37][18:51] = center_align(
                'SVP ' + zod_sec(360 - chart['ayan'])
            )
            chart_grid[39][18:51] = center_align('Sidereal Zodiac')
            chart_grid[41][18:51] = center_align('Campanus Houses')
            chart_grid[43][18:51] = center_align(chart['notes'] or '* * * * *')

            x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
            y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
            houses = [[] for i in range(12)]
            for planet_index in range(12):
                houses[planet_index] = self.sort_house(
                    chart, planet_index, options
                )
                if planet_index > 3 and planet_index < 9:
                    houses[planet_index].reverse()
                for j in range(15):
                    if houses[planet_index][j]:
                        temp = houses[planet_index][j]
                        if len(temp) > 2:
                            planet = houses[planet_index][j][0]
                            chart_grid[y[planet_index] + j][
                                x[planet_index] : x[planet_index] + 16
                            ] = write_to_file(chart, planet)

            for row in chart_grid:
                chartfile.write(' ')
                for col in row:
                    chartfile.write(col)
                chartfile.write('\n')

            chartfile.write('\n\n' + '-' * 72 + '\n')
            chartfile.write(
                'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
            )
            angularity_options = options.get('angularity', {})
            major_limit = angularity_options.get(
                'major_angles', [3.0, 7.0, 10.0]
            )
            minor_limit = angularity_options.get(
                'minor_angles', [1.0, 2.0, 3.0]
            )
            plfg = []
            plang = {}
            dormant = True if 'I' in self.cclass else False
            for planet_index in range(3):
                if major_limit[planet_index] == 0:
                    major_limit[planet_index] = -3
                if minor_limit[planet_index] == 0:
                    minor_limit[planet_index] = -3

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
                    right_align(fmt_dm(planet_data[5] + 180 % 360, True), 7)
                    + ' '
                )

                # Altitude
                chartfile.write(right_align(s_dm(planet_data[6]), 7) + ' ')

                # Meridian Longitude
                chartfile.write(fmt_dm(planet_data[7], True) + ' ')

                # House position
                chartfile.write(
                    right_align(fmt_dm(planet_data[8], True), 7) + ' '
                )

                a1 = planet_data[8] % 90
                if angularity_options['model'] == 1:
                    p1 = major_angularity_curve_midquadrant_background(a1)
                else:
                    p1 = major_angularity_curve_cadent_background(a1)
                a2 = abs(chart['cusps'][1] - planet_data[0])
                if a2 > 180:
                    a2 = 360 - a2
                if inrange(a2, 90, 3):
                    p2 = minor_angularity_curve(abs(a2 - 90))
                else:
                    p2 = -2
                a3 = abs(chart['cusps'][10] - planet_data[0])
                if a3 > 180:
                    a3 = 360 - a3
                if inrange(a3, 90, 3):
                    p3 = minor_angularity_curve(abs(a3 - 90))
                else:
                    p3 = -2
                a4 = abs(chart['ramc'] - planet_data[3])
                if a4 > 180:
                    a4 = 360 - a4
                if inrange(a4, 90, 3):
                    p4 = minor_angularity_curve(abs(a4 - 90))
                else:
                    p4 = -2
                p = max(p1, p2, p3, p4)
                fb = ' '
                fbx = ' '
                a = 90 - a1 if a1 > 45 else a1
                if a <= major_limit[0]:
                    fb = 'F'
                    dormant = False
                elif a <= major_limit[1]:
                    fb = 'F'
                elif a <= major_limit[2]:
                    fb = 'F'
                if fb == ' ':
                    if angularity_options['model'] == 0:
                        if a1 >= 60:
                            a = a1 - 60
                        else:
                            a = (60 - a1) / 2
                    else:
                        a = abs(a - 45)
                    if a <= major_limit[0]:
                        fb = 'B'
                    elif a <= major_limit[1]:
                        fb = 'B'
                    elif a <= major_limit[2]:
                        fb = 'B'
                    if fb == 'B' and angularity_options.get('no_bg', False):
                        fbx = 'B'
                        fb = ' '
                a = abs(a2 - 90)
                if a <= minor_limit[0]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[1]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[2]:
                    fb = 'F'
                a = abs(a3 - 90)
                if a <= minor_limit[0]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[1]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[2]:
                    fb = 'F'
                a = abs(a4 - 90)
                if a <= minor_limit[0]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[1]:
                    fb = 'F'
                    dormant = False
                elif a <= minor_limit[2]:
                    fb = 'F'
                if fb == 'F' or (planet_name == 'Moon' and 'I' in self.cclass):
                    plfg.append(planet_name)
                strength_percent = round((p + 1) * 50)
                if fb == ' ':
                    if fbx == ' ':
                        plang[PLANET_NAMES_SHORT[planet_index]] = ' '
                    else:
                        plang[PLANET_NAMES_SHORT[planet_index]] = fbx
                else:
                    plang[PLANET_NAMES_SHORT[planet_index]] = fb
                if fb == 'F':
                    if p == p1:
                        if planet_data[8] >= 345 or planet_data[8] <= 15:
                            fb = 'A '
                        if inrange(planet_data[8], 90, 15):
                            fb = 'I '
                        if inrange(planet_data[8], 180, 15):
                            fb = 'D '
                        if inrange(planet_data[8], 270, 15):
                            fb = 'M '
                    if p == p2:
                        a = chart['cusps'][1] - planet_data[0]
                        if a < 0:
                            a += 360
                        if inrange(a, 90, 5):
                            fb = 'Z '
                        if inrange(a, 270, 5):
                            fb = 'N '
                    if p == p3:
                        a = chart['cusps'][10] - planet_data[0]
                        if a < 0:
                            a += 360
                        if inrange(a, 90, 5):
                            fb = 'W '
                        if inrange(a, 270, 5):
                            fb = 'E '
                    if p == p4:
                        a = chart['ramc'] - planet_data[3]
                        if a < 0:
                            a += 360
                        if inrange(a, 90, 5):
                            fb = 'Wa'
                        if inrange(a, 270, 5):
                            fb = 'Ea'
                if fb == 'B':
                    fb = ' b'
                if fb == ' ':
                    fb = '  '

                if inrange(planet_data[5], 270, minor_limit[2]):
                    chartfile.write(f'     Vx')
                elif inrange(planet_data[5], 90, minor_limit[2]):
                    chartfile.write(f'     Av')
                else:
                    chartfile.write(f'{strength_percent:3d}% {fb}')
                chartfile.write('\n')
            if dormant:
                chartfile.write('-' * 72 + '\n')
                chartfile.write(center_align('Dormant Ingress', 72) + '\n')

            ea = options.get('ecliptic_aspects', DEFAULT_ECLIPTICAL_ORBS)
            ma = options.get('mundane_aspects', DEFAULT_MUNDANE_ORBS)
            asp = [[], [], [], []]
            asph = ['Class 1', 'Class 2', 'Class 3', 'Other Partile']
            for planet_index in range(14):
                for j in range(planet_index + 1, 14):
                    (easp, cle, orbe) = self.find_ecliptical_aspect(
                        chart, planet_index, j, ea, options, plfg, dormant
                    )
                    (masp, clm, orbm) = self.find_mundane_aspect(
                        chart, planet_index, j, ma, options, plfg, dormant
                    )
                    if easp and masp:
                        if orbm < orbe:
                            easp = ''
                        else:
                            masp = ''
                    if easp:
                        asp[cle - 1].append(easp)
                    if masp:
                        asp[clm - 1].append(masp)
            if len(asp[3]) == 0 or dormant:
                del asp[3]
                del asph[3]
                asp.append([])
                asph.append('')
            for planet_index in range(2, -1, -1):
                if len(asp[planet_index]) == 0:
                    del asp[planet_index]
                    del asph[planet_index]
                    asp.append([])
                    asph.append('')
            if any(asph):
                chartfile.write('-' * 72 + '\n')
                for planet_index in range(0, 3):
                    chartfile.write(
                        center_align(
                            f'{asph[planet_index]} Aspects'
                            if asph[planet_index]
                            else '',
                            24,
                        )
                    )
                chartfile.write('\n')
            for planet_index in range(
                max(len(asp[0]), len(asp[1]), len(asp[2]))
            ):
                if planet_index < len(asp[0]):
                    chartfile.write(left_align(asp[0][planet_index], 24))
                else:
                    chartfile.write(' ' * 24)
                if planet_index < len(asp[1]):
                    chartfile.write(center_align(asp[1][planet_index], 24))
                else:
                    chartfile.write(' ' * 24)
                if planet_index < len(asp[2]):
                    chartfile.write(right_align(asp[2][planet_index], 24))
                else:
                    chartfile.write(' ' * 24)
                chartfile.write('\n')
            chartfile.write('-' * 72 + '\n')
            if asp[3]:
                chartfile.write(center_align(f'{asph[3]} Aspects', 72) + '\n')
                for a in asp[3]:
                    chartfile.write(center_align(a, 72) + '\n')
                chartfile.write('-' * 72 + '\n')
            chartfile.write(center_align('Cosmic State', 72) + '\n')
            moonsi = SIGNS_SHORT[int(chart['Moon'][0] // 30)]
            sunsi = SIGNS_SHORT[int(chart['Sun'][0] // 30)]
            cclass = chart['class']
            for planet_index in range(14):
                if planet_index == 10 and not options.get('use_Eris', 1):
                    continue
                if planet_index == 11 and not options.get('use_Sedna', 0):
                    continue
                if planet_index == 12 and options.get('Node', 0) != 1:
                    continue
                if planet_index == 13 and options.get('Node', 0) != 2:
                    continue
                pa = PLANET_NAMES_SHORT[planet_index]
                pn = PLANET_NAMES[planet_index]
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
                chartfile.write(plang.get(pa, '') + ' |')
                cr = False
                if cclass != 'I':
                    if pa != 'Mo':
                        if moonsi in POS_SIGN[pa]:
                            chartfile.write(f' Mo {moonsi}+')
                            cr = True
                        elif moonsi in NEG_SIGN[pa]:
                            chartfile.write(f' Mo {moonsi}-')
                            cr = True
                    if pa != 'Su':
                        if sunsi in POS_SIGN[pa]:
                            chartfile.write(f' Su {sunsi}+')
                            cr = True
                        elif sunsi in NEG_SIGN[pa]:
                            chartfile.write(f' Su {sunsi}-')
                            cr = True
                asplist = []
                for j in range(3):
                    for entry in asp[j]:
                        if pa in entry:
                            pct = str(200 - int(entry[15:18]))
                            entry = entry[0:15] + entry[20:]
                            if entry[0:2] == pa:
                                entry = entry[3:]
                            else:
                                entry = f'{entry[3:5]} {entry[0:2]}{entry[8:]}'
                            asplist.append([entry, pct])
                asplist.sort(key=lambda p: p[1] + p[0][6:11])
                if asplist:
                    if cr:
                        chartfile.write('\n' + (' ' * 9) + '| ')
                        cr = False
                    else:
                        chartfile.write(' ')
                for j, a in enumerate(asplist):
                    chartfile.write(a[0] + '   ')
                    if j % 4 == 3 and j != len(asplist) - 1:
                        chartfile.write('\n' + (' ' * 9) + '| ')
                plist = []
                for j in range(14):
                    if j == planet_index:
                        continue
                    if j == 10 and not options.get('use_Eris', 1):
                        continue
                    if j == 11 and not options.get('use_Sedna', 0):
                        continue
                    if j == 12 and options.get('Node', 0) != 1:
                        continue
                    if j == 13 and options.get('Node', 0) != 2:
                        continue
                    plna = PLANET_NAMES[j]
                    plong = chart[plna][0]
                    plab = PLANET_NAMES_SHORT[j]
                    if options.get('show_aspects', 0) == 0 or plna in plfg:
                        plist.append([plab, plong])
                plist.append(['As', chart['cusps'][1]])
                plist.append(['Mc', chart['cusps'][10]])
                if len(plist) > 1 and (
                    options.get('show_aspects', 0) == 0 or pn in plfg
                ):
                    # ecliptic midpoints?
                    emp = []
                    for j in range(len(plist) - 1):
                        for k in range(j + 1, len(plist)):
                            mp = self.find_midpoint(
                                [pa, planet_data[0]], plist, j, k, options
                            )
                            if mp:
                                emp.append(mp)
                    if emp:
                        emp.sort(key=lambda p: p[6:8])
                        if cr or asplist:
                            chartfile.write('\n' + (' ' * 9) + '| ')
                        else:
                            chartfile.write(' ')
                        for j, a in enumerate(emp):
                            chartfile.write('   ' + a + '   ')
                            if j % 4 == 3 and j != len(emp) - 1:
                                chartfile.write('\n' + (' ' * 9) + '| ')
            sign = SIGNS_SHORT[int(chart['cusps'][1] // 30)]
            plist = []
            for planet_index in range(14):
                if planet_index == 10 and not options.get('use_Eris', 1):
                    continue
                if planet_index == 11 and not options.get('use_Sedna', 0):
                    continue
                if planet_index == 12 and options.get('Node', 0) != 1:
                    continue
                if planet_index == 13 and options.get('Node', 0) != 2:
                    continue
                plna = PLANET_NAMES[planet_index]
                plong = chart[plna][0]
                plra = chart[plna][3]
                plpvl = chart[plna][7]
                plab = PLANET_NAMES_SHORT[planet_index]
                if options.get('show_aspects', 0) == 0 or plna in plfg:
                    plist.append([plab, plong, plra, plpvl])
            plist.append(['Mc', chart['cusps'][10]])
            if len(plist) > 1:
                emp = []
                for j in range(len(plist) - 1):
                    for k in range(j + 1, len(plist)):
                        mp = self.find_midpoint(
                            ['As', chart['cusps'][1]], plist, j, k, options
                        )
                        if mp:
                            emp.append(mp)
                if emp:
                    emp.sort(key=lambda p: p[6:8])
                    chartfile.write(f'\nAs {sign}    | ')
                    for j, a in enumerate(emp):
                        chartfile.write('   ' + a + '   ')
                        if j % 4 == 3 and j != len(emp) - 1:
                            chartfile.write('\n' + (' ' * 9) + '| ')
            sign = SIGNS_SHORT[int(chart['cusps'][10] // 30)]
            plist[-1] = ['As', chart['cusps'][1]]
            if len(plist) > 1:
                emp = []
                for j in range(len(plist) - 1):
                    for k in range(j + 1, len(plist)):
                        mp = self.find_midpoint(
                            ['Mc', chart['cusps'][10]], plist, j, k, options
                        )
                        if mp:
                            emp.append(mp)
                if emp:
                    emp.sort(key=lambda p: p[6:8])
                    chartfile.write(f'\nMc {sign}    | ')
                    for j, a in enumerate(emp):
                        chartfile.write('   ' + a + '   ')
                        if j % 4 == 3 and j != len(emp) - 1:
                            chartfile.write('\n' + (' ' * 9) + '| ')
            del plist[-1]
            if len(plist) > 1:
                emp = []
                ep = [
                    'Ep',
                    (chart['cusps'][10] + 90) % 360,
                    (chart['ramc'] + 90) % 360,
                ]
                ze = ['Ze', (chart['cusps'][1] - 90) % 360]
                for j in range(len(plist) - 1):
                    for k in range(j + 1, len(plist)):
                        mp = self.mmp_all(ep, ze, plist, j, k, options)
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
                        for j, a in enumerate(empa):
                            chartfile.write('   ' + a + '   ')
                            if j % 4 == 3 and j != len(empa) - 1:
                                chartfile.write('\n' + (' ' * 9) + '| ')
                    if empe:
                        chartfile.write(f'\nEp       | ')
                        for j, a in enumerate(empe):
                            chartfile.write('   ' + a + '   ')
                            if j % 4 == 3 and j != len(empe) - 1:
                                chartfile.write('\n' + (' ' * 9) + '| ')
                    if empz:
                        chartfile.write(f'\nZe       | ')
                        for j, a in enumerate(empz):
                            chartfile.write('   ' + a + '   ')
                            if j % 4 == 3 and j != len(empz) - 1:
                                chartfile.write('\n' + (' ' * 9) + '| ')
            chartfile.write('\n' + '-' * 72 + '\n')
            chartfile.write(
                f"Created by Time Matters {VERSION}  ({datetime.now().strftime('%d %b %Y')})"
            )
            self.filename = filename
        return

    def sort_house(self, chart, h, options):
        house = []
        for planet_name in PLANET_NAMES:
            if planet_name == 'Eris' and not options.get('use_Eris', 1):
                continue
            if planet_name == 'Sedna' and not options.get('use_Sedna', 0):
                continue
            if planet_name == 'Vertex' and not options.get('use_Vertex', 0):
                continue
            if planet_name == 'True Node' and options.get('Node', 0) != 1:
                continue
            if planet_name == 'Mean Node' and options.get('Node', 0) != 2:
                continue
            planet_data = chart[planet_name]
            if planet_data[-1] // 30 == h:
                pos = (planet_data[-1] % 30) / 2
                house.append([planet_name, planet_data[-1], pos])
        house.sort(key=lambda h: h[1])
        return self.spread(house)

    def spread(self, old, start=0):
        new = [[] for i in range(15)]
        placed = 0
        for i in range(len(old)):
            x = int(old[i][-1]) + start
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

    def find_ecliptical_aspect(self, chart, i, j, ea, options, plfg, dormant):
        pn1 = PLANET_NAMES[i]
        pn2 = PLANET_NAMES[j]
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
        pd1 = chart[PLANET_NAMES[i]]
        pd2 = chart[PLANET_NAMES[j]]
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
                if pn1 == 'Moon' and 'I' in self.cclass:
                    break
                if dormant:
                    return ('', 0, 0)
                if options.get('show_aspects', 0) == 1:
                    if pn1 not in plfg and pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if pn1 not in plfg or pn2 not in plfg:
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
        return (f'{pa1} {asp} {pa2} {fmt_dm(abs(d), True)}{p}%  ', acl, d)

    def find_mundane_aspect(self, chart, i, j, ma, options, plfg, dormant):
        pn1 = PLANET_NAMES[i]
        pn2 = PLANET_NAMES[j]
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
        pd1 = chart[PLANET_NAMES[i]]
        pd2 = chart[PLANET_NAMES[j]]
        pa1 = PLANET_NAMES_SHORT[i]
        pa2 = PLANET_NAMES_SHORT[j]
        d = abs(pd1[7] - pd2[7]) % 360
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
                if pn1 == 'Moon' and 'I' in self.cclass:
                    break
                if dormant:
                    return ('', 0, 0)
                if options.get('show_aspects', 0) == 1:
                    if pn1 not in plfg and pn2 not in plfg:
                        if d <= 1 and options.get('partile_nf', False):
                            acl = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if pn1 not in plfg or pn2 not in plfg:
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
        return (f'{pa1} {asp} {pa2} {fmt_dm(abs(d), True)}{p}% M', acl, d)

    def find_midpoint(self, planet, plist, i, j, options):
        mpx = options.get('midpoints', {})
        if planet[0] == 'Ep':
            # mmp is evidently a planet
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
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'d"
        mp90 = mpx.get('90', 0) / 60
        if mp90:
            if d >= 90 - mp90 and d <= 90 + mp90:
                z = abs(d - 90)
                di = mpx.get('is90', 'd')
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'{di}"
        mp45 = mpx.get('45', 0) / 60
        if mp45:
            if d >= 45 - mp45 and d <= 45 + mp45:
                z = abs(d - 45)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'i"
            if d >= 135 - mp45 and d <= 135 + mp45:
                z = abs(d - 135)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'i"
        return ''

    def mmp_major(self, plist, i, j, mmp):
        m = (plist[i][3] + plist[j][3]) / 2
        m %= 90
        if m > mmp and m < 90 - mmp:
            return ''
        z = 90 - m if m > 45 else m
        return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'MA"

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
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'ME"
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
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'MZ"
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
