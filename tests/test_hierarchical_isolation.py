"""
=============================================================================
FILE:    hierarchical_snn.py
PROJECT: FlyRover — Bio-Inspired Autonomous Rover (Mars Surface)
PHASE:   1 — Hierarchical SNN Prototype (Proof of Concept / Toy Model)
=============================================================================

ARCHITECTURAL OVERVIEW
-----------------------
This simulation implements a "Hierarchical Ganglion Architecture" to prevent
"functional conflict" between the rover's locomotion reflexes and the robotic
arm's manipulation reflexes.

DESIGN CHOICES
--------------
1.  NetworkX DiGraph  : Models the connectome-style directed weighted graph.
                        Future: Replace synthetic edges with FlyWire CSV data
                        using:  nx.from_pandas_edgelist(df, 'pre', 'post',
                                                         edge_attr='weight')

2.  NumPy LIF Model   : Each node runs a Leaky Integrate-and-Fire (LIF) neuron
                        with membrane potential v[t], firing threshold theta, and
                        exponential decay tau. Fully vectorizable for scale.

3.  Isolation via     : The graph is partitioned into three DISJOINT sub-graphs.
    Graph Topology      The Central Decision Node holds the ONLY outgoing edges
                        and selects exactly ONE sub-graph per decision cycle.
                        There are ZERO edges between Rover and Arm sub-graphs.

4.  Poisson Stimulus  : Input node fires spikes drawn from a Poisson process,
                        mimicking retinal ganglion cell responses to a looming
                        (expanding) visual stimulus on the Mars surface.

NODE MAP (9 nodes total)
-------------------------
    Node 0  :  Sensor/Vision Input Node  (Poisson spike generator)
    Node 1  :  Central Decision Node     (The router / ganglion hub)
               -- Routes to ROVER (Danger/Escape) or ARM (Target/Approach) --
    -- ROVER SUB-GRAPH (Locomotion) --
    Node 2  :  Rover Interneuron         (amplifies escape signal)
    Node 3  :  Rover Motor -- Backward   (primary escape drive)
    Node 4  :  Rover Motor -- Turn Left  (secondary evasion)
    Node 5  :  Rover Motor -- Turn Right (secondary evasion)
    -- ARM SUB-GRAPH (Manipulation) --
    Node 6  :  Arm Interneuron           (amplifies approach signal)
    Node 7  :  Arm Motor -- Extend       (proboscis extension reflex to gripper)
    Node 8  :  Arm Motor -- Grip         (grasp completion)

STIMULUS: "Looming Danger" -- Expected output: Rover fires, Arm stays SILENT.

FUTURE SCALING NOTES
---------------------
- Replace SYNTHETIC_EDGES with:
      df = pd.read_csv('flywire_connectome.csv')  # 130k node FlyWire data
      G  = nx.from_pandas_edgelist(df, source='pre_root_id',
                                   target='post_root_id',
                                   edge_attr='syn_count')
- Replace NumPy LIF with Brian2 NeuronGroup for continuous-time simulation.
- Add spike sorting / STDP learning rules for synaptic plasticity.
=============================================================================
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict
import os


# =============================================================================
# SECTION 1: CONFIGURATION -- All hyperparameters in one place
# =============================================================================

# --- Simulation ---
SIM_CONFIG = {
    "dt":           1.0,     # ms -- simulation time-step
    "T":            100.0,   # ms -- total simulation duration
    "random_seed":  42,      # for reproducibility
}

# --- Leaky Integrate-and-Fire (LIF) Neuron Parameters ---
LIF_CONFIG = {
    "tau":           10.0,   # ms -- membrane time constant (leak rate)
    "v_rest":        0.0,    # mV -- resting potential
    "v_threshold":   1.0,    # mV -- spike threshold
    "v_reset":       0.0,    # mV -- post-spike reset potential
    "refrac_period": 2,      # steps -- refractory period after spike
}

# --- Stimulus: Looming Danger (Poisson spike train) ---
STIMULUS_CONFIG = {
    "firing_rate":  80.0,    # Hz -- elevated rate simulates rapid looming expansion
    "onset_step":   5,       # step at which stimulus begins
}

# --- Routing Decision ---
# "DANGER" -- activates ROVER sub-graph (escape locomotion)
# "TARGET" -- activates ARM sub-graph  (object manipulation)
ROUTING_DECISION = "DANGER"

# --- Node Roles (for labelling and colour coding) ---
NODE_ROLES = {
    0: {"name": "Sensor/Vision",         "group": "input",   "color": "#00D4FF"},
    1: {"name": "Central Decision Node", "group": "central", "color": "#FF6B35"},
    2: {"name": "Rover Interneuron",     "group": "rover",   "color": "#4CAF50"},
    3: {"name": "Rover Motor Backward",  "group": "rover",   "color": "#81C784"},
    4: {"name": "Rover Motor Turn L",    "group": "rover",   "color": "#A5D6A7"},
    5: {"name": "Rover Motor Turn R",    "group": "rover",   "color": "#A5D6A7"},
    6: {"name": "Arm Interneuron",       "group": "arm",     "color": "#9C27B0"},
    7: {"name": "Arm Motor Extend",      "group": "arm",     "color": "#CE93D8"},
    8: {"name": "Arm Motor Grip",        "group": "arm",     "color": "#CE93D8"},
}
NUM_NODES = len(NODE_ROLES)


# =============================================================================
# SECTION 2: GRAPH CONSTRUCTION
# =============================================================================

def build_connectome_graph(routing_decision: str) -> nx.DiGraph:
    """
    Constructs the hierarchical directed weighted graph.

    The topology enforces isolation:
      - Input  ->  Central Decision Node  (always active)
      - Central -> Rover Sub-graph        (ONLY if routing_decision == "DANGER")
      - Central -> Arm Sub-graph          (ONLY if routing_decision == "TARGET")
      - Rover nodes connect internally    (closed sub-graph)
      - Arm nodes connect internally      (closed sub-graph)
      - NO edges cross between Rover and Arm

    Edge weights represent synaptic strength (analogous to FlyWire 'syn_count').
    Negative weights represent inhibitory synapses.

    Args:
        routing_decision: "DANGER" activates rover path; "TARGET" activates arm.

    Returns:
        G: A NetworkX DiGraph with 'weight' edge attributes.
    """
    G = nx.DiGraph()

    # --- Add all nodes with metadata ---
    for node_id, attrs in NODE_ROLES.items():
        G.add_node(node_id, **attrs)

    # --- Edges: Input -> Central (always present, excitatory) ---
    G.add_edge(0, 1, weight=1.2, synapse_type="excitatory")

    # --- Conditional Routing: Central -> Sub-graph ---
    if routing_decision == "DANGER":
        # Central -> Rover sub-graph (ACTIVE PATH)
        G.add_edge(1, 2, weight=1.5, synapse_type="excitatory")   # strong drive
        # Central -> Arm: INHIBITORY connection (active suppression, bio-realistic)
        G.add_edge(1, 6, weight=-2.0, synapse_type="inhibitory")  # suppresses arm

    elif routing_decision == "TARGET":
        # Central -> Arm sub-graph (ACTIVE PATH)
        G.add_edge(1, 6, weight=1.5, synapse_type="excitatory")
        # Central -> Rover: INHIBITORY (rover holds position while arm works)
        G.add_edge(1, 2, weight=-2.0, synapse_type="inhibitory")

    # --- Internal edges: Rover Sub-graph (nodes 2, 3, 4, 5) ---
    G.add_edge(2, 3, weight=1.3, synapse_type="excitatory")  # Interneuron -> Motor Backward
    G.add_edge(2, 4, weight=0.8, synapse_type="excitatory")  # Interneuron -> Turn Left
    G.add_edge(2, 5, weight=0.8, synapse_type="excitatory")  # Interneuron -> Turn Right
    G.add_edge(3, 4, weight=0.5, synapse_type="excitatory")  # Backward -> Turn Left (coordination)
    G.add_edge(3, 5, weight=0.5, synapse_type="excitatory")  # Backward -> Turn Right

    # --- Internal edges: Arm Sub-graph (nodes 6, 7, 8) ---
    G.add_edge(6, 7, weight=1.3, synapse_type="excitatory")  # Interneuron -> Extend
    G.add_edge(7, 8, weight=1.1, synapse_type="excitatory")  # Extend -> Grip (sequential reflex)

    return G


# =============================================================================
# SECTION 3: LIF NEURON MODEL
# =============================================================================

class LIFNetwork:
    """
    Vectorized Leaky Integrate-and-Fire (LIF) network.

    State variables per node (all as NumPy arrays of shape [NUM_NODES]):
        v           : membrane potential (mV)
        spike       : binary spike indicator at current step
        refrac_left : refractory counter (steps remaining)

    Update rule (Euler integration):
        dv/dt = (v_rest - v) / tau  +  I_syn(t)
        v[t+dt] = v[t] + dt * dv/dt
        if v[t+dt] >= threshold:  fire, reset, enter refractory

    FUTURE SCALING NOTE:
    - This class maps cleanly to a Brian2 NeuronGroup:
          eqs = 'dv/dt = (v_rest - v)/tau + I : volt'
          G   = NeuronGroup(N, eqs, threshold='v > theta', reset='v = v_rest')
    """

    def __init__(self, graph: nx.DiGraph, config: dict):
        """
        Args:
            graph  : NetworkX DiGraph with 'weight' edge attributes.
            config : LIF_CONFIG dict with tau, threshold, reset, refrac.
        """
        self.G         = graph
        self.N         = graph.number_of_nodes()
        self.tau       = config["tau"]
        self.v_rest    = config["v_rest"]
        self.theta     = config["v_threshold"]
        self.v_reset   = config["v_reset"]
        self.refrac    = config["refrac_period"]
        self.dt        = SIM_CONFIG["dt"]

        # --- State arrays ---
        self.v           = np.full(self.N, self.v_rest, dtype=float)  # membrane potential
        self.refrac_left = np.zeros(self.N, dtype=int)                # refractory counter
        self.spike       = np.zeros(self.N, dtype=bool)               # current step spike

        # --- Precompute: weight matrix W[post, pre] for fast synaptic current calc ---
        # This is the key data structure that will hold FlyWire syn_count data later.
        # nx.to_numpy_array returns W_nx[i,j] = weight of edge i->j
        # We transpose so W[post, pre]: each row i sums inputs FROM all pre-synaptic j
        W_nx  = nx.to_numpy_array(graph, nodelist=sorted(graph.nodes()),
                                  weight="weight")
        self.W = W_nx.T   # W[post, pre]

        # --- Spike train history (for plotting) ---
        self.spike_history = defaultdict(list)  # node_id -> [bool per step]

    def step(self, I_ext: np.ndarray) -> np.ndarray:
        """
        Advance the network by one time step dt.

        Args:
            I_ext: External current injection, shape [N].
                   Non-zero only for the input node (Poisson spikes).

        Returns:
            spikes: Boolean array [N] -- True if node fired this step.
        """
        # --- 1. Compute synaptic input current ---
        # I_syn[i] = sum over all pre-synaptic neurons j that spiked:
        #            W[i,j] * spike[j]
        # This is a matrix-vector product: W (post x pre) . spike_prev
        I_syn = self.W @ self.spike.astype(float)

        # --- 2. Euler integration of membrane potential ---
        # dv = (v_rest - v)/tau * dt  +  (I_syn + I_ext) * dt
        leak  = (self.v_rest - self.v) / self.tau
        dv    = (leak + I_syn + I_ext) * self.dt
        self.v += dv

        # --- 3. Enforce refractory period (neurons in refrac cannot spike) ---
        in_refrac = self.refrac_left > 0

        # --- 4. Detect threshold crossings ---
        self.spike = (self.v >= self.theta) & (~in_refrac)

        # --- 5. Reset fired neurons and start refractory countdown ---
        self.v[self.spike]           = self.v_reset
        self.refrac_left[self.spike] = self.refrac

        # --- 6. Decrement refractory counters ---
        self.refrac_left = np.maximum(0, self.refrac_left - 1)

        # --- 7. Record spike history ---
        for nid in range(self.N):
            self.spike_history[nid].append(bool(self.spike[nid]))

        return self.spike.copy()


# =============================================================================
# SECTION 4: POISSON SPIKE GENERATOR (Input Node)
# =============================================================================

def poisson_spike_generator(firing_rate_hz: float, dt_ms: float,
                             step: int, onset_step: int) -> float:
    """
    Generates a Poisson-distributed spike current for the Input Node.

    Models retinal ganglion cell spiking in response to a looming stimulus.
    Before onset_step, the node fires at a low baseline rate (10 Hz).
    After onset_step, it fires at the elevated 'firing_rate_hz' (looming).

    Args:
        firing_rate_hz : Target mean firing rate in Hz (post-stimulus).
        dt_ms          : Simulation time step in milliseconds.
        step           : Current simulation step index.
        onset_step     : Step at which the looming stimulus begins.

    Returns:
        current: Float current injected into the Input Node this step.
                 1.5 if spike, 0.0 if no spike.
    """
    rate = firing_rate_hz if step >= onset_step else 10.0   # baseline vs stimulus
    # Probability of a spike in this dt window: p = rate(Hz) * dt(ms) * 1e-3
    prob  = rate * (dt_ms / 1000.0)
    spike = np.random.random() < prob
    return 1.5 if spike else 0.0


# =============================================================================
# SECTION 5: MAIN SIMULATION LOOP
# =============================================================================

def run_simulation(routing_decision: str = "DANGER") -> tuple:
    """
    Runs the full hierarchical SNN simulation.

    Args:
        routing_decision: "DANGER" (rover fires, arm silent) or
                          "TARGET"  (arm fires, rover silent).

    Returns:
        (network, steps, spike_history): The LIFNetwork object, total steps,
                                          and complete spike history dict.
    """
    np.random.seed(SIM_CONFIG["random_seed"])

    dt    = SIM_CONFIG["dt"]
    T     = SIM_CONFIG["T"]
    steps = int(T / dt)

    print("=" * 70)
    print("  FlyRover -- Hierarchical SNN Prototype  (Phase 1 PoC)")
    print("=" * 70)
    print(f"  Simulation:  {T} ms  |  dt = {dt} ms  |  Steps = {steps}")
    print(f"  Routing:     {routing_decision}")
    print(f"  Stimulus:    Looming (Poisson @ {STIMULUS_CONFIG['firing_rate']} Hz, "
          f"onset step {STIMULUS_CONFIG['onset_step']})")
    print("-" * 70)

    # --- Build graph and network ---
    G       = build_connectome_graph(routing_decision)
    network = LIFNetwork(G, LIF_CONFIG)

    # --- Run event loop ---
    I_ext = np.zeros(NUM_NODES)

    for step in range(steps):
        # Inject Poisson current ONLY into Node 0 (Sensor/Vision)
        I_ext[:] = 0.0
        I_ext[0] = poisson_spike_generator(
            firing_rate_hz = STIMULUS_CONFIG["firing_rate"],
            dt_ms          = dt,
            step           = step,
            onset_step     = STIMULUS_CONFIG["onset_step"],
        )

        # Advance network one step
        spikes = network.step(I_ext)

        # Print spike events every 10 steps to keep terminal clean
        if step % 10 == 0:
            active = [NODE_ROLES[i]["name"] for i in range(NUM_NODES) if spikes[i]]
            print(f"  t={step*dt:5.1f} ms | Active: {active if active else '--'}")

    print("-" * 70)

    # --- Summarise results ---
    _print_results_summary(network)

    return network, steps, network.spike_history


def _print_results_summary(network: LIFNetwork):
    """Prints a human-readable isolation proof to the terminal."""
    print("\n  ISOLATION PROOF -- Total spikes per node:")
    print(f"  {'Node':<5} {'Name':<28} {'Group':<10} {'Spikes':>8}")
    print("  " + "-" * 56)

    rover_total = 0
    arm_total   = 0

    for nid, attrs in NODE_ROLES.items():
        total  = sum(network.spike_history[nid])
        group  = attrs["group"]
        name   = attrs["name"]
        marker = " FIRED" if total > 0 else "  silent"
        print(f"  {nid:<5} {name:<28} {group:<10} {total:>8}  {marker}")
        if group == "rover":
            rover_total += total
        elif group == "arm":
            arm_total   += total

    print("  " + "-" * 56)
    print(f"\n  Rover sub-graph total spikes : {rover_total}")
    print(f"  Arm   sub-graph total spikes : {arm_total}")

    if ROUTING_DECISION == "DANGER":
        if rover_total > 0 and arm_total == 0:
            print("\n  [OK] ISOLATION CONFIRMED: Rover ESCAPED, Arm remained SILENT.")
        else:
            print("\n  [!!] WARNING: Isolation may not be complete -- check weights.")
    elif ROUTING_DECISION == "TARGET":
        if arm_total > 0 and rover_total == 0:
            print("\n  [OK] ISOLATION CONFIRMED: Arm REACHED, Rover remained STILL.")
        else:
            print("\n  [!!] WARNING: Isolation may not be complete -- check weights.")
    print("=" * 70)


# =============================================================================
# SECTION 6: VISUALISATION
# =============================================================================

def plot_results(network: LIFNetwork, steps: int,
                 spike_history: dict, routing_decision: str):
    """
    Produces a 3-panel figure:
      Panel A -- Network topology (hierarchical graph layout)
      Panel B -- Raster plot (spike times per node)
      Panel C -- Smoothed activity traces for key nodes

    The plot is the primary visual proof of signal isolation.
    """
    dt   = SIM_CONFIG["dt"]
    time = np.arange(steps) * dt   # time axis in ms

    fig = plt.figure(figsize=(18, 11), facecolor="#0D1117")
    title_str = (
        "FlyRover -- Hierarchical SNN Prototype  |  Stimulus: "
        + ("LOOMING DANGER => Rover Escape" if routing_decision == "DANGER"
           else "TARGET FOUND => Arm Extend/Grip")
    )
    fig.suptitle(title_str, fontsize=13, color="white", fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35,
                           left=0.06, right=0.97, top=0.92, bottom=0.07)

    ax_graph  = fig.add_subplot(gs[:, 0])   # left column -- full height
    ax_raster = fig.add_subplot(gs[0, 1])   # top right
    ax_vt     = fig.add_subplot(gs[1, 1])   # bottom right

    _style_dark(fig, [ax_graph, ax_raster, ax_vt])
    _draw_graph(ax_graph, network.G, routing_decision)
    _draw_raster(ax_raster, spike_history, time, steps)
    _draw_activity(ax_vt, network, time)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, "hierarchical_snn_output.png")
    
    plt.savefig(output_path,
                dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\n  Figure saved: {output_path}")
    plt.show()


def _style_dark(fig, axes):
    """Apply consistent dark-mode styling."""
    for ax in axes:
        ax.set_facecolor("#161B22")
        ax.tick_params(colors="white", labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")


def _draw_graph(ax, G: nx.DiGraph, routing_decision: str):
    """Draw the hierarchical graph topology with group-coloured nodes."""
    ax.set_title("A -- Network Topology (Hierarchical Ganglion Architecture)",
                 fontsize=10, pad=10)

    # Custom hierarchical layout
    pos = {
        0: (0.5,  1.0),   # Input node at top
        1: (0.5,  0.72),  # Central Decision Node
        # Rover sub-graph (left branch)
        2: (0.18, 0.44),
        3: (0.05, 0.15),
        4: (0.20, 0.15),
        5: (0.32, 0.15),
        # Arm sub-graph (right branch)
        6: (0.82, 0.44),
        7: (0.72, 0.15),
        8: (0.92, 0.15),
    }

    # Separate excitatory / inhibitory edges for different visual styles
    exc_edges = [(u, v) for u, v, d in G.edges(data=True)
                 if d.get("synapse_type") == "excitatory"]
    inh_edges = [(u, v) for u, v, d in G.edges(data=True)
                 if d.get("synapse_type") == "inhibitory"]

    node_colors = [NODE_ROLES[n]["color"] for n in sorted(G.nodes())]
    node_sizes  = [1800 if NODE_ROLES[n]["group"] == "central" else 1200
                   for n in sorted(G.nodes())]

    # Draw excitatory edges (green, solid)
    nx.draw_networkx_edges(G, pos, edgelist=exc_edges, ax=ax,
                           edge_color="#4CAF50", arrows=True,
                           arrowsize=18, width=2.0,
                           connectionstyle="arc3,rad=0.1",
                           node_size=node_sizes)
    # Draw inhibitory edges (red, dashed)
    nx.draw_networkx_edges(G, pos, edgelist=inh_edges, ax=ax,
                           edge_color="#FF5252", arrows=True,
                           arrowsize=18, width=2.0, style="dashed",
                           connectionstyle="arc3,rad=0.1",
                           node_size=node_sizes)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.95)

    # Node labels
    labels = {n: NODE_ROLES[n]["name"] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                            font_size=7, font_color="white", font_weight="bold")

    # Edge weight labels
    edge_labels = {(u, v): f"{d['weight']:.1f}"
                   for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                 font_size=7, font_color="#FFC107",
                                 bbox=dict(alpha=0))

    # Group annotation boxes
    ax.text(0.18, 0.62, "ROVER\nSub-graph", transform=ax.transAxes,
            color="#4CAF50", fontsize=8, ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#0D2B0D", alpha=0.7))
    ax.text(0.82, 0.62, "ARM\nSub-graph", transform=ax.transAxes,
            color="#9C27B0", fontsize=8, ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1E0D2B", alpha=0.7))

    # Legend
    from matplotlib.patches import Patch
    legend_els = [
        Patch(color="#00D4FF", label="Input"),
        Patch(color="#FF6B35", label="Central Decision"),
        Patch(color="#4CAF50", label="Rover Sub-graph"),
        Patch(color="#9C27B0", label="Arm Sub-graph"),
    ]
    ax.legend(handles=legend_els, loc="upper right", fontsize=7,
              facecolor="#21262D", edgecolor="#30363D", labelcolor="white")
    ax.axis("off")


def _draw_raster(ax, spike_history: dict, time: np.ndarray, steps: int):
    """Raster plot: each row = one neuron, tick marks = spike events."""
    ax.set_title("B -- Spike Raster Plot (Isolation Proof)", fontsize=10)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Node")

    group_colors = {
        "input":   "#00D4FF",
        "central": "#FF6B35",
        "rover":   "#4CAF50",
        "arm":     "#CE93D8",
    }

    for nid in range(NUM_NODES):
        spikes   = np.array(spike_history[nid], dtype=bool)
        t_spikes = time[spikes]
        color    = group_colors[NODE_ROLES[nid]["group"]]
        ax.scatter(t_spikes, np.full_like(t_spikes, nid),
                   marker="|", s=60, color=color, linewidths=1.5, alpha=0.9)

    ax.set_yticks(range(NUM_NODES))
    ax.set_yticklabels([f"{i}: {NODE_ROLES[i]['name']}" for i in range(NUM_NODES)],
                       fontsize=7)
    ax.set_xlim(0, time[-1])
    ax.set_ylim(-0.5, NUM_NODES - 0.5)

    # Shade sub-graph regions for clarity
    ax.axhspan(5.5, 8.5, color="#9C27B0", alpha=0.08, label="ARM (should be silent)")
    ax.axhspan(1.5, 5.5, color="#4CAF50", alpha=0.08, label="ROVER (should fire)")
    ax.axvline(STIMULUS_CONFIG["onset_step"] * SIM_CONFIG["dt"],
               color="#FFC107", lw=1.2, ls="--", label="Stimulus onset")
    ax.legend(fontsize=7, facecolor="#21262D", edgecolor="#30363D",
              labelcolor="white", loc="upper right")


def _draw_activity(ax, network: LIFNetwork, time: np.ndarray):
    """
    Smoothed spike activity (convolved with exponential kernel) as a proxy
    for membrane potential dynamics. Key nodes only.
    NOTE: For a full Brian2 port, use StateMonitor to record v(t) directly.
    """
    ax.set_title("C -- Smoothed Activity Traces (Key Nodes)", fontsize=10)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Activity (a.u.)")

    highlight_nodes = {
        1: ("Central Decision Node", "#FF6B35"),
        3: ("Rover Motor Backward",  "#4CAF50"),
        7: ("Arm Motor Extend",      "#CE93D8"),
    }

    for nid, (label, color) in highlight_nodes.items():
        spikes  = np.array(network.spike_history[nid], dtype=float)
        # Exponential post-synaptic kernel: simulates EPSP/IPSP shape
        kernel  = np.exp(-np.arange(20) / LIF_CONFIG["tau"])
        kernel /= kernel.sum()
        smooth  = np.convolve(spikes, kernel, mode="same")
        ax.plot(time, smooth, color=color, lw=1.8, label=label, alpha=0.9)

    ax.axvline(STIMULUS_CONFIG["onset_step"] * SIM_CONFIG["dt"],
               color="#FFC107", lw=1.2, ls="--", label="Stimulus onset")
    ax.axhline(0, color="#30363D", lw=0.8)
    ax.legend(fontsize=7, facecolor="#21262D", edgecolor="#30363D", labelcolor="white")
    ax.set_xlim(0, time[-1])


# =============================================================================
# SECTION 7: ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Run the simulation.
    Change ROUTING_DECISION = "TARGET" at the top of this file to see the
    ARM sub-graph activate and the ROVER fall silent -- bidirectional isolation.
    """
    network, steps, spike_history = run_simulation(ROUTING_DECISION)
    plot_results(network, steps, spike_history, ROUTING_DECISION)
