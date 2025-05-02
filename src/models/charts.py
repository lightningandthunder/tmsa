import itertools
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, TypeVar, TypedDict

from src import log_startup_error, swe
from src.constants import PLANETS, VERSION
from src.models.angles import (
    AngleAxes,
    ForegroundAngles,
    MajorAngles,
    MinorAngles,
    NonForegroundAngles,
)
from src.models.options import NodeTypes, Options
from src.utils import chart_utils
from src.utils.chart_utils import (
    SIGNS_SHORT,
    convert_house_to_pvl,
    fmt_dm,
)
from src.utils.format_utils import to360, version_str_to_tuple

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


class __PointData:
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
    angle_axes_contacted: list[AngleAxes] = field(default_factory=list)
    prime_vertical_angle: NonForegroundAngles = NonForegroundAngles.BLANK
    angularity_strength: float = 0.0
    is_stationary: bool = False
    is_angle: bool = False

    @property
    def is_foreground(self):
        return False

    @property
    def contacted_angle_axis_values_stripped(self):
        return []

    @property
    def is_on_vx_or_av(self):
        return False

    @property
    def is_on_major_angle(self):
        return False

    @property
    def is_square_ramc(self):
        return False

    @property
    def is_on_zenith(self):
        return False

    @property
    def is_on_ep_or_wp(self):
        return False

    @property
    def is_square_asc_or_mc(self):
        return False

    @property
    def short_name_with_role(self):
        return False


@dataclass
class PlanetData(__PointData):
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
    angle_axes_contacted: list[str] = field(default_factory=list)
    prime_vertical_angle: NonForegroundAngles = NonForegroundAngles.BLANK
    angularity_strength: float = 0.0
    is_stationary: bool = False
    is_angle: False

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
        return MajorAngles.contains(self.angle.value) or MinorAngles.contains(
            self.angle.value
        )

    @property
    def is_on_vx_or_av(self):
        return self.prime_vertical_angle.value in self.__prime_vertical_angles

    @property
    def is_on_major_angle(self):
        return MajorAngles.contains(self.angle.value)

    @property
    def is_square_ramc(self):
        return (
            AngleAxes.EASTPOINT_IN_RA.value.strip()
            in self.angle_axes_contacted
        )

    @property
    def is_on_zenith(self):
        return (
            AngleAxes.ZENITH_NADIR.value.strip() in self.angle_axes_contacted
        )

    @property
    def is_on_ep_or_wp(self):
        return (
            AngleAxes.EASTPOINT_WESTPOINT.value.strip()
            in self.angle_axes_contacted
        )

    @property
    def is_square_asc_or_mc(self):
        return self.is_on_zenith or self.is_on_ep_or_wp

    @property
    def short_name_with_role(self):
        return f'{self.role.value}{self.short_name}'


@dataclass
class AngleData(__PointData):
    name: str = ''
    short_name: str = ''
    longitude: float = 0
    latitude: float = 0
    right_ascension: float = 0
    declination: float = 0
    azimuth: float = 0
    altitude: float = 0
    meridian_longitude: float = 0
    prime_vertical_longitude: float = 0
    role: ChartWheelRole = ChartWheelRole.NATAL
    is_angle: True

    def with_ecliptic_and_equatorial_data(
        self,
        longitude: float,
        latitude: float,
        right_ascension: float,
        declination: float,
    ):
        self.longitude = longitude
        self.latitude = latitude
        self.right_ascension = right_ascension
        self.declination = declination
        return self

    def with_azimuth_and_altitude(self, azimuth: float, altitude: float):
        self.azimuth = azimuth
        self.altitude = altitude
        return self

    def with_house_position(self, house: float):
        self.prime_vertical_longitude = convert_house_to_pvl(house)
        return self

    def with_role(self, role: ChartWheelRole):
        self.role = role
        return self

    def precess_to(self, to_chart: T):
        (right_ascension, declination) = swe.cotrans(
            [to360(self.longitude + to_chart.ayanamsa), 0, 0],
            to_chart.obliquity,
        )
        self.right_ascension = right_ascension
        self.declination = declination

        (azimuth, altitude) = swe.calc_azimuth(
            to_chart.julian_day_utc,
            to_chart.geo_longitude,
            to_chart.geo_latitude,
            to360(to_chart.ayanamsa + self.longitude),
            0,
        )
        self.azimuth = azimuth
        self.altitude = altitude

        self.prime_vertical_longitude = swe.calc_house_pos(
            to_chart.ramc,
            to_chart.geo_latitude,
            to_chart.obliquity,
            to360(self.longitude + to_chart.ayanamsa),
            0,
        )

        return self

    @property
    def name_with_role(self):
        return f'{self.role.value}{self.short_name}'


@dataclass
class ChartType(Enum):
    EVENT = 'Event'

    RADIX = 'Radix'
    NATAL = 'Natal'
    SOLAR_RETURN = 'Solar Return'
    SOLAR_RETURN_SINGLE = 'Solar Return Single Wheel'
    DEMI_SOLAR_RETURN = 'Demi-Solar Return'
    DEMI_SOLAR_RETURN_SINGLE = 'Demi-Solar Return Single Wheel'
    LAST_QUARTI_SOLAR_RETURN = 'Last Quarti-Solar Return'
    LAST_QUARTI_SOLAR_RETURN_SINGLE = 'Last Quarti-Solar Return Single Wheel'
    FIRST_QUARTI_SOLAR_RETURN = 'First Quarti-Solar Return'
    FIRST_QUARTI_SOLAR_RETURN_SINGLE = 'First Quarti-Solar Return Single Wheel'

    LUNAR_RETURN = 'Lunar Return'
    LUNAR_RETURN_SINGLE = 'Lunar Return Single Wheel'
    DEMI_LUNAR_RETURN = 'Demi-Lunar Return'
    DEMI_LUNAR_RETURN_SINGLE = 'Demi-Lunar Return Single Wheel'
    FIRST_QUARTI_LUNAR_RETURN = 'First Quarti-Lunar Return'
    FIRST_QUARTI_LUNAR_RETURN_SINGLE = 'First Quarti-Lunar Return Single Wheel'
    LAST_QUARTI_LUNAR_RETURN = 'Last Quarti-Lunar Return'
    LAST_QUARTI_LUNAR_RETURN_SINGLE = 'Last Quarti-Lunar Return Single Wheel'

    KINETIC_LUNAR_RETURN = 'Kinetic Lunar Return'
    KINETIC_LUNAR_RETURN_SINGLE = 'Kinetic Lunar Return Single Wheel'
    DEMI_KINETIC_LUNAR_RETURN = 'Kinetic Demi-Lunar Return'
    DEMI_KINETIC_LUNAR_RETURN_SINGLE = 'Kinetic Demi-Lunar Return Single Wheel'

    KINETIC_SOLAR_RETURN = 'Kinetic Solar Return'
    KINETIC_SOLAR_RETURN_SINGLE = 'Kinetic Solar Return Single Wheel'
    DEMI_KINETIC_SOLAR_RETURN = 'Kinetic Demi-Solar Return'
    DEMI_KINETIC_SOLAR_RETURN_SINGLE = 'Kinetic Demi-Solar Return Single Wheel'

    NOVIENIC_SOLAR_RETURN = 'Novienic Solar Return'
    NOVIENIC_SOLAR_RETURN_SINGLE = 'Novienic Solar Return Single Wheel'
    TEN_DAY_SOLAR_RETURN = '10-Day Solar Return'
    TEN_DAY_SOLAR_RETURN_SINGLE = '10-Day Solar Return Single Wheel'

    NOVIENIC_LUNAR_RETURN = 'Novienic Lunar Return'
    NOVIENIC_LUNAR_RETURN_SINGLE = 'Novienic Lunar Return Single Wheel'
    EIGHTEEN_HOUR_LUNAR_RETURN = '18-Hour Lunar Return'
    EIGHTEEN_HOUR_LUNAR_RETURN_SINGLE = '18-Hour Lunar Return Single Wheel'

    ANLUNAR_RETURN = 'Anlunar Return'
    ANLUNAR_RETURN_SINGLE = 'Anlunar Return Single Wheel'
    DEMI_ANLUNAR_RETURN = 'Demi-Anlunar Return'
    DEMI_ANLUNAR_RETURN_SINGLE = 'Demi-Anlunar Return Single Wheel'

    KINETIC_ANULAR_RETURN = 'Kinetic Anlunar Return'
    KINETIC_ANLUNAR_RETURN_SINGLE = 'Kinetic Anlunar Return Single Wheel'
    KINETIC_DEMI_ANLUNAR_RETURN = 'Kinetic Demi-Anlunar Return'
    KINETIC_DEMI_ANLUNAR_RETURN_SINGLE = (
        'Kinetic Demi-Anlunar Return Single Wheel'
    )

    SOLILUNAR_RETURN = 'Solilunar Return'
    SOLILUNAR_RETURN_SINGLE = 'Solilunar Return Single Wheel'
    DEMI_SOLILUNAR_RETURN = 'Demi-Solilunar Return'
    DEMI_SOLILUNAR_RETURN_SINGLE = 'Demi-Solilunar Return Single Wheel'
    LUNISOLAR_RETURN = 'Lunisolar Return'
    LUNISOLAR_RETURN_SINGLE = 'Lunisolar Return Single Wheel'
    DEMI_LUNISOLAR_RETURN = 'Demi-Lunisolar Return'
    DEMI_LUNISOLAR_RETURN_SINGLE = 'Demi-Lunisolar Return Single Wheel'

    CAP_SOLAR = 'Capsolar'
    ARI_SOLAR = 'Arisolar'
    CAN_SOLAR = 'Cansolar'
    LIB_SOLAR = 'Libsolar'
    CAP_LUNAR = 'Caplunar'
    ARI_LUNAR = 'Arilunar'
    CAN_LUNAR = 'Canlunar'
    LIB_LUNAR = 'Liblunar'


class ChartParams(TypedDict):
    name: str | None
    year: int
    month: int
    day: int
    location: str
    time: float
    zone: str
    correction: float
    version: tuple[int]
    longitude: float
    latitude: float
    type: ChartType


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
    angle_data: dict[str, AngleData]
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
        if 'julian_day_utc' in data:
            self.julian_day_utc = data['julian_day_utc']
        else:
            self.julian_day_utc = swe.julday(
                data['year'],
                data['month'],
                data['day'],
                data['time'] + data['correction'],
                data.get('style', 1),
            )
        if data['zone'] == 'LAT':
            self.julian_day_utc = swe.calc_lat_to_lmt(
                self.julian_day_utc, data['longitude']
            )
        self.ayanamsa = data.get('ayan', swe.calc_ayan(self.julian_day_utc))
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

        if data.get('Vertex') and len(data.get('Vertex')) > 2:
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

        self.angles = angles
        self.cusps = cusps

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

        # Populate angle_data
        # MC, AS, EP, VX
        self.angle_data = {}
        (ramc, dec) = chart_utils.precess_mc(
            self.cusps[10],
            self.ayanamsa,
            self.obliquity,
        )
        self.angle_data['Mc'] = AngleData(
            name='Midheaven',
            short_name='Mc',
            longitude=self.cusps[10],
            latitude=None,
            right_ascension=ramc,
            declination=dec,
            azimuth=180,
            altitude=(90 - self.geo_latitude) + dec,
            meridian_longitude=None,
            prime_vertical_longitude=270,
        )

        ascendant_declination = chart_utils.declination_from_zodiacal(
            # Must use tropical longitude
            to360(self.cusps[1] + self.ayanamsa),
            self.obliquity,
        )

        self.angle_data['As'] = AngleData(
            name='Ascendant',
            short_name='As',
            longitude=self.cusps[1],
            latitude=None,
            right_ascension=None,
            declination=ascendant_declination,
            azimuth=None,
            altitude=0,
            meridian_longitude=None,
            prime_vertical_longitude=0,
        )

        eastpoint_declination = chart_utils.declination_from_zodiacal(
            to360(self.angles[2] + self.ayanamsa), self.obliquity
        )
        self.angle_data['Ep'] = AngleData(
            name='Eastpoint',
            short_name='Ep',
            longitude=self.angles[2],
            latitude=None,
            right_ascension=to360(ramc - 270),
            declination=eastpoint_declination,
            azimuth=None,
            altitude=None,
            meridian_longitude=None,
            prime_vertical_longitude=None,
        )

        vertex_declination = chart_utils.declination_from_zodiacal(
            # This is the TROPICAL longitude, which is needed for this calc
            to360(self.angles[1] + self.ayanamsa),
            self.obliquity,
        )

        self.angle_data['Vx'] = AngleData(
            name='Vertex',
            short_name='Vx',
            longitude=self.angles[1],
            latitude=None,
            right_ascension=None,
            declination=vertex_declination,
            azimuth=270,
            altitude=self.vertex[1] - 180,
            meridian_longitude=None,
            prime_vertical_longitude=None,
        )

        def __dict__(self):
            return {
                'name': self.name,
                'year': self.year,
                'month': self.month,
                'day': self.day,
                'location': self.location,
                'time': self.time,
                'zone': self.zone,
                'correction': self.correction,
                'type': self.type.value,
                'julian_day_utc': self.julian_day_utc,
                'ayanamsa': self.ayanamsa,
                'obliquity': self.obliquity,
                'geo_longitude': self.geo_longitude,
                'geo_latitude': self.geo_latitude,
                'lst': self.lst,
                'ramc': self.ramc,
                'planets': {
                    planet: self.planets[planet].__dict__
                    for planet in self.planets
                },
                'cusps': self.cusps,
                'angles': self.angles,
                'vertex': self.vertex,
                'eastpoint': self.eastpoint,
                'role': self.role.value,
                'notes': self.notes,
                'style': self.style,
                'version': self.version,
            }

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
                log_startup_error(f'Error reading {file_path}')

    # TODO - this doesn't work yet; it's missing a lot of stuff
    @staticmethod
    def from_calculation(params: ChartParams) -> 'ChartObject':
        chart = ChartObject(params)
        chart.version = (
            version_str_to_tuple(VERSION)
            if 'version' not in params
            else params['version']
        )
        chart.style = params['style']
        chart.julian_day_utc = swe.julday(
            params['year'],
            params['month'],
            params['day'],
            params['time'] + params['correction'],
            params['style'],
        )

        for planet in PLANETS:
            planet_definitions = PLANETS[planet]
            [
                longitude,
                latitude,
                speed,
                right_ascension,
                declination,
            ] = swe.calc_planet(
                chart.julian_day_utc, planet_definitions['number']
            )
            [azimuth, altitude] = swe.calc_azimuth(
                chart.julian_day_utc,
                chart.geo_longitude,
                chart.geo_latitude,
                to360(longitude + chart.ayanamsa),
                latitude,
            )
            house_position = swe.calc_house_pos(
                chart.ramc,
                chart.latitude,
                chart.obliquity,
                to360(longitude + chart.ayanamsa),
                latitude,
            )
            meridian_longitude = swe.calc_meridian_longitude(azimuth, altitude)

            data = [
                longitude,
                latitude,
                speed,
                right_ascension,
                declination,
                azimuth,
                altitude,
                meridian_longitude,
                house_position,
            ]

            chart.planets[planet_definitions['long_name']] = data

        return chart

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    def with_role(self, role: ChartWheelRole):
        self.role = role
        return self

    def precess_to(self, to_chart: T):
        for planet in self.planets:
            self.planets[planet].precess_to(to_chart)

        # Precess angles
        for angle in self.angle_data:
            self.angle_data[angle].precess_to(to_chart)

        return self


class AspectType(Enum):
    CONJUNCTION = 'co'
    OCTILE = 'oc'
    SEXTILE = 'sx'
    SQUARE = 'sq'
    TRINE = 'tr'
    OPPOSITION = 'op'
    INCONJUNCT = 'in'

    DECILE = 'dc'

    # Not implemented anywhere
    QUINTILE = 'qu'
    SEPTILE = 'sp'
    NOVILE = 'nv'

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
        elif string == 'in':
            return cls.INCONJUNCT
        elif string == 'op':
            return cls.OPPOSITION
        elif string == 'dc':
            return cls.DECILE
        elif string == 'qu':
            return cls.QUINTILE
        elif string == 'sp':
            return cls.SEPTILE
        elif string == 'nv':
            return cls.NOVILE
        else:
            return None

    @classmethod
    def from_degrees(cls, degrees: int | str):
        if isinstance(degrees, str):
            degrees = int(degrees)

        # Does not handle septile
        if degrees == 0:
            return cls.CONJUNCTION
        if degrees == 10:
            return cls.DECILE
        elif degrees == 30:
            return cls.INCONJUNCT
        elif degrees == 40:
            return cls.NOVILE
        elif degrees == 45:
            return cls.OCTILE
        elif degrees == 60:
            return cls.SEXTILE
        elif degrees == 72:
            return cls.QUINTILE
        elif degrees == 90:
            return cls.SQUARE
        elif degrees == 120:
            return cls.TRINE
        elif degrees == 135:
            return cls.OCTILE
        elif degrees == 150:
            return cls.INCONJUNCT
        elif degrees == 180:
            return cls.OPPOSITION
        else:
            return None

    @staticmethod
    def degrees_from_abbreviation(abbreviation: str) -> int | None:
        # Does not handle septiles
        if abbreviation == 'co':
            return 0
        elif abbreviation == 'dc':
            return 10
        elif abbreviation == 'nv':
            return 40
        elif abbreviation == 'oc':
            return 45
        elif abbreviation == 'sx':
            return 60
        elif abbreviation == 'qu':
            return 72
        elif abbreviation == 'sq':
            return 90
        elif abbreviation == 'tr':
            return 120
        elif abbreviation == 'in':
            return 150
        elif abbreviation == 'op':
            return 180
        else:
            return None

    @classmethod
    def iterate(cls) -> Iterator[tuple['AspectType', int]]:
        for member in AspectType:
            yield (member, cls.degrees_from_abbreviation(member.value))
            if member == AspectType.OCTILE:
                yield (member, 135)
            elif member == AspectType.INCONJUNCT:
                yield (member, 30)

    @classmethod
    def iterate_harmonic_8(cls) -> Iterator[tuple['AspectType', int]]:
        for member in AspectType:
            if member == AspectType.SEXTILE or member == AspectType.TRINE:
                continue
            yield (member, cls.degrees_from_abbreviation(member.value))
            if member == AspectType.OCTILE:
                yield (member, 135)

    @classmethod
    def iterate_harmonic_4(cls) -> Iterator[tuple['AspectType', int]]:
        for member in AspectType:
            if (
                member == AspectType.SEXTILE
                or member == AspectType.TRINE
                or member == AspectType.OCTILE
            ):
                continue
            yield (member, cls.degrees_from_abbreviation(member.value))


class AspectFramework(Enum):
    ECLIPTICAL = ' '
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
    
    def with_framework(self, framework: AspectFramework):
        self.framework = framework
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
        # tUr co rSu  1°23'  95% M
        # It should always be an even number of characters
        # to make alignment consistent
        planet_1_role = self.from_planet_role.value
        planet_2_role = self.to_planet_role.value
        text = (
            f'{planet_1_role}{self.from_planet_short_name} '
            + f'{self.type.value} {planet_2_role}{self.to_planet_short_name} '
            + f'{self.get_formatted_orb()} {round(self.strength):>3}% {self.framework.value}'
        )

        return text if len(text) % 2 == 0 else text + ' '

    def cosmic_state_format(self, planet_short_name: str):
        # Exclude the given planet name from the aspect.
        # This will read: "aspect_type other_planet dm_orb framework"
        if self.from_planet_short_name == planet_short_name:
            return f'{self.type.value} {self.to_planet_role.value}{self.to_planet_short_name} {self.get_formatted_orb()}{self.framework.value}'
        return f'{self.type.value} {self.from_planet_role.value}{self.from_planet_short_name} {self.get_formatted_orb()}{self.framework.value}'

    def includes_planet(
        self, planet_name: str, role: ChartWheelRole | None = None
    ) -> bool:
        planet_short_name = planet_name

        # Normalize long name to short name
        if planet_name in PLANETS:
            planet_short_name = PLANETS[planet_name]['short_name']

        if role:
            if (
                self.from_planet_short_name == planet_short_name
                and self.from_planet_role.value == role.value
            ) or (
                self.to_planet_short_name == planet_short_name
                and self.to_planet_role.value == role.value
            ):
                return True
        if (
            self.from_planet_short_name == planet_short_name
            or self.to_planet_short_name == planet_short_name
        ):
            return True

        return False


@dataclass
class AngleContactAspect:
    type: AspectType = AspectType.CONJUNCTION
    aspect_class: int = 0
    strength: float = 0.0
    orb: float = 0
    framework: AspectFramework = AspectFramework.ECLIPTICAL
    from_planet_short_name: str = ''
    to_planet_short_name: str = ''
    from_planet_role: ChartWheelRole = ''
    to_planet_role: ChartWheelRole = ChartWheelRole.NATAL

    __angle_name_map = {
        'A': 'As',
        'M': 'MC',
        'D': 'Ds',
        'I': 'IC',
        'E': 'EP',
        'EA': 'Ea',
        'W': 'WP',
        'WA': 'Wa',
        'Z': 'Z ',
        'N': 'N ',
    }

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

    def to_planet(self, angle: str, role: ChartWheelRole = None):
        self.to_planet_short_name = angle
        if role:
            self.to_planet_role = role
        return self

    def with_orb(self, orb: float):
        self.orb = float(orb)
        return self

    def with_class(self, aspect_class: int):
        self.aspect_class = int(aspect_class)
        return self

    def with_strength(self, strength: float):
        self.strength = strength
        return self

    def as_type(self, type: AspectType):
        self.type = type
        return self

    def get_formatted_orb(self):
        return fmt_dm(abs(self.orb), True).lstrip()

    def is_hard_aspect(self):
        return True

    def __str__(self):
        # This will read something like this:
        # tUr co Mc  +1°23'  99%
        # It should always be an even number of characters
        # to make alignment consistent
        planet_1_role = self.from_planet_role.value
        angle_name = self.__angle_name_map[
            self.to_planet_short_name.strip().upper()
        ]
        text = (
            f'{planet_1_role}{self.from_planet_short_name} '
            + f'{self.type.value} {" " if planet_1_role != "" else ""}{self.to_planet_role.value}{angle_name} '
            + f'{"+" if self.orb >= 0 else "-"}{self.get_formatted_orb()} {round(self.strength):>3}% '
        )

        return text if len(text) % 2 == 0 else text + ' '

    def cosmic_state_format(self):
        angle_name = self.__angle_name_map[
            self.to_planet_short_name.strip().upper()
        ]

        return f'{angle_name} {self.get_formatted_orb()}'

    def includes_planet(
        self, planet_name: str, role: ChartWheelRole | None = None
    ) -> bool:
        planet_short_name = planet_name

        # Normalize long name to short name
        if planet_name in PLANETS:
            planet_short_name = PLANETS[planet_name]['short_name']

        if role:
            if (
                self.from_planet_short_name == planet_short_name
                and self.from_planet_role.value == role.value
            ) or (
                self.to_planet_short_name == planet_short_name
                and self.to_planet_role.value == role.value
            ):
                return True
        if (
            self.from_planet_short_name == planet_short_name
            or self.to_planet_short_name == planet_short_name
        ):
            return True

        return False


@dataclass
class HalfSum:
    point_a: PlanetData | AngleData
    point_b: PlanetData | AngleData
    longitude: float = 0
    prime_vertical_longitude: float = 0
    right_ascension: float = 0

    def contains(self, planet_name: str, role: ChartWheelRole | None) -> bool:
        if not role:
            return (
                self.point_a.short_name == planet_name
                or self.point_b.short_name == planet_name
            )

        if (
            self.point_a.short_name == planet_name
            and self.point_a.role.value == role.value
        ):
            return True

        if (
            self.point_b.short_name == planet_name
            and self.point_b.role.value == role.value
        ):
            return True

        return False

    @property
    def both_points_are_foreground(self):
        return (
            self.point_a.is_foreground or self.point_a.treat_as_foreground
        ) and (self.point_b.is_foreground or self.point_b.treat_as_foreground)

    @property
    def both_points_foreground_square_ramc(self):
        return (
            not self.point_a.is_angle and self.point_a.is_square_ramc
        ) and (not self.point_b.is_angle and self.point_b.is_square_ramc)

    @property
    def both_points_on_zenith(self):
        return (not self.point_a.is_angle and self.point_a.is_on_zenith) and (
            not self.point_b.is_angle and self.point_b.is_on_zenith
        )

    @property
    def both_points_on_ep(self):
        return (
            not self.point_a.is_angle and self.point_a.is_on_ep_or_wp
        ) and (not self.point_b.is_angle and self.point_b.is_on_ep_or_wp)

    @property
    def contains_angle(self):
        return self.point_a.is_angle or self.point_b.is_angle

    def __str__(self):
        return f'{self.point_a.role.value}{self.point_a.short_name}/{self.point_b.role.value}{self.point_b.short_name}'


class MidpointAspectType(Enum):
    DIRECT = 'd'
    INDIRECT = 'i'


@dataclass
class MidpointAspect:
    from_point_data: PlanetData | AngleData
    midpoint_type: MidpointAspectType = MidpointAspectType.DIRECT
    orb_minutes: int = 0
    framework: AspectFramework = AspectFramework.ECLIPTICAL
    to_midpoint: HalfSum = None

    @property
    def is_ecliptical(self):
        return self.framework.value == AspectFramework.ECLIPTICAL.value

    @property
    def is_mundane(self):
        return self.framework.value == AspectFramework.MUNDANE.value

    def __str__(self):
        framework_suffix = '  '
        if (
            self.framework.value != AspectFramework.ECLIPTICAL.value
            and self.from_point_data not in ['Angle', 'Ea', 'E', 'Z']
        ):
            framework_suffix = f' {self.framework.value}'

        return f"{self.to_midpoint} {round(self.orb_minutes): >2}'{self.midpoint_type.value}{framework_suffix}"


SOLAR_RETURNS = [
    ChartType.SOLAR_RETURN.value,
    ChartType.DEMI_SOLAR_RETURN.value,
    ChartType.FIRST_QUARTI_SOLAR_RETURN.value,
    ChartType.LAST_QUARTI_SOLAR_RETURN.value,
    ChartType.KINETIC_SOLAR_RETURN.value,
    ChartType.DEMI_KINETIC_SOLAR_RETURN.value,
    ChartType.NOVIENIC_SOLAR_RETURN.value,
    ChartType.TEN_DAY_SOLAR_RETURN.value,
    ChartType.SOLILUNAR_RETURN.value,
    ChartType.DEMI_SOLILUNAR_RETURN.value,
]

LUNAR_RETURNS = [
    ChartType.LUNAR_RETURN.value,
    ChartType.DEMI_LUNAR_RETURN.value,
    ChartType.FIRST_QUARTI_LUNAR_RETURN.value,
    ChartType.LAST_QUARTI_LUNAR_RETURN.value,
    ChartType.KINETIC_LUNAR_RETURN.value,
    ChartType.DEMI_KINETIC_LUNAR_RETURN.value,
    ChartType.NOVIENIC_LUNAR_RETURN.value,
    ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value,
    ChartType.ANLUNAR_RETURN.value,
    ChartType.DEMI_ANLUNAR_RETURN.value,
    ChartType.KINETIC_ANULAR_RETURN.value,
    ChartType.KINETIC_DEMI_ANLUNAR_RETURN.value,
    ChartType.LUNISOLAR_RETURN.value,
    ChartType.DEMI_LUNISOLAR_RETURN.value,
]

KINETIC_RETURNS = [
    ChartType.KINETIC_LUNAR_RETURN.value,
    ChartType.DEMI_KINETIC_LUNAR_RETURN.value,
    ChartType.KINETIC_SOLAR_RETURN.value,
    ChartType.DEMI_KINETIC_SOLAR_RETURN.value,
    ChartType.KINETIC_ANULAR_RETURN.value,
    ChartType.KINETIC_DEMI_ANLUNAR_RETURN.value,
]

SOLUNAR_RETURNS = [
    ChartType.SOLAR_RETURN.value,
    ChartType.DEMI_SOLAR_RETURN.value,
    ChartType.LAST_QUARTI_SOLAR_RETURN.value,
    ChartType.FIRST_QUARTI_SOLAR_RETURN.value,
    ChartType.LUNAR_RETURN.value,
    ChartType.DEMI_LUNAR_RETURN.value,
    ChartType.FIRST_QUARTI_LUNAR_RETURN.value,
    ChartType.LAST_QUARTI_LUNAR_RETURN.value,
    ChartType.KINETIC_LUNAR_RETURN.value,
    ChartType.DEMI_KINETIC_LUNAR_RETURN.value,
    ChartType.KINETIC_SOLAR_RETURN.value,
    ChartType.DEMI_KINETIC_SOLAR_RETURN.value,
    ChartType.NOVIENIC_SOLAR_RETURN.value,
    ChartType.TEN_DAY_SOLAR_RETURN.value,
    ChartType.NOVIENIC_LUNAR_RETURN.value,
    ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value,
    ChartType.ANLUNAR_RETURN.value,
    ChartType.DEMI_ANLUNAR_RETURN.value,
    ChartType.KINETIC_ANULAR_RETURN.value,
    ChartType.KINETIC_DEMI_ANLUNAR_RETURN.value,
    ChartType.SOLILUNAR_RETURN.value,
    ChartType.DEMI_SOLILUNAR_RETURN.value,
    ChartType.LUNISOLAR_RETURN.value,
    ChartType.DEMI_LUNISOLAR_RETURN.value,
]

RETURNS_WHERE_MOON_ALWAYS_FOREGROUND = [
    ChartType.SOLAR_RETURN.value,
    ChartType.DEMI_SOLAR_RETURN.value,
    ChartType.LAST_QUARTI_SOLAR_RETURN.value,
    ChartType.FIRST_QUARTI_SOLAR_RETURN.value,
    ChartType.KINETIC_SOLAR_RETURN.value,
    ChartType.DEMI_KINETIC_SOLAR_RETURN.value,
    ChartType.NOVIENIC_SOLAR_RETURN.value,
    ChartType.TEN_DAY_SOLAR_RETURN.value,
    ChartType.NOVIENIC_LUNAR_RETURN.value,
    ChartType.EIGHTEEN_HOUR_LUNAR_RETURN.value,
    ChartType.SOLILUNAR_RETURN.value,
    ChartType.DEMI_SOLILUNAR_RETURN.value,
]

INGRESSES = [
    'Capsolar',
    'Cansolar',
    'Arisolar',
    'Libsolar',
    'Caplunar',
    'Canlunar',
    'Arilunar',
    'Liblunar',
]
