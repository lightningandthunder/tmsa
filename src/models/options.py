import json
from dataclasses import dataclass
from enum import Enum

from src import log_startup_error
from src.defaults.option_defaults import NATAL_DEFAULT


@dataclass
class NodeTypes(Enum):
    DISABLED = 0
    TRUE_NODE = 1
    MEAN_NODE = 2

    @staticmethod
    def from_number(number: int):
        if number == 0:
            return NodeTypes.DISABLED
        elif number == 1:
            return NodeTypes.TRUE_NODE
        elif number == 2:
            return NodeTypes.MEAN_NODE
        else:
            return None


class ShowAspect(Enum):
    ALL = 0
    ONE_PLUS_FOREGROUND = 1
    BOTH_FOREGROUND = 2

    @staticmethod
    def from_number(number: int):
        if number == 0:
            return ShowAspect.ALL
        elif number == 1:
            return ShowAspect.ONE_PLUS_FOREGROUND
        elif number == 2:
            return ShowAspect.BOTH_FOREGROUND
        else:
            return None


class AngularityModel(Enum):
    CLASSIC_CADENT = 0
    MIDQUADRANT = 1
    EUREKA = 2

    @staticmethod
    def from_number(number: int):
        if number == 0:
            return AngularityModel.CLASSIC_CADENT
        elif number == 1:
            return AngularityModel.MIDQUADRANT
        elif number == 2:
            return AngularityModel.EUREKA
        else:
            return None


@dataclass
class AngularitySubOptions:
    model: AngularityModel
    no_bg: bool
    major_angles: list[float]
    minor_angles: list[float]


class Options:
    extra_bodies: list[str] = []
    use_vertex: bool = False
    node_type: NodeTypes = NodeTypes.DISABLED
    show_aspects: ShowAspect = ShowAspect.ALL
    partile_nf: bool = False
    angularity: AngularitySubOptions = None
    ecliptic_aspects: dict[str, list[float]] = {}
    allowed_ecliptic: dict[str, bool] = {}
    allowed_mundane: dict[str, bool] = {}
    mundane_aspects: dict[str, list[float]] = {}
    pvp_aspects: dict[str, list[float]] = {}
    paran_aspects: dict[str, list[float]] = {}
    midpoints: dict[str, list[float]] = {}
    include_fg_under_aspects: bool = False
    enable_novien: bool = False

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return Options(data)
            except json.JSONDecodeError:
                log_startup_error(f'Error reading {file_path}')

    def __init__(self, data: dict[str, any]):
        self.extra_bodies = data.get('extra_bodies', [])
        if data.get('use_Eris', False) and 'Er' not in self.extra_bodies:
            self.extra_bodies.append('Er')
        if data.get('use_Sedna', False) and 'Se' not in self.extra_bodies:
            self.extra_bodies.append('Se')
        self.use_vertex = True if data.get('use_Vertex') else False

        self.node_type = NodeTypes.from_number(
            data.get('Node', data.get('node_type', 0))
        )
        self.show_aspects = ShowAspect.from_number(data.get('show_aspects', 0))
        self.partile_nf = True if data.get('partile_nf') else False
        self.include_fg_under_aspects = (
            True if data.get('include_fg_under_aspects') else False
        )

        self.enable_novien = True if data.get('enable_novien') else False

        if 'angularity' in data:
            self.angularity = AngularitySubOptions(
                AngularityModel.from_number(data['angularity']['model']),
                data['angularity']['no_bg'],
                data['angularity']['major_angles'],
                data['angularity']['minor_angles'],
            )

        for key in [
            'ecliptic_aspects',
            'allowed_ecliptic',
            'mundane_aspects',
            'allowed_mundane',
            'pvp_aspects',
            'paran_aspects',
            'midpoints',
        ]:
            if key in data:
                setattr(self, key, data[key])

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    def __str__(self):
        return str(self.__dict__)


class ProgramOptions:
    quarti_returns_enabled: bool = True

    def __init__(self, data: dict[str, any]):
        self.quarti_returns_enabled = data.get('quarti_returns_enabled', True)

    @staticmethod
    def from_default():
        return ProgramOptions({})

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return ProgramOptions(data)
            except json.JSONDecodeError:
                log_startup_error(f'Error reading {file_path}')
                return ProgramOptions.from_default()

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    def __str__(self):
        return str(self.__dict__)
