"""
Faz 1 kacis demosu: kirmizi top rover'a dogru yuvarlanir, rover'i sadece
sinek connectome'u (config/type_graph.json) surer.

    kamera -> LoomingEncoder -> ConnectomeSNN (LC4/LPLC2 -> DNp02/04/GF...) -> MotorDecoder -> tekerler

Calistirma:  venv/Scripts/python src/sim/escape_demo.py [--gif]
Kontrol deneyi olarak ayni senaryo beyin kapaliyken (rover hareketsiz) de kosar.
"""
import argparse
import os
import sys

import numpy as np

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)
from sim.env import RoverEnv  # noqa: E402
from sim.interface import LoomingEncoder, MotorDecoder  # noqa: E402
from snn.network import ConnectomeSNN  # noqa: E402

BASE_DIR = os.path.dirname(SRC)
GRAPH = os.path.join(BASE_DIR, 'config', 'type_graph.json')
CONTROL_DT = 0.02   # s; her kontrol adiminda SNN 20 ms calisir


def run(brain=True, duration_s=5.0, threat_start=(6.0, 0.0), threat_speed=1.2,
        record_every=0, seed=1):
    from brian2 import seed as brian_seed
    brian_seed(seed)
    env = RoverEnv(threat_start=threat_start, threat_speed=threat_speed)
    encoder = LoomingEncoder(env.eye_fovx_deg)
    decoder = MotorDecoder()
    snn = ConnectomeSNN.from_json(GRAPH) if brain else None

    trace, frames = [], []
    try:
        for k in range(int(duration_s / CONTROL_DT)):
            inputs = encoder.encode(env.eye_image(), CONTROL_DT)
            rates = snn.step(inputs, CONTROL_DT * 1000) if brain else {}
            v, omega = decoder.decode(rates, CONTROL_DT)
            env.step(v, omega, CONTROL_DT)
            trace.append({'t': (k + 1) * CONTROL_DT, 'dist': env.threat_distance(),
                          'rover_x': float(env.rover_xy[0]), 'v': v, **inputs,
                          **{n: rates.get(n, 0.0) for n in ['GF_L', 'GF_R', 'DNp04_L', 'DNp04_R']}})
            if record_every and k % record_every == 0:
                frames.append(env.chase_image())
    finally:
        env.close()
    dists = np.array([s['dist'] for s in trace])
    return {'min_distance': float(dists.min()), 'collided': bool((dists <= 0).any()),
            'rover_dx': trace[-1]['rover_x'], 'trace': trace, 'frames': frames}


def save_gif(frames, path, frame_ms):
    from PIL import Image
    imgs = [Image.fromarray(f) for f in frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=frame_ms, loop=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gif', action='store_true', help='assets/escape_demo.gif kaydet')
    args = ap.parse_args()

    every = 4 if args.gif else 0
    with_brain = run(brain=True, duration_s=7.0, record_every=every)
    without = run(brain=False, duration_s=7.0)
    for label, r in [('Beyin ACIK ', with_brain), ('Beyin KAPALI', without)]:
        print(f"{label}: en yakin mesafe {r['min_distance']:+.2f} m, "
              f"carpisma {'VAR' if r['collided'] else 'yok'}, rover x yer degistirme {r['rover_dx']:+.2f} m")
    first = next((s for s in with_brain['trace'] if s['v'] < -0.05), None)
    if first:
        print(f"Kacis basladi: t={first['t']:.2f} s, mesafe {first['dist']:.2f} m")
    if args.gif:
        path = os.path.join(BASE_DIR, 'assets', 'escape_demo.gif')
        save_gif(with_brain['frames'], path, int(every * CONTROL_DT * 1000))
        print(f"GIF: {path}")


if __name__ == '__main__':
    main()
