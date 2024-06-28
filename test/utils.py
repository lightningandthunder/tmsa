from io import TextIOWrapper

from src.models.charts import AspectFramework, AspectType
from collections.abc import Mapping


def assert_line_contains(
    line: str, text: str, starts_at: int = 0, any_position: bool = False
):
    if any_position:
        if text in line:
            return
        else:
            raise AssertionError(
                f"Line {line[starts_at:]}\ndoes not contain\n'{text}'"
            )

    if starts_at > len(line) - 1:
        raise AssertionError(
            f'Line of length {len(line)} cannot be indexed at {starts_at}'
        )

    if len(text) > len(line[starts_at:]):
        raise AssertionError(
            f'Line of length {len(line[starts_at:])} is shorter than text of length {len(text)}'
        )

    for index, char in enumerate(text):
        if not text[index] == char:
            raise AssertionError(
                f"Line {line[starts_at:]}\ndoes not match\n'{text}'\nat index {index}"
            )


def assert_aspect(
    line: str,
    cclass: int,
    planet_1: str,
    planet_2: str,
    aspect_type: AspectType,
    degrees: int,
    minutes: int,
    strength: int,
    type: AspectFramework = AspectFramework.ECLIPTICAL,
):
    aspects = [a.strip() for a in line.split(' ' * 3) if a]
    actual_class = cclass - 1
    if len(aspects) <= actual_class:
        raise AssertionError(
            f'Line {line} does not contain aspect class {cclass}'
        )

    aspect = aspects[actual_class]
    expected = f"{planet_1} {aspect_type.value} {planet_2} {degrees:2d}°{minutes:2}'{strength:3d}%"

    if type != AspectFramework.ECLIPTICAL:
        expected += f' {type.value.upper()}'

    if not aspect == expected:
        raise AssertionError(
            f'Aspect\n\t{aspect}\ndoes not match\n\t{expected}'
        )


def assert_aspects_of_class(lines: list, cclass: int, aspects: list):
    if not len(lines) == len(aspects):
        raise AssertionError(
            'Number of lines does not match number of aspects'
        )
    for line, aspect in enumerate(aspects):
        assert_aspect(lines[line], cclass=cclass, **aspect)


def assert_aspect_class_empty(lines: list, cclass: int):
    for line in lines:
        if not line.strip() == '':
            raise AssertionError(
                f'Aspect class {cclass} is not empty:\n{line}'
            )


def print_file_output(file: str):
    for index, line in enumerate(file.split('\n')):
        print(f'{index: <3}: {line}')


def read_and_print(file: TextIOWrapper):
    for index, line in enumerate(file.readlines()):
        print(f'{index: <3}: {line}')


class FixtureAspect(Mapping):
    def __init__(
        self,
        planet_1: str,
        planet_2: str,
        aspect_type: AspectType,
        degrees: int,
        minutes: int,
        strength: int,
        type: AspectFramework = AspectFramework.ECLIPTICAL,
    ):
        self.planet_1 = planet_1
        self.planet_2 = planet_2
        self.aspect_type = aspect_type
        self.degrees = degrees
        self.minutes = minutes
        self.strength = strength
        self.type = type

    def __getitem__(self, x):
        return self.__dict__[x]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return f"{self.planet_1} {self.aspect_type.value} {self.planet_2} {self.degrees:2d}°{self.minutes:2}'{self.strength:3d}%"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (
            self.planet_1 == other.planet_1
            and self.planet_2 == other.planet_2
            and self.aspect_type == other.aspect_type
            and self.degrees == other.degrees
            and self.minutes == other.minutes
            and self.strength == other.strength
            and self.type == other.type
        )
