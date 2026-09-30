"""fetch_data.py'nin hesaplama kisminin ag erisimi olmadan testleri."""
import itertools
import json
import os
import sys

import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src', 'data'))
import fetch_data as fd  # noqa: E402

# Ornek devre -- A, B, C bizim noronlarimiz; K, J ara noron
A, B, C, K, J = 1, 2, 3, 10, 11
ROOTS = [A, B, C]
NT = {A: 'ach', B: 'gaba', C: 'glut', K: 'ach', J: 'gaba'}
_ids = itertools.count()


def synapses(pre, post, n, cleft=100):
    rows = []
    for _ in range(n):
        row = {'id': next(_ids), 'pre_pt_root_id': pre, 'post_pt_root_id': post,
               'cleft_score': cleft}
        row.update({nt: (0.9 if nt == NT[pre] else 0.02) for nt in fd.NT_COLUMNS})
        rows.append(row)
    return rows


@pytest.fixture
def circuit():
    rows = (synapses(A, B, 6)              # measured, +6
            + synapses(B, C, 5)            # measured, GABA -> -5
            + synapses(C, A, 4)            # esik alti -> atilir
            + synapses(A, C, 10, cleft=20)  # dusuk cleft_score -> atilir
            + synapses(A, K, 10) + synapses(K, C, 20)   # A->K->C
            + synapses(K, B, 50)                        # A->K->B (measured var, eklenmemeli)
            + synapses(B, J, 8) + synapses(J, A, 10))   # B->J->A, iki baskilayici
    syn = fd.filter_synapses(pd.DataFrame(rows))
    down = syn[syn['pre_pt_root_id'].isin(ROOTS)]
    up = syn[syn['post_pt_root_id'].isin(ROOTS)]
    return down, up, {K: 100, J: 40}


def edges_by_pair(df):
    return {(r.pre_pt_root_id, r.post_pt_root_id): r.weight for r in df.itertuples()}


def test_measured_edges_are_thresholded_and_signed(circuit):
    measured, _, _ = fd.build_edges(*circuit, ROOTS)
    assert edges_by_pair(measured) == {(A, B): 6, (B, C): -5}


def test_glutamate_is_inhibitory(circuit):
    _, _, nt = fd.build_edges(*circuit, ROOTS)
    assert nt[C] == 'glut'
    assert fd.NT_SIGN['glut'] == -1


def test_path_weight_is_input_normalized(circuit):
    _, path, _ = fd.build_edges(*circuit, ROOTS)
    got = edges_by_pair(path)
    # A->K->C: (+1)(+1) * 10/100 * 20 = 2.0
    assert got[(A, C)] == pytest.approx(2.0)
    # B->J->A: (-1)(-1) * 8/40 * 10 = 2.0  (baskilayicinin baskilanmasi = net uyarim)
    assert got[(B, A)] == pytest.approx(2.0)


def test_path_edge_not_added_where_measured_exists(circuit):
    _, path, _ = fd.build_edges(*circuit, ROOTS)
    assert (A, B) not in edges_by_pair(path)


def test_missing_input_total_raises(circuit):
    down, up, _ = circuit
    with pytest.raises(ValueError):
        fd.build_edges(down, up, {K: 100}, ROOTS)


def test_committed_graph_follows_edge_type_rule():
    """AGENTS.md: her kenar measured / path-integrated / engineered olmali."""
    with open(os.path.join(BASE_DIR, 'config', 'connectome_graph.json')) as f:
        graph = json.load(f)
    allowed = {'measured', 'path-integrated', 'engineered'}
    assert {e['edge_type'] for e in graph['edges']} <= allowed
    assert all(str(e['pre_root_id']) in graph['nodes'] and str(e['post_root_id']) in graph['nodes']
               for e in graph['edges'])
