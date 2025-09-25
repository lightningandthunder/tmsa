import bisect
from copy import deepcopy
from io import TextIOWrapper
import math

import src.models.charts as chart_models
from src import *
from src import constants
from src.models.angles import ForegroundAngles
from src.models.options import Options, ShowAspect
from src.utils.chart_utils import (
    POS_SIGN,
    calc_aspect_strength_percent,
    in_harmonic_range,
)
from src.utils.format_utils import to360
from src.user_interfaces.widgets import tkmessagebox


def calc_halfsums(
    options: Options,
    charts: list[chart_models.ChartObject],
) -> list[chart_models.HalfSum]:
    halfsums = []
    cross_wheel_enabled = options.midpoints.get('cross_wheel_enabled', False)
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
                        not cross_wheel_enabled
                        and from_chart.role.value != to_chart.role.value
                    ):
                        break

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

                    primary_data = primary_point
                    secondary_data = secondary_point

                    if primary_point_is_angle:
                        primary_data = chart_models.AngleData(
                            name=primary_point_name,
                            short_name=primary_point_name,
                            longitude=primary_point,
                            role=from_chart.role,
                            is_angle=True,
                        )

                    if secondary_point_is_angle:
                        secondary_data = chart_models.AngleData(
                            name=secondary_point_name,
                            short_name=secondary_point_name,
                            longitude=secondary_point,
                            role=to_chart.role,
                            is_angle=True,
                        )

                    longitude = (
                        primary_data.longitude + secondary_data.longitude
                    ) / 2
                    prime_vertical_longitude = (
                        primary_data.prime_vertical_longitude
                        + secondary_data.prime_vertical_longitude
                    ) / 2
                    right_ascension = (
                        primary_data.right_ascension
                        + secondary_data.right_ascension
                    ) / 2

                    halfsums.append(
                        chart_models.HalfSum(
                            point_a=primary_data,
                            point_b=secondary_data,
                            longitude=longitude,
                            prime_vertical_longitude=prime_vertical_longitude,
                            right_ascension=right_ascension,
                        )
                    )

    return halfsums


def parse_midpoint(
    options: Options,
    point_data: chart_models.PlanetData | chart_models.AngleData,
    halfsum: chart_models.HalfSum,
    coordinates: str,
    use_mundane_orb=False,
):
    raw_orb_degree_decimal = abs(
        getattr(point_data, coordinates) - getattr(halfsum, coordinates)
    )

    raw_orb_degree_decimal = min(
        raw_orb_degree_decimal, to360(360 - raw_orb_degree_decimal)
    )

    framework = (
        chart_models.AspectFramework.ECLIPTICAL
        if not use_mundane_orb
        else chart_models.AspectFramework.MUNDANE
    )

    conjunction_orb = (
        float(
            options.midpoints.get('0', 0)
            if not use_mundane_orb
            else options.midpoints.get('M', 0)
        )
        / 60.0
    )

    is_conjunction, conjunction_orb_degrees = in_harmonic_range(
        value=raw_orb_degree_decimal, orb=conjunction_orb, harmonic=1
    )

    if is_conjunction:
        return chart_models.MidpointAspect(
            midpoint_type=chart_models.MidpointAspectType.DIRECT,
            orb_minutes=round(conjunction_orb_degrees * 60),
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )

    is_opposition, opposition_orb_degrees = in_harmonic_range(
        value=raw_orb_degree_decimal, orb=conjunction_orb, harmonic=2
    )

    if is_opposition:
        return chart_models.MidpointAspect(
            midpoint_type=chart_models.MidpointAspectType.DIRECT,
            orb_minutes=round(opposition_orb_degrees * 60),
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )

    square_orb = (
        float(
            options.midpoints.get('90', 0)
            if not use_mundane_orb
            else options.midpoints.get('M', 0)
        )
        / 60.0
    )

    is_square, square_orb_degrees = in_harmonic_range(
        value=raw_orb_degree_decimal, orb=square_orb, harmonic=4
    )
    if is_square:
        direction = (
            chart_models.MidpointAspectType.DIRECT
            if options.midpoints.get('is90', 'd') == 'd'
            else chart_models.MidpointAspectType.INDIRECT
        )
        return chart_models.MidpointAspect(
            midpoint_type=direction,
            orb_minutes=round(square_orb_degrees * 60),
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )

    if use_mundane_orb:
        return

    octile_orb = float(options.midpoints.get('45', 0)) / 60.0

    is_octile, octile_orb_degrees = in_harmonic_range(
        value=raw_orb_degree_decimal, orb=octile_orb, harmonic=8
    )
    if is_octile:
        return chart_models.MidpointAspect(
            midpoint_type=chart_models.MidpointAspectType.INDIRECT,
            orb_minutes=round(octile_orb_degrees * 60),
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )


def make_midpoint_key(short_name, role: chart_models.ChartWheelRole):
    return f'{role.value}{short_name}'


def calc_midpoints_3(
    options: Options,
    charts: list[chart_models.ChartObject],
    halfsums: list[chart_models.HalfSum],
) -> dict[str, list[chart_models.MidpointAspect]]:
    midpoints = {}

    def insert_sorted(key, midpoint):
        if key not in midpoints:
            midpoints[key] = [midpoint]
        else:
            bisect.insort(
                midpoints[key],
                midpoint,
                key=lambda x: x.orb_minutes,
            )

    only_mundane_enabled = (
        not options.midpoints.get('0')
        and not options.midpoints.get('90')
        and bool(options.midpoints.get('M'))
    )

    # Iterate over each point in each chart, checking it against all halfsums
    for chart in charts:
        for (point_name, point) in chart.iterate_points(
            options,
            include_angles=True,
        ):
            point_short_name = (
                point.short_name
                if hasattr(point, 'short_name')
                else point_name
            )
            key = make_midpoint_key(point_short_name, chart.role)
            midpoints[key] = []

            for halfsum in halfsums:
                if halfsum.contains(point_short_name, role=chart.role):
                    continue

                point_longitude = (
                    point.longitude if hasattr(point, 'longitude') else point
                )

                point_is_angle = False
                planet_data = point

                if point_short_name in constants.ANGLE_ABBREVIATIONS:
                    point_is_angle = True
                    planet_data = chart_models.AngleData(
                        name=point_name,
                        short_name=point_short_name,
                        longitude=point_longitude,
                        role=chart.role,
                    )

                ecliptical_midpoint = None

                if not only_mundane_enabled:
                    ecliptical_midpoint = parse_midpoint(
                        options, planet_data, halfsum, 'longitude'
                    )

                mundane_midpoint = None

                if (
                    not point_is_angle
                    and not halfsum.contains_angle
                    and not options.midpoints.get(
                        'mundane_only_to_angles', True
                    )
                ):
                    mundane_midpoint = parse_midpoint(
                        options,
                        planet_data,
                        halfsum,
                        'prime_vertical_longitude',
                        use_mundane_orb=True,
                    )

                if ecliptical_midpoint and mundane_midpoint:
                    if (
                        ecliptical_midpoint.orb_minutes
                        < mundane_midpoint.orb_minutes
                    ):
                        insert_sorted(key, ecliptical_midpoint)
                    else:
                        insert_sorted(key, mundane_midpoint)
                elif ecliptical_midpoint:
                    insert_sorted(key, ecliptical_midpoint)
                elif mundane_midpoint:
                    insert_sorted(key, mundane_midpoint)

                # Check if we need to use mundane orbs for ecliptical contacts
                if only_mundane_enabled and point_is_angle:
                    pseudo_mundane_midpoint = parse_midpoint(
                        options,
                        planet_data,
                        halfsum,
                        'longitude',
                        use_mundane_orb=True,
                    )
                    if pseudo_mundane_midpoint:
                        pseudo_mundane_midpoint.framework = (
                            chart_models.AspectFramework.ECLIPTICAL
                        )
                        insert_sorted(key, pseudo_mundane_midpoint)

        mundane_angle = chart_models.AngleData(
            name='Angle',
            short_name='Angle',
            prime_vertical_longitude=0.0,
            role=chart.role,
        )

        key = make_midpoint_key(mundane_angle.short_name, chart.role)
        midpoints[key] = []
        # Check major angles
        for halfsum in halfsums:
            # We still don't want natal-only midpoints to natal angles in polywheels, though
            if (
                len(charts) > 1
                and chart.role.value == chart_models.ChartWheelRole.NATAL.value
                and halfsum.point_a.role.value
                == chart_models.ChartWheelRole.NATAL.value
                and halfsum.point_b.role.value
                == chart_models.ChartWheelRole.NATAL.value
            ):
                continue

            if halfsum.contains_angle:
                continue

            # Get all PVL midpoints
            mundane_midpoint = parse_midpoint(
                options,
                mundane_angle,
                halfsum,
                'prime_vertical_longitude',
                use_mundane_orb=True,
            )

            if mundane_midpoint:
                insert_sorted(key, mundane_midpoint)

        eastpoint_ra_angle = chart_models.AngleData(
            name=ForegroundAngles.EASTPOINT_RA.value,
            short_name=ForegroundAngles.EASTPOINT_RA.value,
            right_ascension=to360(chart.ramc - 90),
            role=chart.role,
        )

        key = make_midpoint_key(eastpoint_ra_angle.short_name, chart.role)
        midpoints[key] = []

        for halfsum in halfsums:
            if halfsum.contains_angle:
                continue

            # We still don't want natal-only midpoints to natal angles in polywheels, though
            if (
                len(charts) > 1
                and chart.role.value == chart_models.ChartWheelRole.NATAL.value
                and halfsum.point_a.role.value
                == chart_models.ChartWheelRole.NATAL.value
                and halfsum.point_b.role.value
                == chart_models.ChartWheelRole.NATAL.value
            ):
                continue

            ra_midpoint = parse_midpoint(
                options,
                eastpoint_ra_angle,
                halfsum,
                'right_ascension',
                use_mundane_orb=True,
            )
            if ra_midpoint:
                insert_sorted(key, ra_midpoint)

    return midpoints


def find_outermost_chart(
    charts: list[chart_models.ChartObject],
) -> chart_models.ChartObject:
    outermost_chart = charts[0]
    for chart in charts:
        if chart.role > outermost_chart.role:
            outermost_chart = chart
    return outermost_chart


ASPECT_DEFINITIONS = [
    (0, chart_models.AspectType.CONJUNCTION, 1),
    (180, chart_models.AspectType.OPPOSITION, 2),
    (30, chart_models.AspectType.INCONJUNCT, 2.4),
    (120, chart_models.AspectType.TRINE, 3),
    (90, chart_models.AspectType.SQUARE, 4),
    (60, chart_models.AspectType.SEXTILE, 6),
    (7, chart_models.AspectType.SEPTILE, 7),
    (45, chart_models.AspectType.OCTILE, 8),
    (11, chart_models.AspectType.ELEVEN_HARMONIC, 11),
    (30, chart_models.AspectType.INCONJUNCT, 12),
    (13, chart_models.AspectType.THIRTEEN_HARMONIC, 13),
    (16, chart_models.AspectType.SIXTEEN_HARMONIC, 16),
    (
        5,
        chart_models.AspectType.QUINTILE,
        20,
    ),
    (10, chart_models.AspectType.TEN_DEGREE_SERIES, 36),
]


def parse_aspect(
    value: float,
    options: Options,
    use_mundane_orbs: bool = False,
    use_paran_orbs: bool = False,
    allow_harmonics: list[float] = [],
    allow_divisions: list[int] = [],
) -> tuple[chart_models.AspectType, int, float, str]:
    """Returns an aspect type, aspect class 1-3, orb, and strength percent"""
    normalized_value = to360(value)

    for (dictionary_key_degrees, definition, harmonic) in ASPECT_DEFINITIONS:
        if allow_harmonics and len(allow_harmonics):
            allow = False
            for allowed_harmonic in allow_harmonics:
                if allowed_harmonic == harmonic:
                    allow = True
                    break

            if not allow:
                continue

        if use_mundane_orbs:
            orbs = options.mundane_aspects.get(
                str(dictionary_key_degrees), [0, 0, 0]
            )
        elif use_paran_orbs:
            orbs = options.paran_aspects.get('0', [0, 0, 0])
        else:
            orbs = options.ecliptic_aspects.get(
                str(dictionary_key_degrees), [0, 0, 0]
            )

        if not len(orbs):
            continue

        if not orbs[0]:
            continue

        for class_index in range(len(orbs)):
            if orbs[class_index]:
                (is_in_range, aspect_orb) = in_harmonic_range(
                    normalized_value, orbs[class_index], harmonic
                )
                if is_in_range:
                    max_orb = 360
                    if len(orbs) >= 3 and orbs[2]:
                        max_orb = orbs[2]
                    elif len(orbs) >= 2 and orbs[1]:
                        max_orb = orbs[1] * 1.25
                    else:
                        max_orb = orbs[0] * 2.5

                    strength = calc_aspect_strength_percent(
                        max_orb, aspect_orb
                    )
                    return (definition, class_index + 1, aspect_orb, strength)

    return (None, None, None, None)


def calc_planetary_needs_strength(
    options: chart_models.Options,
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

    class_bonuses = [95, 92, 0, 0, 0]
    for [index, aspect_class] in enumerate(aspects_by_class):
        for aspect in aspect_class:
            if max_luminary_aspect_strength != 0:
                break
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
                class_bonuses[index], max_luminary_aspect_strength
            )

    stationary_strength = 75 if planet.is_stationary else 0
    if stationary_strength > 0 and luminary_strength > 0:
        stationary_strength = 90

    normalized_angularity_strength = planet.angularity_strength

    strength = max(
        normalized_angularity_strength,
        luminary_strength,
        max_luminary_aspect_strength,
        stationary_strength,
    )

    return min(strength, 100)


def find_angle_crossings(
    planet: chart_models.PlanetData, geo_latitude: float
) -> tuple[float, float, float, float]:
    """Returns a list of angle crossings, as RAMC values, for planetary data.
    They are in the order of rising, culminating, setting, anticulminating.
    """
    try:
        geo_co_latitude = 90 - geo_latitude

        planet_never_rises = planet.declination > geo_co_latitude

        if planet_never_rises:
            rising = None
            setting = None
        else:
            ascensional_difference = math.degrees(
                math.asin(
                    math.tan(math.radians(geo_latitude))
                    * math.tan(math.radians(planet.declination))
                )
            )

            rising = to360(
                planet.right_ascension + ascensional_difference - 90
            )
            setting = to360(
                planet.right_ascension - ascensional_difference + 90
            )

        return (
            rising,
            planet.right_ascension,
            setting,
            to360(planet.right_ascension + 180),
        )
    except ValueError:
        tkmessagebox.showerror(
            'Paran calculation error',
            f"Error calculating parans for planet {planet.name}; it probably doesn't rise or set at the given latitude",
        )
        return None


def calc_major_angle_paran(
    from_planet: chart_models.PlanetData,
    to_planet: chart_models.PlanetData,
    options: Options,
    geo_latitude: float,
    whole_chart_is_dormant: bool,
):
    show_aspects_type = options.show_aspects or ShowAspect.ALL
    aspect_is_not_foreground = False

    # See if we can short-circuit by skipping non-foreground aspects
    # when we have Show Partile Non-Foreground off
    if show_aspects_type == ShowAspect.ONE_PLUS_FOREGROUND:
        if (
            not from_planet.is_foreground
            and not from_planet.treat_as_foreground
            and not to_planet.is_foreground
            and not to_planet.treat_as_foreground
        ):
            if not options.partile_nf:
                return None
            else:
                aspect_is_not_foreground = True

    elif show_aspects_type == ShowAspect.BOTH_FOREGROUND:
        if (
            not from_planet.treat_as_foreground
            and not to_planet.treat_as_foreground
        ):
            if (
                not from_planet.is_foreground
                and not from_planet.treat_as_foreground
            ) or (
                not to_planet.is_foreground
                and not to_planet.treat_as_foreground
            ):
                if not options.partile_nf:
                    return None
                else:
                    aspect_is_not_foreground = True

    # For dormant ingresses, only show Moon aspects
    if whole_chart_is_dormant and from_planet.name != 'Moon':
        return None

    parans_a = find_angle_crossings(from_planet, geo_latitude)
    parans_b = find_angle_crossings(to_planet, geo_latitude)

    if not parans_a or not parans_b:
        return None

    aspect = None
    relationship = None

    closest_aspect_class = None
    closest_aspect_orb = None
    closest_aspect_strength = None

    # Figure out the aspect as well as the relationship
    for (angle_id_a, crossing_a) in enumerate(parans_a):
        if crossing_a is None:
            continue
        for (angle_id_b, crossing_b) in enumerate(parans_b):
            if crossing_b is None:
                continue

            orb = abs(crossing_a - crossing_b)
            (aspect_type, aspect_class, aspect_orb, strength) = parse_aspect(
                orb, options, use_paran_orbs=True, allow_harmonics=[1]
            )

            if aspect_type:
                if (
                    closest_aspect_orb is None
                    or aspect_orb < closest_aspect_orb
                ):
                    closest_aspect_class = aspect_class
                    closest_aspect_orb = aspect_orb
                    closest_aspect_strength = strength

                    # Conjunctions will be 0, oppositions will be 2, squares will be 1 or 3
                    relationship = math.fabs(angle_id_a - angle_id_b)

    if closest_aspect_orb is not None:
        if aspect_is_not_foreground:
            if closest_aspect_orb < 1 and options.partile_nf:
                closest_aspect_class = 4
            else:
                # We may have found an aspect, but it's neither foreground nor partile
                return None

        aspect_type = None

        if relationship == 0:
            aspect_type = chart_models.AspectType.CONJUNCTION
        elif relationship % 2 == 0:
            aspect_type = chart_models.AspectType.OPPOSITION
        else:
            aspect_type = chart_models.AspectType.SQUARE

        return (
            chart_models.Aspect()
            .as_paran()
            .from_planet(
                from_planet.short_name,
                role=from_planet.role,
            )
            .to_planet(
                to_planet.short_name,
                role=to_planet.role,
            )
            .as_type(aspect_type)
            .with_class(closest_aspect_class)
            .with_strength(closest_aspect_strength)
            .with_orb(closest_aspect_orb)
        )

    return aspect


def get_signed_orb_to_reference(longitude: float, reference: float) -> float:
    if longitude >= reference:
        if longitude - reference >= 180:
            diff = 360 - longitude
            return (reference + diff) * -1

        return longitude - reference

    if reference - longitude >= 180:
        diff = 360 - reference
        return longitude + diff

    return longitude - reference


def calc_novien_aspects(
    radix: chart_models.ChartObject,
    novien_data: chart_models.ChartObject,
    options: Options,
) -> list[list[chart_models.Aspect]]:
    aspects_by_class = [[], [], []]
    charts = [novien_data, radix]

    novien_options = deepcopy(options)

    novien_options.ecliptic_aspects = {
        '0': options.ecliptic_aspects['0'],
        '90': options.ecliptic_aspects['90'],
        '180': options.ecliptic_aspects['180'],
    }

    novien_to_natal_options = deepcopy(novien_options)

    # Only use class 1 aspects for novien-to-natal
    for key in novien_to_natal_options.ecliptic_aspects:
        novien_to_natal_options.ecliptic_aspects[key] = [
            novien_to_natal_options.ecliptic_aspects[key][0],
            0,
            0,
        ]

    for (from_index, from_chart) in enumerate(charts):
        for to_index in range(from_index, 2):
            to_chart = charts[to_index]
            for (
                primary_index,
                (primary_planet_long_name, _),
            ) in enumerate(from_chart.iterate_points(options)):
                for (
                    secondary_index,
                    (secondary_planet_long_name, _),
                ) in enumerate(to_chart.iterate_points(options)):

                    # Skip natal-natal aspects
                    if from_index == 1 and to_index == 1:
                        break

                    if (
                        secondary_index <= primary_index
                        and from_chart == to_chart
                    ):
                        continue

                    is_novien_to_natal = from_index == 0 and to_index == 1

                    primary_planet = (
                        from_chart.planets[primary_planet_long_name]
                        if hasattr(from_chart, 'planets')
                        else from_chart[primary_planet_long_name]
                    )
                    secondary_planet = (
                        to_chart.planets[secondary_planet_long_name]
                        if hasattr(to_chart, 'planets')
                        else to_chart[secondary_planet_long_name]
                    )

                    raw_orb = (
                        abs(
                            primary_planet.longitude
                            - secondary_planet.longitude
                        )
                        % 360
                    )

                    (
                        aspect_type,
                        aspect_class,
                        aspect_orb,
                        aspect_strength,
                    ) = parse_aspect(
                        value=raw_orb,
                        options=novien_to_natal_options
                        if is_novien_to_natal
                        else novien_options,
                    )

                    if not aspect_type:
                        continue

                    if aspect_class > 2:
                        continue

                    if is_novien_to_natal:
                        aspect_class = 3

                    from_planet = (
                        primary_planet
                        if primary_planet.role >= secondary_planet.role
                        else secondary_planet
                    )

                    to_planet = (
                        primary_planet
                        if from_planet == secondary_planet
                        else secondary_planet
                    )

                    from_planet_role = (
                        chart_models.ChartWheelRole.RADIX
                        if from_index == 1
                        else chart_models.ChartWheelRole.NOVIEN
                    )
                    to_planet_role = (
                        chart_models.ChartWheelRole.RADIX
                        if to_index == 1
                        else chart_models.ChartWheelRole.NOVIEN
                    )

                    aspect = (
                        chart_models.Aspect()
                        .from_planet(
                            from_planet.short_name, role=from_planet_role
                        )
                        .to_planet(to_planet.short_name, role=to_planet_role)
                        .as_type(aspect_type)
                        .with_class(aspect_class)
                        .as_ecliptical()
                        .with_strength(aspect_strength)
                        .with_orb(aspect_orb)
                    )

                    aspects_by_class[aspect.aspect_class - 1].append(aspect)

    return aspects_by_class
