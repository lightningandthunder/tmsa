import bisect


from src import *
from src import constants
from src.models.options import Options
import src.models.charts as chart_models
from src.utils.chart_utils import POS_SIGN, convert_raw_strength_to_modified
from src.utils.format_utils import to360


def calc_halfsums(
    options: Options,
    charts: list[chart_models.ChartObject],
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
