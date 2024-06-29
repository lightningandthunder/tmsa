import json
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

from src import log_error, swe
from src.models.options import Options
from src.utils.chart_utils import convert_house_to_pvl, fmt_dm
from src.utils.format_utils import to360

T = TypeVar('T', bound='ChartObject')


@dataclass
class PlanetData:
    name: str
    short_name: str
    number: int
    longitude: float
    latitude: float
    speed: float
    right_ascension: float
    declination: float
    azimuth: float
    altitude: float
    house: float
    prime_vertical_longitude: float
    meridian_longitude: float
    treat_as_foreground: bool

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
        self.prime_vertical_longitude = convert_house_to_pvl(house)
        return self

    def with_meridian_longitude(self, meridian_longitude: float):
        self.meridian_longitude = meridian_longitude
        return self

    def precess_to(self, to_chart: T):
        (right_ascension, declination) = swe.cotrans(
            [self.longitude + to_chart.ayanamsa, self.latitude, self.speed],
            to_chart.obliquity,
        )
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

        self.prime_vertical_longitude = convert_house_to_pvl(self.house)

        return self


@dataclass
class ChartType(Enum):
    NATAL = 'Natal'
    SOLAR_RETURN = 'Solar Return'
    LUNAR_RETURN = 'Lunar Return'
    KINETIC_LUNAR_RETURN = 'Kinetic Lunar Return'
    KINETIC_SOLAR_RETURN = 'Kinetic Solar Return'
    NOVIENIC_SOLAR_RETURN = 'Novienic Solar Return'
    TEN_DAY_SOLAR_RETURN = '10-Day Solar Return'
    NOVIENIC_LUNAR_RETURN = 'Novienic Lunar Return'
    EIGHTEEN_HOUR_LUNAR_RETURN = '18-Hour Lunar Return'
    ANLUNAR_RETURN = 'Anlunar Return'
    KINETIC_ANULAR_RETURN = 'Kinetic Anlunar Return'
    SOLILUNAR_RETURN = 'Solilunar Return'
    LUNISOLAR_RETURN = 'Lunisolar Return'
    CAP_SOLAR = 'Capsolar'
    ARI_SOLAR = 'Arisolar'
    CAN_SOLAR = 'Cansolar'
    LIB_SOLAR = 'Libsolar'
    CAP_LUNAR = 'Caplunar'
    ARI_LUNAR = 'Arilunar'
    CAN_LUNAR = 'Canlunar'
    LIB_LUNAR = 'Liblunar'


@dataclass
class ChartObject:
    name: str | None
    year: int
    month: int
    day: int
    location: str
    time: str
    zone: str
    correction: str
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
    notes: str | None = None

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

    def precess_to(self, to_chart: T):
        for planet in self.planets:
            self.planets[planet].precess_to(to_chart)

        return self


class ChartWheelRole(Enum):
    RADIX = 'r'
    TRANSIT = 't'
    PROGRESSED = 'p'
    INGRESS = 'i'


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
        elif degrees == 135:
            return cls.OCTILE
        elif degrees == 180:
            return cls.OPPOSITION
        else:
            return None

    @staticmethod
    def degrees_from_abbreviation(abbreviation: str):
        if abbreviation == 'co':
            return 0
        elif abbreviation == 'oc':
            return 45
        elif abbreviation == 'sx':
            return 60
        elif abbreviation == 'sq':
            return 90
        elif abbreviation == 'tr':
            return 120
        elif abbreviation == 'op':
            return 180
        else:
            return None

    @staticmethod
    def abbreviation_from_degrees(degrees: int):
        if degrees == 0:
            return 'co'
        elif degrees == 45:
            return 'oc'
        elif degrees == 60:
            return 'sx'
        elif degrees == 90:
            return 'sq'
        elif degrees == 120:
            return 'tr'
        elif degrees == 135:
            return 'oc'
        elif degrees == 180:
            return 'op'
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
    strength: int
    orb: float
    framework: AspectFramework
    planet1_short_name: str
    planet2_short_name: str
    planet1_role: ChartWheelRole = ''
    planet2_role: ChartWheelRole = ''

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

    def with_strength(self, strength: int):
        self.strength = strength
        return self

    def as_type(self, type: AspectType):
        self.type = type
        return self

    def get_formatted_orb(self):
        return fmt_dm(abs(self.orb), True)

    def __str__(self):
        # This will read something like this:
        # t.Ur co r.Su 1°23' 95% M
        text = (
            f'{self.planet1_role}{self.planet1_short_name} '
            f'{self.type.value} {self.planet2_role}{self.planet2_short_name} '
            f"{self.get_formatted_orb()} {self.strength:.2f}{(' ' + self.framework.value) if self.framework.value != '' else ''}"
        )

        return text.strip
