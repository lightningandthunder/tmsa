import math
from widgets import base_font
from tkinter.font import Font as tkFont


def get_scaled_font(width: int, breakpoint: int) -> tkFont:
    font_size = (
        18 if width > breakpoint else math.floor(18 * (width / breakpoint))
    )

    return (
        base_font
        if font_size == 18
        else tkFont(family='Lucida Console', size=font_size, weight='normal')
    )


def to360(value):
    if value >= 0.0 and value < 360.0:
        return value
    if value >= 360:
        return to360(value - 360.0)
    if value < 0.0:
        return to360(value + 360.0)


def toDMS(value):
    si = -1 if value < 0 else 1
    value = abs(value)
    d = int(value)
    value = (value - d) * 60
    m = int(value)
    value = (value - m) * 60
    s = round(value)
    if s == 60:
        m += 1
        if m == 60:
            d += 1
    return (d, m, s, si)
