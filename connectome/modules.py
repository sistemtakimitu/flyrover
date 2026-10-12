"""
config/modules.yaml yukleyici ve dogrulayici (ADR 0010).

Kurallar:
  - her tohumun tam olarak bir secicisi var: `cell_type` ya da `annotation`
  - ayni secici iki tohumda kullanilamaz (ayrik mod populasyonlari, ADR 0002)
  - role: input -> `module`, role: mode -> `mode` zorunlu; record ikisini de almaz
  - expected_per_side: [alt, ust] (alt <= ust)
  - expansion.direction: directed (girdi -> ileri, mod/kayit -> geri) ya da bidirectional
"""
import os

import pandas as pd
import yaml

from connectome.data import ANNOTATION_COLUMNS, BASE_DIR

MODULES_PATH = os.path.join(BASE_DIR, 'config', 'modules.yaml')
TOP_LEVEL_KEYS = {'version', 'connectome', 'expansion', 'seeds', 'default_mode'}
ROLES = {'input', 'mode', 'record'}
DIRECTIONS = {'directed', 'bidirectional'}
SIDES = ('left', 'right')


class ModulesError(ValueError):
    pass


def _selector_key(spec):
    if 'cell_type' in spec:
        return ('cell_type', spec['cell_type'])
    return ('annotation', tuple(sorted((k, tuple(v) if isinstance(v, list) else v)
                                       for k, v in spec['annotation'].items())))


def validate(cfg):
    missing = TOP_LEVEL_KEYS - set(cfg)
    if missing:
        raise ModulesError(f"eksik alanlar: {sorted(missing)}")
    exp = cfg['expansion']
    if not (0 < exp['theta'] < 1 and exp['max_hops'] >= 0 and exp['min_synapses'] >= 1
            and exp.get('direction') in DIRECTIONS):
        raise ModulesError(f"gecersiz expansion: {exp}")

    seen = {}
    for name, spec in cfg['seeds'].items():
        role = spec.get('role')
        if role not in ROLES:
            raise ModulesError(f"{name}: role {sorted(ROLES)} icinden olmali")
        if ('cell_type' in spec) == ('annotation' in spec):
            raise ModulesError(f"{name}: tam olarak bir secici (cell_type / annotation) gerekli")
        if 'annotation' in spec:
            unknown = set(spec['annotation']) - set(ANNOTATION_COLUMNS)
            if unknown:
                raise ModulesError(f"{name}: bilinmeyen anotasyon sutunlari {sorted(unknown)}")
        if role == 'input' and 'module' not in spec:
            raise ModulesError(f"{name}: input tohumu `module` ister")
        if role == 'mode' and 'mode' not in spec:
            raise ModulesError(f"{name}: mode tohumu `mode` ister")
        if role == 'record' and ('mode' in spec or 'module' in spec):
            raise ModulesError(f"{name}: record tohumu moda/modüle giremez")
        rng = spec.get('expected_per_side')
        if rng is not None and not (len(rng) == 2 and 0 <= rng[0] <= rng[1]):
            raise ModulesError(f"{name}: expected_per_side [alt, ust] olmali")
        key = _selector_key(spec)
        if key in seen:
            raise ModulesError(f"{name} ve {seen[key]} ayni secici: {key}")
        seen[key] = name
    return cfg


def load_modules(path=MODULES_PATH):
    with open(path) as f:
        return validate(yaml.safe_load(f))


def select(ann, spec):
    """Tohum secicisine uyan anotasyon satirlari."""
    if 'cell_type' in spec:
        return ann[ann['cell_type'] == spec['cell_type']]
    mask = pd.Series(True, index=ann.index)
    for col, val in spec['annotation'].items():
        mask &= ann[col].isin(val if isinstance(val, list) else [val])
    return ann[mask]


def side_counts(rows):
    counts = rows['side'].value_counts()
    return {s: int(counts.get(s, 0)) for s in SIDES}


def count_status(counts, expected):
    if expected is None:
        return 'SABITLENMEDI'
    lo, hi = expected
    return 'OK' if all(lo <= counts[s] <= hi for s in SIDES) else 'SAPMA'
