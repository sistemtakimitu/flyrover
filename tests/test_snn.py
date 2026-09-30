"""SNN davranis testleri: hucre tipi grafi uzerinde bilinen devreler calisiyor mu?"""
import os
import sys

import pytest
from brian2 import seed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
from snn.network import ConnectomeSNN  # noqa: E402

GRAPH = os.path.join(BASE_DIR, 'config', 'type_graph.json')


def mean_rates(inputs, steps=15, duration_ms=20):
    """Ilk 5 adimi (gecis) atip kalan adimlarin ortalama hizlari."""
    seed(1)
    snn = ConnectomeSNN.from_json(GRAPH)
    total = {}
    for k in range(steps):
        r = snn.step(inputs, duration_ms)
        if k >= 5:
            for name, v in r.items():
                total[name] = total.get(name, 0) + v / (steps - 5)
    return total


def test_silent_without_input():
    assert all(v == 0 for v in mean_rates({}, steps=8).values())


def test_looming_left_drives_left_escape_only():
    r = mean_rates({'LC4_L': 60})
    for dn in ['DNp04_L', 'DNp02_L', 'GF_L']:
        assert r[dn] > 20, dn
    for other in ['DNp04_R', 'GF_R', 'DNa02_L', 'DNa02_R', 'MDN_L', 'MDN_R']:
        assert r[other] == 0, other


def test_lplc2_drives_giant_fiber():
    r = mean_rates({'LPLC2_R': 60})
    assert r['GF_R'] > 20
    assert r['GF_L'] < r['GF_R']


@pytest.mark.parametrize('side,other', [('L', 'R'), ('R', 'L')])
def test_target_on_one_side_drives_ipsilateral_steering(side, other):
    r = mean_rates({f'LC10a_{side}': 60})
    assert r[f'DNa02_{side}'] > 20
    assert r[f'DNa02_{side}'] > 2 * r[f'DNa02_{other}']
