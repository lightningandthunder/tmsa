import math
from typing import Literal
from src.models.charts import (
    LUNAR_RETURNS,
    SOLAR_RETURNS,
    ChartObject,
    ChartWheelRole,
)
from src.swe import calc_moon_crossing, calc_planet, calc_sun_crossing, revjul
from src.utils.calculation_utils import get_signed_orb_to_reference
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
        difference_to_target = target_signed_orb + signed_orb

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

    while start <= continue_until_date:
        next_increment = cycle_length

        if 'demi' in solunar_name_normalized:
            target = (target_longitude + 180) % 360
            next_increment = math.ceil(cycle_length / 2)
        elif 'quarti' in solunar_name_normalized:
            next_increment = math.ceil(cycle_length / 4)

            if 'first' in solunar_name_normalized:
                target = (target_longitude + 90) % 360
            else:
                target = (target_longitude - 90) % 360

        if target_body == 'Sun':
            date = calc_sun_crossing(target, start)
        else:
            date = calc_moon_crossing(target, start)

        if (
            date
            and (date < continue_until_date)
            or (date - continue_until_date < grace_period)
        ):
            dates.append(date)

        start += next_increment

    return dates


def find_novienic_returns_until_date(
    base_start: float,
    continue_until_date: float,
    grace_period: float,
    target_body: Literal['Sun', 'Moon'],
    target_longitude: float,
    cycle_length: int,
    solunar_type: str,
) -> list[float]:

    pass
