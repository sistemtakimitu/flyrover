"""build_type_graph.py hesaplama testleri (ag/indirme gerektirmez)."""
import os
import sys

import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src', 'data'))
import build_type_graph as btg  # noqa: E402

# Iki LC4_L noronu (1, 2), bir GF_L noronu (10), iki DNp04_L noronu (20, 21),
# ara noronlar: 100 (uyarici), 101 (baskilayici)
ANN = pd.DataFrame({
    'root_id':   [1, 2, 10, 20, 21, 100, 101],
    'cell_type': ['LC4', 'LC4', 'DNp01', 'DNp04', 'DNp04', None, None],
    'side':      ['left'] * 7,
    'top_nt':    ['acetylcholine', 'acetylcholine', 'glutamate', 'acetylcholine',
                  'acetylcholine', 'acetylcholine', 'gaba'],
    'known_nt':  [None, None, 'acetylcholine', None, None, None, None],
})
TYPES = {'LC4': 'LC4', 'GF': 'DNp01', 'DNp04': 'DNp04'}


def conn(*rows):
    return pd.DataFrame(rows, columns=['pre', 'post', 'syn'])


@pytest.fixture
def setup():
    node_of = btg.assign_nodes(ANN, TYPES)
    sign, _ = btg.neuron_signs(ANN)
    return node_of, sign


def weights(edges, etype):
    e = edges[edges['edge_type'] == etype]
    return {(r.pre_node, r.post_node): r.weight for r in e.itertuples()}


def test_nodes_group_all_neurons_of_type_by_side(setup):
    node_of, _ = setup
    assert node_of.value_counts().to_dict() == {'LC4_L': 2, 'DNp04_L': 2, 'GF_L': 1}


def test_known_nt_overrides_prediction(setup):
    _, sign = setup
    assert sign[10] == 1      # GF: tahmin glutamat ama bilinen NT asetilkolin
    assert sign[101] == -1


def test_population_synapses_are_summed_per_target_neuron(setup):
    node_of, sign = setup
    # Tek tek esik alti gibi gorunen LC4 katkilari toplaninca guclu bir kenar olur
    c = conn((1, 10, 6), (2, 10, 7), (1, 20, 10), (2, 21, 10), (1, 21, 3))
    edges = btg.build_type_edges(c, node_of, sign, pd.Series(dtype=float))
    w = weights(edges, 'measured')
    assert w[('LC4_L', 'GF_L')] == pytest.approx(13.0)      # 13 sinaps / 1 GF
    assert w[('LC4_L', 'DNp04_L')] == pytest.approx(10.0)   # 20 sinaps / 2 DNp04 (3'luk atildi)


def test_path_integrated_is_normalized_and_signed(setup):
    node_of, sign = setup
    # LC4 -> 101 (GABA) -> GF : baskilayici dolayli yol
    c = conn((1, 101, 10), (2, 101, 10), (101, 10, 30))
    edges = btg.build_type_edges(c, node_of, sign, pd.Series({101: 40}))
    # (+1)(-1) * 20/40 * 30 / 1 = -15
    assert weights(edges, 'path-integrated')[('LC4_L', 'GF_L')] == pytest.approx(-15.0)


def test_weak_type_edges_dropped(setup):
    node_of, sign = setup
    c = conn((1, 100, 5), (100, 20, 5))
    edges = btg.build_type_edges(c, node_of, sign, pd.Series({100: 1000}))
    assert edges.empty   # 5/1000*5/2 = 0.0125 < MIN_TYPE_WEIGHT
