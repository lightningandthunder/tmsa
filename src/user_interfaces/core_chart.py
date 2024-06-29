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

import src.models.angles as angles_models
import src.models.charts as chart_models
import src.models.options as option_models
import src.constants as constants
import src.utils.chart_utils as chart_utils
from src.utils.os_utils import open_file


def write_to_file(chart, planet_long_name: str):

    planet_data = chart.planets[planet_long_name]
    number = constants.PLANETS[planet_long_name]['number']
    short_name = constants.PLANETS[planet_long_name]['short_name']

    data_line = short_name + ' ' + chart_utils.zod_min(planet_data.longitude)
    if number < 14:
        data_line += ' ' + chart_utils.fmt_dm(planet_data.house % 30)
    else:
        data_line = chart_utils.center_align(data_line, 16)

    return data_line


# TODO - need to work in chart wheel roles; for now this assumes
#        that this is a uniwheel
class ChartReport:
    table_width = 81

    def __init__(
        self,
        charts: dict[chart_models.ChartWheelRole : chart_models.ChartObject],
        temporary: bool,
        options: option_models.Options,
    ):
        self.charts = charts
        self.options = options

        self.try_precess_to_transit_chart(charts)

        core_chart = None
        if chart_models.ChartWheelRole.TRANSIT in charts:
            core_chart = charts[chart_models.ChartWheelRole.TRANSIT]

        elif chart_models.ChartWheelRole.INGRESS in charts:
            core_chart = charts[chart_models.ChartWheelRole.INGRESS]

        else:
            core_chart = charts[chart_models.ChartWheelRole.RADIX]

        self.core_chart = core_chart

        filename = chart_utils.make_chart_path(core_chart, temporary)
        filename = filename[0:-3] + 'txt'
        try:
            chartfile = open(filename, 'w')
        except Exception as e:
            tkmessagebox.showerror(f'Unable to open file:', f'{e}')
            return

        with chartfile:
            self.draw_chart(self.core_chart, chartfile)
            self.write_info_table(self.core_chart, chartfile)

            chartfile.write('\n' + '-' * self.table_width + '\n')
            chartfile.write(
                f"Created by Time Matters {constants.VERSION}  ({datetime.now().strftime('%d %b %Y')})"
            )

    def try_precess_to_transit_chart(
        self, charts: dict[str : chart_models.ChartObject]
    ):
        if len(charts) == 1:
            return

        # Precess radix to transit
        if (
            chart_models.ChartWheelRole.RADIX in charts
            and chart_models.ChartWheelRole.TRANSIT in charts
        ):
            self.charts[chart_models.ChartWheelRole.RADIX].precess_to(
                self.charts[chart_models.ChartWheelRole.TRANSIT]
            )

        # Precess progressed to transit
        if (
            chart_models.ChartWheelRole.PROGRESSED in charts
            and chart_models.ChartWheelRole.TRANSIT in charts
        ):
            self.charts[chart_models.ChartWheelRole.PROGRESSED].precess_to(
                self.charts[chart_models.ChartWheelRole.TRANSIT]
            )

        # If only radix and progressed are present,
        # precess radix to progressed
        if (
            chart_models.ChartWheelRole.RADIX in charts
            and chart_models.ChartWheelRole.PROGRESSED in charts
            and not chart_models.ChartWheelRole.TRANSIT in charts
        ):
            self.charts[chart_models.ChartWheelRole.RADIX].precess_to(
                self.charts[chart_models.ChartWheelRole.PROGRESSED]
            )

    def sort_house(self, chart: chart_models.ChartObject, index: int):
        house = []
        for planet_name, planet_data in chart_utils.iterate_allowed_planets(
            self.options
        ):

            planet_data = chart.planets[planet_name]
            if planet_data.house // 30 == index:
                pos = (planet_data.house % 30) / 2
                house.append([planet_name, planet_data.house, pos])
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
        planet_1: chart_models.PlanetData,
        planet_1_role: str | None,
        planet_2: chart_models.PlanetData,
        planet_2_role: str | None,
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
    ) -> chart_models.Aspect:
        return self._find_non_pvp_aspect(
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
        return self._find_non_pvp_aspect(
            planet_1,
            planet_1_role,
            planet_2,
            planet_2_role,
            foreground_planets,
            whole_chart_is_dormant,
            chart_models.AspectFramework.MUNDANE,
        )

    def _find_non_pvp_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_1_role: str | None,
        planet_2: chart_models.PlanetData,
        planet_2_role: str | None,
        foreground_planets: list[str],
        whole_chart_is_dormant: bool,
        aspect_framework: chart_models.AspectFramework,
    ) -> chart_models.Aspect:
        raw_orb = None
        if aspect_framework == chart_models.AspectFramework.ECLIPTICAL:
            raw_orb = abs(planet_1.longitude - planet_2.longitude) % 360
        elif aspect_framework == chart_models.AspectFramework.MUNDANE:
            raw_orb = (
                abs(
                    planet_1.prime_vertical_longitude
                    - planet_2.prime_vertical_longitude
                )
                % 360
            )
            print(planet_1.prime_vertical_longitude, planet_2.prime_vertical_longitude)
            print("Raw mundane orb: ", raw_orb)

        if raw_orb > 180:
            raw_orb = 360 - raw_orb

        for aspect_type in chart_models.AspectType:
            aspect_degrees = chart_models.AspectType.degrees_from_abbreviation(
                aspect_type.value
            )

            test_orb = None

            if aspect_framework == chart_models.AspectFramework.ECLIPTICAL:
                test_orb = self.options.mundane_aspects[str(aspect_degrees)]
            elif aspect_framework == chart_models.AspectFramework.MUNDANE:
                test_orb = self.options.mundane_aspects[str(aspect_degrees)]

            if test_orb[2]:
                maxorb = test_orb[2]
            elif test_orb[1]:
                maxorb = test_orb[1] * 1.25
            elif test_orb[0]:
                maxorb = test_orb[0] * 2.5
            else:
                return None

            if (
                raw_orb >= aspect_degrees - maxorb
                and raw_orb <= aspect_degrees + maxorb
            ):
                aspect = (
                    chart_models.Aspect()
                    .from_planet(planet_1.short_name, role=planet_1_role)
                    .to_planet(planet_2.short_name, role=planet_2_role)
                    .as_type(
                        chart_models.AspectType.from_string(aspect_type.value)
                    )
                )
                aspect.framework = aspect_framework
                raw_orb = abs(raw_orb - aspect_degrees)

                if raw_orb <= test_orb[0]:
                    aspect = aspect.with_class(1)
                elif raw_orb <= test_orb[1]:
                    aspect = aspect.with_class(2)
                elif raw_orb <= test_orb[2]:
                    aspect = aspect.with_class(3)
                else:
                    return None

                if planet_1.name == 'Moon' and (
                    self.core_chart.type in chart_utils.INGRESSES
                    or self.core_chart.type in chart_utils.SOLAR_RETURNS
                ):
                    break  # i.e. consider transiting Moon aspects always

                if (
                    self.options.show_aspects
                    == option_models.ShowAspect.ONE_PLUS_FOREGROUND
                ):
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
                            return None
                elif (
                    self.options.show_aspects
                    == option_models.ShowAspect.BOTH_FOREGROUND
                ):
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
                            return None
                break
        else:
            return None

        aspect_strength = chart_utils.calc_aspect_strength_percent(
            maxorb, raw_orb
        )
        aspect = aspect.with_strength(aspect_strength).with_orb(raw_orb)

        return aspect

    def find_pvp_aspect(
        self,
        planet_1: chart_models.PlanetData,
        planet_1_role: str | None,
        planet_2: chart_models.PlanetData,
        planet_2_role: str | None,
        max_orb: float,
    ):
        # One or the other planet must be on the prime vertical

        planet_1_on_prime_vertical = chart_utils.inrange(
            planet_1.azimuth, 90, max_orb
        ) or chart_utils.inrange(planet_1.azimuth, 270, max_orb)

        planet_2_on_prime_vertical = chart_utils.inrange(
            planet_2.azimuth, 90, max_orb
        ) or chart_utils.inrange(planet_2.azimuth, 270, max_orb)

        if planet_1_on_prime_vertical and planet_2_on_prime_vertical:
            # check prime vertical to prime vertical in azimuth
            raw_orb = abs(planet_1.azimuth - planet_2.azimuth)
            is_conjunction = chart_utils.inrange(raw_orb, 0, max_orb)

            if is_conjunction or chart_utils.inrange(raw_orb, 180, max_orb):
                t = (
                    chart_models.AspectType.CONJUNCTION
                    if is_conjunction
                    else chart_models.AspectType.OPPOSITION
                )
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
                    max_orb, raw_orb
                )
                aspect = aspect.with_strength(aspect_strength).with_orb(
                    raw_orb
                )

                return aspect

        if planet_1_on_prime_vertical or planet_2_on_prime_vertical:
            # check meridian to prime vertical in azimuth
            planet_on_meridian = (
                planet_1
                if chart_utils.inrange(
                    planet_1.prime_vertical_longitude, 90, max_orb
                )
                or chart_utils.inrange(
                    planet_1.prime_vertical_longitude, 270, max_orb
                )
                else planet_2
                if chart_utils.inrange(
                    planet_2.prime_vertical_longitude, 90, max_orb
                )
                or chart_utils.inrange(
                    planet_2.prime_vertical_longitude, 270, max_orb
                )
                else None
            )

            if planet_on_meridian is not None:

                planet_on_prime_vertical = (
                    planet_1 if planet_1_on_prime_vertical else planet_2
                )
                if planet_on_meridian.name != planet_on_prime_vertical.name:

                    raw_orb = abs(
                        planet_on_meridian.azimuth
                        - planet_on_prime_vertical.azimuth
                    )
                    if (
                        chart_utils.inrange(raw_orb, 0, max_orb)
                        or chart_utils.inrange(raw_orb, 90, max_orb)
                        or chart_utils.inrange(raw_orb, 180, max_orb)
                    ):
                        # These are squares no matter what
                        aspect = (
                            chart_models.Aspect()
                            .as_prime_vertical_paran()
                            .from_planet(
                                planet_on_meridian.short_name,
                                role=planet_1_role,
                            )
                            .to_planet(
                                planet_on_prime_vertical.short_name,
                                role=planet_2_role,
                            )
                            .as_type(chart_models.AspectType.SQUARE)
                            .with_class(1)
                        )
                        aspect_strength = (
                            chart_utils.calc_aspect_strength_percent(
                                max_orb, raw_orb
                            )
                        )
                        aspect = aspect.with_strength(
                            aspect_strength
                        ).with_orb(raw_orb)
                        return aspect

            # check horizon to prime vertical in meridian longitude
            planet_on_horizon = (
                planet_1
                if chart_utils.inrange(
                    planet_1.prime_vertical_longitude, 0, max_orb
                )
                or chart_utils.inrange(
                    planet_1.prime_vertical_longitude, 180, max_orb
                )
                else planet_2
                if chart_utils.inrange(
                    planet_2.prime_vertical_longitude, 0, max_orb
                )
                or chart_utils.inrange(
                    planet_2.prime_vertical_longitude, 180, max_orb
                )
                else None
            )
            if planet_on_horizon is not None:
                planet_on_prime_vertical = (
                    planet_1 if planet_1_on_prime_vertical else planet_2
                )
                if planet_on_horizon.name != planet_on_prime_vertical.name:
                    raw_orb = abs(
                        planet_on_horizon.meridian_longitude
                        - planet_on_prime_vertical.meridian_longitude
                    )
                    if (
                        chart_utils.inrange(raw_orb, 0, max_orb)
                        or chart_utils.inrange(raw_orb, 90, max_orb)
                        or chart_utils.inrange(raw_orb, 180, max_orb)
                    ):
                        # These are squares no matter what
                        aspect = (
                            chart_models.Aspect()
                            .as_prime_vertical_paran()
                            .from_planet(
                                planet_on_horizon.short_name,
                                role=planet_1_role,
                            )
                            .to_planet(
                                planet_on_prime_vertical.short_name,
                                role=planet_2_role,
                            )
                            .as_type(chart_models.AspectType.SQUARE)
                            .with_class(1)
                        )
                        aspect_strength = (
                            chart_utils.calc_aspect_strength_percent(
                                max_orb, raw_orb
                            )
                        )
                        aspect = aspect.with_strength(
                            aspect_strength
                        ).with_orb(raw_orb)
                        return aspect

        return None

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

    def draw_chart(
        self,
        chart: chart_models.ChartObject,
        chartfile: TextIOWrapper,
    ):
        rows = 65
        cols = 69
        chart_grid = [[' ' for _ in range(cols)] for _ in range(rows)]

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
        chart: chart_models.ChartObject,
        chartfile: TextIOWrapper,
    ):
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
                or chart.type in chart_utils.SOLAR_RETURNS
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
            (primary_planet_long_name, primary_planet_info),
        ) in enumerate(chart_utils.iterate_allowed_planets(self.options)):
            for (
                secondary_index,
                (secondary_planet_long_name, secondary_planet_info),
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

                ecliptical_aspect = self.find_ecliptical_aspect(
                    primary_planet_data,
                    None,
                    secondary_planet_data,
                    None,
                    planets_foreground,
                    whole_chart_is_dormant,
                )
                mundane_aspect = self.find_mundane_aspect(
                    primary_planet_data,
                    None,
                    secondary_planet_data,
                    None,
                    planets_foreground,
                    whole_chart_is_dormant,
                )

                pvp_aspect = None
                if self.options.allow_pvp_aspects:
                    pvp_aspect = self.find_pvp_aspect(
                        primary_planet_data,
                        None,
                        secondary_planet_data,
                        None,
                        chart_utils.greatest_nonzero_class_orb(self.options.angularity.minor_angles),
                    )
                print(f'aspects for {primary_planet_long_name} and {secondary_planet_long_name}:')
                print(f'ecliptical: {ecliptical_aspect}')
                print(f'mundane: {mundane_aspect}')

                if (
                    not ecliptical_aspect
                    and not mundane_aspect
                    and not pvp_aspect
                ):
                    continue

                tightest_orb = []
                if ecliptical_aspect:
                    tightest_orb.append(
                        (ecliptical_aspect.orb, ecliptical_aspect)
                    )

                if mundane_aspect:
                    tightest_orb.append((mundane_aspect.orb, mundane_aspect))

                if pvp_aspect:
                    tightest_orb.append((pvp_aspect.orb, pvp_aspect))

                tightest_orb.sort(key=lambda x: x[0])

                tightest_orb = tightest_orb[0]

                # Even if the PVP aspect is the closest, if there is any other aspect, use that instead
                if pvp_aspect and not ecliptical_aspect and not mundane_aspect:
                    aspects_by_class[pvp_aspect.aspect_class - 1].append(
                        pvp_aspect
                    )
                else:
                    # If the pvp aspect is the closest, but other aspects exist, remove the pvp orb
                    # so the next closest aspect can be used
                    if pvp_aspect and tightest_orb[0] == pvp_aspect.orb:
                        tightest_orb.pop(0)

                if (
                    ecliptical_aspect
                    and tightest_orb[0] == ecliptical_aspect.orb
                ):
                    aspects_by_class[
                        ecliptical_aspect.aspect_class - 1
                    ].append(ecliptical_aspect)
                elif mundane_aspect:   # mundane orb
                    aspects_by_class[mundane_aspect.aspect_class - 1].append(
                        mundane_aspect
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
                    chart_utils.center_align(aspect, self.table_width) + '\n'
                )
            chartfile.write('-' * self.table_width + '\n')

    def write_cosmic_state(
        self,
        chartfile: TextIOWrapper,
        chart: chart_models.ChartObject,
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

    def show(self):
        open_file(self.filename)
