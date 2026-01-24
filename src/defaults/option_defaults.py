NATAL_DEFAULT = {
    'use_Vertex': 1,
    'Node': 0,
    'show_aspects': 0,
    'partile_nf': 0,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 0,
        'major_angles': [3.0, 7.0, 10.0],
        'minor_angles': [1.0, 2.0, 3.0],
    },
    'ecliptic_aspects': {
        '0': [3.0, 7.0, 10.0],
        '180': [3.0, 7.0, 10.0],
        '90': [3.0, 6.0, 7.5],
        '45': [1.0, 2.0, 0],
        '120': [3.0, 6.0, 7.5],
        '60': [3.0, 6.0, 7.5],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': True,
        },
        '120': {
            'full': True,
        },
        '60': {
            'full': True,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 0,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': False,
        '0': [1.25, 2.0, 3.0],
        '180': [1.25, 2.0, 3.0],
        '90': [1.25, 2.0, 3.0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 2, 3],
    },
    'extra_bodies': ['Er'],
    'enable_novien': True,
}

RETURN_DEFAULT = {
    'use_Vertex': 0,
    'Node': 0,
    'show_aspects': 2,
    'partile_nf': 1,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 0,
        'major_angles': [3.0, 7.0, 10.0],
        'minor_angles': [1.0, 2.0, 3.0],
    },
    'ecliptic_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
        '120': [0, 0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 0,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': False,
        '0': [1.25, 2.0, 3.0],
        '180': [1.25, 2.0, 3.0],
        '90': [1.25, 2.0, 3.0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 2, 3],
    },
    'extra_bodies': ['Er'],
    'enable_novien': False,
}

TRANSIT_DEFAULT = {
    'use_Vertex': 0,
    'Node': 0,
    'show_aspects': 0,
    'partile_nf': 1,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 1,
        'major_angles': [1.0, 0.0, 0.0],
        'minor_angles': [1.0, 0.0, 0.0],
    },
    'ecliptic_aspects': {
        '0': [1.0, 0, 0],
        '180': [1.0, 0, 0],
        '90': [1.0, 0, 0],
        '45': [1, 0, 0],
        '120': [0, 0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [0, 0, 0],
        '180': [0, 0, 0],
        '90': [0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 60,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': True,
        '0': [0, 0, 0],
        '180': [0, 0, 0],
        '90': [0, 0, 0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 0, 0],
    },
    'extra_bodies': ['Er', 'Ha'],
    'enable_novien': False,
}

PROGRESSED_DEFAULT = {
    'use_Vertex': 0,
    'Node': 0,
    'show_aspects': 2,
    'partile_nf': 1,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 1,
        'major_angles': [2.0, 0.0, 0.0],
        'minor_angles': [2.0, 0.0, 0.0],
    },
    'ecliptic_aspects': {
        '0': [1.0, 0, 0],
        '180': [1.0, 0, 0],
        '90': [1.0, 0, 0],
        '45': [1, 0, 0],
        '120': [0, 0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [0, 0, 0],
        '180': [0, 0, 0],
        '90': [0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 60,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': True,
        '0': [0, 0, 0],
        '180': [0, 0, 0],
        '90': [0, 0, 0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 0, 0],
    },
    'extra_bodies': ['Er', 'Ha'],
    'enable_novien': False,
}

INGRESS_DEFAULT = {
    'use_Vertex': 0,
    'Node': 0,
    'show_aspects': 1,
    'partile_nf': 0,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 0,
        'major_angles': [3.0, 7.0, 10.0],
        'minor_angles': [1.0, 2.0, 3.0],
    },
    'ecliptic_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
        '120': [0, 0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 60,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': True,
        '0': [1.25, 2.0, 3.0],
        '180': [1.25, 2.0, 3.0],
        '90': [1.25, 2.0, 3.0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 2, 3],
    },
    'extra_bodies': ['Er'],
    'enable_novien': False,
}

COSMOBIOLOGY = {
    'use_Vertex': 0,
    'Node': 1,
    'show_aspects': 0,
    'partile_nf': 0,
    'aspect_abbreviation': 2,
    'angularity': {
        'model': 0,
        'no_bg': 1,
        'major_angles': [2.0, 5.0, 0],
        'minor_angles': [2.0, 5.0, 0],
    },
    'ecliptic_aspects': {
        '0': [3.0, 5.0, 0],
        '180': [3.0, 5.0, 0],
        '90': [3.0, 5.0, 0],
        '45': [1.0, 2.0, 0],
        '120': [0, 0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [0, 0, 0],
        '180': [0, 0, 0],
        '90': [0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': False,
        },
        '180': {
            'full': False,
        },
        '90': {
            'full': False,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 60,
        '90': 60,
        '45': 60,
        'M': 0,
        'is90': 'i',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': False,
        '0': [1.25, 2.0, 3.0],
        '180': [1.25, 2.0, 3.0],
        '90': [1.25, 2.0, 3.0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 2, 3],
    },
    'extra_bodies': ['Er'],
    'enable_novien': False,
}

STUDENT_NATAL = {
    'use_Vertex': 0,
    'Node': 0,
    'show_aspects': 0,
    'partile_nf': 0,
    'aspect_abbreviation': 3,
    'angularity': {
        'model': 0,
        'no_bg': 0,
        'major_angles': [3.0, 7.0, 10.0],
        'minor_angles': [1.0, 2.0, 0],
    },
    'ecliptic_aspects': {
        '0': [3.0, 7.0, 0],
        '180': [3.0, 7.0, 0],
        '90': [3.0, 6.0, 0],
        '45': [0, 0, 0],
        '120': [3.0, 6.0, 0],
        '60': [0, 0, 0],
        '30': [0, 0, 0],
        '16': [0, 0, 0],
        '10': [0, 0, 0],
        '5': [0, 0, 0],
        '7': [0, 0, 0],
        '11': [0, 0, 0],
        '13': [0, 0, 0],
    },
    'allowed_ecliptic': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
        '120': {
            'full': False,
        },
        '60': {
            'full': False,
        },
        '30': {
            'full': False,
        },
        '16': {
            'full': False,
        },
        '10': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '5': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '7': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '11': {
            'full': False,
            'half': False,
            'quarter': False,
        },
        '13': {
            'full': False,
            'half': False,
            'quarter': False,
        },
    },
    'mundane_aspects': {
        '0': [3.0, 0, 0],
        '180': [3.0, 0, 0],
        '90': [3.0, 0, 0],
        '45': [0, 0, 0],
    },
    'allowed_mundane': {
        '0': {
            'full': True,
        },
        '180': {
            'full': True,
        },
        '90': {
            'full': True,
        },
        '45': {
            'full': False,
        },
    },
    'midpoints': {
        'enabled': False,
        '0': 0,
        '90': 0,
        '45': 0,
        'M': 0,
        'is90': 'd',
        'mundane_only_to_angles': True,
        'cross_wheel_enabled': False,
    },
    'pvp_aspects': {
        'enabled': False,
        '0': [1.25, 2.0, 3.0],
        '180': [1.25, 2.0, 3.0],
        '90': [1.25, 2.0, 3.0],
    },
    'paran_aspects': {
        'enabled': False,
        '0': [1, 2, 3],
    },
    'extra_bodies': [],
    'enable_novien': False,
}
