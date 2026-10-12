"""
v0 tip grafi (config/type_graph.json) ile graf v1'in karsilastirmasi
-> docs/reports/p0_v0_karsilastirma.md (gorevler/mert.md, H1-H2 adim 6)

v0 agirliklari (src/data/build_type_graph.py):
  measured        : W(A->B) = sum isaret(a) * S_ab / N_B
  path-integrated : W(A->B) = sum_k isaret(a) * isaret(k) * (S_ak / girdi_k) * S_kB / N_B
                    (k: v0 devresinde olmayan her noron)
Her v0 kenari icin ayni formul v1 isaretleriyle (noron basina top_nt) iki kez hesaplanir:
  - tum beyin: k tum FAFB'den
  - v1 alt ag: k yalnizca v1 grafindan
kapsama = v1 alt ag / tum beyin. Path-integrated kenarlar simulasyonda yasak (ADR 0004);
burada "v1 bu dolayli etkiyi gercek noronlarla tasiyor mu" sorusunun erken gostergesidir.
Yol varligi davranis demek degildir.

    python -m connectome.compare_v0 [--no-hash-check]
"""
import argparse
import json
import os
import sys

import pandas as pd

from connectome.build_graph import MANIFEST_PATH, NT_SIGN, shortest_hops, strongest_short_path
from connectome.data import BASE_DIR, load_annotations, load_edges, load_hashes, resolve

V0_PATH = os.path.join(BASE_DIR, 'config', 'type_graph.json')
REPORT_PATH = os.path.join(BASE_DIR, 'docs', 'reports', 'p0_v0_karsilastirma.md')


def load_v1(manifest_path=MANIFEST_PATH):
    with open(manifest_path) as f:
        manifest = json.load(f)
    neurons = pd.read_parquet(os.path.join(BASE_DIR, manifest['files']['neurons']))
    edges = pd.read_parquet(os.path.join(BASE_DIR, manifest['files']['edges']))
    return manifest, neurons, edges


def type_weight(edges5, input_total, sign, src, dst, k_allowed, k_excluded):
    """v0 formulu. k_allowed None ise tum noronlar. Donus: (measured, path) agirliklari."""
    n_b = len(dst)
    a_out = edges5[edges5['pre'].isin(src)]
    direct = a_out[a_out['post'].isin(dst)]
    measured = float((direct['pre'].map(sign) * direct['syn_count']).sum()) / n_b
    a_k = a_out.assign(s=a_out['pre'].map(sign) * a_out['syn_count']).groupby('post')['s'].sum()
    k_b = edges5[edges5['post'].isin(dst)].groupby('pre')['syn_count'].sum()
    ks = a_k.index.intersection(k_b.index).difference(pd.Index(list(k_excluded)))
    if k_allowed is not None:
        ks = ks.intersection(pd.Index(list(k_allowed)))
    w = a_k[ks] * sign.reindex(ks).fillna(0) / input_total.reindex(ks) * k_b[ks]
    return measured, float(w.sum()) / n_b


def compare(v0, neurons, edges, edges5, input_total, sign_all):
    in_v1 = set(neurons['root_id'])
    ct = neurons.set_index('root_id')['cell_type'].to_dict()
    adj = {}
    for pre, post, syn in edges[['pre', 'post', 'syn_count']].itertuples(index=False):
        adj.setdefault(pre, []).append((post, syn))
    nodes = {name: {int(r) for r in node['root_ids']} for name, node in v0['nodes'].items()}
    circuit = set().union(*nodes.values())

    def fmt(path):
        return ' → '.join(ct.get(n) if isinstance(ct.get(n), str) else '(tipsiz)' for n in path)

    def sgn(x):
        return '+' if x > 0 else ('−' if x < 0 else '0')

    rows = []
    for e in v0['edges']:
        src, dst = nodes[e['pre_name']], nodes[e['post_name']]
        src_v1, dst_v1 = src & in_v1, dst & in_v1
        row = {'v0 kenar': f"{e['pre_name']} → {e['post_name']}", 'tür': e['edge_type'],
               'v0': round(e['weight'], 1)}
        if not src_v1 or not dst_v1:
            rows.append({**row, 'durum': 'v1 dışında (tip ertelendi/çıkarıldı)'})
            continue
        m_full, p_full = type_weight(edges5, input_total, sign_all, src, dst, None, circuit)
        _, p_v1 = type_weight(edges5, input_total, sign_all, src, dst, in_v1, circuit)
        if e['edge_type'] == 'measured':
            full, sub, cov = m_full, m_full, 1.0
        else:
            full, sub = p_full, p_v1
            cov = sub / full if full else float('nan')
        width, path = strongest_short_path(adj, src_v1, dst_v1, max_len=2)
        same_v1 = sgn(sub) == sgn(e['weight'])
        rows.append({**row,
                     'tüm beyin (v1 işaret)': round(full, 1),
                     'v1 alt ağ': round(sub, 1),
                     'kapsama': f"{cov:.0%}" if cov == cov else '-',
                     'işaret v0/tüm/v1': f"{sgn(e['weight'])}/{sgn(full)}/{sgn(sub)}",
                     'en kısa': shortest_hops(adj, src_v1, dst_v1),
                     '≤2 en güçlü yol': f"{fmt(path)} ({width})" if path else '-',
                     'durum': 'uyumlu' if same_v1 else 'İŞARET FARKLI'})
    return pd.DataFrame(rows)


def _md(df):
    if df.empty:
        return '_(yok)_'
    lines = ['| ' + ' | '.join(df.columns) + ' |', '|' + '---|' * len(df.columns)]
    for r in df.itertuples(index=False):
        lines.append('| ' + ' | '.join('-' if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
                                       for v in r) + ' |')
    return '\n'.join(lines)


def render(manifest, table):
    summary = table.groupby(['tür', 'durum']).size().rename('kenar').reset_index()
    pi = table[(table['tür'] == 'path-integrated') & table['v1 alt ağ'].notna()]
    cov = (pi['v1 alt ağ'] / pi['tüm beyin (v1 işaret)']).dropna()
    table = table.assign(_o=table['tür'].map({'path-integrated': 0, 'measured': 1}),
                         _w=-table['v0'].abs()).sort_values(['_o', '_w']).drop(columns=['_o', '_w'])
    return '\n'.join([
        '# P0: v0 tip grafı ↔ graf v1 karşılaştırması',
        '',
        '> Bu dosya `python -m connectome.compare_v0` ile üretilir; elle düzenlenmez.',
        '',
        f"- **v1:** `{manifest['graph_id']}` ({manifest['counts']['neurons']} nöron, "
        f"{manifest['counts']['edges']} kenar)",
        '- **v0:** `config/type_graph.json`; ağırlık birimi hedef nöron başına (eşdeğer) sinaps.',
        '- **tüm beyin (v1 işaret):** v0 formülü, ara nöron k tüm FAFB\'den, işaretler v1 kuralıyla '
        '(nöron başına `top_nt`). v0 tip çoğunluğu + `known_nt` kullanıyordu; v0 ile fark bu kuraldan gelir.',
        '- **v1 alt ağ:** aynı formül, k yalnızca v1 grafından. **kapsama** = v1 alt ağ / tüm beyin.',
        '- **≤2 en güçlü yol:** v1\'de en fazla 2 sıçramalık yollar içinde en zayıf kenarı en güçlü olan (darboğaz sinaps).',
        '',
        'Yol varlığı davranış demek değildir; LC10a → DNa02 için asıl test H11 tüm-beyin testidir.',
        '',
        '## Özet',
        '',
        _md(summary),
        '',
        f"Path-integrated kenarlarda kapsama: medyan {cov.median():.0%}, "
        f"en düşük {cov.min():.0%}, en yüksek {cov.max():.0%} ({len(cov)} kenar).",
        '',
        '## Tüm kenarlar (önce path-integrated, |v0 ağırlık| sırasıyla)',
        '',
        _md(table),
        '',
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--no-hash-check', action='store_true')
    args = parser.parse_args(argv)
    verify = not args.no_hash_check
    hashes = load_hashes()
    with open(V0_PATH) as f:
        v0 = json.load(f)
    manifest, neurons, edges = load_v1()
    if manifest['inputs'] != {k: v['sha256'] for k, v in hashes.items()}:
        raise ValueError("v1 manifestindeki girdi hash'leri data_hashes.json ile uyusmuyor")
    ann = load_annotations(resolve('annotations', verify_hash=verify, hashes=hashes))
    raw = load_edges(resolve('connections', verify_hash=verify, hashes=hashes), min_synapses=1)
    input_total = raw.groupby('post')['syn_count'].sum()
    edges5 = raw[raw['syn_count'] >= manifest['parameters']['min_synapses']]
    sign_all = ann.set_index('root_id')['top_nt'].map(NT_SIGN)
    sign_all.update(neurons.set_index('root_id')['sign'])      # v1 noronlari: v1 isareti (NT yedegi dahil)
    table = compare(v0, neurons, edges, edges5, input_total, sign_all.fillna(0))
    with open(REPORT_PATH, 'w') as f:
        f.write(render(manifest, table))
    print(f"Yazildi: {REPORT_PATH}")
    print(table.groupby(['tür', 'durum']).size().to_string())
    return 0


if __name__ == '__main__':
    sys.exit(main())
