import math
from typing import Literal
from src.models.charts import (
    ChartObject,
    ChartType,
    ChartWheelRole,
)
from src.swe import calc_moon_crossing, calc_planet, calc_sun_crossing, revjul
from src.utils.calculation_utils import get_signed_orb_to_reference
from src.utils.format_utils import to360
from src.utils.transits.progressions import (
    ProgressionTypes,
    get_progressed_jd_utc,
)


def set_up_progressed_params(params: dict, date: float, chart_type: str):
    progressed_params = {**params}
    (p_year, p_month, p_day, p_time) = revjul(date, params['style'])
    progressed_params['year'] = p_year
    progressed_params['month'] = p_month
    progressed_params['day'] = p_day
    progressed_params['time'] = p_time
    progressed_params['type'] = chart_type

    progressed_chart = ChartObject(progressed_params).with_role(
        ChartWheelRole.PROGRESSED
    )
    params['progressed_chart'] = progressed_chart
    return params


def find_julian_days_for_aspect_to_progressed_body(
    radix_jd: float,
    search_start_jd: float,
    search_end_jd: float,
    body_number: int,
    radix_sun_longitude: float,
    relationship: Literal['full', 'demi', 'Q1', 'Q3'],
) -> tuple[float, float] | tuple[None, None]:
    """Returns julian day for progressed chart, julian day for transiting chart"""
    low = search_start_jd
    high = search_end_jd

    precision = 7

    previous_check = None

    target_signed_orb = 0

    if relationship == 'demi':
        target_signed_orb = 180
    elif relationship == 'Q1':
        target_signed_orb = -90
    elif relationship == 'Q3':
        target_signed_orb = 90

    while True:
        transit_date = (low + high) / 2
        derived_progressed_date = get_progressed_jd_utc(
            radix_jd,
            transit_date,
            radix_sun_longitude,
            ProgressionTypes.Q2.value,
        )

        transiting_longitude = round(
            calc_planet(transit_date, body_number)[0], precision
        )
        progressed_longitude = round(
            calc_planet(derived_progressed_date, body_number)[0], precision
        )

        signed_orb = get_signed_orb_to_reference(
            transiting_longitude, progressed_longitude
        )
        signed_orb = round(signed_orb, precision)

        # TODO - this needs to be + or - depending on whether the difference to target is + or -
        difference_to_target = (target_signed_orb + signed_orb) % 360

        if previous_check and previous_check == difference_to_target:
            return (None, None)

        if difference_to_target == 0 or high <= low:
            if math.fabs(difference_to_target) > 0.01:
                return (None, None)
            break

        if math.fabs(difference_to_target) < 180:
            if difference_to_target > 0:
                high = transit_date
            else:
                low = transit_date
        else:
            if difference_to_target < 0:
                high = transit_date
            else:
                low = transit_date

        previous_check = difference_to_target

    return (derived_progressed_date, transit_date)


def find_solunar_crossings_until_date(
    base_start: float,
    continue_until_date: float,
    grace_period: float,
    target_body: Literal['Sun', 'Moon'],
    target_longitude: float,
    cycle_length: int,
    solunar_type: str,
) -> list[float]:

    target = target_longitude
    start = base_start

    solunar_name_normalized = solunar_type.lower()

    dates = []

    next_increment = cycle_length

    grace_period_normalized = grace_period or 0

    if 'demi' in solunar_name_normalized:
        target = (target_longitude + 180) % 360
        next_increment = math.ceil(cycle_length / 2)
        grace_period_normalized /= 2

    elif 'quarti' in solunar_name_normalized:
        next_increment = math.ceil(cycle_length / 4)
        grace_period_normalized /= 4

        if 'first' in solunar_name_normalized:
            target = (target_longitude + 90) % 360
        else:
            target = to360(target_longitude - 90)

    while start <= continue_until_date:
        if target_body == 'Sun':
            date = calc_sun_crossing(target, start)
        else:
            date = calc_moon_crossing(target, start)

        if date and (
            (date < continue_until_date)
            or (date - continue_until_date < grace_period)
        ):
            dates.append(date)

        start += next_increment

    return dates


def find_novienic_crossings_until_date(
    base_start: float,
    continue_until_date: float,
    grace_period: float,
    target_body: Literal['Sun', 'Moon'],
    target_longitude: float,
    cycle_length: int,
    solunar_type: str,
) -> list[float]:

    target = target_longitude
    start = base_start

    crossing_func = (
        calc_sun_crossing if target_body == 'Sun' else calc_moon_crossing
    )

    return_dates = []

    definition_increment = 40
    normalized_grace_period = grace_period or 0

    if solunar_type in [
        ChartType.TEN_DAY_SOLAR_RETURN.value,
        ChartType.NOVIENIC_LUNAR_RETURN.value,
    ]:
        definition_increment = 10
        normalized_grace_period /= 4

    while start <= continue_until_date:
        dates_in_cycle = []
        current_increment = 0

        while current_increment < 360:
            date = crossing_func(to360(target + current_increment), start)
            dates_in_cycle.append(date)

            current_increment += definition_increment

        for date in dates_in_cycle:
            if (date < continue_until_date) or (
                date - continue_until_date < normalized_grace_period
            ):
                return_dates.append(date)

        start += cycle_length

    return sorted(return_dates)


def find_progressed_crossings_until_date(
    base_start: float,
    continue_until_date: float,
    grace_period: float,
    target_body: Literal['Sun', 'Moon'],
    radix_julian_day_utc: float,
    radix_sun_longitude: float,
    cycle_length: int,
    solunar_type: str,
) -> list[float]:

    start = base_start
    next_increment = cycle_length

    return_dates = []

    solunar_name_normalized = solunar_type.lower()
    relationship = 'full'

    if 'demi' in solunar_name_normalized:
        next_increment = math.ceil(cycle_length / 2)
        relationship = 'demi'
    elif 'quarti' in solunar_name_normalized:
        next_increment = math.ceil(cycle_length / 4)

        if 'first' in solunar_name_normalized:
            relationship = 'Q1'
        else:
            relationship = 'Q3'

    while start <= continue_until_date:
        lower_bound = start
        higher_bound = start + next_increment

        (
            progressed_jd,
            transit_jd,
        ) = find_julian_days_for_aspect_to_progressed_body(
            radix_julian_day_utc,
            lower_bound,
            higher_bound,
            0 if target_body == 'Sun' else 1,
            radix_sun_longitude,
            relationship,
        )
        if progressed_jd and transit_jd:
            if (transit_jd < continue_until_date) or (
                transit_jd - continue_until_date <= (grace_period or 0)
            ):
                return_dates.append(
                    {
                        'transit': transit_jd,
                        'progressed': progressed_jd,
                    }
                )

        start += next_increment

    return sorted(return_dates, key=lambda x: x['transit'])


def find_progressed_anlunar_crossings_until_date(
    base_start: float,
    continue_until_date: float,
    grace_period: float,
    radix_sun_longitude: float,
    solunar_type: str,
) -> list[dict]:

    start = base_start

    return_dates = []

    relationship = 'full'
    next_increment = 28

    if solunar_type == ChartType.KINETIC_DEMI_ANLUNAR_RETURN.value:
        relationship = 'demi'
        next_increment = 14
    elif solunar_type == ChartType.FIRST_QUARTI_KINETIC_ANLUNAR_RETURN.value:
        relationship = 'Q1'
        next_increment = 7
    elif solunar_type == ChartType.LAST_QUARTI_KINETIC_ANLUNAR_RETURN.value:
        relationship = 'Q3'
        next_increment = 7

    while start <= continue_until_date:
        # Get previous solar return
        solar_return_date = calc_sun_crossing(radix_sun_longitude, start - 366)

        lower_bound = start
        higher_bound = start + next_increment

        (
            progressed_jd,
            transit_jd,
        ) = find_julian_days_for_aspect_to_progressed_body(
            solar_return_date,
            lower_bound,
            higher_bound,
            1,
            radix_sun_longitude,
            relationship,
        )
        if progressed_jd and transit_jd:
            if (transit_jd < continue_until_date) or (
                transit_jd - continue_until_date <= (grace_period or 0)
            ):
                return_dates.append(
                    {
                        'transit': transit_jd,
                        'progressed': progressed_jd,
                    }
                )

        start += next_increment

    return sorted(return_dates, key=lambda x: x['transit'])


def append_applicable_returns(
    returns: list,
    return_args_list: list,
    args: tuple,
    burst: bool,
    active: bool,
):
    if not burst:
        if active:
            returns = returns[-1] if len(returns) else []
        else:
            returns = [returns[0]] if len(returns) else []

    for date in returns:
        if not isinstance(date, dict):
            return_args_list.append(({**args[0]}, date, *args[2:]))
        else:
            transit_date = date.get('transit')
            progressed_date = date.get('progressed')

            if transit_date and progressed_date:
                progressed_params = set_up_progressed_params(
                    {**args[0]},
                    progressed_date,
                    args[2],
                )

                return_args_list.append(
                    (
                        progressed_params,
                        transit_date,
                        *args[2:],
                    )
                )
