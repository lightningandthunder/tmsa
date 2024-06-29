import json
from dataclasses import dataclass, field
from enum import Enum

from src import log_error


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


@dataclass
class Options:
    extra_bodies: list[str] = field(default_factory=lambda: [])
    use_vertex: bool = False
    node_type: NodeTypes = NodeTypes.DISABLED
    show_aspects: ShowAspect = ShowAspect.ALL
    partile_nf: bool = False
    angularity: AngularitySubOptions = None
    ecliptic_aspects: dict[str, list[float]] = field(
        default_factory=lambda: {}
    )
    mundane_aspects: dict[str, list[float]] = field(default_factory=lambda: {})
    midpoints: dict[str, list[float]] = field(default_factory=lambda: {})

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return Options(data)
            except json.JSONDecodeError:
                log_error(f'Error reading {file_path}')

    def __init__(self, data: dict[str, any]):
        self.extra_bodies = []
        if data.get('use_Eris', False):
            self.extra_bodies.append('Er')
        if data.get('use_Sedna', False):
            self.extra_bodies.append('Se')
        self.use_vertex = True if data.get('use_Vertex') else False

        self.node_type = NodeTypes.from_number(data.get('node_type', 0))
        self.show_aspects = ShowAspect.from_number(data.get('show_aspects', 0))
        self.partile_nf = True if data.get('partile_nf') else False
        if 'angularity' in data:
            self.angularity = AngularitySubOptions(
                AngularityModel.from_number(data['angularity']['model']),
                data['angularity']['no_bg'],
                data['angularity']['major_angles'],
                data['angularity']['minor_angles'],
            )
        if 'ecliptic_aspects' in data:
            self.ecliptic_aspects = data['ecliptic_aspects']
        if 'mundane_aspects' in data:
            self.mundane_aspects = data['mundane_aspects']
        if 'midpoints' in data:
            self.midpoints = data['midpoints']

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file, indent=4)
