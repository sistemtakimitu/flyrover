"""
Connectome grafindan (config/*.json) adim adim calistirilabilen Brian2 SNN.

Model Shiu et al. 2024 (Nature, "A Drosophila computational brain model")
tum-beyin LIF modelini izler:
    dv/dt = (g - (v - v_rest)) / tau_m          (refrakter degilken)
    dg/dt = -g / tau_syn
    presinaptik spike -> g_post += weight * w_syn     (weight: isaretli sinaps sayisi)

Kapali dongu kullanimi (simulator her kontrol adiminda):
    snn = ConnectomeSNN.from_json(path)
    rates = snn.step({"LC4_L": 120.0}, duration_ms=20)   # girdi: Hz, cikti: Hz
"""
import json
from dataclasses import dataclass

import numpy as np
from brian2 import (Hz, NeuronGroup, Network, PoissonGroup, SpikeMonitor, Synapses,
                    defaultclock, ms, mV, prefs)

prefs.codegen.target = 'numpy'  # Windows'ta C++ derleyici gerektirmez


@dataclass
class SNNParams:
    # Shiu et al. 2024 parametreleri; w_syn ve w_input FlyRover icin kalibre edilecek.
    v_rest_mV: float = -52.0
    v_reset_mV: float = -52.0
    v_thresh_mV: float = -45.0
    tau_m_ms: float = 20.0
    tau_syn_ms: float = 5.0
    refractory_ms: float = 2.2
    delay_ms: float = 1.8
    w_syn_mV: float = 0.275          # sinaps basina g sicramasi
    w_input_mV: float = 68.75        # girdi spike g sicramasi (Shiu: w_syn * 250)
    path_delay_ms: float = 3.6       # path-integrated kenarlar bir ara noron daha uzun
    dt_ms: float = 0.1


class ConnectomeSNN:
    def __init__(self, names, edges, params=None, sizes=None):
        """
        names : dugum adlari listesi
        edges : [(pre_idx, post_idx, weight, edge_type), ...]
        sizes : her dugumdeki noron sayisi (hucre tipi grafi). Verilmezse hepsi 1.
                Dugum A -> B kenari, A'nin her noronundan B'nin her noronuna
                weight / N_A agirlikla baglanir: A'nin tamami ateslediginde her B
                noronu toplam `weight` sinapslik girdi alir (grafin birimiyle ayni).
        """
        self.p = p = params or SNNParams()
        self.names = list(names)
        self.index = {n: i for i, n in enumerate(self.names)}
        self.sizes = np.array(sizes if sizes is not None else [1] * len(self.names), dtype=int)
        self.start = np.concatenate([[0], np.cumsum(self.sizes)[:-1]])
        n = int(self.sizes.sum())
        defaultclock.dt = p.dt_ms * ms

        ns = {'v_rest': p.v_rest_mV * mV, 'tau_m': p.tau_m_ms * ms, 'tau_syn': p.tau_syn_ms * ms}
        self.neurons = NeuronGroup(
            n,
            '''dv/dt = (g - (v - v_rest)) / tau_m : volt (unless refractory)
               dg/dt = -g / tau_syn : volt''',
            threshold=f'v > {p.v_thresh_mV}*mV', reset=f'v = {p.v_reset_mV}*mV',
            refractory=p.refractory_ms * ms, method='exact', namespace=ns)
        self.neurons.v = p.v_rest_mV * mV

        self.synapses = Synapses(self.neurons, self.neurons, 'w : volt', on_pre='g_post += w')
        pre_i, post_j, w, delay = [], [], [], []
        for a, b, weight, etype in edges:
            ia = np.arange(self.start[a], self.start[a] + self.sizes[a])
            jb = np.arange(self.start[b], self.start[b] + self.sizes[b])
            ii, jj = np.meshgrid(ia, jb, indexing='ij')
            pre_i.append(ii.ravel())
            post_j.append(jj.ravel())
            w.append(np.full(ii.size, weight / self.sizes[a]))
            delay.append(np.full(ii.size, p.path_delay_ms if etype == 'path-integrated' else p.delay_ms))
        if pre_i:
            self.synapses.connect(i=np.concatenate(pre_i), j=np.concatenate(post_j))
            self.synapses.w = np.concatenate(w) * p.w_syn_mV * mV
            self.synapses.delay = np.concatenate(delay) * ms

        self.inputs = PoissonGroup(n, rates=0 * Hz)
        self.input_syn = Synapses(self.inputs, self.neurons, on_pre=f'g_post += {p.w_input_mV}*mV')
        self.input_syn.connect(j='i')

        self.spikes = SpikeMonitor(self.neurons)
        self.net = Network(self.neurons, self.synapses, self.inputs, self.input_syn, self.spikes)
        self._node_of_neuron = np.repeat(np.arange(len(self.names)), self.sizes)
        self._last_count = np.zeros(n, dtype=int)

    @classmethod
    def from_json(cls, path, params=None):
        """config/connectome_graph.json (noron seviyesi) veya config/type_graph.json."""
        with open(path) as f:
            graph = json.load(f)
        ids = list(graph['nodes'])
        names = [graph['nodes'][i]['name'] for i in ids]
        sizes = [graph['nodes'][i].get('n_neurons', 1) for i in ids]
        idx = {rid: k for k, rid in enumerate(ids)}
        edges = [(idx[str(e['pre_root_id'])], idx[str(e['post_root_id'])], e['weight'], e['edge_type'])
                 for e in graph['edges']]
        return cls(names, edges, params, sizes)

    def step(self, input_rates=None, duration_ms=20.0):
        """input_rates: {dugum_adi: Hz} -- dugumdeki her norona bagimsiz Poisson girdi.
        Doner: {dugum_adi: bu adimdaki ortalama atesleme hizi (Hz, noron basina)}."""
        target_hz = np.zeros(len(self.names))
        for name, r in (input_rates or {}).items():
            target_hz[self.index[name]] = r
        self.inputs.rates = np.repeat(target_hz, self.sizes) * Hz
        self.net.run(duration_ms * ms)
        count = np.asarray(self.spikes.count[:])
        new = count - self._last_count
        self._last_count = count.copy()
        per_node = np.bincount(self._node_of_neuron, weights=new, minlength=len(self.names))
        return dict(zip(self.names, per_node / self.sizes / (duration_ms / 1000.0)))
