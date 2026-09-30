"""
FlyWire (FAFB v783) connectome'undan config/neurons.json'daki noronlar arasi
agirlikli, isaretli grafi uretir -> config/connectome_graph.json

Kenar turleri (bkz. .agents/AGENTS.md):
  measured        : A -> B dogrudan sinaps. weight = isaret(A) * sinaps_sayisi
  path-integrated : A -> k -> B (k bizim listemizde olmayan ara noron).
                    weight = sum_k  isaret(A) * isaret(k) * (w_Ak / girdi_k) * w_kB

path-integrated agirligi "B uzerindeki esdeger sinaps sayisi" birimindedir:
A, k'nin toplam girdisinin w_Ak / girdi_k kadarini saglar; k'nin B'ye verdigi
w_kB sinapsin o kadarini A'ya atariz. Boylece measured ile ayni olcektedir ve
paralel zincirler agirligi patlatmaz.

Isaret (Dale ilkesi): her noron tek bir NT salgilar. Noronun tum cikis
sinapslarindaki NT olasiliklari toplanir, baskin olan NT noronun isaretini verir.
"""
import hashlib
import json
import os
import time

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'neurons.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'config', 'connectome_graph.json')
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'cache')

MATERIALIZATION_VERSION = 783
SYNAPSE_TABLE = 'synapses_nt_v1'

# FlyWire standardi (Dorkenwald et al. 2024 / Codex): cleft_score < 50 olan
# sinapslar guvenilmez, 5'ten az sinapsli baglantilar gurultu kabul edilir.
MIN_CLEFT_SCORE = 50
MIN_SYNAPSES = 5
# Esdeger sinaps sayisi bundan kucuk olan dolayli baglantilar atilir.
MIN_PATH_WEIGHT = 1.0

# Drosophila: ACh uyarici; GABA ve glutamat (GluCl uzerinden) baskilayici
# (Shiu et al. 2024 tum-beyin modeliyle ayni kabul). Modulator NT'ler
# (oct, ser, da) muhendislik karari olarak uyarici sayilir.
NT_SIGN = {'ach': 1, 'gaba': -1, 'glut': -1, 'oct': 1, 'ser': 1, 'da': 1}
NT_COLUMNS = list(NT_SIGN)

QUERY_RETRIES = 3
# Bir sorgu bu kadar satir donerse sunucu limitine takilmis olabilir -> parcala.
ROW_LIMIT_GUARD = 200_000


def load_neurons(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    root_ids = []
    id_to_name = {}
    def extract_ids(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict) and "root_id" in v:
                rid = v["root_id"]
                root_ids.append(rid)
                id_to_name[rid] = f"{prefix}{k}"
            elif isinstance(v, dict):
                extract_ids(v, prefix=f"{k}_")
    extract_ids(data)
    return sorted(set(root_ids)), id_to_name


# ---------------------------------------------------------------------------
# Saf hesaplama fonksiyonlari (ag erisimi yok, tests/test_fetch_data.py test eder)
# ---------------------------------------------------------------------------

def filter_synapses(df):
    """Dusuk guvenli sinapslari ve tekrar eden satirlari atar."""
    if df.empty:
        return df
    df = df.drop_duplicates(subset='id')
    return df[df['cleft_score'] >= MIN_CLEFT_SCORE]


def neuron_transmitters(syn_df):
    """Her presinaptik noron icin baskin NT: Series[pre_pt_root_id -> 'ach'|'gaba'|...]."""
    if syn_df.empty:
        return pd.Series(dtype=object)
    cols = [c for c in NT_COLUMNS if c in syn_df.columns]
    return syn_df.groupby('pre_pt_root_id')[cols].sum().idxmax(axis=1)


def connection_counts(syn_df):
    """(pre, post) ciftlerinin sinaps sayilari, MIN_SYNAPSES esigi uygulanmis."""
    if syn_df.empty:
        return pd.DataFrame(columns=['pre_pt_root_id', 'post_pt_root_id', 'weight'])
    counts = (syn_df.groupby(['pre_pt_root_id', 'post_pt_root_id'])
              .size().rename('weight').reset_index())
    return counts[counts['weight'] >= MIN_SYNAPSES]


def build_edges(down_df, up_df, input_totals, root_ids):
    """
    down_df      : root_ids'in TUM cikis sinapslari (filtrelenmis)
    up_df        : root_ids'in TUM giris sinapslari (filtrelenmis)
    input_totals : {ara_noron_id: toplam giris sinaps sayisi}
    Doner: (measured_df, path_df, nt_by_neuron)
    """
    roots = set(root_ids)
    nt_by_neuron = neuron_transmitters(pd.concat([down_df, up_df]).drop_duplicates(subset='id'))
    sign = nt_by_neuron.map(NT_SIGN)

    down = connection_counts(down_df)
    measured = down[down['post_pt_root_id'].isin(roots)].copy()
    measured['weight'] = measured['weight'] * measured['pre_pt_root_id'].map(sign)

    up = connection_counts(up_df)
    a_to_k = down[~down['post_pt_root_id'].isin(roots)]
    k_to_b = up[~up['pre_pt_root_id'].isin(roots)]
    paths = a_to_k.merge(k_to_b, left_on='post_pt_root_id', right_on='pre_pt_root_id',
                         suffixes=('_ak', '_kb'))
    paths = paths[paths['pre_pt_root_id_ak'] != paths['post_pt_root_id_kb']]

    path_cols = ['pre_pt_root_id', 'post_pt_root_id', 'weight', 'n_interneurons']
    if paths.empty:
        return measured, pd.DataFrame(columns=path_cols), nt_by_neuron

    k = paths['post_pt_root_id_ak']
    paths = paths.assign(
        contribution=(paths['pre_pt_root_id_ak'].map(sign) * k.map(sign)
                      * paths['weight_ak'] / k.map(input_totals) * paths['weight_kb']))
    missing = paths['contribution'].isna()
    if missing.any():
        raise ValueError(f"{k[missing].nunique()} ara noronun toplam girdisi eksik")

    path = (paths.groupby(['pre_pt_root_id_ak', 'post_pt_root_id_kb'])
            .agg(weight=('contribution', 'sum'), n_interneurons=('contribution', 'size'))
            .reset_index()
            .rename(columns={'pre_pt_root_id_ak': 'pre_pt_root_id',
                             'post_pt_root_id_kb': 'post_pt_root_id'}))

    measured_pairs = set(zip(measured['pre_pt_root_id'], measured['post_pt_root_id']))
    is_measured = [pair in measured_pairs
                   for pair in zip(path['pre_pt_root_id'], path['post_pt_root_id'])]
    path = path[~np.array(is_measured, dtype=bool) & (path['weight'].abs() >= MIN_PATH_WEIGHT)]
    return measured, path[path_cols], nt_by_neuron


# ---------------------------------------------------------------------------
# CAVEclient sorgulari
# ---------------------------------------------------------------------------

def _with_retries(fn, what):
    for attempt in range(1, QUERY_RETRIES + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == QUERY_RETRIES:
                raise RuntimeError(f"{what} {QUERY_RETRIES} denemede basarisiz") from e
            print(f"  {what} hata verdi ({e}), tekrar deneniyor...")
            time.sleep(2 * attempt)


def _synapse_query(client, ids, direction):
    """Tek parca sorgu; satir limitine yaklasirsa parcayi ikiye bolup tekrarlar."""
    df = _with_retries(
        lambda: client.materialize.synapse_query(
            **{f'{direction}_ids': ids}, synapse_table=SYNAPSE_TABLE),
        f"{direction}_ids={ids}")
    if len(df) >= ROW_LIMIT_GUARD:
        if len(ids) == 1:
            raise RuntimeError(f"{ids[0]} tek basina {len(df)} satir dondu, limit asilmis olabilir")
        mid = len(ids) // 2
        return pd.concat([_synapse_query(client, ids[:mid], direction),
                          _synapse_query(client, ids[mid:], direction)], ignore_index=True)
    return df


def chunked_synapse_query(client, ids, direction, chunk_size=5):
    """direction: 'pre' (ids'in cikislari) veya 'post' (ids'in girisleri)."""
    dfs = []
    for i in range(0, len(ids), chunk_size):
        print(f"  {direction}: {i}/{len(ids)}")
        dfs.append(_synapse_query(client, ids[i:i + chunk_size], direction))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def fetch_input_totals(client, neuron_ids):
    """Her noronun toplam (cleft_score filtreli) giris sinaps sayisi."""
    totals = {}
    for i, nid in enumerate(neuron_ids):
        if i % 25 == 0:
            print(f"  girdi sayimi: {i}/{len(neuron_ids)}")
        count = _with_retries(
            lambda: client.materialize.query_table(
                SYNAPSE_TABLE,
                filter_equal_dict={'post_pt_root_id': int(nid)},
                filter_greater_equal_dict={'cleft_score': MIN_CLEFT_SCORE},
                get_counts=True),
            f"girdi sayimi {nid}")
        totals[nid] = int(count.iloc[0, 0] if isinstance(count, pd.DataFrame) else count)
    return totals


def fetch_soma_coordinates(client, root_ids):
    print("3B koordinat (Soma) verileri sorgulaniyor...")
    try:
        nuclei_df = client.materialize.query_table(
            'nuclei_v1',
            filter_in_dict={'pt_root_id': root_ids}
        )
        soma_dict = {}
        for _, row in nuclei_df.iterrows():
            rid = int(row['pt_root_id'])
            pos = row['pt_position']
            soma_dict[rid] = pos.tolist() if hasattr(pos, 'tolist') else list(pos)
        return soma_dict
    except Exception as e:
        print(f"Soma koordinatlari alinamadi: {e}")
        return {}


def cached(name, root_ids, fn):
    """Yavas sorgulari data/cache/ altinda saklar (neurons.json degisince yenilenir).
    Pickle guvenli: dosyalari sadece bu fonksiyon yazar ve data/ git'e girmez."""
    key = hashlib.sha1(json.dumps(root_ids).encode()).hexdigest()[:10]
    path = os.path.join(CACHE_DIR, f"v{MATERIALIZATION_VERSION}_{name}_{key}.pkl")
    if os.path.exists(path):
        print(f"Onbellekten okunuyor: {os.path.relpath(path, BASE_DIR)}")
        return pd.read_pickle(path)
    result = fn()
    os.makedirs(CACHE_DIR, exist_ok=True)
    pd.to_pickle(result, path)
    return result


def main():
    from caveclient import CAVEclient

    root_ids, id_to_name = load_neurons(CONFIG_PATH)
    print(f"Loaded {len(root_ids)} unique neurons.")

    client = CAVEclient('flywire_fafb_public')
    client.materialize.version = MATERIALIZATION_VERSION

    print("Fetching downstream synapses (outbound)...")
    down_df = filter_synapses(cached('down', root_ids,
                                     lambda: chunked_synapse_query(client, root_ids, 'pre')))
    print("Fetching upstream synapses (inbound)...")
    up_df = filter_synapses(cached('up', root_ids,
                                   lambda: chunked_synapse_query(client, root_ids, 'post')))

    # Sadece esigi gecen iki adimli yollarin ara noronlari icin girdi toplami gerekir
    roots = set(root_ids)
    down_c, up_c = connection_counts(down_df), connection_counts(up_df)
    interneurons = sorted(
        set(down_c.loc[~down_c['post_pt_root_id'].isin(roots), 'post_pt_root_id'])
        & set(up_c.loc[~up_c['pre_pt_root_id'].isin(roots), 'pre_pt_root_id']))
    print(f"Counting total inputs of {len(interneurons)} interneurons...")
    input_totals = cached('input_totals', root_ids,
                          lambda: fetch_input_totals(client, interneurons))

    measured, path, nt_by_neuron = build_edges(down_df, up_df, input_totals, root_ids)
    soma_coords = fetch_soma_coordinates(client, root_ids)

    export_nodes = {}
    for rid in root_ids:
        nt = nt_by_neuron.get(rid)
        export_nodes[rid] = {
            "name": id_to_name.get(rid, str(rid)),
            "soma_xyz": soma_coords.get(rid, None),
            "nt": nt,
            "sign": NT_SIGN.get(nt),
        }

    def edge(pre, post, weight, edge_type, **extra):
        return {
            "pre_name": id_to_name.get(pre, str(pre)),
            "post_name": id_to_name.get(post, str(post)),
            "pre_root_id": pre,
            "post_root_id": post,
            "weight": weight,
            "edge_type": edge_type,
            **extra,
        }

    export_edges = [edge(int(r.pre_pt_root_id), int(r.post_pt_root_id), int(r.weight), "measured")
                    for r in measured.itertuples()]
    export_edges += [edge(int(r.pre_pt_root_id), int(r.post_pt_root_id), round(float(r.weight), 2),
                          "path-integrated", n_interneurons=int(r.n_interneurons))
                     for r in path.itertuples()]

    export_data = {
        "meta": {
            "materialization_version": MATERIALIZATION_VERSION,
            "synapse_table": SYNAPSE_TABLE,
            "min_cleft_score": MIN_CLEFT_SCORE,
            "min_synapses": MIN_SYNAPSES,
            "min_path_weight": MIN_PATH_WEIGHT,
            "nt_sign": NT_SIGN,
            "weight_unit": "signed synapse count (path-integrated: synapse-equivalents onto post)",
        },
        "nodes": export_nodes,
        "edges": export_edges,
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(export_data, f, indent=2)

    n = len(root_ids)
    print(f"Found {len(measured)} measured edges ({(measured['weight'] < 0).sum()} inhibitory).")
    print(f"Added {len(path)} path-integrated (2-hop) edges ({(path['weight'] < 0).sum()} inhibitory).")
    print(f"Graph density: {len(export_edges) / (n * (n - 1)):.1%}")
    print(f"Successfully saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
