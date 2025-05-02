import bisect


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
    value: float, options: Options
) -> tuple[chart_models.AspectType, int, float]:
    '''Returns an aspect type, aspect class (1-indexed), orb, and strength percent'''
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
        (150, chart_models.AspectType.INCONJUNCT, 2.4),
        (72, chart_models.AspectType.QUINTILE, 5),
        (7, chart_models.AspectType.SEPTILE, 7),
        (40, chart_models.AspectType.NOVILE, 9),
        (30, chart_models.AspectType.INCONJUNCT, 12),
        (10, chart_models.AspectType.DECILE, 36),
    ]

    for (degrees, definition, harmonic) in definitions:
        orbs = options.ecliptic_aspects.get(str(degrees))

        if not orbs or not orbs[0]:
            continue

        for orb_index in range(len(orbs)):
            if orbs[orb_index]:
                (is_in_range, aspect_orb) = in_harmonic_range(
                    normalized_value, orbs[orb_index], harmonic
                )
                if is_in_range:
                    max_orb = 360
                    if orbs[2]:
                        max_orb = orbs[2]
                    elif orbs[1]:
                        max_orb = orbs[1] * 1.25
                    else:
                        max_orb = orbs[0] * 2.5

                    strength = calc_aspect_strength_percent(max_orb, aspect_orb)
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
