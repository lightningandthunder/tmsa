from src.constants import PROGRESSION_Q2


def get_progressed_jd_utc(
    base: float, target: float, rate=PROGRESSION_Q2
) -> float:
    difference = target - base
    return base + (difference * rate)
