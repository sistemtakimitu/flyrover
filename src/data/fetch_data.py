import json
import os
import pandas as pd
import numpy as np
from caveclient import CAVEclient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'neurons.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'config', 'connectome_graph.json')

def load_neurons(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    root_ids = []
    id_to_name = {}
    def extract_ids(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict) and "root_id" in v:
                rid = v["root_id"]
                root_ids.append(rid)
                id_to_name[rid] = f"{prefix}{k}"
            elif isinstance(v, dict):
                extract_ids(v, prefix=f"{k}_")
    extract_ids(data)
    return list(set(root_ids)), id_to_name

def determine_edge_sign_and_weight(df, groupby_cols):
    """
    Groups by the given columns, calculates total weight and dominant neurotransmitter.
    Returns a dataframe with columns: [groupby_cols..., 'weight', 'nt_sign']
    """
    agg_funcs = {
        'id': 'count', 
        'gaba': 'sum',
        'ach': 'sum',
        'glut': 'sum'
    }
    grouped = df.groupby(groupby_cols).agg(agg_funcs).reset_index()
    grouped.rename(columns={'id': 'weight'}, inplace=True)
    
    def get_sign(row):
        g = row['gaba']
        a = row['ach']
        gl = row['glut']
        if g > a and g > gl:
            return -1
        return 1
        
    grouped['nt_sign'] = grouped.apply(get_sign, axis=1)
    return grouped[['pre_pt_root_id', 'post_pt_root_id', 'weight', 'nt_sign']]

def chunked_synapse_query(client, pre_ids=None, post_ids=None, chunk_size=5):
    """Safely queries CAVEclient in chunks to avoid timeouts/limits."""
    all_dfs = []
    
    if pre_ids is not None:
        ids_to_chunk = pre_ids
        for i in range(0, len(ids_to_chunk), chunk_size):
            chunk = ids_to_chunk[i:i+chunk_size]
            try:
                df = client.materialize.synapse_query(pre_ids=chunk, synapse_table='synapses_nt_v1')
                all_dfs.append(df)
            except Exception as e:
                print(f"Error in pre_ids chunk {i}: {e}")
    elif post_ids is not None:
        ids_to_chunk = post_ids
        for i in range(0, len(ids_to_chunk), chunk_size):
            chunk = ids_to_chunk[i:i+chunk_size]
            try:
                df = client.materialize.synapse_query(post_ids=chunk, synapse_table='synapses_nt_v1')
                all_dfs.append(df)
            except Exception as e:
                print(f"Error in post_ids chunk {i}: {e}")
                
    if not all_dfs:
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

def fetch_soma_coordinates(client, root_ids):
    print("3B koordinat (Soma) verileri sorgulaniyor...")
    try:
        nuclei_df = client.materialize.query_table(
            'nuclei_v1', 
            filter_in_dict={'pt_root_id': root_ids}
        )
        soma_dict = {}
        for _, row in nuclei_df.iterrows():
            rid = int(row['pt_root_id'])
            pos = row['pt_position']
            soma_dict[rid] = pos.tolist() if hasattr(pos, 'tolist') else list(pos)
        return soma_dict
    except Exception as e:
        print(f"Soma koordinatlari alinamadi: {e}")
        return {}

def main():
    root_ids, id_to_name = load_neurons(CONFIG_PATH)
    print(f"Loaded {len(root_ids)} unique neurons.")

    client = CAVEclient('flywire_fafb_public')
    client.materialize.version = 783

    # 1. Fetch ALL Downstream (Pre -> Interneuron)
    print("Fetching downstream synapses (Bidirectional BFS - Outbound)...")
    down_df = chunked_synapse_query(client, pre_ids=root_ids)
    
    # 2. Fetch ALL Upstream (Interneuron -> Post)
    print("Fetching upstream synapses (Bidirectional BFS - Inbound)...")
    up_df = chunked_synapse_query(client, post_ids=root_ids)

    # 3. Process Monosynaptic (Measured) Edges
    print("Processing Monosynaptic (Measured) Edges...")
    if not down_df.empty:
        mono_df = down_df[down_df['post_pt_root_id'].isin(root_ids)]
        if not mono_df.empty:
            mono_edges = determine_edge_sign_and_weight(mono_df, ['pre_pt_root_id', 'post_pt_root_id'])
        else:
            mono_edges = pd.DataFrame(columns=['pre_pt_root_id', 'post_pt_root_id', 'weight', 'nt_sign'])
    else:
        mono_edges = pd.DataFrame(columns=['pre_pt_root_id', 'post_pt_root_id', 'weight', 'nt_sign'])
    
    # 4. Process Multi-Hop (Path-Integrated) Edges (Depth 2)
    print("Processing Multi-Hop (Path-Integrated) Edges...")
    if not down_df.empty and not up_df.empty:
        down_grouped = determine_edge_sign_and_weight(down_df, ['pre_pt_root_id', 'post_pt_root_id'])
        up_grouped = determine_edge_sign_and_weight(up_df, ['pre_pt_root_id', 'post_pt_root_id'])
        
        # Keep only interneurons (not in root_ids)
        down_inter = down_grouped[~down_grouped['post_pt_root_id'].isin(root_ids)]
        up_inter = up_grouped[~up_grouped['pre_pt_root_id'].isin(root_ids)]
        
        # Merge on the interneuron (post of down == pre of up)
        merged = pd.merge(down_inter, up_inter, 
                          left_on='post_pt_root_id', right_on='pre_pt_root_id', 
                          suffixes=('_down', '_up'))
        
        # Calculate integrated weight and sign
        merged['integrated_weight'] = merged['weight_down'] * merged['weight_up']
        merged['integrated_sign'] = merged['nt_sign_down'] * merged['nt_sign_up']
        
        # Group by Source and Target
        agg_funcs = {
            'integrated_weight': 'sum',
            'integrated_sign': 'mean' 
        }
        multihop_grouped = merged.groupby(['pre_pt_root_id_down', 'post_pt_root_id_up']).agg(agg_funcs).reset_index()
        multihop_grouped['final_sign'] = multihop_grouped['integrated_sign'].apply(lambda x: 1 if x >= 0 else -1)
    else:
        multihop_grouped = pd.DataFrame(columns=['pre_pt_root_id_down', 'post_pt_root_id_up', 'integrated_weight', 'final_sign'])
    
    # 5. Fetch Somas
    soma_coords = fetch_soma_coordinates(client, root_ids)
    
    # 6. Export
    export_nodes = {}
    for rid in root_ids:
        export_nodes[rid] = {
            "name": id_to_name.get(rid, str(rid)),
            "soma_xyz": soma_coords.get(rid, None)
        }
        
    export_edges = []
    existing_pairs = set()
    
    # Add Mono
    for _, row in mono_edges.iterrows():
        pre = int(row['pre_pt_root_id'])
        post = int(row['post_pt_root_id'])
        w = int(row['weight'])
        sign = int(row['nt_sign'])
        
        export_edges.append({
            "pre_name": id_to_name.get(pre, str(pre)),
            "post_name": id_to_name.get(post, str(post)),
            "pre_root_id": pre,
            "post_root_id": post,
            "weight": w * sign,
            "edge_type": "measured"
        })
        existing_pairs.add((pre, post))
        
    # Add Multi-hop
    multihop_added = 0
    for _, row in multihop_grouped.iterrows():
        pre = int(row['pre_pt_root_id_down'])
        post = int(row['post_pt_root_id_up'])
        if (pre, post) in existing_pairs:
            continue
            
        w = int(row['integrated_weight'])
        # Log scaling to prevent exploding weights from parallel chains
        w_scaled = int(np.log1p(w) * 10) 
        if w_scaled < 15: # Filter out extremely weak or random 1-synapse connections
            continue
            
        sign = int(row['final_sign'])
        
        export_edges.append({
            "pre_name": id_to_name.get(pre, str(pre)),
            "post_name": id_to_name.get(post, str(post)),
            "pre_root_id": pre,
            "post_root_id": post,
            "weight": w_scaled * sign,
            "edge_type": "path-integrated"
        })
        multihop_added += 1

    export_data = {
        "nodes": export_nodes,
        "edges": export_edges
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"Found {len(mono_edges)} measured edges.")
    print(f"Added {multihop_added} path-integrated (2-hop) edges.")
    print(f"Successfully saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
