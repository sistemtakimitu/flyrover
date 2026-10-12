"""
Graf v1 (connectome/manifests/fafb783_graph.json) uzerinde adim adim calisan Brian2 SNN.

Model: Shiu et al. 2024 LIF, birebir (src/snn/lif.py; ADR 0004), noron seviyesi seyrek baglanti.
Girdi tohumlarinin noronlari Poisson uyarani alir (v'ye dogrudan, refrakter 0; Shiu ile ayni).
Arka plan girdisi yok (kalibrasyon ADR 0004'teki on-kayitli prosedurle ayrica eklenecek).

Kapali dongu (v0 ConnectomeSNN ile ayni arayuz):
    snn = FafbSNN.from_manifest()
    rates = snn.step({'LC4_L': 100.0}, duration_ms=20)    # girdi: Hz, cikti: {tohum_taraf: Hz}

Kod uretimi: kapali dongude 'cython' (C++ derleyici gerekir) veya 'numpy'. cpp_standalone
her run() cagrisinda bastan baslar; yalnizca toplu (cevrimdisi) kosular icindir.

Calistirma modu:
  'per_run'    : her step() bir net.run(). Brian2 her run()'da ~25 ms sabit maliyet oder
                 (gc.collect + kod nesnelerinin yeniden kurulumu); kisa adimlarda baskin.
  'persistent' : tek bir uzun net.run() arka plan is parcaciginda; her step_ms'de bir
                 NetworkOperation girdiyi alir, ciktiyi verir. Sabit maliyet yok; adim suresi
                 kurulumda sabitlenir. Ayni tohumla iki mod ayni spike'lari uretir.
"""
import json
import os
import queue
import threading

import numpy as np
import pandas as pd
from brian2 import Network, NetworkOperation, ms, second

from lif import LIFNetwork, ShiuParams

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(BASE_DIR, 'connectome', 'manifests', 'fafb783_graph.json')
SIDE_SUFFIX = {'left': 'L', 'right': 'R'}


def seed_groups(neurons, index):
    """Tohum + taraf gruplari {'GF_L': indeksler} ve girdi gruplarinin adlari.
    neurons: [root_id, side, seed, role]; index: root_id -> noron indeksi."""
    labelled = neurons[neurons['seed'] != '']
    keys = labelled['seed'] + '_' + labelled['side'].map(SIDE_SUFFIX).fillna('C')
    groups = {k: np.sort(index[g['root_id']].to_numpy()) for k, g in labelled.groupby(keys)}
    inputs = sorted(k for k, g in labelled.groupby(keys) if (g['role'] == 'input').all())
    return groups, inputs


class FafbSNN:
    def __init__(self, neurons, edges, params=None, codegen='cython', mode='per_run',
                 step_ms=20.0, seed=None):
        """
        neurons : DataFrame [root_id, side, seed, role, ...] (graf v1 neurons.parquet)
        edges   : DataFrame [pre, post, syn_count, sign]     (graf v1 edges.parquet)
        Ciktilar ve girdiler tohum + taraf duzeyinde: 'GF_L', 'LC4_R' ...
        """
        if mode not in ('per_run', 'persistent'):
            raise ValueError(f"mode: per_run | persistent, verilen {mode}")
        self.mode, self.step_ms = mode, float(step_ms)
        neurons = neurons.reset_index(drop=True)
        self.root_ids = neurons['root_id'].to_numpy()
        idx = pd.Series(np.arange(len(neurons)), index=neurons['root_id'])

        self.groups, self.input_groups = seed_groups(neurons, idx)
        input_idx = np.concatenate([self.groups[k] for k in self.input_groups])
        offsets = np.cumsum([0] + [len(self.groups[k]) for k in self.input_groups])
        self._input_slot = {k: np.arange(offsets[n], offsets[n + 1]) for n, k in enumerate(self.input_groups)}
        self._input_idx = input_idx

        self.lif = LIFNetwork(len(neurons), idx[edges['pre']].to_numpy(), idx[edges['post']].to_numpy(),
                              (edges['sign'] * edges['syn_count']).to_numpy(), input_idx,
                              params or ShiuParams(), codegen, seed, prefix='fafb')
        self.p = self.lif.p
        self.net = Network(*self.lif.objects)
        self._last_count = np.zeros(len(neurons), dtype=int)
        if mode == 'persistent':
            self._in, self._out = queue.Queue(), queue.Queue()
            self._thread = None
            self.net.add(NetworkOperation(self._exchange, dt=self.step_ms * ms, when='start',
                                          name='fafb_exchange'))

    @classmethod
    def from_manifest(cls, path=MANIFEST_PATH, params=None, codegen='cython', **kwargs):
        with open(path) as f:
            manifest = json.load(f)
        neurons = pd.read_parquet(os.path.join(BASE_DIR, manifest['files']['neurons']))
        edges = pd.read_parquet(os.path.join(BASE_DIR, manifest['files']['edges']))
        snn = cls(neurons, edges, params, codegen, **kwargs)
        snn.graph_id = manifest['graph_id']
        return snn

    def _rates_vector(self, input_rates):
        rates = np.zeros(len(self._input_idx))
        for key, hz in (input_rates or {}).items():
            if key not in self._input_slot:
                raise KeyError(f"{key} bir girdi grubu degil: {self.input_groups}")
            rates[self._input_slot[key]] = hz
        return rates

    def _collect(self, duration_ms):
        count = self.lif.spike_counts()
        new = count - self._last_count
        self._last_count = count
        seconds = duration_ms / 1000.0
        return {k: float(new[ix].mean() / seconds) for k, ix in self.groups.items()}

    def step(self, input_rates=None, duration_ms=None):
        """input_rates: {'LC4_L': Hz, ...} -- grubun her noronuna bagimsiz Poisson girdi.
        Doner: {grup: bu adimdaki noron basina ortalama atesleme hizi (Hz)} (tum tohum gruplari)."""
        duration_ms = self.step_ms if duration_ms is None else float(duration_ms)
        rates = self._rates_vector(input_rates)
        if self.mode == 'per_run':
            self.lif.set_input_rates(rates)
            self.net.run(duration_ms * ms, namespace={})
            return self._collect(duration_ms)
        if duration_ms != self.step_ms:
            raise ValueError(f"persistent modda adim suresi sabit: {self.step_ms} ms")
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_forever, daemon=True)
            self._thread.start()
        self._in.put(rates)
        out = self._out.get()
        if isinstance(out, BaseException):
            raise out
        return out

    # --- persistent mod ---------------------------------------------------------------------

    def _exchange(self):
        """network_operation: adim basinda onceki adimin ciktisini ver, yeni girdiyi al."""
        if self._started:
            self._out.put(self._collect(self.step_ms))
        self._started = True
        rates = self._in.get()
        if rates is None:
            self.net.stop()
            return
        self.lif.set_input_rates(rates)

    def _run_forever(self):
        self._started = False
        try:
            self.net.run(1e6 * second, namespace={})
        except BaseException as exc:            # is parcacigindaki hata step()'e tasinir
            self._out.put(exc)

    def close(self):
        if self.mode == 'persistent' and self._thread is not None:
            self._in.put(None)
            self._thread.join()
            self._thread = None

    def spike_counts(self):
        """Simulasyon basindan beri noron basina toplam spike (analiz icin)."""
        return pd.Series(self.lif.spike_counts(), index=self.root_ids)
