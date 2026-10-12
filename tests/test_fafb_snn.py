"""src/snn/fafb_snn.py testleri (sentetik kucuk ag, numpy kod uretimi; veri gerektirmez)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src', 'snn'))
from fafb_snn import FafbSNN  # noqa: E402

# IN_L (1, 2) -> ara 100 -> OUT_L (10); IN_R (3) -> INH (101, inhibitor) -> OUT_R (11)
NEURONS = pd.DataFrame({
    'root_id': [1, 2, 3, 100, 101, 10, 11],
    'side':    ['left', 'left', 'right', 'left', 'right', 'left', 'right'],
    'seed':    ['IN', 'IN', 'IN', '', '', 'OUT', 'OUT'],
    'role':    ['input', 'input', 'input', '', '', 'mode', 'mode'],
})
EDGES = pd.DataFrame({
    'pre':       [1, 2, 100, 3, 101],
    'post':      [100, 100, 10, 101, 11],
    'syn_count': [40, 40, 60, 60, 60],
    'sign':      [1, 1, 1, 1, -1],
})


def make(**kw):
    return FafbSNN(NEURONS, EDGES, codegen='numpy', **kw)


def test_groups_and_inputs():
    snn = make()
    assert snn.input_groups == ['IN_L', 'IN_R']
    assert set(snn.groups) == {'IN_L', 'IN_R', 'OUT_L', 'OUT_R'}
    with pytest.raises(KeyError):
        snn.step({'OUT_L': 10.0})


def test_silent_without_input_and_excitatory_path_drives_output():
    snn = make(seed=1)
    assert all(v == 0 for v in snn.step({}, 20.0).values())
    rates = [snn.step({'IN_L': 200.0, 'IN_R': 200.0}, 20.0) for _ in range(5)]
    assert np.mean([r['IN_L'] for r in rates]) > 50
    assert np.mean([r['OUT_L'] for r in rates]) > 0          # uyarici yol
    assert all(r['OUT_R'] == 0 for r in rates)                # inhibitor yol


def test_persistent_mode_matches_per_run_with_same_seed():
    inputs = [{'IN_L': 150.0}, {'IN_L': 150.0, 'IN_R': 80.0}, {}, {'IN_R': 200.0}, {'IN_L': 60.0}]
    a = make(seed=7, mode='per_run')
    ra = [a.step(x, 20.0) for x in inputs]
    b = make(seed=7, mode='persistent', step_ms=20.0)
    rb = [b.step(x) for x in inputs]
    b.close()
    assert ra == rb
    assert (a.spike_counts() == b.spike_counts()).all()


def test_persistent_rejects_other_step_length():
    snn = make(mode='persistent', step_ms=20.0)
    with pytest.raises(ValueError, match='sabit'):
        snn.step({}, 10.0)
    snn.close()
