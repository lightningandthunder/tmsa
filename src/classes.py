import json
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

from src import log_error, swe
from src.utils.format_utils import to360

T = TypeVar('T', bound='ChartObject')


@dataclass
class PlanetData:
    name: str
    body_number: int
    longitude: float
    latitude: float
    speed: float
    right_ascension: float
    declination: float
    azimuth: float
    altitude: float
    house: float
    meridian_longitude: float

    def with_ecliptic_and_equatorial_data(
        self,
        longitude: float,
        latitude: float,
        speed: float,
        right_ascension: float,
        declination: float,
    ):
        self.longitude = longitude
        self.latitude = latitude
        self.speed = speed
        self.right_ascension = right_ascension
        self.declination = declination
        return self

    def with_azimuth_and_altitude(self, azimuth: float, altitude: float):
        self.azimuth = azimuth
        self.altitude = altitude
        return self

    def with_house_position(self, house: float):
        self.house = house
        return self

    def with_meridian_longitude(self, meridian_longitude: float):
        self.meridian_longitude = meridian_longitude
        return self

    def precess(self, to_chart: T):
        # TODO - check me; not sure I lined up the parameters correctly
        (speed, right_ascension, declination) = swe.cotrans(
            [self.longitude + to_chart.ayanamsa, self.latitude, self.speed],
            to_chart.obliquity,
        )
        self.speed = speed
        self.right_ascension = right_ascension
        self.declination = declination

        (azimuth, altitude) = swe.calc_azimuth(
            to_chart.julian_day_utc,
            to_chart.geo_longitude,
            to_chart.geo_latitude,
            to360(to_chart.ayanamsa + self.longitude),
            self.latitude,
        )
        self.azimuth = azimuth
        self.altitude = altitude

        self.meridian_longitude = swe.calc_meridian_longitude(
            azimuth, altitude
        )
        self.house = swe.calc_house_pos(
            to_chart.ramc,
            to_chart.geo_latitude,
            to_chart.obliquity,
            to360(self.longitude + to_chart.ayanamsa),
            self.latitude,
        )

        return self


@dataclass
class Options:
    def __init__(self):
        pass

    @classmethod
    def from_file(cls, file_path: str):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return cls(data)
            except json.JSONDecodeError:
                log_error(f'Error reading {file_path}')


@dataclass
class NatalOptions(Options):
    pass


@dataclass
class SolunarOptions(Options):
    pass


@dataclass
class IngressOptions(Options):
    pass


@dataclass
class MidpointOptions(Options):
    pass


@dataclass
class CosmobiologyOptions(Options):
    pass


@dataclass
class ChartType(Enum):
    NATAL = 'n'
    SOLAR_RETURN = 'sr'
    LUNAR_RETURN = 'lr'
    INGRESS = 'i'


@dataclass
class ChartObject:
    type: ChartType
    julian_day_utc: float
    ayanamsa: float
    obliquity: float
    geo_longitude: float
    geo_latitude: float
    lst: float
    ramc: float
    planets: dict[str, PlanetData]
    cusps: list[float]
    angles: dict[str, float]

    def __init__(self, data: dict):
        self.type = ChartType(data['type'])
        self.julian_day_utc = data['julian_day_utc']
        self.ayanamsa = data['ayanamsa']
        self.obliquity = data['obliquity']
        self.geo_longitude = data['geo_longitude']
        self.geo_latitude = data['geo_latitude']
        self.lst = data['lst']
        self.ramc = data['ramc']
        self.planets = {
            planet: PlanetData(**data['planets'][planet])
            for planet in data['planets']
        }
        self.cusps = data['cusps']
        self.angles = data['angles']

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return ChartObject(data)
            except json.JSONDecodeError:
                log_error(f'Error reading {file_path}')

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    def precess(self, to_chart: T):
        for planet in self.planets:
            self.planets[planet].precess(to_chart)

        return self


class ChartWheelRole(Enum):
    RADIX = 'r'
    TRANSIT = 't'
    PROGRESSED = 'p'
    INGRESS = 'i'


class Wheel:
    def __init__(
        self,
        charts: dict['role':ChartWheelRole, 'chart':ChartObject],
        options: Options,
    ):
        self.charts = charts
        self.options = options

        if len(charts) > 1:
            if (
                ChartWheelRole.RADIX in charts
                and ChartWheelRole.TRANSIT in charts
            ):
                self.charts[ChartWheelRole.RADIX].precess(
                    self.charts[ChartWheelRole.TRANSIT]
                )

            if (
                ChartWheelRole.PROGRESSED in charts
                and ChartWheelRole.TRANSIT in charts
            ):
                self.charts[ChartWheelRole.PROGRESSED].precess(
                    self.charts[ChartWheelRole.TRANSIT]
                )

    def draw(self):
        pass

    def save(self):
        pass


class AspectType(Enum):
    CONJUNCTION = 'co'
    OCTILE = 'oc'
    SEXTILE = 'sx'
    SQUARE = 'sq'
    TRINE = 'tr'
    OPPOSITION = 'op'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def from_string(cls, string: str):
        if string == 'co':
            return cls.CONJUNCTION
        elif string == 'oc':
            return cls.OCTILE
        elif string == 'sx':
            return cls.SEXTILE
        elif string == 'sq':
            return cls.SQUARE
        elif string == 'tr':
            return cls.TRINE
        elif string == 'op':
            return cls.OPPOSITION
        else:
            return None

    @classmethod
    def from_degrees(cls, degrees: int | str):
        if isinstance(degrees, str):
            degrees = int(degrees)

        if degrees == 0:
            return cls.CONJUNCTION
        elif degrees == 45:
            return cls.OCTILE
        elif degrees == 60:
            return cls.SEXTILE
        elif degrees == 90:
            return cls.SQUARE
        elif degrees == 120:
            return cls.TRINE
        elif degrees == 180:
            return cls.OPPOSITION
        else:
            return None


class AspectFramework(Enum):
    ECLIPTICAL = ''
    MUNDANE = 'm'
    PRIME_VERTICAL_PARAN = 'p'


@dataclass
class Aspect:
    type: AspectType
    aspect_class: int
    strength: float
    orb: float
    planet1_short_name: str
    planet1_role: ChartWheelRole = ''
    planet2_short_name: str
    planet2_role: ChartWheelRole = ''
    framework: AspectFramework

    def as_ecliptical(self):
        self.framework = AspectFramework.ECLIPTICAL
        return self

    def as_mundane(self):
        self.framework = AspectFramework.MUNDANE
        return self

    def as_prime_vertical_paran(self):
        self.framework = AspectFramework.PRIME_VERTICAL_PARAN
        return self

    def from_planet(self, planet: str, role: ChartWheelRole = None):
        self.planet1_short_name = planet
        if role:
            self.planet1_role = role
        return self

    def to_planet(self, planet: str, role: ChartWheelRole = None):
        self.planet2_short_name = planet
        if role:
            self.planet2_role = role
        return self

    def with_orb(self, orb: float):
        self.orb = orb
        return self

    def with_class(self, aspect_class: int):
        self.aspect_class = aspect_class
        return self

    def with_strength(self, strength: float):
        self.strength = strength
        return self

    def as_type(self, type: AspectType):
        self.type = type
        return self

    def __str__(self):
        # TODO - not sure if all of this is right
        return (
            f'{self.planet1_role}{self.planet1_short_name} '
            f'{self.type.value} {self.planet2_role}{self.planet2_short_name} '
            f'{self.strength:.2f} {self.framework.value}'
        ).strip()
