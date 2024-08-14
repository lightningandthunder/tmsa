from src.models.angles import ForegroundAngles, NonForegroundAngles
from src.models.charts import ChartWheelRole
from src.models.options import Options
from src.utils.chart_utils import (
    convert_short_name_to_long,
    iterate_allowed_planets,
)


class PlanetStateLookup:
    class PlanetState:
        long_name: str
        short_name: str
        angle: ForegroundAngles | NonForegroundAngles | None
        is_background: bool
        role: ChartWheelRole | None

        def __init__(
            self,
            long_name: str,
            short_name: str,
            angle: ForegroundAngles | NonForegroundAngles,
            is_background: bool,
            role: ChartWheelRole | None = None,
        ) -> None:
            self.long_name = long_name
            self.short_name = short_name
            self.angle = angle
            self.is_background = is_background
            self.role = role

        @property
        def is_foreground(self) -> bool:
            return self.angle in ForegroundAngles

        def __str__(self) -> str:
            return f'{self.role.value}. {self.long_name} - angle: {self.angle} background: {self.is_background} prime vertical: {self.prime_vert_angle}'

    __planets: dict[str, PlanetState]

    def __init__(self):
        self.__planets: dict[str, PlanetStateLookup.PlanetState] = {}

    def register(
        self,
        long_name: str,
        short_name: str,
        angle: ForegroundAngles | NonForegroundAngles,
        is_background: bool,
        role: ChartWheelRole | None,
    ) -> None:
        self.__planets[long_name] = self.PlanetState(
            long_name, short_name, angle, is_background, role
        )

    def lookup(self, name: str, role: ChartWheelRole) -> PlanetState | None:
        long_name = name
        if len(name) <= 2:
            long_name = convert_short_name_to_long(name)
        if long_name in self.__planets:
            matching_planets = [
                planet in self.__planets[long_name]
                for planet in self.__planets
                if planet.role == role
            ]
            return matching_planets[0] if len(matching_planets) > 0 else None

        return None

    def __str__(self) -> str:
        return '\n'.join([str(planet) for planet in self.__planets])
