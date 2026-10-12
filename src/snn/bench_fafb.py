"""
FafbSNN hiz olcumu -> docs/reports/p0_motor_hiz.md (gorevler/mert.md P0, H4 karari)

Her (kod uretimi, calistirma modu) ayri bir surecte olculur: kurulum, ilk adim (derleme dahil) ve
senaryo x adim suresi basina medyan duvar saati. Gercek zaman orani (RTF) = sim / duvar;
RTF >= 1 kapali dongude gercek zamandan hizli demektir.
Senaryolardaki hizlar kalibrasyonsuz bir duman testidir; kabul testi degildir.

    python src/snn/bench_fafb.py [--steps 25]
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_PATH = os.path.join(BASE_DIR, 'docs', 'reports', 'p0_motor_hiz.md')
CONFIGS = [('cython', 'persistent'), ('cython', 'per_run'), ('numpy', 'persistent'), ('numpy', 'per_run')]
STEP_MS = [10.0, 20.0, 50.0]
SCENARIOS = {
    'sessiz': {},
    'LC4 iki taraf 100 Hz': {'LC4_L': 100.0, 'LC4_R': 100.0},
    'tüm girdiler 100 Hz': 'ALL',
}
SMOKE_GROUPS = ['GF', 'DNp02', 'DNp04', 'DNp11', 'MDN', 'DNa01', 'DNa02', 'DNp09', 'MN9']


def measure(codegen, mode, steps):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fafb_snn import FafbSNN
    import numpy as np

    out = {'codegen': codegen, 'mode': mode, 'runs': [], 'build_s': [], 'first_step_s': []}
    for step_ms in STEP_MS:
        t0 = time.perf_counter()
        snn = FafbSNN.from_manifest(codegen=codegen, mode=mode, step_ms=step_ms, seed=0)
        out['build_s'].append(time.perf_counter() - t0)
        out['graph_id'] = snn.graph_id
        t0 = time.perf_counter()
        snn.step({})
        out['first_step_s'].append(time.perf_counter() - t0)
        for name, rates in SCENARIOS.items():
            if rates == 'ALL':
                rates = {k: 100.0 for k in snn.input_groups}
            snn.step(rates)                                # isinma
            walls, acc = [], {}
            before = snn.spike_counts()
            for _ in range(steps):
                t0 = time.perf_counter()
                r = snn.step(rates)
                walls.append(time.perf_counter() - t0)
                for k, v in r.items():
                    acc[k] = acc.get(k, 0.0) + v / steps
            active = int(((snn.spike_counts() - before) > 0).sum())
            wall = float(np.median(walls))
            out['runs'].append({'senaryo': name, 'adim_ms': step_ms, 'medyan_ms': wall * 1000,
                                'rtf': step_ms / 1000 / wall, 'aktif_noron': active,
                                'hiz': {g: round((acc.get(f'{g}_L', 0) + acc.get(f'{g}_R', 0)) / 2, 1)
                                        for g in SMOKE_GROUPS}})
        snn.close()
    out['build_s'] = max(out['build_s'])
    out['first_step_s'] = out['first_step_s'][0]      # derleme yalnizca ilk ornekte
    return out


def render(results, steps):
    lines = ['# P0: Brian2 motoru hız ölçümü (graf v1)', '',
             '> Bu dosya `python src/snn/bench_fafb.py` ile üretilir; elle düzenlenmez.', '',
             f"- **Graf:** `{results[0]['graph_id']}`",
             f"- **Makine:** {platform.platform()}, {platform.machine()}, Python {platform.python_version()}",
             f"- **Ölçüm:** her senaryo × adım süresi için 1 ısınma + {steps} adım, medyan duvar saati. "
             'RTF = simüle süre / duvar saati (≥ 1: gerçek zamandan hızlı).',
             '- **Modlar:** `per_run` her adımda bir `net.run()` (Brian2 her çağrıda ~25 ms sabit maliyet öder); '
             '`persistent` tek uzun `run()` + adım başına `NetworkOperation` (aynı tohumla aynı spike\'lar, birim testli).',
             '- **cpp_standalone ölçülmedi:** her `run()` çağrısında baştan başlar; kapalı döngüde adım adım '
             'kullanılamaz. Yalnızca toplu, çevrimdışı koşular (tüm-beyin kahini) içindir.', '',
             '## Kurulum', '', '| kod üretimi | mod | ağ kurulumu (s, en kötü) | ilk adım, derleme dahil (s) |',
             '|---|---|---|---|']
    for r in results:
        lines.append(f"| {r['codegen']} | {r['mode']} | {r['build_s']:.1f} | {r['first_step_s']:.1f} |")
    lines += ['', '## Adım süresi', '',
              '| kod üretimi | mod | senaryo | adım (ms) | medyan duvar (ms) | RTF | aktif nöron |',
              '|---|---|---|---|---|---|---|']
    for r in results:
        for run in r['runs']:
            lines.append(f"| {r['codegen']} | {r['mode']} | {run['senaryo']} | {run['adim_ms']:.0f} | "
                         f"{run['medyan_ms']:.1f} | {run['rtf']:.2f} | {run['aktif_noron']} |")
    lines += ['', '## Duman testi: mod DN hızları (Hz, sol–sağ ortalaması; cython persistent, 20 ms adım, tohum 0)', '',
              'Kalibrasyonsuz, arka plan girdisiz; kabul testi değildir. Yalnızca ağın sessiz kalmadığını '
              've kalıcı duruma kilitlenmediğini gösterir.', '',
              '| senaryo | ' + ' | '.join(SMOKE_GROUPS) + ' |', '|' + '---|' * (len(SMOKE_GROUPS) + 1)]
    cy = next(r for r in results if (r['codegen'], r['mode']) == ('cython', 'persistent'))
    for run in cy['runs']:
        if run['adim_ms'] == 20.0:
            lines.append(f"| {run['senaryo']} | " + ' | '.join(str(run['hiz'][g]) for g in SMOKE_GROUPS) + ' |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', type=int, default=25)
    parser.add_argument('--child', nargs=2, metavar=('CODEGEN', 'MODE'))
    args = parser.parse_args(argv)
    if args.child:
        print(json.dumps(measure(*args.child, args.steps)))
        return 0
    results = []
    for cg, mode in CONFIGS:
        proc = subprocess.run([sys.executable, os.path.abspath(__file__), '--child', cg, mode,
                               '--steps', str(args.steps)], capture_output=True, text=True, check=True)
        results.append(json.loads(proc.stdout.strip().splitlines()[-1]))
        print(cg, mode, 'tamam')
    with open(REPORT_PATH, 'w') as f:
        f.write(render(results, args.steps))
    print(f"Yazildi: {REPORT_PATH}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
