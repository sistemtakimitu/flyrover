"""Faz 1 kabul testi: connectome ile surulen rover, ustune gelen toptan kacabiliyor mu?
Kapali dongu (MuJoCo + Brian2) ~30-60 s surer."""
import os
import sys

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
from sim.escape_demo import run  # noqa: E402


@pytest.fixture(scope='module')
def with_brain():
    return run(brain=True, duration_s=5.0, threat_speed=1.2)


def test_without_brain_rover_is_hit():
    assert run(brain=False, duration_s=5.0, threat_speed=1.2)['collided']


def test_with_brain_rover_escapes(with_brain):
    assert not with_brain['collided']
    assert with_brain['rover_dx'] < -1.0          # geri kacti


def test_escape_is_triggered_by_nearby_threat_not_far_away(with_brain):
    first = next(s for s in with_brain['trace'] if s['v'] < -0.05)
    assert 0.8 < first['dist'] < 3.0
