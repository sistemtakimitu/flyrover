"""
Shiu et al. 2024 LIF modeli: alt ag motoru (FafbSNN) ve tum-beyin kahini ayni kurulumu kullanir.

Kaynak: github.com/philshiu/Drosophila_brain_model, model.py (commit 91bdd1e, MIT lisansi).
    dv/dt = (v_0 - v + g) / t_mbr : volt (unless refractory)
    dg/dt = -g / tau              : volt (unless refractory)
    esik v > v_th; reset v = v_rst, g = 0; refrakter rfc (2.2 ms; uyarilan noronlarda 0)
    presinaptik spike -> g_post += w (w = isaret * sinaps * w_syn), gecikme 1.8 ms
    uyaran: Poisson spike'lari dogrudan v'ye eklenir (w_syn * 250 = 68.75 mV)
Shiu'nun reset ifadesindeki `w = 0` Brian2'de gecici bir yerel degiskene atamadir (etkisiz);
burada yazilmaz. Shiu PoissonInput (N=1) kullanir; burada PoissonGroup + Synapses kullanilir,
cunku kapali dongude hiz adim adim degisir. Istatistiksel olarak esdegerdir, RNG dizisi farklidir.
"""
from dataclasses import dataclass

import numpy as np
from brian2 import Hz, NeuronGroup, PoissonGroup, SpikeMonitor, Synapses, defaultclock, ms, mV, prefs
from brian2 import seed as brian_seed


@dataclass
class ShiuParams:
    # Shiu et al. 2024; davranisa bakilarak degistirilmez (ADR 0004).
    v_0_mV: float = -52.0
    v_rst_mV: float = -52.0
    v_th_mV: float = -45.0
    t_mbr_ms: float = 20.0
    tau_ms: float = 5.0
    t_rfc_ms: float = 2.2
    t_dly_ms: float = 1.8
    w_syn_mV: float = 0.275
    f_poi: float = 250.0
    dt_ms: float = 0.1


EQS = '''dv/dt = (v_0 - v + g) / t_mbr : volt (unless refractory)
         dg/dt = -g / tau              : volt (unless refractory)
         rfc                           : second'''


class LIFNetwork:
    """n noron, isaretli sinaps sayili kenarlar ve uyarilabilir noronlar icin Poisson girdisi.

    pre, post   : noron indeksleri (0..n-1)
    signed_syn  : isaret * sinaps sayisi (w = signed_syn * w_syn)
    input_idx   : Poisson girdisi alabilen noron indeksleri; refrakterleri 0 (Shiu)
    objects     : Network'e eklenecek Brian2 nesneleri
    """

    def __init__(self, n, pre, post, signed_syn, input_idx, params=None, codegen='cython',
                 seed=None, prefix='lif'):
        prefs.codegen.target = codegen
        if seed is not None:
            brian_seed(seed)
        self.p = p = params or ShiuParams()
        defaultclock.dt = p.dt_ms * ms
        ns = {'v_0': p.v_0_mV * mV, 'v_rst': p.v_rst_mV * mV, 'v_th': p.v_th_mV * mV,
              't_mbr': p.t_mbr_ms * ms, 'tau': p.tau_ms * ms}
        self.neurons = NeuronGroup(n, EQS, method='linear', threshold='v > v_th',
                                   reset='v = v_rst; g = 0 * mV', refractory='rfc',
                                   namespace=ns, name=f'{prefix}_neurons')
        self.neurons.v = p.v_0_mV * mV
        self.neurons.g = 0 * mV
        self.neurons.rfc = p.t_rfc_ms * ms

        self.synapses = Synapses(self.neurons, self.neurons, 'w : volt', on_pre='g_post += w',
                                 delay=p.t_dly_ms * ms, name=f'{prefix}_synapses')
        self.synapses.connect(i=np.asarray(pre), j=np.asarray(post))
        self.synapses.w = np.asarray(signed_syn, dtype=float) * p.w_syn_mV * mV

        input_idx = np.asarray(input_idx, dtype=int)
        self.input_idx = input_idx
        self.neurons.rfc[input_idx] = 0 * ms
        self.inputs = PoissonGroup(len(input_idx), rates=0 * Hz, name=f'{prefix}_inputs')
        self.input_syn = Synapses(self.inputs, self.neurons,
                                  on_pre=f'v_post += {p.w_syn_mV * p.f_poi}*mV', name=f'{prefix}_input_syn')
        self.input_syn.connect(i=np.arange(len(input_idx)), j=input_idx)

        self.spikes = SpikeMonitor(self.neurons, name=f'{prefix}_spikes')
        self.objects = [self.neurons, self.synapses, self.inputs, self.input_syn, self.spikes]

    def set_input_rates(self, rates_hz):
        """rates_hz: input_idx sirasiyla Hz dizisi."""
        self.inputs.rates = np.asarray(rates_hz, dtype=float) * Hz

    def spike_counts(self):
        return np.asarray(self.spikes.count[:])
