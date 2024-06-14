from dataclasses import dataclass


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


@dataclass
class ChartObject:
    chart_type: str
    julian_day: float
    ayanamsa: float
    obliquity: float
    geo_longitude: float
    geo_latitude: float
    ramc: float
    planets: dict[str, PlanetData]
    cusps: list[float]
    angles: dict[str, float]


@dataclass
class Options:
    pass
