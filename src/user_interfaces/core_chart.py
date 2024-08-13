# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
from io import TextIOWrapper

import src.models.angles as angles_models
import src.models.charts as chart_models
import src.models.options as option_models
import src.constants as constants
import src.utils.chart_utils as chart_utils
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
    temporary: bool

    def __init__(
        self,
        charts: list[chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        def s(c):
            return c.role

        self.options = options

        self.charts = sorted(charts, key=s, reverse=True)
        self.temporary = temporary

        self.try_precess_charts()

        filename = chart_utils.make_chart_path(
            self.find_outermost_chart(), temporary
        )
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

    def insert_planet_into_line(
        self,
        chart,
        planet_long_name: str,
        prefix: str = '',
        abbreviation_only: bool = False,
    ) -> str:
        planet_data = chart.planets[planet_long_name]
        number = constants.PLANETS[planet_long_name]['number']
        short_name = constants.PLANETS[planet_long_name]['short_name']

        if abbreviation_only:
            return prefix + short_name

        data_line = (
            prefix
            + short_name
            + ' '
            + chart_utils.zod_min(planet_data.longitude)
        )
        if number < 14:
            data_line += ' ' + chart_utils.fmt_dm(planet_data.house % 30)
        else:
            data_line = chart_utils.center_align(data_line, 16)

        return data_line

    def sort_house(self, charts: list[chart_models.ChartObject], index: int):
        house = []
        for chart in charts:
            for (
                planet_name,
                planet_data,
            ) in chart_utils.iterate_allowed_planets(self.options):

                planet_data = chart.planets[planet_name]
                if planet_data.house // 30 == index:
                    pos = (planet_data.house % 30) / 2
                    house.append(
                        [planet_name, planet_data.house, pos, chart.role.value]
                    )
            house.sort(key=lambda h: h[1])

        return self.spread_planets_within_house(house, 0, len(charts))

    def spread_planets_within_house(
        self, old, start=0, number_of_charts: int = 1
    ):
        new = [[] for _ in range(15)]
        placed = 0
        for i in range(len(old)):
            x = int(old[i][-(number_of_charts)]) + start
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
        planet_1_role: str | None,
        planet_2: chart_models.PlanetData,
        planet_2_role: str | None,
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect:
        return self.__find_non_pvp_aspect(
            planet_1,
            planet_1_role,
            planet_2,
            planet_2_role,
            foreground_planets,
            whole_chart_is_dormant,
            chart_models.AspectFramework.ECLIPTICAL,
        )

    def find_mundane_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_1_role: str | None,
        planet_2: chart_models.PlanetData,
        planet_2_role: str | None,
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect:
        return self.__find_non_pvp_aspect(
            planet_1,
            planet_1_role,
            planet_2,
            planet_2_role,
            foreground_planets,
            whole_chart_is_dormant,
            chart_models.AspectFramework.MUNDANE,
        )

    def __find_non_pvp_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_1_role: chart_models.ChartWheelRole,
        planet_2: chart_models.PlanetData,
        planet_2_role: chart_models.ChartWheelRole,
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
        aspect_framework: chart_models.AspectFramework,
    ) -> chart_models.Aspect:

        raw_orb = None
        aspect = None

        if whole_chart_is_dormant:
            if planet_1.name != 'Moon':
                return None

        if aspect_framework == chart_models.AspectFramework.ECLIPTICAL:
            raw_orb = abs(planet_1.longitude - planet_2.longitude) % 360
        elif aspect_framework == chart_models.AspectFramework.MUNDANE:
            raw_orb = abs(planet_1.house - planet_2.house) % 360

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

            aspect = (
                chart_models.Aspect()
                .from_planet(planet_1.short_name, role=planet_1_role)
                .to_planet(planet_2.short_name, role=planet_2_role)
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

            if planet_1.name == 'Moon' and (
                planet_1_role == chart_utils.INGRESSES
                or planet_1_role == chart_utils.SOLUNAR_RETURNS
            ):
                # Always consider transiting Moon aspects, as long as they're in orb
                break

            # Otherwise, make sure the aspect should be considered at all
            # TODO - this should probably be checked way earlier

            show_aspects = (
                option_models.ShowAspect.from_number(self.options.show_aspects)
                or self.options.show_aspects
            )

            if show_aspects == option_models.ShowAspect.ONE_PLUS_FOREGROUND:
                if (
                    planet_1.name not in foreground_planets
                    and not planet_1.treat_as_foreground
                ) and (
                    planet_2.name not in foreground_planets
                    and not planet_2.treat_as_foreground
                ):
                    if aspect_orb <= 1 and self.options.partile_nf:
                        aspect = aspect.with_class(4)
                    else:
                        continue

            elif show_aspects == option_models.ShowAspect.BOTH_FOREGROUND:
                if (
                    planet_1.name not in foreground_planets
                    and not planet_1.treat_as_foreground
                ) or (
                    planet_2.name not in foreground_planets
                    and not planet_2.treat_as_foreground
                ):
                    if aspect_orb <= 1 and self.options.partile_nf:
                        aspect = aspect.with_class(4)
                    else:
                        continue

            # We have found a valid aspect; stop checking for more aspects
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
        planet_1: chart_models.PlanetData,
        planet_1_role: chart_models.ChartWheelRole,
        planet_2: chart_models.PlanetData,
        planet_2_role: chart_models.ChartWheelRole,
    ):
        max_prime_vertical_orb = (
            chart_utils.greatest_nonzero_class_orb(
                self.options.angularity.minor_angles
            )
            or 3
        )

        # One or the other planet must be on the prime vertical

        planet_1_on_prime_vertical = chart_utils.inrange(
            planet_1.azimuth, 90, max_prime_vertical_orb
        ) or chart_utils.inrange(planet_1.azimuth, 270, max_prime_vertical_orb)

        planet_2_on_prime_vertical = chart_utils.inrange(
            planet_2.azimuth, 90, max_prime_vertical_orb
        ) or chart_utils.inrange(planet_2.azimuth, 270, max_prime_vertical_orb)

        if not planet_1_on_prime_vertical and not planet_2_on_prime_vertical:
            return None

        if planet_1_on_prime_vertical and planet_2_on_prime_vertical:
            # check prime vertical to prime vertical in azimuth
            raw_orb = abs(planet_1.azimuth - planet_2.azimuth)
            conjunction_orb = self.options.pvp_aspects['0'][0]
            opposition_orb = self.options.pvp_aspects['180'][0]
            is_conjunction = chart_utils.inrange(raw_orb, 0, conjunction_orb)

            if is_conjunction or chart_utils.inrange(
                raw_orb, 180, opposition_orb
            ):
                aspect = (
                    chart_models.Aspect()
                    .as_prime_vertical_paran()
                    .from_planet(planet_1.short_name, role=planet_1_role)
                    .to_planet(planet_2.short_name, role=planet_2_role)
                    .as_type(
                        chart_models.AspectType.CONJUNCTION
                        if is_conjunction
                        else chart_models.AspectType.OPPOSITION
                    )
                    .with_class(1)
                )
                aspect_strength = chart_utils.calc_aspect_strength_percent(
                    conjunction_orb if is_conjunction else opposition_orb,
                    raw_orb,
                )

                aspect = aspect.with_strength(aspect_strength).with_orb(
                    raw_orb,
                )

                return aspect

        (planet_on_prime_vertical, prime_vertical_role) = (
            (planet_1, planet_1_role)
            if planet_1_on_prime_vertical
            else (planet_2, planet_2_role)
        )

        (planet_on_other_axis, other_planet_role) = (
            (planet_2, planet_2_role)
            if planet_1_on_prime_vertical
            else (planet_1, planet_1_role)
        )

        (greater_planet, greater_role) = (
            (planet_on_prime_vertical, prime_vertical_role)
            if prime_vertical_role >= other_planet_role
            else (planet_on_other_axis, other_planet_role)
        )

        (lesser_planet, lesser_role) = (
            (planet_on_prime_vertical, prime_vertical_role)
            if prime_vertical_role < other_planet_role
            else (planet_on_other_axis, other_planet_role)
        )

        # check meridian to prime vertical in azimuth
        max_major_angle_orb = (
            chart_utils.greatest_nonzero_class_orb(
                self.options.angularity.major_angles
            )
            or 10
        )

        planet_is_on_meridian = chart_utils.inrange(
            planet_on_other_axis.prime_vertical_longitude,
            90,
            max_major_angle_orb,
        ) or chart_utils.inrange(
            planet_on_other_axis.prime_vertical_longitude,
            270,
            max_major_angle_orb,
        )

        square_orb = self.options.ecliptic_aspects['90'][0]

        if planet_is_on_meridian:

            # TODO - I'm not sure this will cover everything
            if planet_on_other_axis.name != planet_on_prime_vertical.name:

                raw_orb = abs(
                    planet_on_other_axis.azimuth
                    - planet_on_prime_vertical.azimuth
                )
                if (
                    chart_utils.inrange(raw_orb, 0, square_orb)
                    or chart_utils.inrange(raw_orb, 90, square_orb)
                    or chart_utils.inrange(raw_orb, 180, square_orb)
                ):
                    # These are squares no matter what
                    aspect = (
                        chart_models.Aspect()
                        .as_prime_vertical_paran()
                        .from_planet(
                            greater_planet.short_name,
                            role=greater_role,
                        )
                        .to_planet(
                            lesser_planet.short_name,
                            role=lesser_role,
                        )
                        .as_type(chart_models.AspectType.SQUARE)
                        .with_class(1)
                    )
                    aspect_strength = chart_utils.calc_aspect_strength_percent(
                        square_orb, raw_orb
                    )
                    aspect = aspect.with_strength(aspect_strength).with_orb(
                        raw_orb
                    )
                    return aspect

        # check horizon to prime vertical in meridian longitude
        planet_is_on_horizon = chart_utils.inrange(
            planet_on_other_axis.prime_vertical_longitude,
            0,
            max_major_angle_orb,
        ) or chart_utils.inrange(
            planet_on_other_axis.prime_vertical_longitude,
            180,
            max_major_angle_orb,
        )
        if planet_is_on_horizon:
            if planet_on_other_axis.name != planet_on_prime_vertical.name:
                raw_orb = abs(
                    planet_on_other_axis.meridian_longitude
                    - planet_on_prime_vertical.meridian_longitude
                )
                is_conjunction = chart_utils.inrange(
                    raw_orb, 0, conjunction_orb
                )
                if is_conjunction or chart_utils.inrange(
                    raw_orb, 180, opposition_orb
                ):
                    # These are squares no matter what
                    aspect = (
                        chart_models.Aspect()
                        .as_prime_vertical_paran()
                        .from_planet(
                            greater_planet.short_name,
                            role=greater_planet,
                        )
                        .to_planet(
                            lesser_planet.short_name,
                            role=lesser_role,
                        )
                        .as_type(chart_models.AspectType.SQUARE)
                        .with_class(1)
                    )
                    aspect_strength = chart_utils.calc_aspect_strength_percent(
                        conjunction_orb if is_conjunction else opposition_orb,
                        raw_orb,
                    )
                    aspect = aspect.with_strength(aspect_strength).with_orb(
                        raw_orb
                    )
                    return aspect

    def calc_angle_and_strength(
        self,
        planet: chart_models.PlanetData,
        chart: chart_models.ChartObject,
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

        return (
            angularity,
            angularity_strength,
            planet_negates_dormancy,
            is_mundanely_background,
        )

    def find_outermost_chart(self):
        outermost_chart = self.charts[0]
        for chart in self.charts:
            if chart.role < outermost_chart.role:
                outermost_chart = chart
        return outermost_chart

    def find_innermost_chart(self):
        innermost_chart = self.charts[0]
        for chart in self.charts:
            if chart.role > innermost_chart.role:
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
        planets_foreground: list[str],
        from_chart: chart_models.ChartObject,
        to_chart: chart_models.ChartObject,
        primary_planet_long_name: str,
        secondary_planet_long_name: str,
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect | None:
        # If options say to skip one or both planets' aspects outside the foreground,
        # just skip calculating anything
        show_aspects = (
            self.options.show_aspects or option_models.ShowAspect.ALL
        )

        if show_aspects == option_models.ShowAspect.ONE_PLUS_FOREGROUND:
            if (
                primary_planet_long_name not in planets_foreground
                and secondary_planet_long_name not in planets_foreground
            ):
                if not self.options.partile_nf:
                    return None

        if show_aspects == option_models.ShowAspect.BOTH_FOREGROUND:
            if (
                primary_planet_long_name not in planets_foreground
                or secondary_planet_long_name not in planets_foreground
            ):
                if not self.options.partile_nf:
                    return None

        primary_planet_data = from_chart.planets[primary_planet_long_name]
        secondary_planet_data = to_chart.planets[secondary_planet_long_name]

        ecliptical_aspect = self.find_ecliptical_aspect(
            primary_planet_data,
            from_chart.role,
            secondary_planet_data,
            to_chart.role,
            planets_foreground,
            whole_chart_is_dormant,
        )
        mundane_aspect = self.find_mundane_aspect(
            primary_planet_data,
            from_chart.role,
            secondary_planet_data,
            to_chart.role,
            planets_foreground,
            whole_chart_is_dormant,
        )

        pvp_aspect = None
        if self.options.allow_pvp_aspects or False:
            pvp_aspect = self.find_pvp_aspect(
                primary_planet_data,
                from_chart.role,
                secondary_planet_data,
                to_chart.role,
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

        return tightest_aspect

    def write_aspects(
        self,
        chartfile: TextIOWrapper,
        whole_chart_is_dormant: bool,
        planets_foreground: list[str],
    ) -> list[list[chart_models.Aspect]]:

        aspects_by_class = [[], [], [], []]

        for from_chart in self.charts:
            for to_chart in self.charts:
                for (
                    primary_index,
                    (primary_planet_long_name, _),
                ) in enumerate(
                    chart_utils.iterate_allowed_planets(self.options)
                ):
                    for (
                        secondary_index,
                        (secondary_planet_long_name, _),
                    ) in enumerate(
                        chart_utils.iterate_allowed_planets(self.options)
                    ):
                        if secondary_index <= primary_index:
                            continue

                        maybe_aspect = self.parse_aspect(
                            planets_foreground,
                            from_chart,
                            to_chart,
                            primary_planet_long_name,
                            secondary_planet_long_name,
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

        return aspects_by_class

    def write_info_table(self, chartfile: TextIOWrapper):
        chartfile.write(
            'Pl Longitude   Lat   Speed    RA     Decl   Azi     Alt      ML     PVL    Ang G\n'
        )

        planets_foreground = []
        planet_foreground_angles = {}

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

            chart_is_dormant = self.write_info_table_section(
                chartfile,
                chart,
                planets_foreground,
                planet_foreground_angles,
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
            planets_foreground,
        )

        self.write_cosmic_state(
            chartfile,
            planet_foreground_angles,
            aspects_by_class,
        )

    def write_info_table_section(
        self,
        chartfile: TextIOWrapper,
        chart: chart_models.ChartObject,
        planets_foreground: list[str],
        planet_foreground_angles: dict[str, str],
    ):
        angularity_options = self.options.angularity

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
                    angularity = angles_models.NonForegroundAngles.ANTI_VERTEX

            chartfile.write(f'{strength_percent:3d}% {angularity}')
            chartfile.write('\n')

        return whole_chart_is_dormant

    def write_cosmic_state(
        self,
        chartfile: TextIOWrapper,
        planet_foreground_angles: dict[str, str],
        aspects_by_class: list[list[chart_models.Aspect]],
    ):
        chartfile.write(
            chart_utils.center_align('Cosmic State', self.table_width) + '\n'
        )

        # Iterate from transiting chart to radix
        for (index, chart) in enumerate(reversed(self.charts)):
            if index != 0:
                chartfile.write('-' * self.table_width + '\n')
            if len(self.charts) > 1:
                if chart.role == chart_models.ChartWheelRole.TRANSIT:
                    chartfile.write(
                        chart_utils.center_align(
                            'Transiting Planets', self.table_width
                        )
                        + '\n'
                    )

                elif chart.role == chart_models.ChartWheelRole.PROGRESSED:
                    chartfile.write(
                        chart_utils.center_align(
                            'Progressed Planets', self.table_width
                        )
                        + '\n'
                    )

                elif chart.role == chart_models.ChartWheelRole.SOLAR:
                    chartfile.write(
                        chart_utils.center_align(
                            'Solar Return Planets', self.table_width
                        )
                        + '\n'
                    )

                elif chart.role == chart_models.ChartWheelRole.RADIX:
                    chartfile.write(
                        chart_utils.center_align(
                            'Radical Planets', self.table_width
                        )
                        + '\n'
                    )

            moon_sign = chart_utils.SIGNS_SHORT[
                int(chart.planets['Moon'].longitude // 30)
            ]
            sun_sign = chart_utils.SIGNS_SHORT[
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

                angle = planet_foreground_angles.get(
                    planet_short_name, angles_models.NonForegroundAngles.BLANK
                )
                if str(angle).strip() == '':
                    angle = ' '
                elif str(angle).strip() in [
                    a.value.strip().upper()
                    for a in angles_models.ForegroundAngles
                ]:
                    angle = 'F'
                else:
                    angle = 'B'
                chartfile.write(angle + ' |')

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
                        if aspect.includes_planet(planet_short_name):
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
                    chartfile.write(aspect[0] + '   ')
                    if (
                        aspect_index % 4 == 3
                        and aspect_index != len(aspect_list) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')

    @abstractmethod
    def draw_chart(
        self,
        chartfile: TextIOWrapper,
    ):
        pass

    def show(self):
        open_file(self.filename)
