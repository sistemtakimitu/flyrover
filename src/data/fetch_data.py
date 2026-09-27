import json
import os
import pandas as pd
from caveclient import CAVEclient

# Proje yollarini belirle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'neurons.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'config', 'connectome_graph.json')

def load_neurons(config_path):
    """Neurons.json dosyasindan root ID'leri cikarir."""
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    root_ids = []
    id_to_name = {}
    
    def extract_ids(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict) and "root_id" in v:
                root_id = v["root_id"]
                root_ids.append(root_id)
                id_to_name[root_id] = f"{prefix}{k}"
            elif isinstance(v, dict):
                extract_ids(v, prefix=f"{k}_")
                
    extract_ids(data)
    return root_ids, id_to_name

def fetch_synapses(client, root_ids):
    """CAVEclient ile verilen nöronlar arasindaki sinapslari ceker."""
    print(f"[{len(root_ids)}] adet nöron arasindaki sinapslar sorgulaniyor...")
    
    try:
        # FlyWire public versiyonundan sinapslari al
        synapses_df = client.materialize.synapse_query(
            pre_ids=root_ids,
            post_ids=root_ids,
            synapse_table='synapses_nt_v1'
        )
        return synapses_df
    except Exception as e:
        print(f"Sinapslar cekilirken hata olustu: {e}")
        return pd.DataFrame()

def fetch_soma_coordinates(client, root_ids):
    """Nöronlarin 3D konumlarini (soma / hücre gövdesi) bulmak icin tabloyu sorgular."""
    print("3B koordinat (Soma) verileri sorgulaniyor...")
    try:
        # Flywire public'te nucleus tablosu üzerinden koordinat alinir
        nuclei_df = client.materialize.query_table(
            'nuclei_v1', 
            filter_in_dict={'pt_root_id': root_ids}
        )
        # xyz koordinatlarini al (genelde pt_position sütununda array halinde gelir)
        soma_dict = {}
        for _, row in nuclei_df.iterrows():
            rid = int(row['pt_root_id'])
            pos = row['pt_position'] # [x, y, z]
            soma_dict[rid] = pos.tolist() if hasattr(pos, 'tolist') else list(pos)
        return soma_dict
    except Exception as e:
        print(f"Soma koordinatlari alinamadi (Tablo ismi farkli olabilir): {e}")
        return {}

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Hata: {CONFIG_PATH} bulunamadi.")
        return

    root_ids, id_to_name = load_neurons(CONFIG_PATH)
    print(f"Bulunan Nöron Sayisi: {len(root_ids)}")

    if not root_ids:
        print("Uyari: neurons.json icinde root_id bulunamadi.")
        return

    # CAVEClient baslat (Versiyon 783'e sabitleniyor - NASA standardi)
    print("\nCAVEclient baglantisi saglaniyor (flywire_fafb_public, v783)...")
    client = CAVEclient('flywire_fafb_public')
    client.materialize.version = 783
    
    # 1. Sinaps (Baglanti) verilerini cek
    syn_df = fetch_synapses(client, root_ids)
    
    # 2. Soma (3B konum) verilerini cek (Görsellestirme icin lazim olacak)
    soma_coords = fetch_soma_coordinates(client, root_ids)
    
    # Node (Nöron) verilerini hazirla
    export_nodes = {}
    for rid in root_ids:
        export_nodes[rid] = {
            "name": id_to_name.get(rid, str(rid)),
            "soma_xyz": soma_coords.get(rid, None)
        }

    # Edge (Baglanti) verilerini hazirla
    export_edges = []
    if syn_df.empty:
        print("Verilen nöronlar arasinda direkt sinaps (baglanti) bulunamadi.")
    else:
        edges = syn_df.groupby(['pre_pt_root_id', 'post_pt_root_id']).size().reset_index(name='weight')
        for _, row in edges.iterrows():
            pre = int(row['pre_pt_root_id'])
            post = int(row['post_pt_root_id'])
            w = int(row['weight'])
            
            export_edges.append({
                "pre_name": id_to_name.get(pre, str(pre)),
                "post_name": id_to_name.get(post, str(post)),
                "pre_root_id": pre,
                "post_root_id": post,
                "weight": w,
                "edge_type": "measured"  # Dogrudan ölcülmüs (1-hop) gercek sinaps
            })
            
    export_data = {
        "nodes": export_nodes,
        "edges": export_edges
    }

    # Json olarak kaydet
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(export_data, f, indent=2)
        
    print(f"\nBasarili! Baglanti ve 3D koordinat verileri kaydedildi: {OUTPUT_PATH}")
    if not syn_df.empty:
        print(f"Toplam {len(export_edges)} farkli direkt (unique) baglanti bulundu.")

if __name__ == "__main__":
    main()