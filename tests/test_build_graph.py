"""connectome/build_graph.py testleri (sentetik veri, ag/indirme gerektirmez)."""
import copy
import os
import sys

import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from connectome import build_graph as bg  # noqa: E402

# Girdi tohumu IN (1, 2) -> ara 100 -> ara 101 -> DN tohumu OUT (10 sol, 11 sag)
# 200: IN'in yukari akisi (directed'da alinmamali); 300: OUT'un asagi akisi (alinmamali)
# 102: 100'un zayif ciktisi (theta'ya gore); 103: top_nt'si yok
ANN = pd.DataFrame({
    'root_id':     [1, 2, 100, 101, 10, 11, 200, 300, 102, 103],
    'cell_type':   ['IN', 'IN', 'MID', 'MID2', 'OUT', 'OUT', 'UP', 'DOWN', 'WEAK', 'NONT'],
    'side':        ['left', 'right', 'left', 'left', 'left', 'right', 'left', 'left', 'left', 'left'],
    'super_class': ['visual_projection', 'visual_projection', 'central', 'central',
                    'descending', 'descending', 'optic', 'central', 'central', 'central'],
    'top_nt':      ['acetylcholine', 'acetylcholine', 'gaba', 'acetylcholine', 'acetylcholine',
                    'acetylcholine', 'acetylcholine', 'acetylcholine', 'acetylcholine', None],
    'top_nt_conf': [0.9] * 10,
})
EDGES = pd.DataFrame([
    (200, 1, 50), (200, 2, 50),         # yukari akis
    (1, 100, 40), (2, 100, 40),
    (100, 101, 30), (100, 102, 5),      # 102: 100'un cikisinin %14'u
    (101, 10, 20), (101, 11, 20),
    (10, 300, 60),                      # asagi akis
    (103, 101, 10),                     # NT'siz noron, 101'in anlamli girdisi
    (1, 2, 3),                          # esik alti
], columns=['pre', 'post', 'syn_count'])
CFG = {
    'version': 1, 'connectome': {}, 'default_mode': {},
    'expansion': {'theta': 0.05, 'max_hops': 2, 'min_synapses': 5, 'direction': 'directed'},
    'seeds': {
        'IN':  {'role': 'input', 'module': 'm', 'cell_type': 'IN', 'expected_per_side': [1, 1]},
        'OUT': {'role': 'mode', 'mode': 'KAC', 'cell_type': 'OUT', 'expected_per_side': [1, 1]},
    },
}


def run(cfg=CFG, edges=EDGES, overrides=()):
    return bg.build(cfg, ANN, edges, lambda ids: {i: 'glutamate' for i in ids}, list(overrides))


def test_directed_expansion_skips_upstream_of_inputs_and_downstream_of_outputs():
    neurons, *_ = run()
    ids = set(neurons['root_id'])
    assert {1, 2, 10, 11, 100, 101, 103} <= ids
    assert 200 not in ids and 300 not in ids


def test_theta_threshold_on_partner_fraction():
    # 100 -> 102: 5 / (30 + 5) = 0.14 of 100's output
    neurons, *_ = run()
    assert 102 in set(neurons['root_id'])           # theta = 0.05
    cfg = copy.deepcopy(CFG)
    cfg['expansion']['theta'] = 0.2
    neurons, *_ = run(cfg)
    assert 102 not in set(neurons['root_id'])


def test_bidirectional_includes_upstream():
    cfg = copy.deepcopy(CFG)
    cfg['expansion']['direction'] = 'bidirectional'
    neurons, *_ = run(cfg)
    assert {200, 300} <= set(neurons['root_id'])


def test_edges_are_induced_neuron_level_and_thresholded():
    neurons, edges, *_ = run()
    ids = set(neurons['root_id'])
    assert set(edges['pre']) <= ids and set(edges['post']) <= ids
    assert (edges['syn_count'] >= 5).all()
    assert ((1, 2) not in set(zip(edges['pre'], edges['post'])))
    assert set(edges['source']) == {'measured'}


def test_signs_weights_and_nt_fallback():
    neurons, edges, *_ = run()
    n = neurons.set_index('root_id')
    assert n.loc[100, 'sign'] == -1                 # gaba
    assert (n.loc[103, 'nt'], n.loc[103, 'nt_source'], n.loc[103, 'sign']) == ('glutamate', 'synapse_avg', -1)
    e = edges.set_index(['pre', 'post'])
    assert e.loc[(100, 101), 'weight_mv'] == pytest.approx(-30 * bg.W_SYN_MV)
    assert e.loc[(1, 100), 'weight_mv'] == pytest.approx(40 * bg.W_SYN_MV)


def test_sign_override_applies_to_whole_type():
    override = {'cell_type': 'MID', 'sign': 1, 'source': 'x', 'reviewer': 'y'}
    neurons, edges, *_ = run(overrides=[override])
    n = neurons.set_index('root_id')
    assert (n.loc[100, 'sign'], n.loc[100, 'sign_source']) == (1, 'override')
    assert edges.set_index(['pre', 'post']).loc[(100, 101), 'sign'] == 1


def test_override_for_missing_type_fails():
    with pytest.raises(bg.GraphError, match='agda yok'):
        run(overrides=[{'cell_type': 'YOK', 'sign': 1, 'source': 'x', 'reviewer': 'y'}])


def test_seed_count_deviation_stops_build():
    cfg = copy.deepcopy(CFG)
    cfg['seeds']['IN']['expected_per_side'] = [2, 3]
    with pytest.raises(bg.GraphError, match='beklenen'):
        run(cfg)


def test_graph_hash_deterministic_and_sensitive():
    n1, e1, *_ = run()
    n2, e2, *_ = run()
    assert bg.graph_hash(n1, e1) == bg.graph_hash(n2, e2)
    shuffled = e1.sample(frac=1, random_state=0)
    assert bg.graph_hash(n1, shuffled) == bg.graph_hash(n1, e1)     # satir sirasi onemsiz
    changed = e1.copy()
    changed.loc[0, 'syn_count'] += 1
    assert bg.graph_hash(n1, changed) != bg.graph_hash(n1, e1)


def test_reachability_paths():
    adj = {1: [(100, 40)], 2: [(100, 40)], 100: [(101, 30), (5, 90)], 5: [(6, 90)], 6: [(101, 90)],
           101: [(10, 20)]}
    assert bg.shortest_hops(adj, {1, 2}, {10}) == 3
    width, path = bg.strongest_short_path(adj, {1}, {10}, max_len=3)
    assert (width, path) == (20, [1, 100, 101, 10])
    assert bg.strongest_short_path(adj, {1}, {10}, max_len=2) == (0, [])


def test_engineered_edges_reject_path_integrated(tmp_path):
    p = tmp_path / 'e.yaml'
    p.write_text("edges:\n  - {pre_cell_type: A, post_cell_type: B, syn_count: 9, sign: 1,"
                 " kind: path-integrated, reason: r, reviewer: x}\n")
    with pytest.raises(bg.GraphError, match='path-integrated'):
        bg.load_engineered_edges(p)
    p.write_text("edges:\n  - {pre_cell_type: A, post_cell_type: B, syn_count: 9, sign: 1,"
                 " reason: r, reviewer: x}\n")
    with pytest.raises(bg.GraphError, match='desteklemez'):
        bg.load_engineered_edges(p)


def test_sign_overrides_schema(tmp_path):
    p = tmp_path / 's.yaml'
    p.write_text("overrides:\n  - {cell_type: DNp01, sign: 1, source: '', reviewer: x}\n")
    with pytest.raises(bg.GraphError, match='gecersiz'):
        bg.load_sign_overrides(p)


def test_repo_override_files_are_valid():
    assert bg.load_sign_overrides() == []
    assert bg.load_engineered_edges() == []
