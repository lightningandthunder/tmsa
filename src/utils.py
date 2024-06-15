import math
from src.user_interfaces.widgets import base_font
from tkinter.font import Font as tkFont
import os
from src.constants import PLATFORM
import shutil
import subprocess


def open_file(file: str):
    match PLATFORM:
        case 'Win32GUI':
            os.startfile(file)
        case 'linux':
            if shutil.which('xdg-open'):
                subprocess.call(['xdg-open', file])
            elif 'EDITOR' in os.environ:
                subprocess.call([os.environ['EDITOR'], file])
        case 'darwin':
            subprocess.run(['open', '-a', 'TextEdit', file])


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


def cotangent(radians: float) -> float:
    return 1 / math.tan(radians)


def arccotangent(radians: float) -> float:
    return math.atan(1 / radians)


def display_name(path):
    name = os.path.basename(path)
    name = name[0:-4]
    if name.count('~') == 1:
        return name.replace('~', ': ')
    parts = name.split('~')
    index = parts[0].find(';')
    if index > -1:
        parts[0] = parts[0][0:index]
    return f'{parts[0]} ({parts[1]}) {parts[2]}'


def north_azimuth(azimuth: float):
    return azimuth > 270 or azimuth < 90


def southern_azimuth(azimuth: float):
    return 90 < azimuth < 270


def add_360_if_negative(angle: float):
    if angle < 0:
        angle += 360
    return angle
