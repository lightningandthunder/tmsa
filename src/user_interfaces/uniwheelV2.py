# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
from datetime import datetime

from chart_utils import *
from constants import VERSION
from utils import open_file


def write_to_file(chart, planet):
    planet_data = chart[planet]
    index = PLANET_NAMES.index(planet)
    short_name = PLANET_NAMES_SHORT[index]

    data_line = short_name + ' ' + zod_min(planet_data[0])
    if index < 14:
        data_line += ' ' + fmt_dm(planet_data[-1] % 30)
    else:
        data_line = center_align(data_line, 16)

    return data_line


class UniwheelV2:
    def __init__(self, chart, temporary, options):
        self.table_width = 81

        filename = make_chart_path(chart, temporary)
        filename = filename[0:-3] + 'txt'
        try:
            chartfile = open(filename, 'w')
        except Exception as e:
            tkmessagebox.showerror(f'Unable to open file:', f'{e}')
            return

        with chartfile:
            self.draw_chart(chart, chartfile, options)
            self.write_info_table(chart, chartfile, options)

            chartfile.write('\n' + '-' * self.table_width + '\n')
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
        return self.spread_planets_within_house(house)

    def spread_planets_within_house(self, old, start=0):
        new = [[] for _ in range(15)]
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

    def find_ecliptical_aspect(
        self,
        chart,
        planet_index_1,
        planet_index_2,
        ecliptical_orbs,
        options,
        foreground_planets,
        whole_chart_is_dormant,
    ):
        planet_name_1 = PLANET_NAMES[planet_index_1]
        planet_name_2 = PLANET_NAMES[planet_index_2]
        if (
            planet_name_1 == 'Eris' or planet_name_2 == 'Eris'
        ) and not options.get('use_Eris', 1):
            return ('', 0, 0)
        if (
            planet_name_1 == 'Sedna' or planet_name_2 == 'Sedna'
        ) and not options.get('use_Sedna', 0):
            return ('', 0, 0)
        if (
            planet_name_1 == 'True Node' or planet_name_2 == 'True Node'
        ) and options.get('Node', 0) != 1:
            return ('', 0, 0)
        if (
            planet_name_1 == 'Mean Node' or planet_name_2 == 'Mean Node'
        ) and options.get('Node', 0) != 2:
            return ('', 0, 0)
        planet_data_1 = chart[PLANET_NAMES[planet_index_1]]
        planet_data_2 = chart[PLANET_NAMES[planet_index_2]]
        planet_short_name_1 = PLANET_NAMES_SHORT[planet_index_1]
        planet_short_name_2 = PLANET_NAMES_SHORT[planet_index_2]
        aspect_strings = [
            '0',
            '180',
            '90',
            '45',
            '45',
            '120',
            '60',
            '30',
            '30',
        ]
        aspect_ints = [0, 180, 90, 45, 135, 120, 60, 30, 150]
        aspect_names = ['co', 'op', 'sq', 'oc', 'oc', 'tr', 'sx', 'in', 'in']
        raw_orb = abs(planet_data_1[0] - planet_data_2[0]) % 360
        if raw_orb > 180:
            raw_orb = 360 - raw_orb
        for planet_index_1 in range((len(aspect_strings) - 1)):
            test_orb = ecliptical_orbs[aspect_strings[planet_index_1]]
            if test_orb[2]:
                maxorb = test_orb[2]
            elif test_orb[1]:
                maxorb = test_orb[1] * 1.25
            elif test_orb[0]:
                maxorb = test_orb[0] * 2.5
            else:
                maxorb = -1
            if (
                raw_orb >= aspect_ints[planet_index_1] - maxorb
                and raw_orb <= aspect_ints[planet_index_1] + maxorb
            ):
                aspect = aspect_names[planet_index_1]
                if maxorb <= 0:
                    return ('', 0, 0)
                strength = 60 / maxorb
                raw_orb = abs(raw_orb - aspect_ints[planet_index_1])
                if raw_orb <= test_orb[0]:
                    aspect_class = 1
                elif raw_orb <= test_orb[1]:
                    aspect_class = 2
                elif raw_orb <= test_orb[2]:
                    aspect_class = 3
                else:
                    return ('', 0, 0)
                if planet_name_1 == 'Moon' and 'I' in self.cclass:
                    break
                if whole_chart_is_dormant:
                    return ('', 0, 0)
                if options.get('show_aspects', 0) == 1:
                    if (
                        planet_name_1 not in foreground_planets
                        and planet_name_2 not in foreground_planets
                    ):
                        if raw_orb <= 1 and options.get('partile_nf', False):
                            aspect_class = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if (
                        planet_name_1 not in foreground_planets
                        or planet_name_2 not in foreground_planets
                    ):
                        if raw_orb <= 1 and options.get('partile_nf', False):
                            aspect_class = 4
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)
        strength_percent = math.cos(math.radians(raw_orb * strength))
        strength_percent = round((strength_percent - 0.5) * 200)
        strength_percent = f'{strength_percent:3d}'
        return (
            f'{planet_short_name_1} {aspect} {planet_short_name_2} {fmt_dm(abs(raw_orb), True)}{strength_percent}%  ',
            aspect_class,
            raw_orb,
        )

    def find_mundane_aspect(
        self,
        chart,
        planet_index_1,
        planet_index_2,
        mundane_orbs,
        options,
        planets_foreground,
        dormant,
    ):
        planet_name_1 = PLANET_NAMES[planet_index_1]
        planet_name_2 = PLANET_NAMES[planet_index_2]
        if (
            planet_name_1 == 'Eris' or planet_name_2 == 'Eris'
        ) and not options.get('use_Eris', 1):
            return ('', 0, 0)
        if (
            planet_name_1 == 'Sedna' or planet_name_2 == 'Sedna'
        ) and not options.get('use_Sedna', 0):
            return ('', 0, 0)
        if (
            planet_name_1 == 'True Node' or planet_name_2 == 'True Node'
        ) and options.get('Node', 0) != 1:
            return ('', 0, 0)
        if (
            planet_name_1 == 'Mean Node' or planet_name_2 == 'Mean Node'
        ) and options.get('Node', 0) != 2:
            return ('', 0, 0)
        planet_data_1 = chart[PLANET_NAMES[planet_index_1]]
        planet_data_2 = chart[PLANET_NAMES[planet_index_2]]
        planet_short_name_1 = PLANET_NAMES_SHORT[planet_index_1]
        planet_short_name_2 = PLANET_NAMES_SHORT[planet_index_2]

        raw_orb = abs(planet_data_1[8] - planet_data_2[8]) % 360
        if raw_orb > 180:
            raw_orb = 360 - raw_orb
        aspect_strings = ['0', '180', '90', '45', '135']
        aspect_ints = [0, 180, 90, 45, 135]
        aspect_names = ['co', 'op', 'sq', 'oc', 'oc']
        for aspect_string_index in range((len(aspect_strings) - 1)):
            test_aspect_orb = mundane_orbs[aspect_strings[aspect_string_index]]
            if test_aspect_orb[2]:
                maxorb = test_aspect_orb[2]
            elif test_aspect_orb[1]:
                maxorb = test_aspect_orb[1] * 1.25
            elif test_aspect_orb[0]:
                maxorb = test_aspect_orb[0] * 2.5
            else:
                maxorb = -1
            if (
                raw_orb >= aspect_ints[aspect_string_index] - maxorb
                and raw_orb <= aspect_ints[aspect_string_index] + maxorb
            ):
                asp = aspect_names[aspect_string_index]
                if maxorb <= 0:
                    return ('', 0, 0)
                strength = 60 / maxorb
                raw_orb = abs(raw_orb - aspect_ints[aspect_string_index])
                if raw_orb <= test_aspect_orb[0]:
                    aspect_class = 1
                elif raw_orb <= test_aspect_orb[1]:
                    aspect_class = 2
                elif raw_orb <= test_aspect_orb[2]:
                    aspect_class = 3
                else:
                    return ('', 0, 0)
                if planet_name_1 == 'Moon' and 'I' in self.cclass:
                    break
                if dormant:
                    return ('', 0, 0)
                if options.get('show_aspects', 0) == 1:
                    if (
                        planet_name_1 not in planets_foreground
                        and planet_name_2 not in planets_foreground
                    ):
                        if raw_orb <= 1 and options.get('partile_nf', False):
                            aspect_class = 4
                        else:
                            return ('', 0, 0)
                elif options.get('show_aspects', 0) == 2:
                    if (
                        planet_name_1 not in planets_foreground
                        or planet_name_2 not in planets_foreground
                    ):
                        if raw_orb <= 1 and options.get('partile_nf', False):
                            aspect_class = 4
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)
        strength_percent = math.cos(math.radians(raw_orb * strength))
        strength_percent = round((strength_percent - 0.5) * 200)
        strength_percent = f'{strength_percent:3d}'

        return (
            f'{planet_short_name_1} {asp} {planet_short_name_2} {fmt_dm(abs(raw_orb), True)}{strength_percent}% M',
            aspect_class,
            raw_orb,
        )

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

    def draw_chart(self, chart, chartfile, options):
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

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
        line = str(chart['day']) + ' ' + month_abrev[chart['month'] - 1] + ' '
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
        chart_grid[33][18:51] = center_align('RAMC ' + fmt_dms(chart['ramc']))
        chart_grid[35][18:51] = center_align('OE ' + fmt_dms(chart['oe']))
        chart_grid[37][18:51] = center_align(
            'SVP ' + zod_sec(360 - chart['ayan'])
        )
        chart_grid[39][18:51] = center_align('Sidereal Zodiac')
        chart_grid[41][18:51] = center_align('Campanus Houses')
        chart_grid[43][18:51] = center_align(chart['notes'] or '* * * * *')

        x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
        y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
        houses = [[] for _ in range(12)]
        for index in range(12):
            houses[index] = self.sort_house(chart, index, options)
            if index > 3 and index < 9:
                houses[index].reverse()
            for sub_index in range(15):
                if houses[index][sub_index]:
                    temp = houses[index][sub_index]
                    if len(temp) > 2:
                        planet = houses[index][sub_index][0]
                        chart_grid[y[index] + sub_index][
                            x[index] : x[index] + 16
                        ] = write_to_file(chart, planet)

        for row in chart_grid:
            chartfile.write(' ')
            for col in row:
                chartfile.write(col)
            chartfile.write('\n')

        chartfile.write('\n\n' + '-' * self.table_width + '\n')

    def write_info_table(self, chart, chartfile, options):
        chartfile.write(
            'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
        )
        angularity_options = options.get('angularity', {})
        planets_foreground = []
        planet_foreground_angles = {}

        # Default to true if this is an ingress chart
        whole_chart_is_dormant = True if 'I' in self.cclass else False

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
            chartfile.write(left_align(PLANET_NAMES_SHORT[planet_index], 3))
            chartfile.write(zod_sec(planet_data[0]) + ' ')
            chartfile.write(fmt_lat(planet_data[1], True) + ' ')
            if abs(planet_data[2]) >= 1:
                chartfile.write(s_dm(planet_data[2]) + ' ')
            else:
                chartfile.write(s_ms(planet_data[2]) + ' ')
            chartfile.write(right_align(fmt_dm(planet_data[3], True), 7) + ' ')
            chartfile.write(fmt_lat(planet_data[4], True) + ' ')

            # Azimuth
            chartfile.write(right_align(fmt_dm(planet_data[5], True), 7) + ' ')

            # Altitude
            chartfile.write(right_align(s_dm(planet_data[6]), 7) + ' ')

            # Meridian Longitude
            chartfile.write(
                fmt_dm(planet_data[7], degree_digits=3, noz=True) + ' '
            )

            # House position
            chartfile.write(right_align(fmt_dm(planet_data[8], True), 7) + ' ')

            # Angularity
            (
                angularity,
                strength_percent,
                planet_negates_dormancy,
                is_mundanely_background,
            ) = self.calc_angle_and_strength(
                planet_data,
                chart,
                angularity_options,
            )

            if planet_negates_dormancy:
                whole_chart_is_dormant = False

            planet_foreground_angles[
                PLANET_NAMES_SHORT[planet_index]
            ] = angularity

            angularity_is_empty = angularity.strip() == ''
            angularity_is_background = angularity.strip().lower() == 'b'

            if (
                not angularity_is_empty
                and not angularity_is_background
            ) or (planet_name == 'Moon' and 'I' in self.cclass):
                planets_foreground.append(planet_name)

            if angularity_is_background or is_mundanely_background:
                planet_foreground_angles[
                    PLANET_NAMES_SHORT[planet_index]
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

        if whole_chart_is_dormant:
            chartfile.write('-' * self.table_width + '\n')
            chartfile.write(
                center_align('Dormant Ingress', self.table_width) + '\n'
            )

        # Aspects
        ecliptical_orbs = options.get(
            'ecliptic_aspects', DEFAULT_ECLIPTICAL_ORBS
        )
        mundane_orbs = options.get('mundane_aspects', DEFAULT_MUNDANE_ORBS)
        aspects_by_class = [[], [], [], []]
        aspect_class_headers = [
            'Class 1',
            'Class 2',
            'Class 3',
            'Other Partile',
        ]

        for planet_index in range(14):
            for remaining_planet in range(planet_index + 1, 14):
                # If options say to skip one or both planets' aspects outside the foreground,
                # just skip calculating anything
                planet_name_1 = PLANET_NAMES[planet_index]
                planet_name_2 = PLANET_NAMES[remaining_planet]

                # 1+ FG, i.e. 1 or more foreground
                if options.get('show_aspects', 0) == 1:
                    if (
                        planet_name_1 not in planets_foreground
                        and planet_name_2 not in planets_foreground
                    ):
                        if not options.get('partile_nf', False):
                            continue

                # 2 FG
                if options.get('show_aspects', 0) == 2:
                    if (
                        planet_name_1 not in planets_foreground
                        or planet_name_2 not in planets_foreground
                    ):
                        if not options.get('partile_nf', False):
                            continue

                (
                    ecliptical_aspect,
                    ecliptical_aspect_class,
                    ecliptical_orb,
                ) = self.find_ecliptical_aspect(
                    chart,
                    planet_index,
                    remaining_planet,
                    ecliptical_orbs,
                    options,
                    planets_foreground,
                    whole_chart_is_dormant,
                )
                (
                    mundane_aspect,
                    mundane_aspect_class,
                    mundane_orb,
                ) = self.find_mundane_aspect(
                    chart,
                    planet_index,
                    remaining_planet,
                    mundane_orbs,
                    options,
                    planets_foreground,
                    whole_chart_is_dormant,
                )

                if ecliptical_aspect and mundane_aspect:
                    if mundane_orb < ecliptical_orb:
                        ecliptical_aspect = ''
                    else:
                        mundane_aspect = ''
                if ecliptical_aspect:
                    aspects_by_class[ecliptical_aspect_class - 1].append(
                        ecliptical_aspect
                    )
                if mundane_aspect:
                    aspects_by_class[mundane_aspect_class - 1].append(
                        mundane_aspect
                    )

        if len(aspects_by_class[3]) == 0 or whole_chart_is_dormant:
            del aspects_by_class[3]
            del aspect_class_headers[3]
            aspects_by_class.append([])
            aspect_class_headers.append('')
        for planet_index in range(2, -1, -1):
            if len(aspects_by_class[planet_index]) == 0:
                del aspects_by_class[planet_index]
                del aspect_class_headers[planet_index]
                aspects_by_class.append([])
                aspect_class_headers.append('')
        if any(aspect_class_headers):
            chartfile.write('-' * self.table_width + '\n')
            for planet_index in range(0, 3):
                chartfile.write(
                    center_align(
                        f'{aspect_class_headers[planet_index]} Aspects'
                        if aspect_class_headers[planet_index]
                        else '',
                        24,
                    )
                )
            chartfile.write('\n')

        # Write aspects from all classes to file
        for planet_index in range(
            max(
                len(aspects_by_class[0]),
                len(aspects_by_class[1]),
                len(aspects_by_class[2]),
            )
        ):
            if planet_index < len(aspects_by_class[0]):
                chartfile.write(
                    left_align(aspects_by_class[0][planet_index], width=24)
                )
            else:
                chartfile.write(' ' * 24)
            if planet_index < len(aspects_by_class[1]):
                chartfile.write(
                    center_align(aspects_by_class[1][planet_index], width=24)
                )
            else:
                chartfile.write(' ' * 24)
            if planet_index < len(aspects_by_class[2]):
                chartfile.write(
                    right_align(aspects_by_class[2][planet_index], width=24)
                )
            else:
                chartfile.write(' ' * 24)
            chartfile.write('\n')

        chartfile.write('-' * self.table_width + '\n')
        if aspects_by_class[3]:
            chartfile.write(
                center_align(
                    f'{aspect_class_headers[3]} Aspects',
                    width=self.table_width,
                )
                + '\n'
            )
            for a in aspects_by_class[3]:
                chartfile.write(center_align(a, self.table_width) + '\n')
            chartfile.write('-' * self.table_width + '\n')

        # Cosmic State
        chartfile.write(center_align('Cosmic State', self.table_width) + '\n')
        moon_sign = SIGNS_SHORT[int(chart['Moon'][0] // 30)]
        sun_sign = SIGNS_SHORT[int(chart['Sun'][0] // 30)]
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
            planet_short_name = PLANET_NAMES_SHORT[planet_index]
            planet_name = PLANET_NAMES[planet_index]
            planet_data = chart[planet_name]
            if planet_short_name != 'Mo':
                chartfile.write('\n')
            chartfile.write(planet_short_name + ' ')
            sign = SIGNS_SHORT[int(planet_data[0] // 30)]
            if sign in POS_SIGN[planet_short_name]:
                plus_minus = '+'
            elif sign in NEG_SIGN[planet_short_name]:
                plus_minus = '-'
            else:
                plus_minus = ' '
            chartfile.write(f'{sign}{plus_minus} ')
            angle = planet_foreground_angles.get(planet_short_name, '')
            if angle.strip() == '':
                angle = ' '
            elif angle.strip() == 'b':
                angle = 'B'
            else:
                angle = 'F'
            chartfile.write(angle + ' |')

            # This has something to do with what row we're on
            cr = False

            if cclass != 'I':
                if planet_short_name != 'Mo':
                    if moon_sign in POS_SIGN[planet_short_name]:
                        chartfile.write(f' Mo {moon_sign}+')
                        cr = True
                    elif moon_sign in NEG_SIGN[planet_short_name]:
                        chartfile.write(f' Mo {moon_sign}-')
                        cr = True
                if planet_short_name != 'Su':
                    if sun_sign in POS_SIGN[planet_short_name]:
                        chartfile.write(f' Su {sun_sign}+')
                        cr = True
                    elif sun_sign in NEG_SIGN[planet_short_name]:
                        chartfile.write(f' Su {sun_sign}-')
                        cr = True
            aspect_list = []
            for index_class in range(3):
                for entry in aspects_by_class[index_class]:
                    if planet_short_name in entry:
                        pct = str(200 - int(entry[15:18]))
                        entry = entry[0:15] + entry[20:]
                        if entry[0:2] == planet_short_name:
                            entry = entry[3:]
                        else:
                            entry = f'{entry[3:5]} {entry[0:2]}{entry[8:]}'
                        aspect_list.append([entry, pct])
            aspect_list.sort(key=lambda p: p[1] + p[0][6:11])
            if aspect_list:
                if cr:
                    chartfile.write('\n' + (' ' * 9) + '| ')
                    cr = False
                else:
                    chartfile.write(' ')
            for remaining_planet, aspect in enumerate(aspect_list):
                chartfile.write(aspect[0] + '   ')
                if (
                    remaining_planet % 4 == 3
                    and remaining_planet != len(aspect_list) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '| ')
            plist = []
            for remaining_planet in range(14):
                if remaining_planet == planet_index:
                    continue
                if remaining_planet == 10 and not options.get('use_Eris', 1):
                    continue
                if remaining_planet == 11 and not options.get('use_Sedna', 0):
                    continue
                if remaining_planet == 12 and options.get('Node', 0) != 1:
                    continue
                if remaining_planet == 13 and options.get('Node', 0) != 2:
                    continue
                plna = PLANET_NAMES[remaining_planet]
                plong = chart[plna][0]
                plab = PLANET_NAMES_SHORT[remaining_planet]
                if (
                    options.get('show_aspects', 0) == 0
                    or plna in planets_foreground
                ):
                    plist.append([plab, plong])
            plist.append(['As', chart['cusps'][1]])
            plist.append(['Mc', chart['cusps'][10]])
            if len(plist) > 1 and (
                options.get('show_aspects', 0) == 0
                or planet_name in planets_foreground
            ):
                # ecliptic midpoints?
                emp = []
                for remaining_planet in range(len(plist) - 1):
                    for k in range(remaining_planet + 1, len(plist)):
                        mp = self.find_midpoint(
                            [planet_short_name, planet_data[0]],
                            plist,
                            remaining_planet,
                            k,
                            options,
                        )
                        if mp:
                            emp.append(mp)
                if emp:
                    emp.sort(key=lambda p: p[6:8])
                    if cr or aspect_list:
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
            if (
                options.get('show_aspects', 0) == 0
                or plna in planets_foreground
            ):
                plist.append([plab, plong, plra, plpvl])
        plist.append(['Mc', chart['cusps'][10]])
        if len(plist) > 1:
            emp = []
            for remaining_planet in range(len(plist) - 1):
                for k in range(remaining_planet + 1, len(plist)):
                    mp = self.find_midpoint(
                        ['As', chart['cusps'][1]],
                        plist,
                        remaining_planet,
                        k,
                        options,
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
        sign = SIGNS_SHORT[int(chart['cusps'][10] // 30)]
        plist[-1] = ['As', chart['cusps'][1]]
        if len(plist) > 1:
            emp = []
            for remaining_planet in range(len(plist) - 1):
                for k in range(remaining_planet + 1, len(plist)):
                    mp = self.find_midpoint(
                        ['Mc', chart['cusps'][10]],
                        plist,
                        remaining_planet,
                        k,
                        options,
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
        del plist[-1]
        if len(plist) > 1:
            emp = []
            ep = [
                'Ep',
                (chart['cusps'][10] + 90) % 360,
                (chart['ramc'] + 90) % 360,
            ]
            ze = ['Ze', (chart['cusps'][1] - 90) % 360]
            for remaining_planet in range(len(plist) - 1):
                for k in range(remaining_planet + 1, len(plist)):
                    mp = self.mmp_all(
                        ep, ze, plist, remaining_planet, k, options
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

    def show(self):
        open_file(self.filename)
