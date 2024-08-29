from src.swe import calc_planet
from src.utils.transits.progressions import get_progressed_jd_utc


def find_klr_julian_day(
    radix_moon: float, radix_jd: float, base_jd: float, harmonic: int = 1
) -> float:
    prev_orb = 360 / harmonic
    current_orb = 360 / harmonic

    max_jd = base_jd + 28
    target_jd = (base_jd + max_jd) / 2
    while prev_orb > 0.001:
        progressed_jd = get_progressed_jd_utc(radix_jd, target_jd)
        target_longitude = calc_planet(target_jd, 0)[0]

        current_orb = abs(target_longitude - radix_moon)
        if current_orb < prev_orb:

            base_jd = target_jd
