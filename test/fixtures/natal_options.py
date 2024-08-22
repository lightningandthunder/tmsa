import pytest


@pytest.fixture
def natal_options():
    return {
        'use_Eris': 1,
        'use_Sedna': 0,
        'use_Vertex': 1,
        'Node': 0,
        'show_aspects': 0,
        'partile_nf': 1,
        'angularity': {
            'model': 2,
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
        },
        'mundane_aspects': {
            '0': [3.0, 0, 0],
            '180': [3.0, 0, 0],
            '90': [3.0, 0, 0],
            '45': [0, 0, 0],
        },
        'midpoints': {'0': 90, '90': 90, '45': 90, 'M': 0, 'is90': 'd'},
    }
