"""
Graf uretici v1: config/modules.yaml -> noron seviyesi alt ag + manifest (ADR 0004, 0010)

Adimlar:
  1. Tohum tiplerinin tum noronlari (taraf basina beklenen sayi disindaysa durur)
  2. Genisletme: bir noronun toplam girdisinin (cikisinin) >= theta'sini saglayan ve
     >= min_synapses sinapsli ortaklari, max_hops sicramaya kadar eklenir.
     directed: girdi tohumlarindan yalnizca cikis, mod/kayit tohumlarindan yalnizca giris yonu.
     Toplamlar esiksiz tum sinapslarla hesaplanir (noronun gercek girdisinin/cikisinin payi).
  3. Kenarlar: ag icindeki tum noron-noron ciftleri (>= min_synapses). Tip seviyesi kenar yok.
  4. Isaret: anotasyondaki top_nt (yoksa sinaps duzeyi NT ortalamasi), sonra sign_overrides.yaml.
  5. Cikti: data/graphs/<graph_id>/{neurons,edges}.parquet (gitignore),
     connectome/manifests/fafb783_graph.json (commit edilir), docs/reports/p0_graf_v1.md.

graph_id, noron ve kenar tablolarinin kanonik CSV'sinin SHA-256'sindan gelir: ayni girdi -> ayni hash.

    python -m connectome.build_graph [--no-hash-check]
"""
import argparse
import hashlib
import heapq
import io
import json
import os
import sys

import pandas as pd
import yaml

from connectome.data import (BASE_DIR, load_annotations, load_edges, load_hashes,
                             load_presynaptic_nt, resolve, sha256)
from connectome.modules import MODULES_PATH, count_status, load_modules, select, side_counts

BUILDER_VERSION = 1
W_SYN_MV = 0.275                     # Shiu et al. 2024
NT_SIGN = {'acetylcholine': 1, 'gaba': -1, 'glutamate': -1,
           # Modulator NT'ler: repo v0 ve fetch_data.py ile ayni (+1); sayilari raporlanir.
           'dopamine': 1, 'serotonin': 1, 'octopamine': 1}
SIGN_OVERRIDES_PATH = os.path.join(BASE_DIR, 'connectome', 'sign_overrides.yaml')
ENGINEERED_EDGES_PATH = os.path.join(BASE_DIR, 'connectome', 'engineered_edges.yaml')
GRAPHS_DIR = os.path.join(BASE_DIR, 'data', 'graphs')
MANIFEST_PATH = os.path.join(BASE_DIR, 'connectome', 'manifests', 'fafb783_graph.json')
REPORT_PATH = os.path.join(BASE_DIR, 'docs', 'reports', 'p0_graf_v1.md')
NEURON_COLUMNS = ['root_id', 'cell_type', 'side', 'super_class', 'top_nt', 'top_nt_conf',
                  'nt', 'nt_source', 'sign', 'sign_source', 'seed', 'role', 'group', 'hop', 'origin']
EDGE_COLUMNS = ['pre', 'post', 'syn_count', 'sign', 'weight_mv', 'source']


class GraphError(ValueError):
    pass


# --- elle duzenlenen dosyalar ------------------------------------------------------------

def load_sign_overrides(path=SIGN_OVERRIDES_PATH):
    with open(path) as f:
        rows = (yaml.safe_load(f) or {}).get('overrides') or []
    seen = set()
    for r in rows:
        if set(r) != {'cell_type', 'sign', 'source', 'reviewer'}:
            raise GraphError(f"sign_overrides: alanlar cell_type, sign, source, reviewer olmali: {r}")
        if r['sign'] not in (1, -1) or not str(r['source']).strip() or not str(r['reviewer']).strip():
            raise GraphError(f"sign_overrides: gecersiz satir: {r}")
        if r['cell_type'] in seen:
            raise GraphError(f"sign_overrides: {r['cell_type']} iki kez")
        seen.add(r['cell_type'])
    return rows


def load_engineered_edges(path=ENGINEERED_EDGES_PATH):
    with open(path) as f:
        rows = (yaml.safe_load(f) or {}).get('edges') or []
    required = {'pre_cell_type', 'post_cell_type', 'syn_count', 'sign', 'reason', 'reviewer'}
    for r in rows:
        if 'path' in str(r.get('kind', '')).lower() or any('path' in k for k in r):
            raise GraphError(f"engineered_edges: path-integrated kenar yasak (ADR 0004): {r}")
        if set(r) != required:
            raise GraphError(f"engineered_edges: alanlar {sorted(required)} olmali: {r}")
    if rows:
        # Engineered kenarin noron duzeyinde nasil dagitilacagi ayri bir karar (ADR); v1 desteklemez.
        raise GraphError("engineered_edges: v1 uretici engineered kenar desteklemez; dosya bos olmali")
    return rows


# --- genisletme ----------------------------------------------------------------------------

def significant_partners(raw_edges, theta, min_synapses):
    """{post: {pre}} anlamli girdiler ve {pre: {post}} anlamli ciktilar."""
    total_in = raw_edges.groupby('post')['syn_count'].sum()
    total_out = raw_edges.groupby('pre')['syn_count'].sum()
    e = raw_edges[raw_edges['syn_count'] >= min_synapses]
    frac_in = e['syn_count'] / e['post'].map(total_in)
    frac_out = e['syn_count'] / e['pre'].map(total_out)
    inputs_of = e[frac_in >= theta].groupby('post')['pre'].agg(set).to_dict()
    outputs_of = e[frac_out >= theta].groupby('pre')['post'].agg(set).to_dict()
    return inputs_of, outputs_of


def grow(start, graphs, max_hops):
    """{noron: sicrama} -- start'tan graphs uzerinden en fazla max_hops sicrama."""
    hop = {n: 0 for n in start}
    frontier = set(start)
    for h in range(1, max_hops + 1):
        nxt = set()
        for g in graphs:
            for n in frontier:
                nxt |= g.get(n, set())
        nxt -= hop.keys()
        hop.update({n: h for n in nxt})
        frontier = nxt
    return hop


def expand(seed_ids, roles, inputs_of, outputs_of, max_hops, direction):
    """Tohum basina genisletme. Donus: {tohum: {noron: sicrama}}"""
    reach = {}
    for name, ids in seed_ids.items():
        if direction == 'bidirectional':
            graphs = (inputs_of, outputs_of)
        else:
            graphs = (outputs_of,) if roles[name] == 'input' else (inputs_of,)
        reach[name] = grow(ids, graphs, max_hops)
    return reach


# --- tablolar --------------------------------------------------------------------------------

def neuron_table(ann, cfg, seed_ids, reach, fallback_nt, overrides):
    seeds = cfg['seeds']
    seed_of = {n: name for name, ids in seed_ids.items() for n in ids}
    hop, origin = {}, {}
    for name, r in reach.items():
        side = 'forward' if seeds[name]['role'] == 'input' else 'backward'
        for n, h in r.items():
            hop[n] = min(h, hop.get(n, h))
            if h > 0:
                origin.setdefault(n, set()).add(side)
    ids = sorted(hop)
    df = ann.set_index('root_id').reindex(ids)[['cell_type', 'side', 'super_class', 'top_nt', 'top_nt_conf']]
    df.index.name = 'root_id'
    df = df.reset_index()
    df['nt'] = df['top_nt']
    df['nt_source'] = 'annotation'
    missing = df['nt'].isna()
    df.loc[missing, 'nt'] = df.loc[missing, 'root_id'].map(fallback_nt)
    df.loc[missing, 'nt_source'] = 'synapse_avg'
    if df['nt'].isna().any():
        raise GraphError(f"NT bulunamayan noronlar: {df.loc[df['nt'].isna(), 'root_id'].tolist()[:10]}")
    df['sign'] = df['nt'].map(NT_SIGN).astype(int)
    df['sign_source'] = 'nt'
    for o in overrides:
        hit = df['cell_type'] == o['cell_type']
        if not hit.any():
            raise GraphError(f"sign_overrides: {o['cell_type']} agda yok")
        df.loc[hit, 'sign'] = o['sign']
        df.loc[hit, 'sign_source'] = 'override'
    df['seed'] = df['root_id'].map(seed_of).fillna('')
    df['role'] = df['seed'].map(lambda s: seeds[s]['role'] if s else '')
    df['group'] = df['seed'].map(lambda s: (seeds[s].get('mode') or seeds[s].get('module') or '') if s else '')
    df['hop'] = df['root_id'].map(hop).astype(int)
    df['origin'] = df['root_id'].map(
        lambda n: 'seed' if n in seed_of else '+'.join(sorted(origin.get(n, ()))))
    return df[NEURON_COLUMNS]


def edge_table(edges, neurons):
    ids = set(neurons['root_id'])
    e = edges[edges['pre'].isin(ids) & edges['post'].isin(ids)].copy()
    e['sign'] = e['pre'].map(neurons.set_index('root_id')['sign']).astype(int)
    e['weight_mv'] = e['sign'] * e['syn_count'] * W_SYN_MV
    e['source'] = 'measured'
    return e.sort_values(['pre', 'post'])[EDGE_COLUMNS].reset_index(drop=True)


def graph_hash(neurons, edges):
    """Kanonik CSV (sirali satirlar, sabit sutunlar) uzerinden SHA-256."""
    h = hashlib.sha256()
    for df in (neurons.sort_values('root_id'), edges.sort_values(['pre', 'post'])):
        buf = io.StringIO()
        df.to_csv(buf, index=False, float_format='%.6g', lineterminator='\n')
        h.update(buf.getvalue().encode())
    return h.hexdigest()


# --- erisilebilirlik (rapor) -----------------------------------------------------------------

def shortest_hops(adj, sources, targets):
    """Coklu kaynakli BFS; hedefe en kisa sicrama sayisi (yoksa None)."""
    dist = {s: 0 for s in sources}
    frontier = list(sources)
    while frontier:
        nxt = []
        for n in frontier:
            for m, _ in adj.get(n, ()):
                if m not in dist:
                    dist[m] = dist[n] + 1
                    if m in targets:
                        return dist[m]
                    nxt.append(m)
        frontier = nxt
    return None


def strongest_short_path(adj, sources, targets, max_len):
    """En fazla max_len sicramalik yollar icinde en zayif kenari en guclu olan yol.
    Donus: (darbogaz, [noronlar]) ya da (0, []). Kisitsiz en genis yol yogun tekrarli agda
    uzun dolambaclara sapar; uzunluk siniri yolu yorumlanabilir tutar."""
    best = {s: (float('inf'), None) for s in sources}       # noron -> (genislik, ebeveyn)
    layers = [best]
    for _ in range(max_len):
        prev, cur = layers[-1], {}
        for n, (width, _) in prev.items():
            for m, w in adj.get(n, ()):
                cand = min(width, w)
                if cand > cur.get(m, (0, None))[0]:
                    cur[m] = (cand, n)
        layers.append(cur)
    hit = [(layer[t][0], depth, t) for depth, layer in enumerate(layers) if depth
           for t in targets if t in layer]
    if not hit:
        return 0, []
    width, depth, node = max(hit, key=lambda x: (x[0], -x[1], -x[2]))
    path = [node]
    for d in range(depth, 0, -1):
        path.append(layers[d][path[-1]][1])
    return int(width), path[::-1]


def reachability(neurons, edges, seed_ids, reach, cfg, max_len):
    seeds = cfg['seeds']
    adj_all, adj_exc = {}, {}
    for pre, post, syn, sign in edges[['pre', 'post', 'syn_count', 'sign']].itertuples(index=False):
        adj_all.setdefault(pre, []).append((post, syn))
        if sign > 0:
            adj_exc.setdefault(pre, []).append((post, syn))
    ct = neurons.set_index('root_id')['cell_type']
    rows = []
    for src in [n for n, s in seeds.items() if s['role'] == 'input']:
        for dst in [n for n, s in seeds.items() if s['role'] != 'input']:
            meet = set(reach[src]) & set(reach[dst])
            width, path = strongest_short_path(adj_all, seed_ids[src], seed_ids[dst], max_len)
            rows.append({
                'girdi': src, 'hedef': dst,
                'bulusma': len(meet),
                'en_kisa': shortest_hops(adj_all, seed_ids[src], seed_ids[dst]),
                'en_kisa_uyarici': shortest_hops(adj_exc, seed_ids[src], seed_ids[dst]),
                'guclu_yol_darbogaz': width,
                'guclu_yol': ' → '.join(str(ct.get(n)) if isinstance(ct.get(n), str) else '(tipsiz)'
                                           for n in path) or '-',
            })
    return pd.DataFrame(rows)


# --- rapor ve manifest -------------------------------------------------------------------------

def _md(df):
    if df.empty:
        return '_(yok)_'
    lines = ['| ' + ' | '.join(df.columns) + ' |', '|' + '---|' * len(df.columns)]
    for r in df.itertuples(index=False):
        lines.append('| ' + ' | '.join('-' if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
                                       for v in r) + ' |')
    return '\n'.join(lines)


def render_report(manifest, neurons, edges, reach_df, seed_table):
    p = manifest['parameters']
    by_origin = neurons.groupby('origin').size().rename('noron').reset_index()
    by_hop = neurons.groupby('hop').size().rename('noron').reset_index()
    by_class = neurons['super_class'].fillna('(yok)').value_counts().rename_axis('super_class') \
        .rename('noron').reset_index()
    inter = neurons[neurons['seed'] == '']
    top_types = inter['cell_type'].fillna('(tipsiz)').value_counts().head(25) \
        .rename_axis('ara tip').rename('noron').reset_index()
    nt = neurons.groupby(['nt', 'nt_source', 'sign']).size().rename('noron').reset_index()
    edge_sign = edges.groupby('sign').agg(kenar=('syn_count', 'size'), sinaps=('syn_count', 'sum')).reset_index()
    return '\n'.join([
        '# P0: Graf v1 (FAFB v783)',
        '',
        '> Bu dosya `python -m connectome.build_graph` ile üretilir; elle düzenlenmez.',
        '',
        f"- **graph_id:** `{manifest['graph_id']}`",
        f"- **SHA-256:** `{manifest['sha256']}`",
        f"- **Nöron:** {manifest['counts']['neurons']} · **kenar:** {manifest['counts']['edges']} · "
        f"**sinaps:** {manifest['counts']['synapses']}",
        f"- **Parametreler:** θ = {p['theta']}, max_hops = {p['max_hops']}, min_synapses = {p['min_synapses']}, "
        f"direction = {p['direction']}, w_syn = {p['w_syn_mv']} mV",
        '',
        '## Tohumlar',
        '',
        _md(seed_table),
        '',
        '## Ağın bileşimi',
        '',
        _md(by_origin), '', _md(by_hop), '', _md(by_class),
        '',
        '## En sık ara tipler (tohum olmayan)',
        '',
        _md(top_types),
        '',
        '## Nörotransmitter ve işaret',
        '',
        'Modülatör NT\'ler (dopamin, serotonin, oktopamin) +1 alır (v0 ile aynı); `synapse_avg` = anotasyonda '
        'top_nt yok, sinaps düzeyi NT ortalamasından.',
        '',
        _md(nt), '', _md(edge_sign),
        '',
        '## Girdi → mod erişilebilirliği (alt ağ içinde)',
        '',
        '- **bulusma:** girdinin ileri genişletmesi ile hedefin geri genişletmesinin ortak nöron sayısı.',
        '- **en_kisa / en_kisa_uyarici:** alt ağda en kısa yol (sıçrama); ikincisi yalnızca uyarıcı kenarlarla.',
        f"- **guclu_yol_darbogaz / guclu_yol:** en fazla {2 * p['max_hops']} sıçramalık (ileri + geri genişletme derinliği) "
        'yollar içinde en zayıf kenarı en güçlü olan yol; darboğaz o kenarın sinaps sayısı, yol tip adlarıyla. '
        'İşaret gözetmez.',
        '',
        'Yol varlığı davranış demek değildir; asıl test kabul testleri ve tüm-beyin kahinidir.',
        '',
        _md(reach_df),
        '',
    ])


def build(cfg, ann, raw_edges, fallback_nt_fn, overrides):
    exp = cfg['expansion']
    seeds = cfg['seeds']
    seed_rows, seed_ids = [], {}
    for name, spec in seeds.items():
        sel = select(ann, spec)
        counts = side_counts(sel)
        status = count_status(counts, spec.get('expected_per_side'))
        seed_rows.append({'tohum': name, 'rol': spec['role'], 'sol': counts['left'],
                          'sag': counts['right'], 'durum': status})
        if status == 'SAPMA':
            raise GraphError(f"{name}: taraf basina sayi {counts} beklenen {spec['expected_per_side']} disinda")
        seed_ids[name] = set(sel['root_id'])

    inputs_of, outputs_of = significant_partners(raw_edges, exp['theta'], exp['min_synapses'])
    roles = {n: s['role'] for n, s in seeds.items()}
    reach = expand(seed_ids, roles, inputs_of, outputs_of, exp['max_hops'], exp['direction'])
    all_ids = set().union(*reach.values())
    known = set(ann.loc[ann['top_nt'].notna() & ann['root_id'].isin(all_ids), 'root_id'])
    fallback = fallback_nt_fn(all_ids - known)
    neurons = neuron_table(ann, cfg, seed_ids, reach, fallback, overrides)
    edges = edge_table(raw_edges[raw_edges['syn_count'] >= exp['min_synapses']], neurons)
    return neurons, edges, seed_ids, reach, pd.DataFrame(seed_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--no-hash-check', action='store_true')
    args = parser.parse_args(argv)
    verify = not args.no_hash_check

    cfg = load_modules()
    overrides = load_sign_overrides()
    load_engineered_edges()
    hashes = load_hashes()
    conn_path = resolve('connections', verify_hash=verify, hashes=hashes)
    ann = load_annotations(resolve('annotations', verify_hash=verify, hashes=hashes))
    raw = load_edges(conn_path, min_synapses=1)

    neurons, edges, seed_ids, reach, seed_table = build(
        cfg, ann, raw, lambda ids: load_presynaptic_nt(conn_path, ids), overrides)
    digest = graph_hash(neurons, edges)
    graph_id = f"fafb783-{digest[:12]}"

    out_dir = os.path.join(GRAPHS_DIR, graph_id)
    os.makedirs(out_dir, exist_ok=True)
    neurons.to_parquet(os.path.join(out_dir, 'neurons.parquet'), index=False)
    edges.to_parquet(os.path.join(out_dir, 'edges.parquet'), index=False)

    exp = cfg['expansion']
    manifest = {
        'graph_id': graph_id,
        'sha256': digest,
        'builder_version': BUILDER_VERSION,
        'files': {'neurons': f"data/graphs/{graph_id}/neurons.parquet",
                  'edges': f"data/graphs/{graph_id}/edges.parquet"},
        'inputs': {k: v['sha256'] for k, v in hashes.items()},
        'config_sha256': {
            'modules.yaml': sha256(MODULES_PATH),
            'sign_overrides.yaml': sha256(SIGN_OVERRIDES_PATH),
            'engineered_edges.yaml': sha256(ENGINEERED_EDGES_PATH),
        },
        'parameters': {**{k: exp[k] for k in ('theta', 'max_hops', 'min_synapses', 'direction')},
                       'w_syn_mv': W_SYN_MV, 'nt_sign': NT_SIGN,
                       'partner_fraction_total': 'all_synapses'},
        'counts': {'neurons': len(neurons), 'edges': len(edges), 'synapses': int(edges['syn_count'].sum()),
                   'seed_neurons': int((neurons['seed'] != '').sum()),
                   'sign_overrides': int((neurons['sign_source'] == 'override').sum()),
                   'nt_from_synapse_avg': int((neurons['nt_source'] == 'synapse_avg').sum())},
        'seeds': {n: sorted(int(i) for i in ids) for n, ids in seed_ids.items()},
    }
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    reach_df = reachability(neurons, edges, seed_ids, reach, cfg, max_len=2 * exp['max_hops'])
    with open(REPORT_PATH, 'w') as f:
        f.write(render_report(manifest, neurons, edges, reach_df, seed_table))
    print(f"{graph_id}: {len(neurons)} noron, {len(edges)} kenar")
    print(f"Yazildi: {out_dir}, {MANIFEST_PATH}, {REPORT_PATH}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
