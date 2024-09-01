from dataclasses import dataclass
from enum import Enum


@dataclass
class AngleAxes(Enum):
    HORIZONTAL = 'H'
    MERIDIAN = 'M'
    PRIME_VERTICAL = 'V'
    ZENITH_NADIR = 'Z'
    EASTPOINT_WESTPOINT = 'E'
    EASTPOINT_IN_RA = 'Ea'

    def __str__(self):
        return self.value


@dataclass
class ForegroundAngles(Enum):
    ASCENDANT = 'A '
    DESCENDANT = 'D '
    MC = 'M '
    IC = 'I '
    ZENITH = 'Z '
    NADIR = 'N '
    EASTPOINT = 'E '
    WESTPOINT = 'W '
    EASTPOINT_RA = 'Ea'
    WESTPOINT_RA = 'Wa'

    def __str__(self):
        return self.value


@dataclass
class NonForegroundAngles(Enum):
    VERTEX = 'Vx'
    ANTIVERTEX = 'Av'
    BACKGROUND = ' b'
    BLANK = '  '

    def __str__(self):
        return self.value
