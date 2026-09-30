"""
Faz 1: Brian2 Tababli Biyolojik SNN İzolasyon Testi (Gerçek CAVEclient Verisiyle)
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from brian2 import *

# Fix macOS compilation warnings for Brian2
prefs.codegen.target = 'numpy'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'connectome_graph.json')

# =============================================================================
# SNN BIOPHYSICAL PARAMETERS (Shiu et al., 2023 / neuro-fly estimates)
# =============================================================================
V_REST   = -70 * mV
V_RESET  = -70 * mV
V_THRESH = -50 * mV
TAU_MBR  = 20 * ms   # Membrane time constant
T_REFRAC = 2 * ms    # Refractory period

# Scaling factor: translates synapse count/weight into voltage impact
WEIGHT_SCALAR = 0.5 * mV 

def load_graph_data():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Missing connectome file: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)
        
    nodes = data['nodes']
    edges = data['edges']
    
    # Map root_ids to integer indices (0 to N-1) for Brian2
    root_to_idx = {rid: i for i, rid in enumerate(nodes.keys())}
    idx_to_name = {i: nodes[rid]['name'] for rid, i in root_to_idx.items()}
    
    return root_to_idx, idx_to_name, edges

def build_and_run_snn(stimulus_target_name="threat_detection_LC4_L"):
    root_to_idx, idx_to_name, edges = load_graph_data()
    N = len(root_to_idx)
    print(f"Biyolojik SNN Kuruluyor... Toplam Nöron (Node): {N}")
    
    # Define LIF Equations
    eqs = '''
    dv/dt = (V_REST - v)/TAU_MBR + I_ext/TAU_MBR : volt (unless refractory)
    I_ext : volt
    '''
    
    G = NeuronGroup(N, eqs, threshold='v > V_THRESH', reset='v = V_RESET', 
                    refractory=T_REFRAC, method='exact')
    G.v = V_REST
    G.I_ext = 0 * mV
    
    # Define Synapses
    S = Synapses(G, G, 'w : volt', on_pre='v_post += w')
    
    src, tgt, w_list, delay_list = [], [], [], []
    
    for edge in edges:
        pre_idx = root_to_idx[str(edge['pre_root_id'])]
        post_idx = root_to_idx[str(edge['post_root_id'])]
        
        # Scale the connection weight
        weight = edge['weight'] * WEIGHT_SCALAR
        
        # Faz 1.2: Biyolojik Gecikme (Delay)
        if edge.get('edge_type') == 'path-integrated':
            delay = 2.0 * ms
        else:
            delay = 0.5 * ms
            
        src.append(pre_idx)
        tgt.append(post_idx)
        w_list.append(weight)
        delay_list.append(delay)
        
    S.connect(i=src, j=tgt)
    S.w = w_list
    S.delay = delay_list
    
    print(f"Toplam Baglanti (Synapse) Sayisi: {len(src)}")
    
    # Setup Monitors
    spike_mon = SpikeMonitor(G)
    state_mon = StateMonitor(G, 'v', record=True)
    
    # Find stimulus target index
    stim_idx = None
    for idx, name in idx_to_name.items():
        if name == stimulus_target_name:
            stim_idx = idx
            break
            
    if stim_idx is None:
        raise ValueError(f"Stimulus target '{stimulus_target_name}' not found in graph.")
        
    # Run Simulation
    print("Simülasyon Basliyor (0-10ms: Rölanti)...")
    run(10*ms)
    
    print(f"Uyaran Uygulaniyor: {stimulus_target_name} (10-30ms)...")
    G.I_ext[stim_idx] = 200 * mV # Guclu akim
    run(20*ms)
    
    print("Uyaran Kesildi, Recovery bekleniyor (30-60ms)...")
    G.I_ext[stim_idx] = 0 * mV
    run(30*ms)
    
    print(f"Simulasyon Tamamlandi. Toplam Spike Sayisi: {spike_mon.num_spikes}")
    return G, S, spike_mon, state_mon, idx_to_name

def plot_results(spike_mon, state_mon, idx_to_name):
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
    
    ax_raster = fig.add_subplot(gs[0])
    ax_vt = fig.add_subplot(gs[1])
    
    # Dark Mode Styling
    for ax in [ax_raster, ax_vt]:
        ax.set_facecolor("#161B22")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
    fig.patch.set_facecolor("#0D1117")
    
    # 1. Raster Plot
    ax_raster.plot(spike_mon.t/ms, spike_mon.i, '|', color="#00D4FF", markersize=8, markeredgewidth=1.5)
    ax_raster.set_title("A -- Biyolojik Spike Raster Plot (İzolasyon Testi)", fontsize=14, pad=10)
    ax_raster.set_ylabel("Nöron İndeksi")
    ax_raster.set_ylim(-1, len(idx_to_name))
    
    # 2. Voltage Traces (Key Neurons)
    key_neurons = {
        "threat_detection_LC4_L": "#00D4FF",
        "emergency_escape_DN_GF_1": "#FF5252",
        "stopping_and_braking_DNp09_1": "#FFC107",
        "steering_motor_DN_DNa01_1": "#4CAF50" # Unrelated / should have different pattern
    }
    
    for idx, name in idx_to_name.items():
        # Match substring to handle L/R or _1/_2 variants safely
        for key, color in key_neurons.items():
            if key in name:
                ax_vt.plot(state_mon.t/ms, state_mon.v[idx]/mV, label=name, color=color, lw=1.5)
                break
                
    ax_vt.axhline(V_THRESH/mV, ls='--', color='gray', lw=1, label='Eşik (Threshold)')
    ax_vt.axhline(V_REST/mV, ls=':', color='gray', lw=1, label='Dinlenme (Rest)')
    
    # Stimulus window highlighting
    ax_vt.axvspan(10, 30, color='white', alpha=0.05, label='Stimulus Window (LC4)')
    ax_raster.axvspan(10, 30, color='white', alpha=0.05)
    
    ax_vt.set_title("B -- Kritik Nöronların Membran Voltajı (mV)", fontsize=14, pad=10)
    ax_vt.set_xlabel("Zaman (ms)")
    ax_vt.set_ylabel("Membran Voltajı (mV)")
    
    ax_vt.legend(facecolor="#21262D", edgecolor="#30363D", labelcolor="white", loc="upper right")
    
    output_path = os.path.join(BASE_DIR, "brian2_isolation_test.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\nSonuc Grafigi Kaydedildi: {output_path}")

if __name__ == "__main__":
    # Test Senaryosu: LC4_L (Tehdit Algilama) uyarilir
    # Beklenti: Sadece Acil Durum / Kacis aglari (GF, DNp09) ateslenmeli. 
    # Diger kollar sessiz kalmali (veya inhibe edilmeli).
    _, _, spike_mon, state_mon, idx_to_name = build_and_run_snn("threat_detection_LC4_L")
    plot_results(spike_mon, state_mon, idx_to_name)
