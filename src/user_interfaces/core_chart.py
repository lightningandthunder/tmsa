# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import math
import tkinter.messagebox as tkmessagebox
from datetime import datetime
from io import TextIOWrapper

import src.constants as constants
import src.utils.chart_utils as chart_utils
from src.models.angles import ForegroundAngles, NonForegroundAngles
from src.models.charts import (Aspect, AspectType, ChartObject, ChartWheelRole,
                               PlanetData)
from src.models.options import AngularityModel, Options, ShowAspect
from src.utils.os_utils import open_file


def write_to_file(chart, planet):
    planet_data = chart[planet]
    index = constants.PLANET_NAMES.index(planet)
    short_name = constants.PLANET_NAMES_SHORT[index]

    data_line = short_name + ' ' + chart_utils.zod_min(planet_data[0])
    if index < 14:
        data_line += ' ' + chart_utils.fmt_dm(planet_data[-1] % 30)
    else:
        data_line = chart_utils.center_align(data_line, 16)

    return data_line


# TODO - need to work in chart wheel roles; for now this assumes
#        that this is a uniwheel
class ChartReport:
    table_width = 81

    def __init__(
        self,
        charts: dict[str:ChartObject],
        temporary: bool,
        options: Options,
    ):
        self.charts = charts
        self.options = options

        self.try_precess_to_transit_chart(charts)

        core_chart = (
            charts[ChartWheelRole.TRANSIT]
            if ChartWheelRole.TRANSIT in charts
            else charts[ChartWheelRole.RADIX]
        )

        filename = chart_utils.make_chart_path(core_chart, temporary)
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

    def try_precess_to_transit_chart(self, charts: dict[str:ChartObject]):
        if ChartWheelRole.RADIX in charts and ChartWheelRole.TRANSIT in charts:
            self.charts[ChartWheelRole.RADIX].precess(
                self.charts[ChartWheelRole.TRANSIT]
            )

        if (
            ChartWheelRole.PROGRESSED in charts
            and ChartWheelRole.TRANSIT in charts
        ):
            self.charts[ChartWheelRole.PROGRESSED].precess(
                self.charts[ChartWheelRole.TRANSIT]
            )

    def sort_house(self, chart: ChartObject, index: int):
        house = []
        # TODO - vertex isn't in this list
        for planet_name, planet_info in constants.PLANETS.items():
            if (
                planet_info['number'] > 9
                and planet_info['short_name'] not in self.options.extra_bodies
            ):
                continue

            planet_data = chart.planets[planet_name]
            if planet_data[-1] // 30 == index:
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
        planet_1: PlanetData,
        planet_2: PlanetData,
        ecliptical_orbs: list[float],
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
        chart_is_ingress: bool,
    ):
        if (
            planet_1.short_name not in self.options.extra_bodies
            and planet_2.short_name not in self.options.extra_bodies
        ):
            return ('', 0, 0)

        raw_orb = abs(planet_1.longitude - planet_2.longitude) % 360
        if raw_orb > 180:
            raw_orb = 360 - raw_orb

        for aspect_string in AspectType:
            aspect_degrees = AspectType.degrees_from_abbreviation(
                aspect_string
            )
            test_orb = ecliptical_orbs[str(aspect_degrees)]
            if test_orb[2]:
                maxorb = test_orb[2]
            elif test_orb[1]:
                maxorb = test_orb[1] * 1.25
            elif test_orb[0]:
                maxorb = test_orb[0] * 2.5
            else:
                maxorb = -1
            if (
                raw_orb >= aspect_degrees - maxorb
                and raw_orb <= aspect_degrees + maxorb
            ):
                aspect = (
                    Aspect()
                    .as_ecliptical()
                    .from_planet(planet_1)
                    .to_planet(planet_2)
                    .as_type(AspectType.from_string(aspect_string))
                )
                if maxorb <= 0:
                    return ('', 0, 0)
                raw_orb = abs(raw_orb - aspect_degrees)
                if raw_orb <= test_orb[0]:
                    aspect = aspect.with_class(1)
                elif raw_orb <= test_orb[1]:
                    aspect = aspect.with_class(2)
                elif raw_orb <= test_orb[2]:
                    aspect = aspect.with_class(3)
                else:
                    return ('', 0, 0)

                if planet_1.name == 'Moon' and chart_is_ingress:
                    break
                if chart_is_ingress and whole_chart_is_dormant:
                    return ('', 0, 0)

                if self.options.show_aspects == ShowAspect.ONE_PLUS_FOREGROUND:
                    if (
                        planet_1.name not in foreground_planets
                        and not planet_1.treat_as_foreground
                    ) and (
                        planet_2.name not in foreground_planets
                        and not planet_2.treat_as_foreground
                    ):
                        if raw_orb <= 1 and self.options.partile_nf:
                            aspect = aspect.with_class(4)
                        else:
                            return ('', 0, 0)
                elif self.options.show_aspects == ShowAspect.BOTH_FOREGROUND:
                    if (
                        planet_1.name not in foreground_planets
                        and not planet_1.treat_as_foreground
                    ) or (
                        planet_2.name not in foreground_planets
                        and not planet_2.treat_as_foreground
                    ):
                        if raw_orb <= 1 and self.options.partile_nf:
                            aspect = aspect.with_class(4)
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)

        strength = 60 / maxorb
        strength_percent = math.cos(math.radians(raw_orb * strength))
        strength_percent = round((strength_percent - 0.5) * 200)
        strength_percent = f'{strength_percent:3d}'
        aspect = aspect.with_strength(strength_percent).with_orb(
            chart_utils.fmt_dm(abs(raw_orb), True)
        )
        return (
            str(aspect),
            aspect.aspect_class,
            raw_orb,
        )

    def find_mundane_aspect(
        self,
        planet_1: PlanetData,
        planet_2: PlanetData,
        mundane_orbs: list[float],
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
        chart_is_ingress: bool,
    ):
        if (
            planet_1.short_name not in self.options.extra_bodies
            and planet_2.short_name not in self.options.extra_bodies
        ):
            return ('', 0, 0)

        raw_orb = abs(planet_1.house - planet_2.house) % 360
        if raw_orb > 180:
            raw_orb = 360 - raw_orb
        allowed_mundane_aspects = [0, 180, 90, 45, 135]

        for aspect_string in AspectType:
            aspect_degrees = AspectType.degrees_from_abbreviation(
                aspect_string
            )
            if aspect_degrees not in allowed_mundane_aspects:
                continue

            test_orb = mundane_orbs[str(aspect_degrees)]
            if test_orb[2]:
                maxorb = test_orb[2]
            elif test_orb[1]:
                maxorb = test_orb[1] * 1.25
            elif test_orb[0]:
                maxorb = test_orb[0] * 2.5
            else:
                maxorb = -1
            if (
                raw_orb >= aspect_degrees - maxorb
                and raw_orb <= aspect_degrees + maxorb
            ):
                aspect = (
                    Aspect()
                    .as_mundane()
                    .from_planet(planet_1)
                    .to_planet(planet_2)
                    .as_type(AspectType.from_string(aspect_string))
                )

                if maxorb <= 0:
                    return ('', 0, 0)

                raw_orb = abs(raw_orb - aspect_degrees)
                if raw_orb <= test_orb[0]:
                    aspect = aspect.with_class(1)
                elif raw_orb <= test_orb[1]:
                    aspect = aspect.with_class(2)
                elif raw_orb <= test_orb[2]:
                    aspect = aspect.with_class(3)
                else:
                    return ('', 0, 0)

                if planet_1.name == 'Moon' and chart_is_ingress:
                    break
                if chart_is_ingress and whole_chart_is_dormant:
                    return ('', 0, 0)

                if self.show_aspects == ShowAspect.ONE_PLUS_FOREGROUND:
                    if (
                        planet_1.name not in foreground_planets
                        and not planet_1.treat_as_foreground
                    ) and (
                        planet_2.name not in foreground_planets
                        and not planet_2.treat_as_foreground
                    ):
                        if raw_orb <= 1 and self.options.partile_nf:
                            aspect = aspect.with_class(4)
                        else:
                            return ('', 0, 0)
                elif self.options.show_aspects == ShowAspect.BOTH_FOREGROUND:
                    if (
                        planet_1.name not in foreground_planets
                        and not planet_1.treat_as_foreground
                    ) or (
                        planet_2.name not in foreground_planets
                        and not planet_2.treat_as_foreground
                    ):
                        if raw_orb <= 1 and self.options.partile_nf:
                            aspect = aspect.with_class(4)
                        else:
                            return ('', 0, 0)
                break
        else:
            return ('', 0, 0)

        strength = 60 / maxorb
        strength_percent = math.cos(math.radians(raw_orb * strength))
        strength_percent = round((strength_percent - 0.5) * 200)
        strength_percent = f'{strength_percent:3d}'
        aspect = aspect.with_strength(strength_percent).with_orb(
            chart_utils.fmt_dm(abs(raw_orb), True)
        )
        return (
            str(aspect),
            aspect.aspect_class,
            raw_orb,
        )

    def find_pvp_aspect(self, chart: ChartObject, planet_index: int):
        # I need to ask Jim more about this, but...
        # Find conjunct/opp in azimuth across horizon - these are conj/opp.
        # Find azimuth squares to planets near meridian (90* of azimuth) - squares.
        # That is still measured in azimuth.
        # Find ML squares of one planet on horizon and one on PV measured in ML;
        # what that actually means is planet co horizon in PVL
        # plus planet co Vx/Av in azimuth...? Those should be affected by
        # "class 3 orbs for minor angles," which i'll need to default down to
        # class 2 and class 1 if any are absent
        return ('', 0, 0)

    def calc_angle_and_strength(
        self,
        planet: PlanetData,
        chart: ChartObject,
    ) -> tuple[str, float, bool, bool]:
        # I should be able to rewrite this mostly using self. variables

        angularity_options = self.options.angularity

        major_angle_orbs = angularity_options.major_angles
        minor_angle_orbs = angularity_options.minor_angles

        for orb_class in range(3):
            if major_angle_orbs[orb_class] == 0:
                major_angle_orbs[orb_class] = -3
            if minor_angle_orbs[orb_class] == 0:
                minor_angle_orbs[orb_class] = -3

        house_quadrant_position = planet.house % 90
        if angularity_options.model == AngularityModel.MIDQUADRANT:
            mundane_angularity_strength = (
                chart_utils.major_angularity_curve_midquadrant_background(
                    house_quadrant_position
                )
            )
        elif angularity_options.model == AngularityModel.CLASSIC_CADENT:
            mundane_angularity_strength = (
                chart_utils.major_angularity_curve_cadent_background(
                    house_quadrant_position
                )
            )
        else:   # model == eureka
            mundane_angularity_strength = (
                chart_utils.major_angularity_curve_eureka_formula(
                    house_quadrant_position
                )
            )

        aspect_to_asc = abs(chart.cusps[1] - planet.longitude)
        if aspect_to_asc > 180:
            aspect_to_asc = 360 - aspect_to_asc
        if chart_utils.inrange(aspect_to_asc, 90, 3):
            square_asc_strength = chart_utils.minor_angularity_curve(
                abs(aspect_to_asc - 90)
            )
        else:
            square_asc_strength = -2

        aspect_to_mc = abs(chart.cusps[10] - planet.longitude)
        if aspect_to_mc > 180:
            aspect_to_mc = 360 - aspect_to_mc
        if chart_utils.inrange(aspect_to_mc, 90, 3):
            square_mc_strength = chart_utils.minor_angularity_curve(
                abs(aspect_to_mc - 90)
            )
        else:
            square_mc_strength = -2

        ramc_aspect = abs(chart.ramc - planet.right_ascension)
        if ramc_aspect > 180:
            ramc_aspect = 360 - ramc_aspect
        if chart_utils.inrange(ramc_aspect, 90, 3):
            ramc_square_strength = chart_utils.minor_angularity_curve(
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

        is_mundanely_background = False
        is_foreground = False

        mundane_angularity_orb = (
            90 - house_quadrant_position
            if house_quadrant_position > 45
            else house_quadrant_position
        )

        if mundane_angularity_orb <= max(major_angle_orbs):
            is_foreground = True

        else:
            if mundane_angularity_strength <= 25:
                if not angularity_options.no_bg:
                    is_mundanely_background = True

        zenith_nadir_orb = abs(aspect_to_asc - 90)
        if zenith_nadir_orb <= max(minor_angle_orbs):
            is_foreground = True

        ep_wp_eclipto_orb = abs(aspect_to_mc - 90)
        if ep_wp_eclipto_orb <= max(minor_angle_orbs):
            is_foreground = True

        ep_wp_ascension_orb = abs(ramc_aspect - 90)
        if ep_wp_ascension_orb <= max(minor_angle_orbs):
            is_foreground = True

        angularity_orb = -1
        angularity = NonForegroundAngles.BLANK

        # if foreground, get specific angle - we can probably do this all at once
        if is_foreground:
            # Foreground in prime vertical longitude
            if angularity_strength == mundane_angularity_strength:
                if planet.house >= 345:
                    angularity_orb = 360 - planet.house
                    angularity = ForegroundAngles.ASCENDANT
                elif planet.house <= 15:
                    angularity_orb = planet.house
                    angularity = ForegroundAngles.ASCENDANT
                elif chart_utils.inrange(planet.house, 90, 15):
                    angularity_orb = abs(planet.house - 90)
                    angularity = ForegroundAngles.IC
                elif chart_utils.inrange(planet.house, 180, 15):
                    angularity_orb = abs(planet.house - 180)
                    angularity = ForegroundAngles.DESCENDANT
                elif chart_utils.inrange(planet.house, 270, 15):
                    angularity_orb = abs(planet.house - 270)
                    angularity = ForegroundAngles.MC

            # Foreground on Zenith/Nadir
            if angularity_strength == square_asc_strength:
                zenith_nadir_orb = chart.cusps[1] - planet.longitude
                if zenith_nadir_orb < 0:
                    zenith_nadir_orb += 360

                if chart_utils.inrange(zenith_nadir_orb, 90, 5):
                    angularity_orb = abs(zenith_nadir_orb - 90)
                    angularity = ForegroundAngles.ZENITH
                elif chart_utils.inrange(zenith_nadir_orb, 270, 5):
                    angularity_orb = abs(zenith_nadir_orb - 270)
                    angularity = ForegroundAngles.NADIR

            # Foreground on Eastpoint/Westpoint
            if angularity_strength == square_mc_strength:
                ep_wp_eclipto_orb = chart.cusps[10] - planet.longitude
                if ep_wp_eclipto_orb < 0:
                    ep_wp_eclipto_orb += 360
                if chart_utils.inrange(ep_wp_eclipto_orb, 90, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 90)
                    angularity = ForegroundAngles.WESTPOINT
                if chart_utils.inrange(ep_wp_eclipto_orb, 270, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 270)
                    angularity = ForegroundAngles.EASTPOINT

            if angularity_strength == ramc_square_strength:
                ep_wp_ascension_orb = chart['ramc'] - planet.right_ascension
                if ep_wp_ascension_orb < 0:
                    ep_wp_ascension_orb += 360
                if chart_utils.inrange(ep_wp_ascension_orb, 90, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 90)
                    angularity = ForegroundAngles.WESTPOINT_RA
                if chart_utils.inrange(ep_wp_ascension_orb, 270, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 270)
                    angularity = ForegroundAngles.EASTPOINT_RA

        if angularity.strip() == '' and is_mundanely_background:
            angularity = NonForegroundAngles.BACKGROUND

        # TODO - not sure how to handle this
        if 'I' not in self.cclass:
            # It's not an ingress; dormancy is always negated
            planet_negates_dormancy = True
        else:
            planet_negates_dormancy = chart_utils.angularity_activates_ingress(
                angularity_orb, str(angularity)
            )

        return (
            angularity,
            angularity_strength,
            planet_negates_dormancy,
            is_mundanely_background,
        )

    def draw_chart(
        self,
        chart: ChartObject,
        chartfile: TextIOWrapper,
    ):
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

        # TODO - I don't really understand the difference between these two
        self.cclass = chart.type
        if not self.cclass:
            self.cclass = chart_utils.get_return_class(chart['type'])

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
        cusps = [chart_utils.zod_min(c) for c in chart['cusps']]
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

        if chart['type'] not in constants.INGRESSES:
            name = chart['name']
            if ';' in name:
                name = name.split(';')[0]
            chart_grid[21][18:51] = chart_utils.center_align(name)
        chtype = chart['type']
        if chtype.endswith(' Single Wheel'):
            chtype = chtype.replace(' Single Wheel', '')
        chart_grid[23][18:51] = chart_utils.center_align(chtype)
        line = (
            str(chart['day'])
            + ' '
            + constants.MONTHS[chart['month'] - 1]
            + ' '
        )
        line += (
            f'{chart.year} ' if chart.year > 0 else f'{-chart.year + 1} BCE '
        )
        if not chart['style']:
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
            chart['notes'] or '* * * * *'
        )

        x = [1, 1, 18, 35, 52, 52, 52, 52, 35, 18, 1, 1]
        y = [33, 49, 49, 49, 49, 33, 17, 1, 1, 1, 1, 17]
        houses = [[] for _ in range(12)]
        for index in range(12):
            houses[index] = self.sort_house(chart, index)
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

    def write_info_table(
        self,
        chart: ChartObject,
        chartfile: TextIOWrapper,
    ):
        chartfile.write(
            'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
        )
        angularity_options = self.options.angularity
        planets_foreground = []
        planet_foreground_angles = {}

        # TODO - I don't understand this
        # Default to true if this is an ingress chart
        whole_chart_is_dormant = True if 'I' in self.cclass else False

        for planet_name, _ in chart_utils.iterate_allowed_planets(
            self.options
        ):
            planet_data = chart.planets[planet_name]

            # TODO - I need to figure out what's up with this index business
            planet_index = constants.PLANET_NAMES.index(planet_name)
            chartfile.write(chart_utils.left_align(planet_data.short_name, 3))

            # Write planet data to info table
            # TODO - I feel like I can add all of these trailing spaces to the functions
            chartfile.write(chart_utils.zod_sec(planet_data.longitude) + ' ')
            chartfile.write(
                chart_utils.fmt_lat(planet_data.latitude, True) + ' '
            )
            if abs(planet_data[2]) >= 1:
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

            if not angularity == NonForegroundAngles.BLANK:
                planets_foreground.append(planet_name)

            elif planet_name == 'Moon' and 'I' in self.cclass:
                planet_data.treat_as_foreground = True

            if is_mundanely_background:
                planet_foreground_angles[
                    planet_data.short_name
                ] = NonForegroundAngles.BACKGROUND

            # Conjunctions to Vertex/Antivertex
            minor_limit = angularity_options.get(
                'minor_angles', [1.0, 2.0, 3.0]
            )

            if (
                angularity == NonForegroundAngles.BLANK
                or is_mundanely_background
            ):
                if chart_utils.inrange(planet_data[5], 270, minor_limit[2]):
                    angularity = NonForegroundAngles.VERTEX
                elif chart_utils.inrange(planet_data[5], 90, minor_limit[2]):
                    angularity = NonForegroundAngles.ANTIVERTEX

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
            self.options.ecliptic_aspects or constants.DEFAULT_ECLIPTICAL_ORBS
        )

        mundane_orbs = (
            self.options.mundane_aspects or constants.DEFAULT_MUNDANE_ORBS
        )
        aspects_by_class = [[], [], [], []]
        aspect_class_headers = [
            'Class 1',
            'Class 2',
            'Class 3',
            'Other Partile',
        ]

        for primary_index, primary_planet in enumerate(
            constants.PLANETS.values()
        ):
            for secondary_index, secondary_planet in enumerate(
                constants.PLANETS.values()
            ):
                if secondary_index <= primary_index:
                    continue

                # If options say to skip one or both planets' aspects outside the foreground,
                # just skip calculating anything

                show_aspects = self.options.show_aspects or ShowAspect.ALL

                if show_aspects == ShowAspect.ONE_PLUS_FOREGROUND:
                    if (
                        primary_planet['long_name'] not in planets_foreground
                        and secondary_planet['long_name']
                        not in planets_foreground
                    ):
                        if not self.options.partile_nf:
                            continue

                if show_aspects == ShowAspect.BOTH_FOREGROUND:
                    if (
                        primary_planet['long_name'] not in planets_foreground
                        or secondary_planet['long_name']
                        not in planets_foreground
                    ):
                        if not self.options.partile_nf:
                            continue

                (
                    ecliptical_aspect,
                    ecliptical_aspect_class,
                    ecliptical_orb,
                ) = self.find_ecliptical_aspect(
                    chart,
                    planet_index,
                    secondary_index,
                    ecliptical_orbs,
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
                    secondary_index,
                    mundane_orbs,
                    planets_foreground,
                    whole_chart_is_dormant,
                )

                (pvp_aspect, pvp_aspect_class, pvp_orb) = self.find_pvp_aspect(
                    chart,
                    planet_index,
                    secondary_index,
                )

                tightest_orb = [
                    (ecliptical_orb, ecliptical_aspect),
                    (mundane_orb, mundane_aspect),
                    (pvp_orb, pvp_aspect),
                ].sort(key=lambda x: x[0])[0]
                if tightest_orb[0] == ecliptical_orb:
                    aspects_by_class[ecliptical_aspect_class - 1].append(
                        ecliptical_aspect
                    )
                elif tightest_orb[0] == mundane_orb:
                    aspects_by_class[mundane_aspect_class - 1].append(
                        mundane_aspect
                    )
                else:  # pvp orb
                    aspects_by_class[pvp_aspect_class - 1].append(pvp_aspect)

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
                        aspects_by_class[0][aspect_index], width=24
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class[1]):
                chartfile.write(
                    chart_utils.center_align(
                        aspects_by_class[1][aspect_index], width=24
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class[2]):
                chartfile.write(
                    chart_utils.right_align(
                        aspects_by_class[2][aspect_index], width=24
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
                    chart_utils.center_align(aspect, self.table_width) + '\n'
                )
            chartfile.write('-' * self.table_width + '\n')

    def write_cosmic_state(
        self,
        chartfile: TextIOWrapper,
        chart: ChartObject,
        planet_foreground_angles: dict[str, str],
        aspects_by_class: list[list[str]],
        planets_foreground: list[str],
    ):
        chartfile.write(
            chart_utils.center_align('Cosmic State', self.table_width) + '\n'
        )
        moon_sign = constants.SIGNS_SHORT[
            int(chart.planets['Moon'].longitude // 30)
        ]
        sun_sign = constants.SIGNS_SHORT[
            int(chart.planets['Sun'].longitude // 30)
        ]
        cclass = chart['class']

        for index, (planet_name, planet_info) in enumerate(
            constants.PLANETS.items()
        ):
            if (
                planet_info['number'] > 9
                and planet_info['short_name'] not in self.options.extra_bodies
            ):
                continue

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
                planet_short_name, NonForegroundAngles.BLANK
            )
            if angle.strip() == '':
                angle = ' '
            elif angle.strip() in [a.value.strip() for a in ForegroundAngles]:
                angle = 'F'
            else:
                angle = 'B'
            chartfile.write(angle + ' |')

            need_another_row = False

            if cclass != 'I':
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
            # TODO - I'd like to split this out
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

            plist = []
            for index, (planet_name, planet_info) in enumerate(
                chart_utils.iterate_allowed_planets(self.options)
            ):
                planet_longitude = chart.planets[planet_name].longitude
                planet_short_name = planet_info['short_name']
                if (
                    (self.options.show_aspects or ShowAspect.ALL)
                    == ShowAspect.ALL
                    or planet_short_name in planets_foreground
                ):
                    plist.append([planet_short_name, planet_longitude])

            # Left off here

            plist.append(['As', chart['cusps'][1]])
            plist.append(['Mc', chart['cusps'][10]])
            if len(plist) > 1 and (
                (self.options.show_aspects or ShowAspect.ALL) == ShowAspect.ALL
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

        sign = constants.SIGNS_SHORT[int(chart['cusps'][1] // 30)]
        plist = []
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
            plra = chart[plna][3]
            plpvl = chart[plna][7]
            planet_short_name = constants.PLANET_NAMES_SHORT[planet_index]
            if (
                self.options.get('show_aspects', 0) == 0
                or plna in planets_foreground
            ):
                plist.append(
                    [planet_short_name, planet_longitude, plra, plpvl]
                )
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
        sign = constants.SIGNS_SHORT[int(chart['cusps'][10] // 30)]
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
                        ep, ze, plist, remaining_planet, k, self.options
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
