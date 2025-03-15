# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import bisect
import math
import os
from typing import Iterator

from src import *
from src import constants
from src import swe
from src.models.options import NodeTypes, Options
import src.models.charts as chart_models
import src.models.angles as angles_models
from src.user_interfaces.widgets import *
from src.utils.format_utils import to360

SIGNS_SHORT = [
    'Ar',
    'Ta',
    'Ge',
    'Cn',
    'Le',
    'Vi',
    'Li',
    'Sc',
    'Sg',
    'Cp',
    'Aq',
    'Pi',
]
PLANET_NAMES = [
    'Moon',
    'Sun',
    'Mercury',
    'Venus',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Pluto',
    'Eris',
    'Sedna',
    'Mean Node',
    'True Node',
    'Eastpoint',
    'Vertex',
]
PLANET_NAMES_SHORT = [
    'Mo',
    'Su',
    'Me',
    'Ve',
    'Ma',
    'Ju',
    'Sa',
    'Ur',
    'Ne',
    'Pl',
    'Er',
    'Se',
    'No',
    'No',
    'Ep',
    'Vx',
]


def convert_long_name_to_short(name: str) -> str:
    return constants.PLANETS[name]['short_name']


def convert_short_name_to_long(name: str) -> str:
    for planet in constants.PLANETS:
        if constants.PLANETS[planet]['short_name'] == name:
            return planet


DEFAULT_ECLIPTICAL_ORBS = {
    '0': [3.0, 7.0, 10.0],
    '180': [3.0, 7.0, 10.0],
    '90': [3.0, 6.0, 7.5],
    '45': [1.0, 2.0, 0],
    '120': [3.0, 6.0, 7.5],
    '60': [3.0, 6.0, 7.5],
    '30': [0, 0, 0],
}
DEFAULT_MUNDANE_ORBS = {
    '0': [3.0, 0, 0],
    '180': [3.0, 0, 0],
    '90': [3.0, 0, 0],
    '45': [0, 0, 0],
}

RULERSHIPS = {
    'Ar': ['Su', 'Pl'],
    'Ta': ['Mo', 'Ve'],
    'Ge': ['Me'],
    'Cn': ['Mo', 'Ju'],
    'Le': ['Su'],
    'Vi': ['Me'],
    'Li': ['Ve', 'Sa'],
    'Sc': ['Ma'],
    'Sg': ['Ju'],
    'Cp': ['Ma', 'Sa'],
    'Aq': ['Ur'],
    'Pi': ['Ve', 'Ne'],
}

POS_SIGN = {
    'Mo': ['Cn', 'Ta'],
    'Su': ['Le', 'Ar'],
    'Me': ['Ge', 'Vi'],
    'Ve': ['Ta', 'Li', 'Pi'],
    'Ma': ['Sc', 'Cp'],
    'Ju': ['Sg', 'Cn'],
    'Sa': ['Cp', 'Li'],
    'Ur': ['Aq'],
    'Ne': ['Pi'],
    'Pl': ['Ar'],
    'Er': [],
    'Se': [],
    'No': [],
    'MN': [],
    'TN': [],
    'Ch': [],
    'Ce': [],
    'Pa': [],
    'Jn': [],
    'Vs': [],
    'Or': [],
    'Ha': [],
    'Mk': [],
    'Go': [],
    'Qu': [],
    'Sl': [],
}

NEG_SIGN = {
    'Mo': ['Cp', 'Sc'],
    'Su': ['Aq', 'Li'],
    'Me': ['Sg', 'Pi'],
    'Ve': ['Sc', 'Ar', 'Vi'],
    'Ma': ['Ta', 'Cn'],
    'Ju': ['Ge', 'Cp'],
    'Sa': ['Cn', 'Ar'],
    'Ur': ['Le'],
    'Ne': ['Vi'],
    'Pl': ['Li'],
    'Er': [],
    'Se': [],
    'No': [],
    'MN': [],
    'TN': [],
    'Ch': [],
    'Ce': [],
    'Pa': [],
    'Jn': [],
    'Vs': [],
    'Or': [],
    'Ha': [],
    'Mk': [],
    'Go': [],
    'Qu': [],
    'Sl': [],
}

DS = '\N{DEGREE SIGN}'

DQ = '"'
SQ = "'"


def major_angularity_curve_cadent_background(orb):
    if orb <= 10:
        orb *= 6
    elif orb > 10 and orb <= 40:
        orb = 2 * orb + 40
    elif orb > 40 and orb <= 60:
        orb *= 3
    else:
        orb = 6 * orb - 180

    return _major_angle_angularity_strength_percent(orb)


def major_angularity_curve_midquadrant_background(orb):
    if orb > 45:
        orb = 90 - orb
    if orb <= 10:
        orb *= 6
    elif orb > 10 and orb <= 35:
        orb = 2.4 * orb + 36
    else:
        orb = 6 * orb - 90

    return _major_angle_angularity_strength_percent(orb)


def _major_angle_angularity_strength_percent(orb: float) -> float:
    # Normalize the -1 to +1 range to a percentage
    raw = math.cos(math.radians(orb))
    # Convert from -1 to +1 to 0 to +2
    raw = raw + 1
    # Reduce to 0 to +1
    raw /= 2
    # Convert to percentage
    return round(raw * 100)


def major_angularity_curve_eureka_formula(orb):
    initial_angularity = math.cos(math.radians(orb * 4))
    # Reduce the weight - this essentially is a square of the calculated score
    faded_angularity = initial_angularity * ((initial_angularity + 1) / 2)
    # Same curve as angularity, but shifted 60 degrees
    cadency_strength = -1 * math.cos(math.radians(4 * (orb - 60)))
    # Reduce the weight of this term as before
    faded_cadency_strength = cadency_strength * (
        1 - ((cadency_strength + 1) / 2)
    )

    # This is a curve that moves between -1.125 and +1.125
    penultimate_score = faded_angularity + faded_cadency_strength
    # Convert to -1 to +1
    penultimate_score /= 1.125
    # Convert to 0 to +1
    raw_decimal = (penultimate_score + 1) / 2
    return round(raw_decimal * 100)


def calculate_angularity_curve(orb_degrees: float):
    return math.cos(math.radians(orb_degrees * 4))


def minor_angularity_curve(orb_degrees: float):
    # Cosine curve
    raw = math.cos(math.radians(orb_degrees * 30))
    # Convert from -1 to +1 to 0 to +2
    raw += 1
    # Spread this curve across 50 percentage points
    raw *= 25
    # Finally, add 50 get a percentage
    raw += 50

    return round(raw)


def inrange(value: float, center: float, orb: float) -> bool:
    return value >= center - orb and value <= center + orb


def zod_min(value):
    value %= 360
    deg = int(value)
    minute = round((value - deg) * 60)
    d = 0
    s = 0
    if minute == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        minute = 0
        deg += 1
    return f'{(deg % 30) or d:2d}{SIGNS_SHORT[(deg // 30) + s]}{minute:2d}'


def zod_sec(value):
    value %= 360
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    d = 0
    s = 0
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        if deg % 30 == 29:
            d = 30
            s = -1
        minute = 0
        deg += 1
    return f'{(deg % 30) or d:2d}{SIGNS_SHORT[deg // 30 + s]}{minute:2d}\'{sec:2d}"'


def center_align(value, width=33):
    if len(value) > width:
        value = value[0:width]
    left = (width - len(value)) // 2
    left = ' ' * left
    right = (width + 1 - len(value)) // 2
    right = ' ' * right
    return left + value + right


def left_align(value, width):
    if len(value) > width:
        value = value[0:width]
    return value + ' ' * (width - len(value))


def right_align(value, width):
    if len(value) > width:
        value = value[0:width]
    return ' ' * (width - len(value)) + value


def fmt_hms(time):
    day = 0
    if time >= 24:
        day = 1
        time -= 24
    elif time < 0:
        day = -1
        time += 24
    hour = int(time)
    time = (time - hour) * 60
    minute = int(time)
    time = (time - minute) * 60
    sec = round(time)
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        minute = 0
        hour += 1
    if hour == 24:
        hour = 0
        day += 1
    if day == 0:
        day = ''
    elif day == 2:
        day = ' +2 days'
    else:
        day = f' {day:+d} day'
    return f'{hour:2d}:{minute:02d}:{sec:02d}{day}'


def fmt_lat(value, nosec=False):
    sym = 'N'
    if value < 0:
        sym = 'S'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    if nosec:
        minute = round(value)
        sec = 0
    else:
        minute = int(value)
        value = (value - minute) * 60
        sec = round(value)
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        deg += 1
        minute = 0
    if nosec:
        return f'{deg:2d}{sym}{minute:2d}'
    return f'{deg:2d}{sym}{minute:2d}\'{sec:2d}"'


def fmt_long(value):
    sym = 'E'
    if value < 0:
        sym = 'W'
        value = -value
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        deg += 1
        minute = 0
    return f'{deg:3d}{sym}{minute:2d}\'{sec:2d}"'


def fmt_dms(value):
    deg = int(value)
    value = (value - deg) * 60
    minute = int(value)
    value = (value - minute) * 60
    sec = round(value)
    if sec == 60:
        sec = 0
        minute += 1
    if minute == 60:
        minute = 0
        deg += 1
    return f'{deg:2d}{DS}{minute:2}\'{sec:2}"'


def fmt_minutes(value):
    return int(value) * 60 + (value - int(value)) * 60


def fmt_dm(value, noz=False, degree_digits=2):
    deg = int(value)
    value = (value - deg) * 60
    minute = round(value)
    if minute == 60:
        minute = 0
        deg += 1
    if noz:
        if degree_digits == 2:
            return f"{deg:2d}{DS}{minute:2}'"
        if degree_digits == 3:
            return f"{deg:>3d}{DS}{minute:>2}'"
    if degree_digits == 2:
        return f"{deg:>02d}{DS}{minute:>02}'"
    if degree_digits == 3:
        return f"{deg:>03d}{DS}{minute:>02}'"


def signed_degree_minute(value):
    if value < 0:
        return f'-{fmt_dm(-value, True)}'
    elif value > 0:
        return f'+{fmt_dm(value, True)}'
    else:
        return f' {fmt_dm(0)}'


def signed_minute_second(value):
    if value < 0:
        s = '-'
    elif value > 0:
        s = '+'
    else:
        s = ' '
    value = abs(value) * 60
    min = int(value)
    value = (value - min) * 60
    sec = round(value)
    if sec == 60:
        sec = 0
        min += 1
    return f'{s}{min:2}\'{sec:2}"'


def angularity_activates_ingress(orb: float, angle: str) -> bool:
    if orb < 0:
        return False

    if angle.strip() in ['A', 'D', 'M', 'I']:
        return orb <= 3.0
    return orb <= 2.0


def make_chart_path(chart, temporary, is_ingress=False):
    if isinstance(chart, dict):
        ingress = (
            True
            if chart['type'][0:3] in ['Ari', 'Can', 'Lib', 'Cap']
            or not chart['name']
            else False
        )
    else:
        ingress = is_ingress
    if isinstance(chart, dict):
        if ingress:
            first = f"{chart['year']}-{chart['month']}-{chart['day']}"
            second = chart['location']
            third = chart['type']
        else:
            first = chart['name']
            index = first.find(';')
            if index > -1:
                first = first[0:index]
            second = f"{chart['year']}-{chart['month']:02d}-{chart['day']:02d}"
            third = chart['type']
    else:
        if ingress:
            first = f'{chart.year}-{chart.month}-{chart.day}'
            second = chart.location
            third = chart.type.value
        else:
            first = chart.name
            index = first.find(';')
            if index > -1:
                first = first[0:index]
            second = f'{chart.year}-{chart.month:02d}-{chart.day:02d}'
            third = chart.type.value
    filename = f'{first}~{second}~{third}.dat'
    if ingress:
        filepath = os.path.join(
            f"{chart['year'] if isinstance(chart, dict) else chart.year}",
            filename,
        )
    else:
        filepath = os.path.join(first[0], first, filename)
    path = TEMP_CHARTS if temporary else CHART_PATH
    return os.path.abspath(os.path.join(path, filepath))


def iterate_allowed_planets(
    options: Options,
) -> Iterator[tuple[str, dict[str, any]]]:
    for planet_name, data in constants.PLANETS.items():
        if (
            data['number'] > 11
            and data['short_name'] not in options.extra_bodies
        ):
            continue
        elif (
            planet_name == 'True Node'
            and options.node_type.value != NodeTypes.TRUE_NODE.value
        ):
            continue
        elif (
            planet_name == 'Mean Node'
            and options.node_type.value != NodeTypes.MEAN_NODE.value
        ):
            continue

        else:
            yield planet_name, data


def calc_aspect_strength_percent(max_orb: int, raw_orb: float) -> str:
    strength = 60 / max_orb
    strength_percent = math.cos(math.radians(raw_orb * strength))
    strength_percent = round((strength_percent - 0.5) * 200)
    return f'{strength_percent:3d}'


def convert_house_to_pvl(house: float) -> float:
    zero_index_house = house - 1
    return (int(zero_index_house) * 30) + (
        ((zero_index_house) - int(zero_index_house)) * 30
    )


def greatest_nonzero_class_orb(orbs: list[float]) -> float:
    for i in range(len(orbs) - 1, -1, -1):
        if orbs[i] > 0:
            return orbs[i]
    return 0


def decimal_longitude_to_sign(longitude: float) -> str:
    sign = SIGNS_SHORT[int(longitude // 30)]
    sign_degrees = int(longitude % 30)

    raw_degrees = int(longitude)
    mins = int((longitude - raw_degrees) * 60)

    seconds = int((((longitude - raw_degrees) * 60) - mins) * 60)

    return f'{sign_degrees: >2}{sign}{mins: >2}\'{seconds: >2}"'


def declination_from_zodiacal(longitude: float, obliquity: float) -> float:
    sin_dec = math.sin(math.radians(longitude)) * math.sin(
        math.radians(obliquity)
    )
    return math.degrees(math.asin(sin_dec))


def right_ascension_from_zodiacal(longitude: float, obliquity: float) -> float:
    tan_ra = math.tan(math.radians(longitude)) * math.cos(
        math.radians(obliquity)
    )
    return to360(math.degrees(math.atan(tan_ra)))


def precess_mc(
    longitude: float, ayanamsa: float, obliquity: float
) -> tuple[float, float]:
    (right_ascension, declination) = swe.cotrans(
        [longitude + ayanamsa, 0, 0],
        obliquity,
    )
    return (right_ascension, declination)


def calc_halfsums(
    charts: list[chart_models.ChartObject], options: Options
) -> list[chart_models.HalfSum]:
    halfsums = []
    for (from_index, from_chart) in enumerate(charts):
        for (to_index, to_chart) in enumerate(charts):
            if to_index < from_index:
                continue
            for (
                primary_index,
                (primary_point_name, primary_point),
            ) in enumerate(
                from_chart.iterate_points(options, include_angles=True)
            ):
                for (
                    secondary_index,
                    (secondary_point_name, secondary_point),
                ) in enumerate(
                    to_chart.iterate_points(options, include_angles=True)
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
                        secondary_point_name in constants.ANGLE_ABBREVIATIONS
                    )
                    if primary_point_is_angle and secondary_point_is_angle:
                        continue
                    elif primary_point_is_angle or secondary_point_is_angle:
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
                            primary_point.longitude + secondary_point.longitude
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


def calc_midpoints_2(
    options: Options,
    charts: list[chart_models.ChartObject],
    halfsums: dict[str, chart_models.HalfSum],
) -> dict[str, list[dict[str, any]]]:
    midpoints = {}

    midpoint_orbs = options.midpoints
    square_direction = (
        chart_models.MidpointAspectType.DIRECT
        if options.midpoints['is90'] == 'd'
        else chart_models.MidpointAspectType.INDIRECT
    )

    # Iterate over each point in each chart, checking it against all halfsums
    for chart in charts:
        for (point_name, point) in chart.iterate_points(
            options,
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
                    max_orb = options.midpoints[
                        str(aspect_degrees_for_options)
                    ]
                else:
                    continue

                point_longitude = None

                for halfsum in halfsums:
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
                        ) * 60
                    elif aspect_degrees == 90:
                        raw_orb_90 = abs(
                            abs(halfsum.longitude - point_longitude) - 90
                        )
                        raw_orb_270 = abs(
                            abs(halfsum.longitude - point_longitude) - 270
                        )
                        raw_orb = min(raw_orb_90, raw_orb_270) * 60
                    else:
                        raw_orb = (
                            abs(
                                abs(halfsum.longitude - point_longitude)
                                - aspect_degrees
                            )
                        ) * 60
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


def calc_mundane_midpoints_2(
    options: Options,
    charts: list[chart_models.ChartObject],
    halfsums: dict[str, chart_models.HalfSum],
) -> dict[str, list[dict[str, any]]]:
    midpoints = {}

    outermost_chart = find_outermost_chart(charts)

    max_mundane_orb = options.midpoints.get('M', None)
    max_ecliptic_orb = options.midpoints.get('0', None)

    if not max_mundane_orb and not max_ecliptic_orb:
        return midpoints

    eastpoint = outermost_chart.eastpoint[0]
    zenith = to360(eastpoint + 90)
    eastpoint_ra = to360(outermost_chart.ramc - 90)

    square_direction = (
        chart_models.MidpointAspectType.DIRECT
        if options.midpoints['is90'] == 'd'
        else chart_models.MidpointAspectType.INDIRECT
    )

    for halfsum in halfsums:
        if halfsum.contains('As') or halfsum.contains('Mc'):
            continue

        for (
            _,
            aspect_degrees,
        ) in chart_models.AspectType.iterate_harmonic_4():
            direction = (
                chart_models.MidpointAspectType.DIRECT
                if aspect_degrees in [0, 180]
                else square_direction
            )
            pvl_orb = 360
            ra_orb = 360
            eastpoint_orb = 360
            zenith_orb = 360

            pvl_orb = (
                abs(halfsum.prime_vertical_longitude - aspect_degrees) * 60
            )

            ra_orb = (
                abs(
                    abs(halfsum.right_ascension - eastpoint_ra)
                    - aspect_degrees
                )
                * 60
            )

            zenith_orb = (
                abs(abs(zenith - halfsum.longitude) - aspect_degrees) * 60
            )

            eastpoint_orb = (
                abs(abs(eastpoint - halfsum.longitude) - aspect_degrees)
            ) * 60

        for (orb, angle) in [
            (pvl_orb, 'Angle'),
            (ra_orb, 'Ea'),
        ]:
            if orb <= max_mundane_orb:
                midpoint = chart_models.MidpointAspect(
                    midpoint_type=direction,
                    orb_minutes=int(round(orb, 0)),
                    framework=chart_models.AspectFramework.MUNDANE,
                    from_point=angle,
                    to_midpoint=str(halfsum),
                    from_point_role=outermost_chart.role,
                    is_mundane=True,
                )

                if angle not in midpoints:
                    midpoints[angle] = [midpoint]
                else:
                    bisect.insort(
                        midpoints[angle],
                        midpoint,
                        key=lambda x: x.orb_minutes,
                    )

        max_orb_for_zenith_eastpoint = max_ecliptic_orb or max_mundane_orb

        for (orb, angle) in [
            (eastpoint_orb, 'E'),
            (zenith_orb, 'Z'),
        ]:
            if orb <= max_orb_for_zenith_eastpoint:
                midpoint = chart_models.MidpointAspect(
                    midpoint_type=direction,
                    orb_minutes=int(round(orb, 0)),
                    framework=chart_models.AspectFramework.MUNDANE,
                    from_point=angle,
                    to_midpoint=str(halfsum),
                    from_point_role=outermost_chart.role,
                    is_mundane=True,
                )
                if angle not in midpoints:
                    midpoints[angle] = [midpoint]
                else:
                    bisect.insort(
                        midpoints[angle],
                        midpoint,
                        key=lambda x: x.orb_minutes,
                    )

    return midpoints


def merge_midpoints(
    ecliptic_midpoints: dict[str, list[chart_models.MidpointAspect]],
    mundane_midpoints: dict[str, list[chart_models.MidpointAspect]],
) -> list[chart_models.MidpointAspect]:
    keys = set(ecliptic_midpoints.keys()).union(set(mundane_midpoints.keys()))
    merged_midpoints = {}
    for key in keys:
        if key not in merged_midpoints:
            merged_midpoints[key] = []

        ecliptic_index = 0
        mundane_index = 0
        while ecliptic_index < len(
            ecliptic_midpoints[key]
        ) and mundane_index < len(mundane_midpoints[key]):
            if (
                ecliptic_midpoints[key][ecliptic_index].orb_minutes
                < mundane_midpoints[key][mundane_index].orb_minutes
            ):
                merged_midpoints[key].append(
                    ecliptic_midpoints[key][ecliptic_index]
                )
                ecliptic_index += 1
            else:
                merged_midpoints[key].append(
                    mundane_midpoints[key][mundane_index]
                )
                mundane_index += 1

        # Deal with leftovers from one or the other list
        if ecliptic_index < len(ecliptic_midpoints[key]):
            merged_midpoints[key].extend(
                ecliptic_midpoints[key][ecliptic_index:]
            )
        if mundane_index < len(mundane_midpoints[key]):
            merged_midpoints[key].extend(
                mundane_midpoints[key][mundane_index:]
            )

    return merged_midpoints


def find_outermost_chart(
    charts: list[chart_models.ChartObject],
) -> chart_models.ChartObject:
    outermost_chart = charts[0]
    for chart in charts:
        if chart.role > outermost_chart.role:
            outermost_chart = chart
    return outermost_chart


def calc_planetary_needs_strength(
    planet: chart_models.PlanetData,
    chart: chart_models.ChartObject,
    aspects_by_class: list[list[chart_models.Aspect]],
) -> int:
    luminary_strength = 0
    rules_sun_sign = chart.sun_sign in POS_SIGN[planet.short_name]
    rules_moon_sign = chart.moon_sign in POS_SIGN[planet.short_name]
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
        max_luminary_aspect_strength = max(95, max_luminary_aspect_strength)

    if max_luminary_aspect_strength == 0:
        for aspect in aspects_by_class[1]:
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
        max_luminary_aspect_strength = max(92, max_luminary_aspect_strength)

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
