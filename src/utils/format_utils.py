import math
import os


def normalize_text(text, nocap=False, maxlen=33):
    text = text.strip()
    cap = True
    spok = True
    result = ''
    for ch in text:
        if ch.isalpha():
            if cap and not nocap:
                result += ch.upper()
                cap = False
            else:
                result += ch
            spok = True
        elif ch.isspace() and spok:
            result += ' '
            spok = False
            cap = True
        elif ch not in ':\\?*"/<>|~;':
            result += ch
            cap = True
            spok = True
    if len(result) > maxlen:
        result = result[0 : len(result) - maxlen]
    return result


def to360(value):
    if value >= 0.0 and value < 360.0:
        return value
    if value >= 360:
        return value % 360
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


def version_str_to_tuple(version: str) -> tuple[int | str]:
    return tuple(
        map(
            lambda x: int(x) if 'a' not in x and 'b' not in x else str(x),
            (version.split('.')),
        )
    )


def version_tuple_to_str(version: tuple[int | str]) -> str:
    return '.'.join(map(str, version))


def parse_version_from_txt_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        last_line = file.readlines()[-1]
        elements = last_line.split(' ')
        for element in elements:
            if '.' in element:
                return version_str_to_tuple(element)
    return (0, 0, 0)
