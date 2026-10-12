"""
FlyWire v783 girdilerinin hash dogrulamali yuklenmesi.

Dosyalar data/cache/ altinda (gitignore); beklenen SHA-256 degerleri
connectome/data_hashes.json'da. Hash uyusmazsa yukleme durur (ADR 0006 B1).
"""
import hashlib
import json
import os

import pandas as pd
import pyarrow.feather as feather

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'cache')
HASHES_PATH = os.path.join(BASE_DIR, 'connectome', 'data_hashes.json')

ANNOTATION_COLUMNS = ['root_id', 'super_class', 'cell_class', 'cell_sub_class',
                      'cell_type', 'hemibrain_type', 'side', 'nerve',
                      'top_nt', 'top_nt_conf', 'known_nt']


def sha256(path, chunk_size=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()


def load_hashes(path=HASHES_PATH):
    with open(path) as f:
        return json.load(f)


def resolve(name, cache_dir=CACHE_DIR, verify_hash=True, hashes=None):
    """data_hashes.json'daki girdinin yolu; verify_hash ise SHA-256 kontrol edilir."""
    entry = (hashes or load_hashes())[name]
    path = os.path.join(cache_dir, entry['file'])
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} yok. Kaynak: {entry['source']}")
    if verify_hash:
        actual = sha256(path)
        if actual != entry['sha256']:
            raise ValueError(f"{entry['file']} hash uyusmuyor: {actual} != {entry['sha256']}")
    return path


def load_annotations(path):
    ann = pd.read_csv(path, sep='\t', usecols=ANNOTATION_COLUMNS, low_memory=False,
                      dtype={c: str for c in ANNOTATION_COLUMNS if c != 'root_id'})
    ann['root_id'] = ann['root_id'].astype('int64')
    ann['top_nt_conf'] = pd.to_numeric(ann['top_nt_conf'], errors='coerce')
    return ann


def load_edges(path, min_synapses=1):
    """Noron-noron kenarlari: neuropil'ler uzerinden toplanmis sinaps sayisi."""
    table = feather.read_table(path, columns=['pre_pt_root_id', 'post_pt_root_id', 'syn_count'])
    edges = (table.to_pandas()
             .rename(columns={'pre_pt_root_id': 'pre', 'post_pt_root_id': 'post'})
             .groupby(['pre', 'post'], as_index=False)['syn_count'].sum())
    return edges[edges['syn_count'] >= min_synapses].reset_index(drop=True)
