"""
Graf v1 (connectome/manifests/fafb783_graph.json) uzerinde adim adim calisan Brian2 SNN.

Model Shiu et al. 2024 LIF (ADR 0004), noron seviyesi seyrek baglanti:
    dv/dt = (g - (v - v_rest)) / tau_m          (refrakter degilken)
    dg/dt = -g / tau_syn
    presinaptik spike -> g_post += sign * syn_count * w_syn   (gecikme 1.8 ms)
Girdi: girdi tohumlarinin her noronuna bagimsiz Poisson spike'lari (Shiu: w_syn * 250).
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
                 network_operation girdiyi alir, ciktiyi verir. Sabit maliyet yok; adim suresi
                 kurulumda sabitlenir. Ayni tohumla iki mod ayni spike'lari uretir.
"""
import queue
import threading
import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from brian2 import (Hz, NeuronGroup, Network, PoissonGroup, SpikeMonitor, Synapses,
                    NetworkOperation, defaultclock, ms, mV, prefs, second)
from brian2 import seed as brian_seed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(BASE_DIR, 'connectome', 'manifests', 'fafb783_graph.json')
SIDE_SUFFIX = {'left': 'L', 'right': 'R'}


@dataclass
class FafbParams:
    # Shiu et al. 2024; davranisa bakilarak degistirilmez (ADR 0004).
    v_rest_mV: float = -52.0
    v_reset_mV: float = -52.0
    v_thresh_mV: float = -45.0
    tau_m_ms: float = 20.0
    tau_syn_ms: float = 5.0
    refractory_ms: float = 2.2
    delay_ms: float = 1.8
    w_syn_mV: float = 0.275
    w_input_mV: float = 68.75        # Shiu: w_syn * 250
    dt_ms: float = 0.1


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
        prefs.codegen.target = codegen
        if seed is not None:
            brian_seed(seed)
        self.mode, self.step_ms = mode, float(step_ms)
        self.p = p = params or FafbParams()
        neurons = neurons.reset_index(drop=True)
        self.root_ids = neurons['root_id'].to_numpy()
        idx = pd.Series(np.arange(len(neurons)), index=neurons['root_id'])
        defaultclock.dt = p.dt_ms * ms

        ns = {'v_rest': p.v_rest_mV * mV, 'tau_m': p.tau_m_ms * ms, 'tau_syn': p.tau_syn_ms * ms}
        self.neurons = NeuronGroup(
            len(neurons),
            '''dv/dt = (g - (v - v_rest)) / tau_m : volt (unless refractory)
               dg/dt = -g / tau_syn : volt''',
            threshold=f'v > {p.v_thresh_mV}*mV', reset=f'v = {p.v_reset_mV}*mV',
            refractory=p.refractory_ms * ms, method='exact', namespace=ns, name='fafb_neurons')
        self.neurons.v = p.v_rest_mV * mV

        self.synapses = Synapses(self.neurons, self.neurons, 'w : volt', on_pre='g_post += w',
                                 name='fafb_synapses')
        self.synapses.connect(i=idx[edges['pre']].to_numpy(), j=idx[edges['post']].to_numpy())
        self.synapses.w = (edges['sign'] * edges['syn_count']).to_numpy() * p.w_syn_mV * mV
        self.synapses.delay = p.delay_ms * ms

        # Tohum + taraf gruplari
        labelled = neurons[neurons['seed'] != '']
        keys = labelled['seed'] + '_' + labelled['side'].map(SIDE_SUFFIX).fillna('C')
        self.groups = {k: np.sort(idx[g['root_id']].to_numpy()) for k, g in labelled.groupby(keys)}
        self.input_groups = sorted(k for k, g in labelled.groupby(keys) if (g['role'] == 'input').all())
        input_idx = np.concatenate([self.groups[k] for k in self.input_groups])
        offsets = np.cumsum([0] + [len(self.groups[k]) for k in self.input_groups])
        self._input_slot = {k: np.arange(offsets[n], offsets[n + 1]) for n, k in enumerate(self.input_groups)}
        self._input_idx = input_idx

        self.inputs = PoissonGroup(len(input_idx), rates=0 * Hz, name='fafb_inputs')
        self.input_syn = Synapses(self.inputs, self.neurons, on_pre=f'g_post += {p.w_input_mV}*mV',
                                  name='fafb_input_syn')
        self.input_syn.connect(i=np.arange(len(input_idx)), j=input_idx)

        self.spikes = SpikeMonitor(self.neurons, name='fafb_spikes')
        self.net = Network(self.neurons, self.synapses, self.inputs, self.input_syn, self.spikes)
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
        count = np.asarray(self.spikes.count[:])
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
            self.inputs.rates = rates * Hz
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
        self.inputs.rates = rates * Hz

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
        return pd.Series(np.asarray(self.spikes.count[:]), index=self.root_ids)
