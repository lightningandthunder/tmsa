import bisect


from src import *
from src import constants
from src.models.options import Options
import src.models.charts as chart_models
from src.utils.chart_utils import (
    POS_SIGN,
    convert_raw_strength_to_modified,
    inrange,
)
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

                    primary_data = primary_point
                    secondary_data = secondary_point

                    if primary_point_is_angle:
                        primary_data = chart_models.AngleData(
                            name=primary_point_name,
                            short_name=primary_point_name,
                            longitude=primary_point,
                            role=from_chart.role,
                        )

                    if secondary_point_is_angle:
                        secondary_data = chart_models.AngleData(
                            name=secondary_point_name,
                            short_name=secondary_point_name,
                            longitude=secondary_point,
                            role=to_chart.role,
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


# TODO - make this use PlanetData and AngleData instead of loose info
def parse_midpoint(
    options: Options,
    point_data: chart_models.PlanetData | chart_models.AngleData,
    halfsum: chart_models.HalfSum,
    coordinates: str,
    use_mundane_orb=False,
):
    raw_orb_mins = (
        abs(getattr(point_data, coordinates) - getattr(halfsum, coordinates))
        % 180
    ) * 60

    framework = (
        chart_models.AspectFramework.ECLIPTICAL
        if not use_mundane_orb
        else chart_models.AspectFramework.MUNDANE
    )

    conjunction_orb = (
        options.midpoints.get('0', 0)
        if not use_mundane_orb
        else options.midpoints.get('M', 0)
    )

    if inrange(value=raw_orb_mins, center=0, orb=conjunction_orb):
        return chart_models.MidpointAspect(
            midpoint_type=chart_models.MidpointAspectType.DIRECT,
            orb_minutes=raw_orb_mins,
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )

    square_orb = (
        options.midpoints.get('90', 0)
        if not use_mundane_orb
        else options.midpoints.get('M', 0)
    )

    if inrange(value=raw_orb_mins, center=90, orb=square_orb):
        direction = (
            chart_models.MidpointAspectType.DIRECT
            if options.midpoints.get('is90', 'd') == 'd'
            else chart_models.MidpointAspectType.INDIRECT
        )
        return chart_models.MidpointAspect(
            midpoint_type=direction,
            orb_minutes=raw_orb_mins,
            framework=framework,
            from_point_data=point_data,
            to_midpoint=halfsum,
        )

    if use_mundane_orb:
        return

    octile_orb = (
        options.midpoints.get('45', 0)
        if not use_mundane_orb
        else options.midpoints.get('M', 0)
    )

    if inrange(value=raw_orb_mins, center=45, orb=octile_orb) or inrange(
        value=raw_orb_mins, center=135, orb=octile_orb
    ):
        return chart_models.MidpointAspect(
            midpoint_type=chart_models.MidpointAspectType.INDIRECT,
            orb_minutes=raw_orb_mins,
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
                        role=None,
                    )

                # Get all ecliptical midpoints
                ecliptical_midpoint = parse_midpoint(
                    options, planet_data, halfsum, 'longitude'
                )
                if ecliptical_midpoint:
                    insert_sorted(key, ecliptical_midpoint)

                # Get all PVL midpoints
                pvl_midpoint = parse_midpoint(
                    options,
                    planet_data,
                    halfsum,
                    'prime_vertical_longitude',
                    use_mundane_orb=True,
                )
                if pvl_midpoint:
                    insert_sorted(key, pvl_midpoint)

                # Get all RA midpoints
                ra_midpoint = parse_midpoint(
                    options,
                    planet_data,
                    halfsum,
                    'right_ascension',
                    use_mundane_orb=True,
                )
                if ra_midpoint:
                    insert_sorted(key, ra_midpoint)

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
                        temp_key = make_midpoint_key(
                            short_name='Z'
                            if point_short_name == 'As'
                            else 'EP',
                            role=chart.role,
                        )
                        insert_sorted(temp_key, pseudo_mundane_midpoint)

    return midpoints


# TODO - still need to calculate mundane contacts to major angles
def find_applicable_midpoints_for_point(
    midpoints: dict[str, list[chart_models.MidpointAspect]],
    options: Options,
    planet_data: chart_models.PlanetData | chart_models.AngleData,
    must_be_foreground: bool = False,
) -> list[chart_models.MidpointAspect]:

    only_mundane_enabled = (
        not options.midpoints.get('0')
        and not options.midpoints.get('90')
        and bool(options.midpoints.get('M'))
    )

    square_is_direct = options.midpoints.get('is90') == 'd'

    if planet_data.short_name in constants.ANGLE_ABBREVIATIONS:
        pass

    key = make_midpoint_key(planet_data.short_name, planet_data.role)

    # TODO - these midpoints should be getting inserted in order

    applicable_midpoints = []
    # In natals, all ecliptical midpoints apply
    if not must_be_foreground and not only_mundane_enabled:
        for mid in midpoints[key]:
            if (
                mid.framework.value
                == chart_models.AspectFramework.ECLIPTICAL.value
            ):
                applicable_midpoints.append(mid)

    # In natal: Ecliptic On: Any ecliptic contact to Asc/MC counts.
    # In natal: List all mundane contacts to major angles.

    # Assume 2 planets are straddling ascendant...
    # Ecliptic On / Direct: list as Asc.
    # Ecliptic On / Indirect: list as Asc.
    # Ecliptic No / Direct: list as Zenith.
    #   (i.e. include even if ecliptic is off)
    # Ecliptic No / Indirect: Not listed.

    # Ingress PVL, at least one planet angular in PVL: counts.
    # Ingress PVL, neither planet angular in PVL: doesn't count.
    # Ingress RA, both planets angular in RA: counts.
    # Ingress RA, one planet angular in RA: doesn't count.
    # In ingress: Both foreground on Z/N: ecliptic contact counts.
    # In ingress: Planets not foreground: doesn't count.

    # In ingress: ecliptic planet=planet/planet:
    #   if planet is foreground somehow, counts.
    #   if planet is not foreground somehow, doesn't count.

    pass


def planet_aspecting_halfsum_is_foreground(
    planet: chart_models.PlanetData,
    midpoint: chart_models.MidpointAspect,
    require_same_framework: bool = False,
):
    return True


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
