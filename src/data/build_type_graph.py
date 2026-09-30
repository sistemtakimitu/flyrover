"""
Hucre tipi seviyesinde connectome grafi -> config/type_graph.json

Neden: tek bir temsilci noron gercek etkiyi temsil etmez. Ornegin DNp04'e ~55 LC4
birden baglanir; tek LC4'un sinapslari biyolojik parametrelerle DNp04'u atesleyemez.
Burada her (hucre tipi, taraf) bir dugumdur ve o tipin TUM noronlarini kapsar.

Veri (ikisi de acik, token gerektirmez; data/cache/ altina indirilir):
  - FlyWire baglanti tablosu v783 (Dorkenwald et al. 2024, Zenodo 10676866)
  - FlyWire noron etiketleri (Schlegel et al. 2024, flyconnectome/flywire_annotations)

Agirliklar (fetch_data.py ile ayni mantik, tip seviyesinde):
  measured        : W(A->B) = isaret(A) * sum(sinaps A->B) / N_B
  path-integrated : W(A->B) = sum_k isaret(A)*isaret(k) * (S_Ak / girdi_k) * S_kB / N_B
Birim: "B tipinin bir noronunun aldigi ortalama (esdeger) sinaps sayisi".
"""
import json
import os
import sys
import urllib.request

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_data import BASE_DIR, CACHE_DIR, MIN_SYNAPSES, NT_SIGN  # noqa: E402

TYPES_PATH = os.path.join(BASE_DIR, 'config', 'cell_types.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'config', 'type_graph.json')

CONNECTIONS_URL = ('https://zenodo.org/records/10676866/files/'
                   'proofread_connections_783.feather?download=1')
ANNOTATIONS_URL = ('https://raw.githubusercontent.com/flyconnectome/flywire_annotations/'
                   'main/supplemental_files/Supplemental_file1_neuron_annotations.tsv')
CONNECTIONS_PATH = os.path.join(CACHE_DIR, 'proofread_connections_783.feather')
ANNOTATIONS_PATH = os.path.join(CACHE_DIR, 'flywire_annotations.tsv')

# Tip seviyesinde bundan zayif kenarlar (hedef noron basina < 1 esdeger sinaps) atilir.
MIN_TYPE_WEIGHT = 1.0

NT_NAMES = {'acetylcholine': 'ach', 'gaba': 'gaba', 'glutamate': 'glut',
            'octopamine': 'oct', 'serotonin': 'ser', 'dopamine': 'da'}
SIDES = {'left': 'L', 'right': 'R', 'center': 'C'}


def download(url, path):
    if not os.path.exists(path):
        os.makedirs(CACHE_DIR, exist_ok=True)
        print(f"Indiriliyor: {url}")
        urllib.request.urlretrieve(url, path + '.part')
        os.replace(path + '.part', path)


def load_types(path=TYPES_PATH, phases=None):
    """{kisa_ad: resmi_cell_type} -- istenen fazlarin birlesimi."""
    with open(path) as f:
        cfg = json.load(f)['faz']
    out = {}
    for phase, types in cfg.items():
        if phases is None or phase in phases:
            out.update(types)
    return out


# ---------------------------------------------------------------------------
# Saf hesaplama (tests/test_build_type_graph.py)
# ---------------------------------------------------------------------------

def neuron_signs(ann):
    """Her noron icin isaret. Tip biliniyorsa tipin cogunluk NT'si (tek noron tahmin
    hatalarini duzeltir), yoksa noronun kendi NT'si. known_nt, top_nt'den onceliklidir."""
    nt = ann['known_nt'].where(ann['known_nt'].isin(NT_NAMES), ann['top_nt']).map(NT_NAMES)
    typed = ann['cell_type'].notna()
    type_nt = nt[typed].groupby(ann.loc[typed, 'cell_type']).agg(
        lambda s: s.mode().iloc[0] if not s.mode().empty else None)
    nt = nt.where(~typed, ann['cell_type'].map(type_nt))
    return pd.Series(nt.map(NT_SIGN).fillna(1).astype(int).values, index=ann['root_id']), \
        pd.Series(nt.values, index=ann['root_id'])


def assign_nodes(ann, types):
    """root_id -> dugum adi ('LC4_L' gibi); sadece secilen tipler."""
    official_to_alias = {v: k for k, v in types.items()}
    sel = ann[ann['cell_type'].isin(official_to_alias)]
    names = sel['cell_type'].map(official_to_alias) + '_' + sel['side'].map(SIDES).fillna('C')
    return pd.Series(names.values, index=sel['root_id'].values)


def build_type_edges(conn, node_of, sign, input_total):
    """
    conn        : DataFrame[pre, post, syn] (noron ciftleri, noropillere gore toplanmis)
    node_of     : Series root_id -> dugum adi (devredeki noronlar)
    sign        : Series root_id -> +1/-1 (tum noronlar)
    input_total : Series root_id -> toplam giris sinapsi
    Doner: DataFrame[pre_node, post_node, weight, edge_type]
    """
    conn = conn[conn['syn'] >= MIN_SYNAPSES]
    size = node_of.value_counts()
    in_circuit = conn['pre'].isin(node_of.index), conn['post'].isin(node_of.index)

    direct = conn[in_circuit[0] & in_circuit[1]].assign(
        A=lambda d: d['pre'].map(node_of), B=lambda d: d['post'].map(node_of),
        s=lambda d: d['pre'].map(sign) * d['syn'])
    direct = direct[direct['A'] != direct['B']]
    measured = direct.groupby(['A', 'B'])['s'].sum().reset_index(name='weight')
    measured['weight'] = measured['weight'] / measured['B'].map(size)
    measured = measured[measured['weight'].abs() >= MIN_TYPE_WEIGHT]

    a_k = (conn[in_circuit[0] & ~in_circuit[1]]
           .assign(A=lambda d: d['pre'].map(node_of))
           .groupby(['A', 'post'])['syn'].sum().reset_index(name='s_ak')
           .rename(columns={'post': 'k'}))
    k_b = (conn[~in_circuit[0] & in_circuit[1]]
           .assign(B=lambda d: d['post'].map(node_of))
           .groupby(['pre', 'B'])['syn'].sum().reset_index(name='s_kb')
           .rename(columns={'pre': 'k'}))
    paths = a_k.merge(k_b, on='k')
    paths = paths[paths['A'] != paths['B']]
    if paths.empty:
        return measured.assign(edge_type='measured').rename(
            columns={'A': 'pre_node', 'B': 'post_node'})
    a_sign = node_of.groupby(node_of).apply(lambda s: sign.reindex(s.index).mode().iloc[0])
    paths['w'] = (paths['A'].map(a_sign) * paths['k'].map(sign)
                  * paths['s_ak'] / paths['k'].map(input_total) * paths['s_kb'])
    path = paths.groupby(['A', 'B'])['w'].sum().reset_index(name='weight')
    path['weight'] = path['weight'] / path['B'].map(size)
    have = set(zip(measured['A'], measured['B']))
    path = path[[p not in have for p in zip(path['A'], path['B'])]]
    path = path[path['weight'].abs() >= MIN_TYPE_WEIGHT]

    return pd.concat([measured.assign(edge_type='measured'),
                      path.assign(edge_type='path-integrated')], ignore_index=True) \
        .rename(columns={'A': 'pre_node', 'B': 'post_node'})


# ---------------------------------------------------------------------------

def main(phases=None):
    download(ANNOTATIONS_URL, ANNOTATIONS_PATH)
    download(CONNECTIONS_URL, CONNECTIONS_PATH)

    ann = pd.read_csv(ANNOTATIONS_PATH, sep='\t', low_memory=False,
                      usecols=['root_id', 'cell_type', 'side', 'top_nt', 'known_nt'])
    types = load_types(phases=phases)
    missing = set(types.values()) - set(ann['cell_type'].dropna())
    if missing:
        raise ValueError(f"FlyWire etiketlerinde bulunamayan tipler: {sorted(missing)}")
    node_of = assign_nodes(ann, types)
    sign, nt = neuron_signs(ann)
    print(f"{node_of.nunique()} dugum, {len(node_of)} noron")

    print("Baglanti tablosu okunuyor...")
    raw = pd.read_feather(CONNECTIONS_PATH, columns=['pre_pt_root_id', 'post_pt_root_id', 'syn_count'])
    conn = (raw.groupby(['pre_pt_root_id', 'post_pt_root_id'])['syn_count'].sum()
            .reset_index().rename(columns={'pre_pt_root_id': 'pre', 'post_pt_root_id': 'post',
                                           'syn_count': 'syn'}))
    input_total = conn.groupby('post')['syn'].sum()
    del raw

    edges = build_type_edges(conn, node_of, sign, input_total)

    nodes = {}
    for name, ids in node_of.groupby(node_of):
        alias, side = name.rsplit('_', 1)
        node_nt = nt.reindex(ids.index).mode()
        node_nt = node_nt.iloc[0] if not node_nt.empty else None
        nodes[name] = {
            "name": name,
            "cell_type": types[alias],
            "side": side,
            "n_neurons": int(len(ids)),
            "nt": node_nt,
            "sign": NT_SIGN.get(node_nt, 1),
            "root_ids": [int(r) for r in ids.index],
        }
    export = {
        "meta": {
            "level": "cell_type",
            "materialization_version": 783,
            "min_synapses": MIN_SYNAPSES,
            "min_type_weight": MIN_TYPE_WEIGHT,
            "nt_sign": NT_SIGN,
            "weight_unit": "signed mean synapses per target neuron (path-integrated: synapse-equivalents)",
            "sources": [CONNECTIONS_URL.split('?')[0], ANNOTATIONS_URL],
        },
        "nodes": nodes,
        "edges": [{"pre_name": r.pre_node, "post_name": r.post_node,
                   "pre_root_id": r.pre_node, "post_root_id": r.post_node,
                   "weight": round(float(r.weight), 2), "edge_type": r.edge_type}
                  for r in edges.sort_values(['edge_type', 'pre_node', 'post_node']).itertuples()],
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(export, f, indent=2)
    n = len(nodes)
    print(f"{(edges.edge_type == 'measured').sum()} measured, "
          f"{(edges.edge_type == 'path-integrated').sum()} path-integrated kenar; "
          f"yogunluk {len(edges) / (n * (n - 1)):.1%}")
    print(f"Kaydedildi: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
