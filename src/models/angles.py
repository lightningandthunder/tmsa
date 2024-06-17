from dataclasses import dataclass
from enum import Enum


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
    ANTI_VERTEX = 'Av'
    BACKGROUND = ' b'
    BLANK = '  '

    def __str__(self):
        return self.value
