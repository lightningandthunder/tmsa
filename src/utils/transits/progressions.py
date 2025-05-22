from enum import Enum

from src.constants import PROGRESSION_Q2
from src.swe import calc_planet, calc_sun_crossing


class ProgressionTypes(Enum):
    Q1 = 'Q1'
    Q2 = 'Q2'
    PSSR = 'PSSR'
    TERTIARY = 'Tertiary'
    QUATERNARY = 'Quaternary'


SIDEREAL_YEAR_LENGTH = 365.256363004
SOLAR_RA_PER_YEAR_PLUS_PRECESSION = 360.0139583333


def get_progressed_jd_utc(
    base_jd: float,
    target_jd: float,
    radix_sun_longitude: float,
    progression_type: ProgressionTypes,
    base_is_ssr: bool = False,
    use_apparent_rate: bool = False,
) -> float:

    # This is the simplified way to do it
    # prog_days = (target_jd - base_jd) * PROGRESSION_Q2
    # prog_jd = base_jd + prog_days
    # return prog_jd

    if progression_type in [
        ProgressionTypes.Q1.value,
        ProgressionTypes.Q2.value,
    ]:
        age = int(target_jd - base_jd)

        years_old = int(age / SIDEREAL_YEAR_LENGTH)

        previous_ssr_jd = (
            calc_sun_crossing(radix_sun_longitude, target_jd - 366)
            if not base_is_ssr
            else base_jd
        )
        next_ssr_jd = calc_sun_crossing(radix_sun_longitude, target_jd)

        time_increment = None
        if use_apparent_rate:
            # get RA of both suns
            transiting_sun_ra = calc_planet(target_jd, 0)[3]
            ssr_sun_ra = calc_planet(previous_ssr_jd, 0)[3]

            time_increment = (
                transiting_sun_ra - ssr_sun_ra
            ) / SOLAR_RA_PER_YEAR_PLUS_PRECESSION
        else:
            time_increment = (target_jd - previous_ssr_jd) / (
                next_ssr_jd - previous_ssr_jd
            )

        day_length = 1.0
        if progression_type == ProgressionTypes.Q1.value:
            day_length = 0.997269566
        elif progression_type == ProgressionTypes.PSSR.value:
            day_length = (next_ssr_jd - previous_ssr_jd) - 364

        age = years_old + time_increment
        age *= day_length

        progression_jd = base_jd + age

        # print('Progressed JD: ', progression_jd)

        return progression_jd
