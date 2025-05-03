import bisect
import math


from src import *
from src import constants
from src.models.angles import ForegroundAngles
from src.models.options import Options
import src.models.charts as chart_models
from src.utils.chart_utils import (
    POS_SIGN,
    calc_aspect_strength_percent,
    convert_raw_strength_to_modified,
    in_harmonic_range,
)
from src.utils.format_utils import to360


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


def parse_aspect(
    value: float,
    options: Options,
    use_mundane_orbs: bool = False,
    use_paran_orbs: bool = False,
    allow_harmonics: list[float] = [1],
) -> tuple[chart_models.AspectType, int, float, str]:
    """Returns an aspect type, aspect class (1-indexed), orb, and strength percent"""
    normalized_value = to360(value)

    definitions = [
        # Hard aspects
        (0, chart_models.AspectType.CONJUNCTION, 1),
        (180, chart_models.AspectType.OPPOSITION, 2),
        (90, chart_models.AspectType.SQUARE, 4),
        (45, chart_models.AspectType.OCTILE, 8),
        # Soft aspects
        (120, chart_models.AspectType.TRINE, 3),
        (60, chart_models.AspectType.SEXTILE, 6),
        # Overlapping or niche cases
        (30, chart_models.AspectType.INCONJUNCT, 2.4),
        (7, chart_models.AspectType.SEPTILE, 7),
        (40, chart_models.AspectType.NOVILE, 9),
        (30, chart_models.AspectType.INCONJUNCT, 12),
        (
            72,
            chart_models.AspectType.QUINTILE,
            20,
        ),  # 18°, 36°, 72°; covers decile and vigintile/semidecile
        (10, chart_models.AspectType.NOVILE_SQUARE, 36),  # or Trigintasextile?
    ]

    # Note that definition_degrees is not the actual degrees used,
    # only the key in the options dict for the orb.
    # Examples are semisextile and quincunx sharing 150,
    # and septile using 7 despite the actual aspect being 51.whatever
    for (definition_degrees, definition, harmonic) in definitions:
        if allow_harmonics:
            allow = False
            for allowed_harmonic in allow_harmonics:
                if allowed_harmonic % harmonic == 0:
                    allow = True
                    break

            if not allow:
                continue

        if use_mundane_orbs:
            orbs = options.mundane_aspects.get(str(definition_degrees), [0])
        elif use_paran_orbs:
            orbs = options.paran_aspects.get('0', [0])
        else:
            orbs = options.ecliptic_aspects.get(str(definition_degrees), [0])

        if not orbs[0]:
            continue

        for orb_index in range(len(orbs)):
            if orbs[orb_index]:
                (is_in_range, aspect_orb) = in_harmonic_range(
                    normalized_value, orbs[orb_index], harmonic
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
                    return (definition, orb_index + 1, aspect_orb, strength)

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

    normalized_angularity_strength = planet.angularity_strength

    if options.use_raw_angularity_score:
        # Figure out which angularity model we're using and flesh out the 0-100 score
        normalized_angularity_strength = convert_raw_strength_to_modified(
            options, planet.angularity_strength, planet.angle
        )

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

    ascensional_difference = math.degrees(
        math.asin(
            math.tan(math.radians(geo_latitude))
            * math.tan(math.radians(planet.declination))
        )
    )
    geo_co_latitude = 90 - geo_latitude

    planet_never_rises = planet.declination > geo_co_latitude

    rising = (
        None
        if planet_never_rises
        else to360(planet.right_ascension + ascensional_difference - 90)
    )
    setting = (
        None
        if planet_never_rises
        else to360(planet.right_ascension - ascensional_difference + 90)
    )

    return (
        rising,
        planet.right_ascension,
        setting,
        to360(planet.right_ascension + 180),
    )


def calc_major_angle_paran(
    from_planet: chart_models.PlanetData,
    to_planet: chart_models.PlanetData,
    options: Options,
    geo_latitude: float,
):
    parans_a = find_angle_crossings(from_planet, geo_latitude)
    parans_b = find_angle_crossings(to_planet, geo_latitude)

    lowest_orb = None
    aspect = None

    closest_aspect_type = None
    closest_aspect_class = None
    closest_aspect_orb = None
    closest_aspect_strength = None

    for crossing_a in parans_a:
        for crossing_b in parans_b:
            orb = to360(abs(crossing_a - crossing_b))
            (aspect_type, aspect_class, aspect_orb, strength) = parse_aspect(
                orb, options, use_paran_orbs=True, allow_harmonics=[4]
            )

            if aspect_type:
                if lowest_orb is None or aspect_orb < lowest_orb:
                    lowest_orb = aspect_orb
                    closest_aspect_type = aspect_type
                    closest_aspect_class = aspect_class
                    closest_aspect_orb = aspect_orb
                    closest_aspect_strength = strength

    if lowest_orb is not None:
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
            .as_type(closest_aspect_type)
            .with_class(closest_aspect_class)
            .with_strength(closest_aspect_strength)
            .with_orb(closest_aspect_orb)
        )

    return aspect
