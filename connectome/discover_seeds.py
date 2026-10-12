"""
Tohum tipi kesfi -> docs/reports/p0_tohum_tipleri.md (gorevler/mert.md, H1-H2 adim 3)

Her tohum icin anotasyonda bulunan noron sayisi (taraf basina), beklenen aralik,
NT dagilimi; ad cakismalari; Shiu et al. 2024 kimlikleriyle karsilastirma ve
girdi -> DN arasinda theta'siz bir on yol taramasi (dogrudan + 2 sicrama).
Rapor tamamen bu scriptle uretilir; elle duzenlenmez.

    python -m connectome.discover_seeds [--no-hash-check]
"""
import argparse
import os
import sys

import pandas as pd
import yaml

from connectome.data import BASE_DIR, load_annotations, load_edges, load_hashes, resolve
from connectome.modules import count_status, load_modules, select, side_counts

REPORT_PATH = os.path.join(BASE_DIR, 'docs', 'reports', 'p0_tohum_tipleri.md')
SHIU_PATH = os.path.join(BASE_DIR, 'connectome', 'reference', 'shiu2024.yaml')
LOW_NT_CONF = 0.5
TOP_INTERMEDIATES = 3


def seed_table(ann, seeds):
    rows = []
    for name, spec in seeds.items():
        sel = select(ann, spec)
        counts = side_counts(sel)
        nt = sel['top_nt'].value_counts()
        rows.append({
            'tohum': name,
            'rol': spec.get('mode') or spec.get('module') or 'kayit',
            'secici': spec.get('cell_type') or _fmt_annotation(spec['annotation']),
            'sol': counts['left'], 'sag': counts['right'], 'toplam': len(sel),
            'beklenen': spec.get('expected_per_side'),
            'durum': count_status(counts, spec.get('expected_per_side')),
            'top_nt': ', '.join(f"{k} {v}" for k, v in nt.items()) or '-',
            'nt_guven': round(float(sel['top_nt_conf'].mean()), 2) if len(sel) else None,
            'known_nt': ', '.join(sorted(sel['known_nt'].dropna().unique())) or '-',
            'super_class': ', '.join(sorted(sel['super_class'].dropna().unique())),
        })
    return pd.DataFrame(rows)


def _fmt_annotation(annotation):
    return '; '.join(f"{k}={'|'.join(v) if isinstance(v, list) else v}"
                     for k, v in annotation.items())


def nt_warnings(table):
    """Karisik NT tahmini veya dusuk ortalama guven: isaret duzeltmesi adayi."""
    mixed = table['top_nt'].str.contains(',')
    low = table['nt_guven'].fillna(1) < LOW_NT_CONF
    return table[mixed | low][['tohum', 'secici', 'top_nt', 'nt_guven', 'known_nt']]


def name_collisions(ann, seeds):
    """Tohum adi ile anotasyondaki cell_type / hemibrain_type eslesmeyen satirlar."""
    rows = []
    for name, spec in seeds.items():
        ct = spec.get('cell_type')
        if ct is None:
            continue
        labels = {name, ct}
        hit = ann[(ann['cell_type'] != ct) &
                  (ann['cell_type'].isin(labels) | ann['hemibrain_type'].isin(labels))]
        for (cell_type, hb), grp in hit.groupby(['cell_type', 'hemibrain_type'], dropna=False):
            rows.append({'tohum': name, 'secilen cell_type': ct,
                         'cakisan cell_type': cell_type,
                         'hemibrain_type': hb if isinstance(hb, str) else '-',
                         'n': len(grp)})
    return pd.DataFrame(rows, columns=['tohum', 'secilen cell_type', 'cakisan cell_type',
                                       'hemibrain_type', 'n'])


def shiu_comparison(ann, ref):
    """Shiu et al. kimliklerinin v783 anotasyonundaki karsiliklari."""
    rows = []
    for group, ids in ref.items():
        sub = ann[ann['root_id'].isin(ids)]
        missing = len(set(ids) - set(sub['root_id']))
        for (sub_class, ct, side), grp in sub.groupby(
                ['cell_sub_class', 'cell_type', 'side'], dropna=False):
            rows.append({'grup': group, 'cell_sub_class': sub_class if isinstance(sub_class, str) else '-',
                         'cell_type': ct, 'taraf': side, 'n': len(grp)})
        if missing:
            rows.append({'grup': group, 'cell_sub_class': '(v783 anotasyonunda yok)',
                         'cell_type': '-', 'taraf': '-', 'n': missing})
    return pd.DataFrame(rows)


def path_scan(ann, edges, seeds):
    """Girdi tohumu -> mod/kayit tohumu: dogrudan sinaps ve en guclu 2 sicramali ara tipler.

    2 sicrama skoru, ara tip basina min(girdi -> ara, ara -> hedef) sinaps toplamidir
    (darbogaz). theta uygulanmaz; yalnizca on gostergedir, graf ureticinin yerini tutmaz.
    """
    ct = ann.set_index('root_id')['cell_type']
    ids = {name: set(select(ann, spec)['root_id']) for name, spec in seeds.items()}
    inputs = [n for n, s in seeds.items() if s['role'] == 'input']
    targets = [n for n, s in seeds.items() if s['role'] != 'input']
    rows = []
    for src in inputs:
        out = edges[edges['pre'].isin(ids[src])]
        fwd = out.groupby('post')['syn_count'].sum()
        for dst in targets:
            direct = int(out.loc[out['post'].isin(ids[dst]), 'syn_count'].sum())
            back = edges[edges['post'].isin(ids[dst])].groupby('pre')['syn_count'].sum()
            mids = fwd.index.intersection(back.index).difference(ids[src] | ids[dst])
            hop = pd.DataFrame({'a': fwd[mids], 'b': back[mids],
                                'tip': ct.reindex(mids).fillna('(tipsiz)').values})
            by_type = hop.groupby('tip')[['a', 'b']].sum().min(axis=1).sort_values(ascending=False)
            rows.append({'girdi': src, 'hedef': dst, 'dogrudan': direct,
                         '2_sicrama_en_iyi': int(by_type.iloc[0]) if len(by_type) else 0,
                         'ara_tipler': ', '.join(f"{t} ({int(v)})"
                                                 for t, v in by_type.head(TOP_INTERMEDIATES).items()) or '-'})
    return pd.DataFrame(rows)


def _md(df):
    if df.empty:
        return '_(yok)_'
    cols = list(df.columns)
    lines = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for _, r in df.iterrows():
        lines.append('| ' + ' | '.join('-' if v is None else str(v) for v in r) + ' |')
    return '\n'.join(lines)


def render(hashes, verified, cfg, table, warnings, collisions, shiu, paths):
    exp = cfg['expansion']
    return '\n'.join([
        '# P0: Tohum tipi keşfi (FAFB v783)',
        '',
        '> Bu dosya `python -m connectome.discover_seeds` ile üretilir; elle düzenlenmez. '
        'Yorum ve kararlar ADR 0010 ve PR açıklamasında.',
        '',
        '## Girdiler',
        '',
        _md(pd.DataFrame([{'girdi': k, 'dosya': v['file'], 'sha256': v['sha256'],
                           'doğrulandı': 'evet' if verified else 'hayır (--no-hash-check)'}
                          for k, v in hashes.items()])),
        '',
        f"Genişletme parametreleri (bu raporda kullanılmaz, kayıt için): θ = {exp['theta']}, "
        f"max_hops = {exp['max_hops']}, min_synapses = {exp['min_synapses']}.",
        '',
        '## Tohum tipleri: beklenen ve bulunan',
        '',
        f"Durum: {int((table['durum'] == 'OK').sum())} OK, "
        f"{int((table['durum'] == 'SAPMA').sum())} SAPMA, "
        f"{int((table['durum'] == 'SABITLENMEDI').sum())} sabitlenmedi.",
        '',
        _md(table),
        '',
        f"## NT uyarıları (karışık tahmin veya ortalama güven < {LOW_NT_CONF})",
        '',
        'İşaret düzeltmesi adayları; düzeltme yalnızca `connectome/sign_overrides.yaml` ile, kaynak ve hakem onayıyla (ADR 0004).',
        '',
        _md(warnings),
        '',
        '## Ad çakışmaları',
        '',
        'Tohum adı veya seçilen `cell_type` ile anotasyonda başka bir tipe karşılık gelen satırlar.',
        '',
        _md(collisions),
        '',
        '## Shiu et al. 2024 kimlikleri (v783 anotasyonundaki karşılıkları)',
        '',
        _md(shiu),
        '',
        f"## Ön yol taraması (θ'sız, kenar ≥ {exp['min_synapses']} sinaps)",
        '',
        'Doğrudan: girdi tipinden hedef tipe toplam sinaps. 2 sıçrama: ara tip başına '
        'min(girdi → ara, ara → hedef) toplam sinapsı; en güçlü 3 ara tip. '
        'Graf üreticinin θ eşikli genişletmesinin yerini tutmaz.',
        '',
        _md(paths),
        '',
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--no-hash-check', action='store_true')
    parser.add_argument('--out', default=REPORT_PATH)
    args = parser.parse_args(argv)

    cfg = load_modules()
    hashes = load_hashes()
    verify = not args.no_hash_check
    ann = load_annotations(resolve('annotations', verify_hash=verify, hashes=hashes))
    edges = load_edges(resolve('connections', verify_hash=verify, hashes=hashes),
                       min_synapses=cfg['expansion']['min_synapses'])
    with open(SHIU_PATH) as f:
        shiu_ref = yaml.safe_load(f)

    seeds = cfg['seeds']
    table = seed_table(ann, seeds)
    report = render(hashes, verify, cfg, table, nt_warnings(table),
                    name_collisions(ann, seeds), shiu_comparison(ann, shiu_ref),
                    path_scan(ann, edges, seeds))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        f.write(report)
    print(f"Yazildi: {args.out}")
    print(table[['tohum', 'secici', 'sol', 'sag', 'beklenen', 'durum']].to_string(index=False))
    return 1 if (table['durum'] == 'SAPMA').any() else 0


if __name__ == '__main__':
    sys.exit(main())
