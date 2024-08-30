# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
import bisect
import copy
from io import TextIOWrapper

import src.models.angles as angles_models
import src.models.charts as chart_models
import src.models.options as option_models
import src.constants as constants
import src.utils.chart_utils as chart_utils
from src.utils.format_utils import to360
from src.utils.os_utils import open_file
import tkinter.messagebox as tkmessagebox
from datetime import datetime


class CoreChart(object, metaclass=ABCMeta):
    table_width: int = 81
    rows = 69
    columns = 69
    filename: str = ''
    options: option_models.Options
    charts: list[chart_models.ChartObject]
    halfsums: list[chart_models.HalfSum]
    temporary: bool

    def __init__(
        self,
        charts: list[chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        self.options = options

        self.charts = sorted(charts, key=lambda x: x.role, reverse=True)
        self.temporary = temporary

        # For now, only enable natal midpoints
        if (
            len(charts) == 1
            and charts[0].type == chart_models.ChartType.NATAL
            # and self.options.enable_natal_midpoints
        ):
            self.halfsums = self.calc_halfsums()

        for chart in self.charts:
            for (
                planet_name,
                _,
            ) in chart.iterate_points(self.options):
                chart.planets[planet_name].role = chart.role

                if planet_name == 'Moon' and (
                    chart.type.value in chart_utils.INGRESSES
                    or chart.type.value
                    in chart_utils.RETURNS_WHERE_MOON_ALWAYS_FOREGROUND
                ):
                    chart.planets[planet_name].treat_as_foreground = True

        self.try_precess_charts()

        self.filename = chart_utils.make_chart_path(
            self.find_outermost_chart(), temporary
        )
        self.filename = self.filename[0:-3] + 'txt'
        try:
            chartfile = open(self.filename, 'w')
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

    def insert_planet_into_line(
        self,
        chart,
        planet_long_name: str,
        prefix: str = '',
        abbreviation_only: bool = False,
        width: int = None,
    ) -> str:
        planet_data = chart.planets[planet_long_name]
        short_name = constants.PLANETS[planet_long_name]['short_name']

        if abbreviation_only:
            return prefix + short_name

        data_line = (
            prefix
            + short_name
            + ' '
            + chart_utils.zod_min(planet_data.longitude)
        )

        data_line += ' ' + chart_utils.fmt_dm(planet_data.house % 30)

        if width:
            data_line = data_line[0:width]

        return data_line

    def sort_house(self, charts: list[chart_models.ChartObject], index: int):
        house = []
        for chart in charts:
            for (
                planet_name,
                planet_data,
            ) in chart.iterate_points(self.options):

                planet_data = chart.planets[planet_name]
                if planet_data.house // 30 == index:
                    pos = (planet_data.house % 30) / 2
                    house.append(
                        [planet_name, planet_data.house, pos, chart.role.value]
                    )
            house.sort(key=lambda h: h[1])

        return self.spread_planets_within_house(house, 0)

    def spread_planets_within_house(
        self,
        house_info,
        start=0,
    ):
        new = [[] for _ in range(15)]
        placed = 0
        for i in range(len(house_info)):
            zero_indexed_house = int(house_info[i][-2]) + start
            limit = 15 - len(house_info) + placed
            if zero_indexed_house > limit:
                zero_indexed_house = limit
            while True:
                if len(new[zero_indexed_house]):
                    zero_indexed_house += 1
                else:
                    break
            new[zero_indexed_house] = house_info[i]
            placed += 1
        return new

    def try_precess_charts(self):
        if len(self.charts) == 1:
            return

        radix = None
        for chart in self.charts:
            if chart.role == chart_models.ChartWheelRole.RADIX:
                radix = chart
                break

        transit = None
        for chart in self.charts:
            if chart.role == chart_models.ChartWheelRole.TRANSIT:
                transit = chart
                break

        progressed = None
        for chart in self.charts:
            if chart.role == chart_models.ChartWheelRole.PROGRESSED:
                progressed = chart
                break

        if transit:
            if radix:
                radix.precess_to(transit)

            if progressed:
                progressed.precess_to(transit)
        else:
            if radix and progressed:
                radix.precess_to(progressed)

    def find_ecliptical_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_2: chart_models.PlanetData,
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect:
        return self.__find_non_pvp_aspect(
            planet_1,
            planet_2,
            whole_chart_is_dormant,
            chart_models.AspectFramework.ECLIPTICAL,
        )

    def find_mundane_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_2: chart_models.PlanetData,
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect:
        return self.__find_non_pvp_aspect(
            planet_1,
            planet_2,
            whole_chart_is_dormant,
            chart_models.AspectFramework.MUNDANE,
        )

    def __find_non_pvp_aspect(
        self,
        primary_planet: chart_models.PlanetData,
        secondary_planet: chart_models.PlanetData,
        whole_chart_is_dormant: bool,
        aspect_framework: chart_models.AspectFramework,
    ) -> chart_models.Aspect:
        # If options say to skip one or both planets' aspects outside the foreground,
        # just skip calculating anything
        show_aspects = (
            self.options.show_aspects or option_models.ShowAspect.ALL
        )

        aspect_is_not_foreground = False

        if show_aspects == option_models.ShowAspect.ONE_PLUS_FOREGROUND:
            if (
                not primary_planet.is_foreground
                and not primary_planet.treat_as_foreground
                and not secondary_planet.is_foreground
                and not secondary_planet.treat_as_foreground
            ):
                if not self.options.partile_nf:
                    return None
                else:
                    aspect_is_not_foreground = True

        elif show_aspects == option_models.ShowAspect.BOTH_FOREGROUND:
            if (
                not primary_planet.is_foreground
                and not primary_planet.treat_as_foreground
            ) or (
                not secondary_planet.is_foreground
                and not secondary_planet.treat_as_foreground
            ):
                if not self.options.partile_nf:
                    return None
                else:
                    aspect_is_not_foreground = True

        raw_orb = None
        aspect = None

        if whole_chart_is_dormant:
            if primary_planet.name != 'Moon':
                return None

        if aspect_framework == chart_models.AspectFramework.ECLIPTICAL:
            raw_orb = (
                abs(primary_planet.longitude - secondary_planet.longitude)
                % 360
            )
        elif aspect_framework == chart_models.AspectFramework.MUNDANE:
            raw_orb = abs(primary_planet.house - secondary_planet.house) % 360

        if raw_orb > 180:
            raw_orb = 360 - raw_orb

        ecliptic_orbs = (
            self.options.ecliptic_aspects
            or chart_utils.DEFAULT_ECLIPTICAL_ORBS
        )
        mundane_orbs = (
            self.options.mundane_aspects or chart_utils.DEFAULT_MUNDANE_ORBS
        )

        for (aspect_type, aspect_degrees) in chart_models.AspectType.iterate():
            test_orbs = None

            # If the aspect is a sesquisquare, we need to use the orb for semisquare,
            # as it's the only orb in options
            aspect_degrees_for_options = (
                45 if aspect_degrees == 135 else aspect_degrees
            )

            if aspect_framework == chart_models.AspectFramework.ECLIPTICAL:
                if str(aspect_degrees_for_options) in ecliptic_orbs:
                    test_orbs = ecliptic_orbs[str(aspect_degrees_for_options)]
                else:
                    continue
            elif aspect_framework == chart_models.AspectFramework.MUNDANE:
                if str(aspect_degrees_for_options) in mundane_orbs:
                    test_orbs = mundane_orbs[str(aspect_degrees_for_options)]
                else:
                    continue

            if test_orbs[2]:
                maxorb = test_orbs[2]
            elif test_orbs[1]:
                maxorb = test_orbs[1] * 1.25
            elif test_orbs[0]:
                maxorb = test_orbs[0] * 2.5
            else:
                continue

            if not (
                raw_orb >= aspect_degrees - maxorb
                and raw_orb <= aspect_degrees + maxorb
            ):
                continue

            greater_planet = (
                primary_planet
                if primary_planet.role >= secondary_planet.role
                else secondary_planet
            )
            lesser_planet = (
                primary_planet
                if greater_planet == secondary_planet
                else secondary_planet
            )

            aspect = (
                chart_models.Aspect()
                .from_planet(
                    greater_planet.short_name, role=greater_planet.role
                )
                .to_planet(lesser_planet.short_name, role=lesser_planet.role)
                .as_type(aspect_type)
            )
            aspect.framework = aspect_framework
            aspect_orb = abs(raw_orb - aspect_degrees)

            if aspect_orb <= test_orbs[0]:
                aspect = aspect.with_class(1)
            elif aspect_orb <= test_orbs[1]:
                aspect = aspect.with_class(2)
            elif aspect_orb <= test_orbs[2]:
                aspect = aspect.with_class(3)
            else:
                aspect = None
                continue

            if primary_planet.name == 'Moon' and (
                primary_planet.role == chart_utils.INGRESSES
                or primary_planet.role == chart_utils.SOLUNAR_RETURNS
            ):
                # Always consider transiting Moon aspects, as long as they're in orb
                break

            # Otherwise, make sure the aspect should be considered at all

            show_aspects = (
                option_models.ShowAspect.from_number(self.options.show_aspects)
                or self.options.show_aspects
            )

            if (
                show_aspects == option_models.ShowAspect.ONE_PLUS_FOREGROUND
                or show_aspects == option_models.ShowAspect.BOTH_FOREGROUND
            ):
                if aspect_is_not_foreground:
                    if aspect_orb <= 1 and self.options.partile_nf:
                        aspect = aspect.with_class(4)
                    else:
                        # We may have found an aspect, but it's neither foreground nor partile
                        aspect = None

            # We have found a valid aspect (or run out of aspects to try)
            break

        if not aspect:
            return None

        aspect_strength = chart_utils.calc_aspect_strength_percent(
            maxorb, aspect_orb
        )
        aspect = aspect.with_strength(aspect_strength).with_orb(aspect_orb)

        return aspect

    def find_pvp_aspect(
        self,
        primary_planet: chart_models.PlanetData,
        secondary_planet: chart_models.PlanetData,
    ):
        # At least one planet must be on the prime vertical
        if (
            not primary_planet.is_on_prime_vertical
            and not secondary_planet.is_on_prime_vertical
        ):
            return None

        # default to square; conjunction and opposition only possible if both
        # planets are on the prime vertical
        aspect_type = chart_models.AspectType.SQUARE

        greater_planet = (
            primary_planet
            if primary_planet.role >= secondary_planet.role
            else secondary_planet
        )
        lesser_planet = (
            primary_planet
            if greater_planet == secondary_planet
            else secondary_planet
        )

        if (
            primary_planet.is_on_prime_vertical
            and secondary_planet.is_on_prime_vertical
        ):
            # check prime vertical to prime vertical in azimuth
            raw_orb = abs(primary_planet.azimuth - secondary_planet.azimuth)

            conjunction_orb = (
                self.options.pvp_aspects['0'][0]
                if self.options.pvp_aspects
                else 3
            )
            opposition_orb = (
                self.options.pvp_aspects['180'][0]
                if self.options.pvp_aspects
                else 3
            )
            if chart_utils.inrange(raw_orb, 0, conjunction_orb):
                aspect_type = chart_models.AspectType.CONJUNCTION
                raw_orb = conjunction_orb
            elif chart_utils.inrange(raw_orb, 180, opposition_orb):
                aspect_type = chart_models.AspectType.OPPOSITION
                raw_orb = opposition_orb

        planet_on_prime_vertical = (
            primary_planet
            if primary_planet.is_on_prime_vertical
            else secondary_planet
        )
        planet_on_other_axis = (
            primary_planet
            if secondary_planet.is_on_prime_vertical
            else secondary_planet
        )

        planet_is_on_meridian = (
            planet_on_other_axis.angle.value
            == angles_models.ForegroundAngles.MC.value
            or planet_on_other_axis.angle.value
            == angles_models.ForegroundAngles.IC.value
        )
        planet_is_on_horizon = (
            planet_on_other_axis.angle.value
            == angles_models.ForegroundAngles.ASCENDANT.value
            or planet_on_other_axis.angle.value
            == angles_models.ForegroundAngles.DESCENDANT.value
        )

        if not planet_is_on_meridian and not planet_is_on_horizon:
            return None

        square_orb = (
            self.options.pvp_aspects['90'][0]
            if self.options.pvp_aspects
            else 3
        )

        if planet_is_on_meridian:
            raw_orb = abs(
                planet_on_other_axis.azimuth - planet_on_prime_vertical.azimuth
            )

        elif planet_is_on_horizon:
            raw_orb = abs(
                planet_on_other_axis.meridian_longitude
                - planet_on_prime_vertical.meridian_longitude
            )

        normalized_orb = None
        if aspect_type == chart_models.AspectType.CONJUNCTION:
            normalized_orb = raw_orb
        elif aspect_type == chart_models.AspectType.OPPOSITION:
            normalized_orb = abs(180 - raw_orb)
        elif aspect_type == chart_models.AspectType.SQUARE:
            if chart_utils.inrange(raw_orb, 0, square_orb):
                normalized_orb = raw_orb
            if chart_utils.inrange(raw_orb, 90, square_orb):
                normalized_orb = abs(90 - raw_orb)
            if chart_utils.inrange(raw_orb, 180, square_orb):
                normalized_orb = abs(180 - raw_orb)
            if chart_utils.inrange(raw_orb, 360, square_orb):
                normalized_orb = abs(360 - raw_orb)

        if not normalized_orb:
            return None

        aspect = (
            chart_models.Aspect()
            .as_prime_vertical_paran()
            .from_planet(
                greater_planet.short_name,
                role=greater_planet.role,
            )
            .to_planet(
                lesser_planet.short_name,
                role=lesser_planet.role,
            )
            .as_type(aspect_type)
            .with_class(1)
        )
        aspect_strength = chart_utils.calc_aspect_strength_percent(
            square_orb, normalized_orb
        )
        aspect = aspect.with_strength(aspect_strength).with_orb(normalized_orb)
        return aspect

    def calc_angle_and_strength(
        self,
        planet: chart_models.PlanetData,
    ) -> tuple[angles_models.ForegroundAngles, float, bool, bool]:
        # I should be able to rewrite this mostly using self. variables

        chart = self.find_outermost_chart()

        angularity_options = self.options.angularity

        major_angle_orbs = angularity_options.major_angles
        minor_angle_orbs = angularity_options.minor_angles

        for orb_class in range(3):
            if major_angle_orbs[orb_class] == 0:
                major_angle_orbs[orb_class] = -3
            if minor_angle_orbs[orb_class] == 0:
                minor_angle_orbs[orb_class] = -3

        house_quadrant_position = planet.house % 90
        if (
            angularity_options.model
            == option_models.AngularityModel.MIDQUADRANT
        ):
            mundane_angularity_strength = (
                chart_utils.major_angularity_curve_midquadrant_background(
                    house_quadrant_position
                )
            )
        elif (
            angularity_options.model
            == option_models.AngularityModel.CLASSIC_CADENT
        ):
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
        angularity = angles_models.NonForegroundAngles.BLANK

        # if foreground, get specific angle - we can probably do this all at once
        if is_foreground:
            # Foreground in prime vertical longitude
            if angularity_strength == mundane_angularity_strength:
                if planet.house >= 345:
                    angularity_orb = 360 - planet.house
                    angularity = angles_models.ForegroundAngles.ASCENDANT
                elif planet.house <= 15:
                    angularity_orb = planet.house
                    angularity = angles_models.ForegroundAngles.ASCENDANT
                elif chart_utils.inrange(planet.house, 90, 15):
                    angularity_orb = abs(planet.house - 90)
                    angularity = angles_models.ForegroundAngles.IC
                elif chart_utils.inrange(planet.house, 180, 15):
                    angularity_orb = abs(planet.house - 180)
                    angularity = angles_models.ForegroundAngles.DESCENDANT
                elif chart_utils.inrange(planet.house, 270, 15):
                    angularity_orb = abs(planet.house - 270)
                    angularity = angles_models.ForegroundAngles.MC

            # Foreground on Zenith/Nadir
            if angularity_strength == square_asc_strength:
                zenith_nadir_orb = chart.cusps[1] - planet.longitude
                if zenith_nadir_orb < 0:
                    zenith_nadir_orb += 360

                if chart_utils.inrange(zenith_nadir_orb, 90, 5):
                    angularity_orb = abs(zenith_nadir_orb - 90)
                    angularity = angles_models.ForegroundAngles.ZENITH
                elif chart_utils.inrange(zenith_nadir_orb, 270, 5):
                    angularity_orb = abs(zenith_nadir_orb - 270)
                    angularity = angles_models.ForegroundAngles.NADIR

            # Foreground on Eastpoint/Westpoint
            if angularity_strength == square_mc_strength:
                ep_wp_eclipto_orb = chart.cusps[10] - planet.longitude
                if ep_wp_eclipto_orb < 0:
                    ep_wp_eclipto_orb += 360
                if chart_utils.inrange(ep_wp_eclipto_orb, 90, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 90)
                    angularity = angles_models.ForegroundAngles.WESTPOINT
                if chart_utils.inrange(ep_wp_eclipto_orb, 270, 5):
                    angularity_orb = abs(ep_wp_eclipto_orb - 270)
                    angularity = angles_models.ForegroundAngles.EASTPOINT

            if angularity_strength == ramc_square_strength:
                ep_wp_ascension_orb = chart.ramc - planet.right_ascension
                if ep_wp_ascension_orb < 0:
                    ep_wp_ascension_orb += 360
                if chart_utils.inrange(ep_wp_ascension_orb, 90, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 90)
                    angularity = angles_models.ForegroundAngles.WESTPOINT_RA
                if chart_utils.inrange(ep_wp_ascension_orb, 270, 5):
                    angularity_orb = abs(ep_wp_ascension_orb - 270)
                    angularity = angles_models.ForegroundAngles.EASTPOINT_RA

        if str(angularity.value).strip() == '' and is_mundanely_background:
            angularity = angles_models.NonForegroundAngles.BACKGROUND

        if chart.type not in chart_utils.INGRESSES:
            # It's not an ingress; dormancy is always negated
            planet_negates_dormancy = True
        else:
            planet_negates_dormancy = chart_utils.angularity_activates_ingress(
                angularity_orb, str(angularity)
            )

        planet.angularity_strength = angularity_strength
        return (
            angularity,
            angularity_strength,
            planet_negates_dormancy,
            is_mundanely_background,
        )

    def find_outermost_chart(self):
        outermost_chart = self.charts[0]
        for chart in self.charts:
            if chart.role > outermost_chart.role:
                outermost_chart = chart
        return outermost_chart

    def find_innermost_chart(self):
        innermost_chart = self.charts[0]
        for chart in self.charts:
            if chart.role < innermost_chart.role:
                innermost_chart = chart
        return innermost_chart

    def make_chart_grid(self, rows: int, cols: int):
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

        chart = self.find_outermost_chart()

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

        return chart_grid

    def parse_aspect(
        self,
        primary_planet_data: chart_models.PlanetData,
        secondary_planet_data: chart_models.PlanetData,
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect | None:
        ecliptical_aspect = self.find_ecliptical_aspect(
            primary_planet_data,
            secondary_planet_data,
            whole_chart_is_dormant,
        )
        mundane_aspect = self.find_mundane_aspect(
            primary_planet_data,
            secondary_planet_data,
            whole_chart_is_dormant,
        )

        # Skip existing ecliptical aspects between radical planets
        if (
            primary_planet_data.role.value
            == chart_models.ChartWheelRole.RADIX.value
            and secondary_planet_data.role.value
            == chart_models.ChartWheelRole.RADIX.value
        ):
            if ecliptical_aspect and (
                not mundane_aspect
                or mundane_aspect.orb > ecliptical_aspect.orb
            ):
                # For now, we also don't allow PVP aspects if there's already an ecliptical aspect
                return None

        tightest_aspect = None

        if ecliptical_aspect or mundane_aspect:
            tightest_aspect = min(
                ecliptical_aspect,
                mundane_aspect,
                key=lambda x: x.orb if x else 1000,
            )
        elif self.options.pvp_aspects.get('enabled', False):
            # This may also be None; that's fine
            tightest_aspect = self.find_pvp_aspect(
                primary_planet_data,
                secondary_planet_data,
            )

        return tightest_aspect

    def write_aspects(
        self,
        chartfile: TextIOWrapper,
        whole_chart_is_dormant: bool,
    ) -> list[list[chart_models.Aspect]]:

        aspects_by_class = [[], [], [], []]

        for (from_index, from_chart) in enumerate(self.charts):
            for to_index in range(from_index, len(self.charts)):
                to_chart = self.charts[to_index]
                for (
                    primary_index,
                    (primary_planet_long_name, _),
                ) in enumerate(from_chart.iterate_points(self.options)):
                    for (
                        secondary_index,
                        (secondary_planet_long_name, _),
                    ) in enumerate(to_chart.iterate_points(self.options)):
                        if (
                            secondary_index <= primary_index
                            and from_chart == to_chart
                        ):
                            continue

                        primary_planet = from_chart.planets[
                            primary_planet_long_name
                        ]
                        secondary_planet = to_chart.planets[
                            secondary_planet_long_name
                        ]

                        maybe_aspect = self.parse_aspect(
                            primary_planet,
                            secondary_planet,
                            whole_chart_is_dormant,
                        )

                        if maybe_aspect:
                            aspects_by_class[
                                maybe_aspect.aspect_class - 1
                            ].append(maybe_aspect)

        aspect_class_headers = [
            'Class 1',
            'Class 2',
            'Class 3',
            'Other Partile',
        ]

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

        # For each aspect class, insert dividers where the roles change
        aspects_by_class_with_dividers = copy.deepcopy(aspects_by_class)
        for aspect_class in aspects_by_class_with_dividers:
            previous_roles = [None, None]
            for (index, aspect) in enumerate(aspect_class):
                if index > 0 and (
                    aspect.from_planet_role.value != previous_roles[0]
                    or aspect.to_planet_role.value != previous_roles[1]
                ):
                    aspect_class.insert(index, '-' * 24)
                previous_roles[0] = aspect.from_planet_role.value
                previous_roles[1] = aspect.to_planet_role.value

        # Write aspects from all classes to file
        for aspect_index in range(
            max(
                len(aspects_by_class_with_dividers[0]),
                len(aspects_by_class_with_dividers[1]),
                len(aspects_by_class_with_dividers[2]),
            )
        ):
            previous_roles = [None, None]
            if aspect_index < len(aspects_by_class_with_dividers[0]):
                chartfile.write(
                    chart_utils.left_align(
                        str(aspects_by_class_with_dividers[0][aspect_index]),
                        width=24,
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class_with_dividers[1]):
                chartfile.write(
                    chart_utils.center_align(
                        str(aspects_by_class_with_dividers[1][aspect_index]),
                        width=24,
                    )
                )
            else:
                chartfile.write(' ' * 24)
            if aspect_index < len(aspects_by_class_with_dividers[2]):
                chartfile.write(
                    chart_utils.right_align(
                        str(aspects_by_class_with_dividers[2][aspect_index]),
                        width=24,
                    )
                )
            else:
                chartfile.write(' ' * 24)
            chartfile.write('\n')

        chartfile.write('-' * self.table_width + '\n')
        if aspects_by_class_with_dividers[3]:
            chartfile.write(
                chart_utils.center_align(
                    f'{aspects_by_class_with_dividers[3]} Aspects',
                    width=self.table_width,
                )
                + '\n'
            )
            for aspect in aspects_by_class_with_dividers[3]:
                chartfile.write(
                    chart_utils.center_align(str(aspect), self.table_width)
                    + '\n'
                )
            chartfile.write('-' * self.table_width + '\n')

        return aspects_by_class

    def write_info_table(self, chartfile: TextIOWrapper):
        chartfile.write(
            'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
        )

        # Default to true if this is an ingress chart
        whole_chart_is_dormant = (
            True
            if len(self.charts) == 0
            and self.charts[0].type in chart_utils.INGRESSES
            else False
        )
        for (chart_index, chart) in enumerate(self.charts):
            if chart_index > 0:
                chartfile.write('-' * self.table_width + '\n')

            if len(self.charts) > 1:
                section_title = ''

                if chart.role == chart_models.ChartWheelRole.TRANSIT:
                    section_title = 'Transiting Planets'
                elif chart.role == chart_models.ChartWheelRole.PROGRESSED:
                    section_title = 'Progressed Planets'
                elif chart.role == chart_models.ChartWheelRole.SOLAR:
                    section_title = 'Solar Return Planets'
                elif chart.role == chart_models.ChartWheelRole.RADIX:
                    section_title = 'Radical Planets'

                chartfile.write(
                    chart_utils.center_align(section_title, self.table_width)
                    + '\n'
                )

            chart_is_dormant = self.write_info_table_section(
                chartfile,
                chart,
            )
            if not chart_is_dormant:
                whole_chart_is_dormant = False

        if whole_chart_is_dormant:
            chartfile.write('-' * self.table_width + '\n')
            chartfile.write(
                chart_utils.center_align('Dormant Ingress', self.table_width)
                + '\n'
            )
            return

        aspects_by_class = self.write_aspects(
            chartfile,
            whole_chart_is_dormant,
        )

        self.write_cosmic_state(
            chartfile,
            aspects_by_class,
        )

    def write_info_table_section(
        self,
        chartfile: TextIOWrapper,
        chart: chart_models.ChartObject,
    ):
        whole_chart_is_dormant = True
        angularity_options = self.options.angularity
        for planet_name, _ in chart.iterate_points(self.options):
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
            ) = self.calc_angle_and_strength(planet_data)

            if planet_negates_dormancy:
                whole_chart_is_dormant = False

            # This will not include vertex/antivertex, which we calculate shortly after
            planet_data.angle = angularity

            # Conjunctions to Vertex/Antivertex
            minor_limit = angularity_options.minor_angles or [1.0, 2.0, 3.0]

            if (
                angularity == angles_models.NonForegroundAngles.BLANK
                or is_mundanely_background
            ):
                if chart_utils.inrange(
                    planet_data.azimuth, 270, minor_limit[-1]
                ):
                    angularity = angles_models.NonForegroundAngles.VERTEX
                    planet_data.prime_vertical_angle = angularity
                elif chart_utils.inrange(
                    planet_data.azimuth, 90, minor_limit[-1]
                ):
                    angularity = angles_models.NonForegroundAngles.ANTIVERTEX
                    planet_data.prime_vertical_angle = angularity

            chartfile.write(f'{strength_percent:3d}% {angularity}')
            chartfile.write('\n')

        # Write angles to info table

        # Midheaven

        # Longitude
        chartfile.write(
            f'Mc {chart_utils.decimal_longitude_to_sign(chart.cusps[10])} '
        )
        # Latitude
        chartfile.write(' ' * 7)
        # Speed
        chartfile.write(' ' * 7)
        # Right Ascension
        ra = chart_utils.right_ascension_from_zodiacal(
            chart.cusps[10], chart.obliquity
        )
        chartfile.write(chart_utils.fmt_dm(ra, True, degree_digits=3) + ' ')
        # Declination
        dec = chart_utils.declination_from_zodiacal(
            chart.cusps[10], chart.obliquity
        )
        chartfile.write(chart_utils.fmt_lat(dec, True) + ' ')
        # Azimuth
        chartfile.write("180° 0' ")
        # Altitude - TODO
        chartfile.write(' ' * 8)
        # Meridian Longitude
        chartfile.write(' ' * 8)
        # PVL
        chartfile.write("270° 0'")

        chartfile.write('\n')

        # Ascendant

        # Longitude
        chartfile.write(
            f'As {chart_utils.decimal_longitude_to_sign(chart.cusps[1])} '
        )
        # Latitude
        chartfile.write(' ' * 7)
        # Speed
        chartfile.write(' ' * 7)
        # Right Ascension
        ra = chart_utils.right_ascension_from_zodiacal(
            chart.cusps[1], chart.obliquity
        )
        chartfile.write(chart_utils.fmt_dm(ra, True, degree_digits=3) + ' ')
        # Declination
        dec = chart_utils.declination_from_zodiacal(
            chart.cusps[1], chart.obliquity
        )
        chartfile.write(chart_utils.fmt_lat(dec, True) + ' ')
        # Azimuth
        chartfile.write(' ' * 7)
        # Altitude
        chartfile.write("   0° 0' ")
        # Meridian Longitude
        chartfile.write(' ' * 8)
        # PVL
        chartfile.write("  0° 0'")

        chartfile.write('\n')

        # Eastpoint

        # Longitudes
        chartfile.write(
            f'Ep {chart_utils.decimal_longitude_to_sign(chart.angles[2])} '
        )
        # Latitude
        chartfile.write(' ' * 7)
        # Speed
        chartfile.write(' ' * 7)
        # Right Ascension
        ra = to360(chart.ramc - 90)
        chartfile.write(chart_utils.fmt_dm(ra, True, degree_digits=3) + ' ')

        # Declination
        dec = chart_utils.declination_from_zodiacal(
            chart.angles[2], chart.obliquity
        )
        chartfile.write(chart_utils.fmt_lat(dec, True))

        chartfile.write('\n')

        # Vertex
        if self.options.use_vertex:
            # Longitude
            chartfile.write(
                f'Vx {chart_utils.decimal_longitude_to_sign(chart.angles[1])} '
            )
            # Latitude
            chartfile.write(' ' * 7)
            # Speed
            chartfile.write(' ' * 7)
            # Right Ascension
            chartfile.write(' ' * 8)

            # Declination
            dec = chart_utils.declination_from_zodiacal(
                chart.angles[1], chart.obliquity
            )
            chartfile.write(chart_utils.fmt_lat(dec, True) + ' ')
            # Azimuth
            chartfile.write("270° 0' ")
            # Altitude - TODO
            chartfile.write(' ' * 7)
            chartfile.write('\n')

        return whole_chart_is_dormant

    def write_cosmic_state(
        self,
        chartfile: TextIOWrapper,
        aspects_by_class: list[list[chart_models.Aspect]],
    ):
        chartfile.write(
            chart_utils.center_align('Cosmic State', self.table_width) + '\n'
        )

        midpoints = {}
        if self.options.enable_natal_midpoints:
            midpoints = self.calc_midpoints()

        # Iterate from transiting chart to radix
        for (index, chart) in enumerate(self.charts):
            if index != 0:
                chartfile.write(f'\n{"-" * self.table_width} \n')
            if len(self.charts) > 1:
                title = None
                if chart.role == chart_models.ChartWheelRole.TRANSIT:
                    title = 'Transiting Planets'
                elif chart.role == chart_models.ChartWheelRole.PROGRESSED:
                    title = 'Progressed Planets'
                elif chart.role == chart_models.ChartWheelRole.SOLAR:
                    title = 'Solar Return Planets'
                elif chart.role == chart_models.ChartWheelRole.RADIX:
                    title = 'Radical Planets'

                if title:
                    chartfile.write(
                        chart_utils.center_align(title, self.table_width)
                        + '\n'
                    )

            moon_sign = chart_utils.SIGNS_SHORT[
                int(chart.planets['Moon'].longitude // 30)
            ]
            sun_sign = chart_utils.SIGNS_SHORT[
                int(chart.planets['Sun'].longitude // 30)
            ]

            for index, (_, planet_data) in enumerate(
                chart.iterate_points(self.options)
            ):
                planet_short_name = planet_data.short_name

                if index != 0:
                    chartfile.write('\n')

                chartfile.write(planet_short_name + ' ')

                sign = chart_utils.SIGNS_SHORT[
                    int(planet_data.longitude // 30)
                ]

                if sign in chart_utils.POS_SIGN[planet_short_name]:
                    plus_minus = '+'
                elif sign in chart_utils.NEG_SIGN[planet_short_name]:
                    plus_minus = '-'
                else:
                    plus_minus = ' '
                chartfile.write(f'{sign}{plus_minus} ')

                angle = str(planet_data.angle.value)

                if angle.strip() == '':
                    angle = ' '
                elif str(planet_data.angle.value).strip() in [
                    a.value.strip().upper()
                    for a in angles_models.ForegroundAngles
                ]:
                    angle = 'F'
                else:
                    angle = 'B'
                chartfile.write(angle + ' |')

                # Write needs hierarchy strength for natals
                strength_hierarchy_written = False
                if (
                    len(self.charts) == 1
                    and chart.type.value == chart_models.ChartType.NATAL.value
                ):
                    strength = self.calc_planetary_needs_strength(
                        planet_data, chart, aspects_by_class
                    )
                    chartfile.write((f' ({int(strength)}%)').ljust(16))
                    strength_hierarchy_written = True

                need_another_row = False

                if chart.type not in chart_utils.INGRESSES:
                    if planet_short_name != 'Mo':
                        if (
                            moon_sign
                            in chart_utils.POS_SIGN[planet_short_name]
                        ):
                            chartfile.write(f' Mo {moon_sign}+')
                            need_another_row = True
                        elif (
                            moon_sign
                            in chart_utils.NEG_SIGN[planet_short_name]
                        ):
                            chartfile.write(f' Mo {moon_sign}-')
                            need_another_row = True
                    if planet_short_name != 'Su':
                        if sun_sign in chart_utils.POS_SIGN[planet_short_name]:
                            chartfile.write(f' Su {sun_sign}+')
                            need_another_row = True
                        elif (
                            sun_sign in chart_utils.NEG_SIGN[planet_short_name]
                        ):
                            chartfile.write(f' Su {sun_sign}-')
                            need_another_row = True

                aspect_list = []

                for class_index in range(3):
                    for aspect in aspects_by_class[class_index]:
                        if aspect.includes_planet(planet_short_name) and (
                            aspect.from_planet_role.value == chart.role.value
                            or aspect.to_planet_role.value == chart.role.value
                        ):
                            # This lets us sort by strength descending, basically;
                            # The sort is still ascending, but the strength is inverted.
                            percent = str(200 - aspect.strength)
                            aspect_list.append(
                                [
                                    aspect.cosmic_state_format(
                                        planet_short_name
                                    ),
                                    percent,
                                    aspect.orb,
                                ]
                            )

                aspect_list.sort(key=lambda p: p[1] + str(p[2]))

                if aspect_list:
                    if need_another_row:
                        chartfile.write('\n' + (' ' * 9) + '| ')
                        need_another_row = False
                    else:
                        chartfile.write(' ')

                for aspect_index, aspect in enumerate(aspect_list):
                    chartfile.write(
                        aspect[0]
                        + ' '
                        + ('' if aspect[0][-1] in ['M', 'p'] else ' ')
                        + ' ' * 2
                    )

                    if strength_hierarchy_written:
                        if (
                            aspect_index == 2
                            and aspect_index != len(aspect_list) - 1
                            or (
                                aspect_index >= 5
                                and aspect_index % 4 == 3
                                and aspect_index != len(aspect_list) - 1
                            )
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')

                    else:
                        if (
                            aspect_index % 4 == 3
                            and aspect_index != len(aspect_list) - 1
                        ):
                            chartfile.write('\n' + (' ' * 9) + '| ')

                # Midpoints
                related_midpoints = midpoints.get(
                    f'{planet_data.role.value}{planet_data.name}', []
                )
                if len(related_midpoints) > 0:
                    chartfile.write('\n' + (' ' * 9) + '|    ')
                for (midpoint_index, midpoint) in enumerate(related_midpoints):
                    chartfile.write(str(midpoint) + (' ' * 6))
                    if (
                        midpoint_index % 4 == 3
                        and midpoint_index != len(related_midpoints) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '|    ')

            chartfile.write('\n')
            # Write midpoints for Ascendant/MC
            ascendant_midpoints = midpoints.get(f'{chart.role.value}As', [])
            if len(ascendant_midpoints) > 0:
                ascendant_sign = chart_utils.SIGNS_SHORT[
                    int(chart.cusps[1] // 30)
                ]
                chartfile.write(f'As {ascendant_sign}    |    ')
            for (midpoint_index, midpoint) in enumerate(ascendant_midpoints):
                chartfile.write(str(midpoint) + (' ' * 6))
                if (
                    midpoint_index % 4 == 3
                    and midpoint_index != len(ascendant_midpoints) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '|    ')

            midheaven_midpoints = midpoints.get(f'{chart.role.value}Mc', [])
            if len(midheaven_midpoints) > 0:
                midheaven_sign = chart_utils.SIGNS_SHORT[
                    int(chart.cusps[10] // 30)
                ]
                chartfile.write(f'\nMc {midheaven_sign}    |    ')
            for (midpoint_index, midpoint) in enumerate(midheaven_midpoints):
                chartfile.write(str(midpoint) + (' ' * 6))
                if (
                    midpoint_index % 4 == 3
                    and midpoint_index != len(midheaven_midpoints) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '|    ')

    def get_return_class(self, t: chart_models.ChartType) -> str:
        t = t.type.value.lower()
        if t[0:3] in ['cap', 'can', 'ari', 'lib']:
            return 'SI' if 'solar' in t else 'LI'
        if 'return' in t:
            return 'SR' if 'solar' in t else 'LR'
        return 'N'

    def calc_midpoints(self):
        midpoints = {}

        midpoint_orbs = self.options.midpoints
        square_direction = (
            chart_models.MidpointAspectType.DIRECT
            if self.options.midpoints['is90'] == 'd'
            else chart_models.MidpointAspectType.INDIRECT
        )
        for chart in self.charts:
            for (point_name, point) in chart.iterate_points(
                self.options,
                include_angles=True,
            ):
                for (
                    _,
                    aspect_degrees,
                ) in chart_models.AspectType.iterate():
                    max_orb = None
                    raw_orb = None

                    # If the aspect is a sesquisquare, we need to use the orb for semisquare,
                    # as it's the only orb in options
                    aspect_degrees_for_options = None
                    if aspect_degrees == 135:
                        # We handle all 45° multiples at once
                        continue
                    elif aspect_degrees == 180:
                        aspect_degrees_for_options = 0
                    else:
                        aspect_degrees_for_options = aspect_degrees

                    if str(aspect_degrees_for_options) in midpoint_orbs:
                        max_orb = self.options.midpoints[
                            str(aspect_degrees_for_options)
                        ]
                    else:
                        continue
                    for halfsum in self.halfsums:
                        if halfsum.contains(
                            point.short_name
                            if hasattr(point, 'short_name')
                            else point_name
                        ):
                            continue
                        point_longitude = (
                            point.longitude
                            if hasattr(point, 'longitude')
                            else point
                        )
                        if aspect_degrees == 45:
                            raw_orb_0 = abs(
                                halfsum.longitude - point_longitude
                            )
                            raw_orb_45 = abs(raw_orb_0 - 45)
                            raw_orb_135 = abs(raw_orb_0 - 135)
                            raw_orb_225 = abs(raw_orb_0 - 225)
                            raw_orb_315 = abs(raw_orb_0 - 315)
                            raw_orb = (
                                min(
                                    raw_orb_45,
                                    raw_orb_135,
                                    raw_orb_225,
                                    raw_orb_315,
                                )
                                * 60
                            )
                        else:
                            raw_orb = (
                                abs(
                                    abs(halfsum.longitude - point_longitude)
                                    - aspect_degrees
                                )
                                * 60
                            )

                        if raw_orb <= max_orb:
                            midpoint_direction = None
                            if aspect_degrees in [0, 180]:
                                midpoint_direction = (
                                    chart_models.MidpointAspectType.DIRECT
                                )
                            if aspect_degrees in [45, 135]:
                                midpoint_direction = (
                                    chart_models.MidpointAspectType.INDIRECT
                                )
                            else:
                                midpoint_direction = square_direction
                            midpoint = chart_models.MidpointAspect(
                                midpoint_type=midpoint_direction,
                                orb_minutes=int(round(raw_orb, 0)),
                                framework=chart_models.AspectFramework.ECLIPTICAL,
                                from_point=point_name,
                                to_midpoint=str(halfsum),
                                from_point_role=chart.role,
                            )
                            midpoint_name = f'{chart.role.value}{point_name}'
                            if midpoint_name not in midpoints:
                                midpoints[midpoint_name] = [midpoint]
                            else:
                                # make sure it stays sorted
                                bisect.insort(
                                    midpoints[midpoint_name],
                                    midpoint,
                                    key=lambda x: x.orb_minutes,
                                )

        return midpoints

    def calc_mundane_midpoints(self):
        midpoints = {}

        midpoint_orbs = self.options.midpoints.get('mundane', 0)
        if midpoint_orbs == 0:
            return midpoints

        for (
            _,
            aspect_degrees,
        ) in chart_models.AspectType.iterate():
            max_orb = None
            raw_orb = None

            # If the aspect is a sesquisquare, we need to use the orb for semisquare,
            # as it's the only orb in options
            aspect_degrees_for_options = None
            if aspect_degrees == 135:
                # We handle all 45° multiples at once
                continue
            elif aspect_degrees == 180:
                aspect_degrees_for_options = 0
            else:
                aspect_degrees_for_options = aspect_degrees

            if str(aspect_degrees_for_options) in midpoint_orbs:
                max_orb = self.options.midpoints[
                    str(aspect_degrees_for_options)
                ]
            else:
                continue
            for halfsum in self.halfsums:
                if halfsum.contains(
                    point.name if hasattr(point, 'name') else point_name
                ):
                    continue
                point_longitude = (
                    point.longitude if hasattr(point, 'longitude') else point
                )
                if aspect_degrees == 45:
                    raw_orb_0 = abs(halfsum.longitude - point_longitude)
                    raw_orb_45 = abs(raw_orb_0 - 45)
                    raw_orb_135 = abs(raw_orb_0 - 135)
                    raw_orb_225 = abs(raw_orb_0 - 225)
                    raw_orb_315 = abs(raw_orb_0 - 315)
                    raw_orb = (
                        min(
                            raw_orb_45,
                            raw_orb_135,
                            raw_orb_225,
                            raw_orb_315,
                        )
                        * 60
                    )
                else:
                    raw_orb = (
                        abs(
                            abs(halfsum.longitude - point_longitude)
                            - aspect_degrees
                        )
                        * 60
                    )

                if raw_orb <= max_orb:
                    midpoint_direction = None
                    if aspect_degrees in [0, 180]:
                        midpoint_direction = (
                            chart_models.MidpointAspectType.DIRECT
                        )
                    if aspect_degrees in [45, 135]:
                        midpoint_direction = (
                            chart_models.MidpointAspectType.INDIRECT
                        )
                    else:
                        midpoint_direction = square_direction
                    midpoint = chart_models.MidpointAspect(
                        midpoint_type=midpoint_direction,
                        orb_minutes=int(round(raw_orb, 0)),
                        framework=chart_models.AspectFramework.ECLIPTICAL,
                        from_point=point_name,
                        to_midpoint=str(halfsum),
                        from_point_role=chart.role,
                    )
                    midpoint_name = f'{chart.role.value}{point_name}'
                    if midpoint_name not in midpoints:
                        midpoints[midpoint_name] = [midpoint]
                    else:
                        # make sure it stays sorted
                        bisect.insort(
                            midpoints[midpoint_name],
                            midpoint,
                            key=lambda x: x.orb_minutes,
                        )

        for k, v in midpoints.items():
            print(k)
            for m in v:
                print(k, m)
        return midpoints

    def calc_halfsums(self):
        halfsums = []
        for from_chart in self.charts:
            for to_chart in self.charts:
                for (
                    primary_index,
                    (primary_point_name, primary_point),
                ) in enumerate(
                    from_chart.iterate_points(
                        self.options, include_angles=True
                    )
                ):
                    for (
                        secondary_index,
                        (secondary_point_name, secondary_point),
                    ) in enumerate(
                        to_chart.iterate_points(
                            self.options, include_angles=True
                        )
                    ):
                        if (
                            secondary_index <= primary_index
                            and from_chart == to_chart
                        ):
                            continue
                        primary_point_is_angle = (
                            primary_point_name in constants.ANGLE_ABBREVIATIONS
                        )
                        secondary_point_is_angle = (
                            secondary_point_name
                            in constants.ANGLE_ABBREVIATIONS
                        )
                        if primary_point_is_angle and secondary_point_is_angle:
                            continue
                        elif (
                            primary_point_is_angle or secondary_point_is_angle
                        ):
                            longitude = (
                                (
                                    primary_point.longitude
                                    if secondary_point_is_angle
                                    else primary_point
                                )
                                + (
                                    secondary_point.longitude
                                    if primary_point_is_angle
                                    else secondary_point
                                )
                            ) / 2
                            prime_vertical_longitude = 0
                            right_ascension = 0
                        else:
                            longitude = (
                                primary_point.longitude
                                + secondary_point.longitude
                            ) / 2
                            prime_vertical_longitude = (
                                primary_point.prime_vertical_longitude
                                + secondary_point.prime_vertical_longitude
                            ) / 2
                            right_ascension = (
                                primary_point.right_ascension
                                + secondary_point.right_ascension
                            ) / 2

                        halfsums.append(
                            chart_models.HalfSum(
                                point_a=primary_point.short_name
                                if hasattr(primary_point, 'short_name')
                                else primary_point_name,
                                point_b=secondary_point.short_name
                                if hasattr(secondary_point, 'short_name')
                                else secondary_point_name,
                                longitude=longitude,
                                prime_vertical_longitude=prime_vertical_longitude,
                                right_ascension=right_ascension,
                            )
                        )

        return halfsums

    def calc_planetary_needs_strength(
        self,
        planet: chart_models.PlanetData,
        chart: chart_models.ChartObject,
        aspects_by_class: list[list[chart_models.Aspect]],
    ) -> int:
        luminary_strength = 0
        rules_sun_sign = (
            chart.sun_sign in chart_utils.POS_SIGN[planet.short_name]
        )
        rules_moon_sign = (
            chart.moon_sign in chart_utils.POS_SIGN[planet.short_name]
        )
        if rules_sun_sign and rules_moon_sign:
            luminary_strength = 95
        elif rules_sun_sign or rules_moon_sign:
            luminary_strength = 90

        max_luminary_aspect_strength = 0
        for aspect in aspects_by_class[0]:
            if (
                aspect.includes_planet(planet.short_name)
                and aspect.is_hard_aspect()
            ):
                if (
                    (planet.name == 'Sun' and aspect.includes_planet('Mo'))
                    or (planet.name == 'Moon' and aspect.includes_planet('Su'))
                    or (
                        planet.name not in ['Sun', 'Moon']
                        and (
                            aspect.includes_planet('Su')
                            or aspect.includes_planet('Mo')
                        )
                    )
                ):
                    max_luminary_aspect_strength = max(
                        max_luminary_aspect_strength, aspect.strength
                    )

        if luminary_strength > 0 and max_luminary_aspect_strength > 0:
            max_luminary_aspect_strength = max(
                95, max_luminary_aspect_strength
            )

        if max_luminary_aspect_strength == 0:
            for aspect in aspects_by_class[1]:
                if (
                    aspect.includes_planet(planet.short_name)
                    and aspect.is_hard_aspect()
                ):
                    if (
                        (planet.name == 'Sun' and aspect.includes_planet('Mo'))
                        or (
                            planet.name == 'Moon'
                            and aspect.includes_planet('Su')
                        )
                        or (
                            planet.name not in ['Sun', 'Moon']
                            and (
                                aspect.includes_planet('Su')
                                or aspect.includes_planet('Mo')
                            )
                        )
                    ):
                        max_luminary_aspect_strength = max(
                            max_luminary_aspect_strength, aspect.strength
                        )

        if luminary_strength > 0 and max_luminary_aspect_strength > 0:
            max_luminary_aspect_strength = max(
                92, max_luminary_aspect_strength
            )

        stationary_strength = 75 if planet.is_stationary else 0
        if stationary_strength > 0 and luminary_strength > 0:
            stationary_strength = 90

        strength = max(
            planet.angularity_strength,
            luminary_strength,
            max_luminary_aspect_strength,
            stationary_strength,
        )

        return min(strength, 100)

    @abstractmethod
    def draw_chart(
        self,
        chartfile: TextIOWrapper,
    ):
        pass

    def show(self):
        open_file(self.filename)
