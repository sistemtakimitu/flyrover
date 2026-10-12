"""connectome/ tohum kesfi testleri (ag/indirme gerektirmez)."""
import copy
import json
import os
import sys

import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from connectome import data, discover_seeds as ds, modules  # noqa: E402

# 2 LC10a (1, 2), ara noron AOTU019 (100), DNa02 sol/sag (10, 11),
# iki seker GRN'si (20 sugar, 21 sugar/low_salt), bir su GRN'si (22)
ANN = pd.DataFrame({
    'root_id':        [1, 2, 100, 10, 11, 20, 21, 22, 30],
    'cell_type':      ['LC10a', 'LC10a', 'AOTU019', 'DNa02', 'DNa02', 'LB3c', 'LB3b', 'LB3a', 'DNa01'],
    'hemibrain_type': [None, None, None, 'DNa02', 'DNa02', None, None, None, 'VES006'],
    'cell_class':     [None, None, None, None, None, 'gustatory', 'gustatory', 'gustatory', None],
    'cell_sub_class': [None, None, None, None, None, 'sugar', 'sugar/low_salt', 'water', None],
    'super_class':    ['visual_projection'] * 2 + ['central', 'descending', 'descending']
                      + ['sensory'] * 3 + ['descending'],
    'side':           ['left', 'right', 'left', 'left', 'right', 'left', 'right', 'left', 'left'],
    'top_nt':         ['acetylcholine'] * 9,
    'top_nt_conf':    [0.9] * 9,
    'known_nt':       [None] * 9,
})
SEEDS = {
    'LC10a': {'role': 'input', 'module': 'hedef', 'cell_type': 'LC10a', 'expected_per_side': [1, 1]},
    'GRN_sugar': {'role': 'input', 'module': 'uzan', 'expected_per_side': [1, 1],
                  'annotation': {'cell_class': 'gustatory', 'cell_sub_class': ['sugar', 'sugar/low_salt']}},
    'DNa01': {'role': 'mode', 'mode': 'YAKLAS', 'cell_type': 'DNae001', 'expected_per_side': [1, 1]},
    'DNa02': {'role': 'mode', 'mode': 'YAKLAS', 'cell_type': 'DNa02', 'expected_per_side': [1, 1]},
}
CFG = {'version': 1, 'connectome': {}, 'expansion': {'theta': 0.01, 'max_hops': 2, 'min_synapses': 5},
       'seeds': SEEDS, 'default_mode': {}}


def test_repo_modules_yaml_is_valid():
    cfg = modules.load_modules()
    assert {s['role'] for s in cfg['seeds'].values()} == {'input', 'mode', 'record'}


@pytest.mark.parametrize('mutate, message', [
    (lambda c: c['seeds']['DNa02'].update(cell_type='DNae001'), 'ayni secici'),
    (lambda c: c['seeds']['DNa02'].pop('mode'), '`mode` ister'),
    (lambda c: c['seeds']['LC10a'].update(annotation={'cell_type': 'x'}), 'tam olarak bir secici'),
    (lambda c: c['seeds']['GRN_sugar']['annotation'].update(organ='labellum'), 'bilinmeyen'),
    (lambda c: c['seeds']['DNa02'].update(role='record'), 'record tohumu'),
    (lambda c: c['seeds']['DNa02'].update(expected_per_side=[2, 1]), 'expected_per_side'),
    (lambda c: c.pop('expansion'), 'eksik alanlar'),
])
def test_validate_rejects(mutate, message):
    cfg = copy.deepcopy(CFG)
    mutate(cfg)
    with pytest.raises(modules.ModulesError, match=message):
        modules.validate(cfg)


def test_annotation_selector_takes_list_and_excludes_water():
    sel = modules.select(ANN, SEEDS['GRN_sugar'])
    assert sorted(sel['root_id']) == [20, 21]


def test_count_status():
    assert modules.count_status({'left': 1, 'right': 1}, [1, 1]) == 'OK'
    assert modules.count_status({'left': 1, 'right': 0}, [1, 1]) == 'SAPMA'
    assert modules.count_status({'left': 5, 'right': 5}, None) == 'SABITLENMEDI'


def test_seed_table_flags_missing_type():
    table = ds.seed_table(ANN, SEEDS).set_index('tohum')
    assert table.loc['DNa02', 'durum'] == 'OK'
    assert table.loc['DNa01', 'toplam'] == 0          # DNae001 bu sentetik veride yok
    assert table.loc['DNa01', 'durum'] == 'SAPMA'


def test_name_collision_reports_flywire_dna01():
    col = ds.name_collisions(ANN, SEEDS)
    row = col[col['tohum'] == 'DNa01'].iloc[0]
    assert (row['cakisan cell_type'], row['hemibrain_type']) == ('DNa01', 'VES006')


def test_path_scan_two_hop_bottleneck():
    edges = pd.DataFrame({'pre':  [1, 2, 100, 100],
                          'post': [100, 100, 10, 11],
                          'syn_count': [30, 20, 7, 9]})
    paths = ds.path_scan(ANN, edges, SEEDS)
    row = paths[(paths['girdi'] == 'LC10a') & (paths['hedef'] == 'DNa02')].iloc[0]
    assert row['dogrudan'] == 0
    assert row['2_sicrama_en_iyi'] == 16                # min(30+20, 7+9)
    assert row['ara_tipler'] == 'AOTU019 (16)'


def test_resolve_checks_hash(tmp_path):
    path = tmp_path / 'x.tsv'
    path.write_text('abc')
    hashes = {'annotations': {'file': 'x.tsv', 'sha256': data.sha256(path), 'source': 'test'}}
    assert data.resolve('annotations', cache_dir=tmp_path, hashes=hashes) == str(path)
    hashes['annotations']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='hash'):
        data.resolve('annotations', cache_dir=tmp_path, hashes=hashes)


def test_load_edges_sums_over_neuropils(tmp_path):
    df = pd.DataFrame({'pre_pt_root_id': [1, 1, 2], 'post_pt_root_id': [10, 10, 10],
                       'neuropil': ['A', 'B', 'A'], 'syn_count': [3, 4, 2]})
    path = tmp_path / 'c.feather'
    df.to_feather(path)
    edges = data.load_edges(path, min_synapses=5)
    assert edges.to_dict('records') == [{'pre': 1, 'post': 10, 'syn_count': 7}]


def test_data_hashes_json_has_both_inputs():
    with open(data.HASHES_PATH) as f:
        hashes = json.load(f)
    assert set(hashes) == {'connections', 'annotations'}
    assert all(len(v['sha256']) == 64 for v in hashes.values())
