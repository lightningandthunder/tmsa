import itertools
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, TypeVar

from src import log_error, swe
from src.constants import PLANETS
from src.models.angles import ForegroundAngles, NonForegroundAngles
from src.models.options import NodeTypes, Options
from src.utils.chart_utils import (
    SIGNS_SHORT,
    convert_house_to_pvl,
    fmt_dm,
)
from src.utils.format_utils import to360

T = TypeVar('T', bound='ChartObject')


class ChartWheelRole(Enum):
    NATAL = ''
    TRANSIT = 't'
    PROGRESSED = 'p'
    SOLAR = 's'
    RADIX = 'r'
    INGRESS = 'i'

    def __eq__(self, other):
        if isinstance(other, ChartWheelRole):
            return self.value == other.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ChartWheelRole):
            order = {
                'i': 1,
                'r': 2,
                's': 3,
                'p': 4,
                't': 5,
                '': 6,
            }
            return order[self.value] < order[other.value]
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, ChartWheelRole):
            return self < other or self == other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, ChartWheelRole):
            return not self < other and self != other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, ChartWheelRole):
            return self > other or self == other
        return NotImplemented


@dataclass
class PlanetData:
    name: str = ''
    short_name: str = ''
    number: int = -1
    longitude: float = 0
    latitude: float = 0
    speed: float = 0
    right_ascension: float = 0
    declination: float = 0
    azimuth: float = 0
    altitude: float = 0
    house: float = 0
    prime_vertical_longitude: float = 0
    meridian_longitude: float = 0
    treat_as_foreground: bool = False
    role: ChartWheelRole = ChartWheelRole.NATAL
    angle: ForegroundAngles | NonForegroundAngles = NonForegroundAngles.BLANK
    all_angles_contacted: list[ForegroundAngles | NonForegroundAngles] = field(
        default_factory=lambda: []
    )
    prime_vertical_angle: NonForegroundAngles = NonForegroundAngles.BLANK
    angularity_strength: int = 0
    is_stationary: bool = False

    __prime_vertical_angles = [
        NonForegroundAngles.VERTEX.value,
        NonForegroundAngles.ANTIVERTEX.value,
    ]

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

    def with_role(self, role: ChartWheelRole):
        self.role = role
        return self

    def with_angle(self, angle: ForegroundAngles | NonForegroundAngles):
        self.angle = angle
        return self

    def with_prime_vertical_angle(self, angle: NonForegroundAngles):
        self.prime_vertical_angle = angle
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

        self.prime_vertical_longitude = self.house

        return self

    @property
    def is_foreground(self):
        return self.angle != NonForegroundAngles.BLANK

    @property
    def is_on_prime_vertical(self):
        return self.prime_vertical_angle.value in self.__prime_vertical_angles

    @property
    def name_with_role(self):
        return f'{self.role.value}{self.short_name}'


@dataclass
class ChartType(Enum):
    RADIX = 'Radix'
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
    vertex: list[float]
    eastpoint: list[float]
    role: ChartWheelRole
    notes: str | None = None
    style: int = 1
    version: tuple[int | str] = (0, 0, 0)
    sun_sign: str = ''
    moon_sign: str = ''

    def __init__(self, data: dict):
        self.type = ChartType(data['type'])
        self.name = data.get('name', None)
        self.year = data['year']
        self.month = data['month']
        self.day = data['day']
        self.location = data['location']
        self.time = data['time']
        self.zone = data['zone']
        self.correction = data['correction']

        planet_data = data['Sun'][0]
        planet = PlanetData()

        self.sun_sign = SIGNS_SHORT[int(data['Sun'][0] // 30)]
        self.moon_sign = SIGNS_SHORT[int(data['Moon'][0] // 30)]

        self.julian_day_utc = swe.julday(
            data['year'],
            data['month'],
            data['day'],
            data['time'] + data['correction'],
            data.get('style', 1),
        )
        if data['zone'] == 'LAT':
            self.julian_day_utc = swe.calc_lat_to_lmt(
                self.jd, data['longitude']
            )
        self.ayanamsa = data['ayan']
        self.obliquity = data.get(
            'oe', swe.calc_obliquity(self.julian_day_utc)
        )
        self.geo_longitude = data['longitude']
        self.geo_latitude = data['latitude']

        (cusps, angles) = swe.calc_cusps(
            self.julian_day_utc, self.geo_latitude, self.geo_longitude
        )
        if data.get('ramc', None):
            self.ramc = data['ramc']
        else:
            self.ramc = angles[0]

        if data.get('lst', None):
            self.lst = data['lst']
        else:
            self.lst = self.ramc / 15

        if data.get('Vertex'):
            self.vertex = data['Vertex']
        else:
            self.vertex = [
                angles[1],
                swe.calc_house_pos(
                    self.ramc,
                    self.geo_latitude,
                    self.obliquity,
                    to360(angles[1] + self.ayanamsa),
                    0,
                ),
            ]

        if data.get('Eastpoint'):
            self.eastpoint = data['Eastpoint']
        else:
            self.eastpoint = [
                angles[2],
                swe.calc_house_pos(
                    self.ramc,
                    self.geo_latitude,
                    self.obliquity,
                    to360(angles[2] + self.ayanamsa),
                    0,
                ),
            ]
        if data.get('planets'):
            self.planets = {
                planet: PlanetData(**data['planets'][planet])
                for planet in data['planets']
            }

        else:
            self.planets = {}

            for long_name in PLANETS:
                if long_name not in data:
                    continue
                planet_data = data[long_name]
                planet = PlanetData()

                planet.name = long_name
                planet.short_name = PLANETS[long_name]['short_name']
                planet.number = PLANETS[long_name]['number']

                planet.longitude = planet_data[0]
                planet.latitude = planet_data[1]
                planet.speed = planet_data[2]
                planet.right_ascension = planet_data[3]
                planet.declination = planet_data[4]
                planet.azimuth = planet_data[5]
                planet.altitude = planet_data[6]

                planet.is_stationary = swe.is_planet_stationary(
                    planet.name, self.julian_day_utc
                )

                if len(planet_data) >= 9:
                    planet.meridian_longitude = planet_data[7]
                    planet.house = planet_data[8]
                    planet.prime_vertical_longitude = planet_data[8]
                else:
                    planet.house = planet_data[7]
                    planet.prime_vertical_longitude = planet_data[7]
                    planet.meridian_longitude = swe.calc_meridian_longitude(
                        planet.azimuth, planet.altitude
                    )

                self.planets[long_name] = planet

        self.cusps = cusps
        self.angles = angles

        self.notes = data.get('notes', None)

        self.version = data.get('version', (0, 0, 0))

    def iterate_points(
        self, options: Options, include_angles: bool = False
    ) -> Iterator[tuple[str, dict[str, any]]]:
        iterator = (
            self.planets.items()
            if not include_angles
            else itertools.chain(self.planets.items(), enumerate(self.cusps))
        )
        for point, data in iterator:
            if (
                hasattr(data, 'number')
                and data.number > 11
                and data.short_name not in options.extra_bodies
            ):
                continue
            elif (
                point == 'True Node'
                and options.node_type.value != NodeTypes.TRUE_NODE.value
            ):
                continue
            elif (
                point == 'Mean Node'
                and options.node_type.value != NodeTypes.MEAN_NODE.value
            ):
                continue

            elif point == 1:
                yield 'As', data

            elif point == 10:
                yield 'Mc', data

            elif type(point) == int:
                continue

            else:
                yield point, data

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

    def with_role(self, role: ChartWheelRole):
        self.role = role
        return self

    def precess_to(self, to_chart: T):
        for planet in self.planets:
            self.planets[planet].precess_to(to_chart)

        return self


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
    def degrees_from_abbreviation(abbreviation: str) -> int | None:
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

    @classmethod
    def iterate(cls) -> Iterator[tuple['AspectType', int]]:
        for member in AspectType:
            yield (member, cls.degrees_from_abbreviation(member.value))
            if member == AspectType.OCTILE:
                yield (member, 135)


class AspectFramework(Enum):
    ECLIPTICAL = ''
    MUNDANE = 'M'
    PRIME_VERTICAL_PARAN = 'p'
    POTENTIAL_PARAN = 'P'


@dataclass
class Aspect:
    type: AspectType = AspectType.CONJUNCTION
    aspect_class: int = 0
    strength: int = 0
    orb: float = 0
    framework: AspectFramework = AspectFramework.ECLIPTICAL
    from_planet_short_name: str = ''
    to_planet_short_name: str = ''
    from_planet_role: ChartWheelRole = ''
    to_planet_role: ChartWheelRole = ''

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
        self.from_planet_short_name = planet
        if role:
            self.from_planet_role = role
        return self

    def to_planet(self, planet: str, role: ChartWheelRole = None):
        self.to_planet_short_name = planet
        if role:
            self.to_planet_role = role
        return self

    def with_orb(self, orb: float):
        self.orb = float(orb)
        return self

    def with_class(self, aspect_class: int):
        self.aspect_class = int(aspect_class)
        return self

    def with_strength(self, strength: int):
        self.strength = int(strength)
        return self

    def as_type(self, type: AspectType):
        self.type = type
        return self

    def get_formatted_orb(self):
        return fmt_dm(abs(self.orb), True)

    def is_hard_aspect(self):
        return self.type in [
            AspectType.CONJUNCTION,
            AspectType.OPPOSITION,
            AspectType.SQUARE,
        ]

    def is_hard_aspect_8th_harmonic(self):
        return self.type in [
            AspectType.CONJUNCTION,
            AspectType.OPPOSITION,
            AspectType.SQUARE,
            AspectType.OCTILE,
        ]

    def is_soft_aspect(self):
        return self.type in [AspectType.SEXTILE, AspectType.TRINE]

    def is_minor_aspect(self):
        return self.type in [
            AspectType.OCTILE,
            AspectType.TRINE,
            AspectType.SEXTILE,
        ]

    def __str__(self):
        # This will read something like this:
        # t.Ur co r.Su 1°23' 95% M
        planet_1_role = self.from_planet_role.value
        planet_2_role = self.to_planet_role.value
        text = (
            f'{planet_1_role}{self.from_planet_short_name} '
            f'{self.type.value} {planet_2_role}{self.to_planet_short_name} '
            f"{self.get_formatted_orb()} {self.strength}%{(' ' + self.framework.value) if self.framework else ' '}"
        )

        return text

    def cosmic_state_format(self, planet_short_name: str):
        # Exclude the given planet name from the aspect.
        # This will read: "aspect_type other_planet dm_orb framework"
        if self.from_planet_short_name == planet_short_name:
            return f'{self.type.value} {self.to_planet_role.value}{self.to_planet_short_name} {self.get_formatted_orb()}{self.framework.value}'
        return f'{self.type.value} {self.from_planet_role.value}{self.from_planet_short_name} {self.get_formatted_orb()}{self.framework.value}'

    def includes_planet(self, planet_name: str) -> bool:
        # This would be short name
        if (
            self.from_planet_short_name == planet_name
            or self.to_planet_short_name == planet_name
        ):
            return True

        # Otherwise, it might be long name
        if planet_name in PLANETS:
            planet_short_name = PLANETS[planet_name]['short_name']
            return (
                self.from_planet_short_name == planet_short_name
                or self.to_planet_short_name == planet_short_name
            )

        return False


@dataclass
class HalfSum:
    point_a: str = ''
    point_b: str = ''
    point_a_role: ChartWheelRole = ChartWheelRole.NATAL
    point_b_role: ChartWheelRole = ChartWheelRole.NATAL
    longitude: float = 0
    prime_vertical_longitude: float = 0
    right_ascension: float = 0

    def contains(self, planet_name: str) -> bool:
        return self.point_a == planet_name or self.point_b == planet_name

    def __str__(self):
        return f'{self.point_a_role.value}{self.point_a}/{self.point_b_role.value}{self.point_b}'


class MidpointAspectType(Enum):
    DIRECT = 'd'
    INDIRECT = 'i'


@dataclass
class MidpointAspect:
    midpoint_type: MidpointAspectType = MidpointAspectType.DIRECT
    orb_minutes: int = 0
    framework: AspectFramework = AspectFramework.ECLIPTICAL
    from_point: str = ''
    to_midpoint: HalfSum = None
    from_point_role: ChartWheelRole = ''

    def __str__(self):
        framework_suffix = (
            f' {self.framework.value}'
            if self.framework.value != AspectFramework.ECLIPTICAL.value
            else ''
        )
        return f"{self.to_midpoint} {self.orb_minutes: >2}'{self.midpoint_type.value}{framework_suffix}"
