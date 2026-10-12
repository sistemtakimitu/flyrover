# P0: Tohum tipi keşfi (FAFB v783)

> Bu dosya `python -m connectome.discover_seeds` ile üretilir; elle düzenlenmez. Yorum ve kararlar ADR 0010 ve PR açıklamasında.

## Girdiler

| girdi | dosya | sha256 | doğrulandı |
|---|---|---|---|
| connections | proofread_connections_783.feather | 24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf | evet |
| annotations | flywire_annotations.tsv | b214970b55d2fbe0853bba536fdcb9e28730f4eb7ab06f600491df795da683cd | evet |

Genişletme parametreleri (bu raporda kullanılmaz, kayıt için): θ = 0.01, max_hops = 2, min_synapses = 5.

## Tohum tipleri: beklenen ve bulunan

Durum: 19 OK, 0 SAPMA, 0 sabitlenmedi.

| tohum | rol | secici | sol | sag | toplam | beklenen | durum | top_nt | nt_guven | known_nt | super_class |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LC4 | kacis | LC4 | 54 | 50 | 104 | [45, 60] | OK | acetylcholine 104 | 0.6 | acetylcholine | visual_projection |
| LPLC2 | kacis | LPLC2 | 108 | 102 | 210 | [90, 115] | OK | acetylcholine 210 | 0.54 | acetylcholine | visual_projection |
| LC10a | hedef | LC10a | 115 | 119 | 234 | [100, 130] | OK | acetylcholine 232, glutamate 2 | 0.65 | acetylcholine, acetylcholine; gaba-negative | visual_projection |
| LC11 | dur | LC11 | 66 | 61 | 127 | [55, 75] | OK | acetylcholine 127 | 0.78 | gaba-negative | visual_projection |
| GRN_sugar | uzan | cell_class=gustatory; cell_sub_class=sugar|sugar/low_salt | 33 | 24 | 57 | [20, 40] | OK | acetylcholine 45, serotonin 7, glutamate 5 | 0.47 | - | sensory |
| GF | KAC | DNp01 | 1 | 1 | 2 | [1, 1] | OK | glutamate 1, acetylcholine 1 | 0.29 | - | descending |
| DNp02 | KAC | DNp02 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.69 | acetylcholine | descending |
| DNp04 | KAC | DNp04 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.84 | acetylcholine | descending |
| DNp11 | KAC | DNp11 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.74 | acetylcholine | descending |
| MDN | KAC | MDN | 2 | 2 | 4 | [2, 2] | OK | acetylcholine 4 | 0.8 | acetylcholine | descending |
| DNa01 | YAKLAS | DNae001 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.88 | - | descending |
| DNa02 | YAKLAS | DNa02 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.79 | acetylcholine | descending |
| DNp09 | DUR | DNp09 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.89 | acetylcholine | descending |
| MN9 | UZAN | CB0701 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.45 | - | motor |
| DNg13 | kayit | DNg13 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.73 | acetylcholine | descending |
| DNb05 | kayit | DNb05 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.88 | acetylcholine | descending |
| DNb06 | kayit | DNb06 | 1 | 1 | 2 | [1, 1] | OK | acetylcholine 2 | 0.77 | - | descending |
| Foxglove | kayit | CB0890 | 1 | 1 | 2 | [1, 1] | OK | gaba 2 | 0.53 | gaba | central |
| Bluebell | kayit | DNg60 | 1 | 1 | 2 | [1, 1] | OK | gaba 2 | 0.54 | gaba | descending |

## NT uyarıları (karışık tahmin veya ortalama güven < 0.5)

İşaret düzeltmesi adayları; düzeltme yalnızca `connectome/sign_overrides.yaml` ile, kaynak ve hakem onayıyla (ADR 0004).

| tohum | secici | top_nt | nt_guven | known_nt |
|---|---|---|---|---|
| LC10a | LC10a | acetylcholine 232, glutamate 2 | 0.65 | acetylcholine, acetylcholine; gaba-negative |
| GRN_sugar | cell_class=gustatory; cell_sub_class=sugar|sugar/low_salt | acetylcholine 45, serotonin 7, glutamate 5 | 0.47 | - |
| GF | DNp01 | glutamate 1, acetylcholine 1 | 0.29 | - |
| MN9 | CB0701 | acetylcholine 2 | 0.45 | - |

## Ad çakışmaları

Tohum adı veya seçilen `cell_type` ile anotasyonda başka bir tipe karşılık gelen satırlar.

| tohum | secilen cell_type | cakisan cell_type | hemibrain_type | n |
|---|---|---|---|---|
| DNa01 | DNae001 | DNa01 | VES006 | 2 |
| DNp09 | DNp09 | DNp71 | DNp09 | 2 |
| DNb06 | DNb06 | DNge070 | DNb06 | 2 |

## Shiu et al. 2024 kimlikleri (v783 anotasyonundaki karşılıkları)

| grup | cell_sub_class | cell_type | taraf | n |
|---|---|---|---|---|
| MN9 | ingestion_motor_neuron | CB0701 | right | 1 |
| sugar | high_salt/heavy_metal | LB3d | left | 5 |
| sugar | putative_attractive | LB4b | left | 4 |
| sugar | sugar | LB3c | left | 9 |
| sugar | sugar/low_salt | LB3b | left | 2 |
| sugar | (v783 anotasyonunda yok) | - | - | 1 |

## Ön yol taraması (θ'sız, kenar ≥ 5 sinaps)

Doğrudan: girdi tipinden hedef tipe toplam sinaps. 2 sıçrama: ara tip başına min(girdi → ara, ara → hedef) toplam sinapsı; en güçlü 3 ara tip. Graf üreticinin θ eşikli genişletmesinin yerini tutmaz.

| girdi | hedef | dogrudan | 2_sicrama_en_iyi | ara_tipler |
|---|---|---|---|---|
| LC4 | GF | 757 | 269 | PVLP122b (269), PVLP010 (250), PVLP151 (123) |
| LC4 | DNp02 | 962 | 82 | PVLP010 (82), LHAD1g1 (36), PVLP130 (30) |
| LC4 | DNp04 | 1850 | 81 | PVLP130 (81), PVLP151 (72), PVLP024 (65) |
| LC4 | DNp11 | 860 | 154 | PVLP022 (154), PVLP015 (97), PVLP024 (68) |
| LC4 | MDN | 0 | 78 | PVLP141 (78), PVLP137 (7) |
| LC4 | DNa01 | 0 | 6 | PLP029 (6) |
| LC4 | DNa02 | 0 | 179 | PVLP141 (179), PLP029 (53), CB1958 (12) |
| LC4 | DNp09 | 0 | 32 | LC31b (32), LHAD1g1 (13), AVLP016 (5) |
| LC4 | MN9 | 0 | 0 | - |
| LC4 | DNg13 | 0 | 5 | PVLP137 (5) |
| LC4 | DNb05 | 0 | 14 | PLP029 (14), LPLC4 (10), PVLP021 (7) |
| LC4 | DNb06 | 0 | 0 | - |
| LC4 | Foxglove | 0 | 0 | - |
| LC4 | Bluebell | 0 | 0 | - |
| LPLC2 | GF | 844 | 254 | LHAD1g1 (254), PVLP151 (189), LC4 (183) |
| LPLC2 | DNp02 | 0 | 187 | LC4 (187), DNg40 (59), LHAD1g1 (36) |
| LPLC2 | DNp04 | 1007 | 206 | LC4 (206), PVLP130 (81), PVLP151 (72) |
| LPLC2 | DNp11 | 0 | 82 | PVLP022 (82), LC4 (75), LPLC4 (40) |
| LPLC2 | MDN | 0 | 48 | PVLP141 (48), PVLP137 (7) |
| LPLC2 | DNa01 | 0 | 16 | DNp09 (16) |
| LPLC2 | DNa02 | 0 | 48 | PVLP141 (48), AVLP370a (20), DNp09 (16) |
| LPLC2 | DNp09 | 16 | 132 | LC31b (132), AVLP531 (75), PVLP150 (47) |
| LPLC2 | MN9 | 0 | 0 | - |
| LPLC2 | DNg13 | 0 | 5 | PVLP137 (5) |
| LPLC2 | DNb05 | 0 | 1404 | LPLC4 (1404), PVLP076 (45), LPT48_vCal3 (16) |
| LPLC2 | DNb06 | 0 | 0 | - |
| LPLC2 | Foxglove | 0 | 17 | DNp71 (17), DNpe025 (16) |
| LPLC2 | Bluebell | 0 | 0 | - |
| LC10a | GF | 0 | 0 | - |
| LC10a | DNp02 | 0 | 0 | - |
| LC10a | DNp04 | 0 | 0 | - |
| LC10a | DNp11 | 0 | 6 | LC14a1 (6), Li24 (6), LC9 (5) |
| LC10a | MDN | 0 | 175 | AOTU019 (175), CB3127 (29) |
| LC10a | DNa01 | 0 | 55 | AOTU015a (55), LAL026 (37), LAL028, LAL029 (32) |
| LC10a | DNa02 | 0 | 337 | AOTU019 (337), AOTU025 (321), AOTU015a (198) |
| LC10a | DNp09 | 0 | 5 | LC9 (5) |
| LC10a | MN9 | 0 | 0 | - |
| LC10a | DNg13 | 0 | 92 | CB1080 (92), CB0007 (64), CB2070 (28) |
| LC10a | DNb05 | 0 | 10 | LPLC4 (10), PLP245 (6) |
| LC10a | DNb06 | 0 | 138 | AOTU023 (138) |
| LC10a | Foxglove | 0 | 0 | - |
| LC10a | Bluebell | 0 | 0 | - |
| LC11 | GF | 0 | 27 | PVLP026 (27), AVLP076 (5), PVLP100 (5) |
| LC11 | DNp02 | 0 | 8 | PVLP100 (8), AVLP080 (6), CB0154 (5) |
| LC11 | DNp04 | 0 | 33 | PVLP120 (33), AVLP086 (14), PVLP100 (10) |
| LC11 | DNp11 | 0 | 55 | LC9 (55), LPLC4 (38), LMa2 (11) |
| LC11 | MDN | 0 | 0 | - |
| LC11 | DNa01 | 0 | 0 | - |
| LC11 | DNa02 | 0 | 5 | LC9 (5) |
| LC11 | DNp09 | 0 | 295 | PVLP150 (295), PVLP020 (263), LC9 (87) |
| LC11 | MN9 | 0 | 0 | - |
| LC11 | DNg13 | 0 | 5 | PLP208 (5) |
| LC11 | DNb05 | 0 | 474 | LPLC4 (474) |
| LC11 | DNb06 | 0 | 23 | LT82b (23) |
| LC11 | Foxglove | 0 | 0 | - |
| LC11 | Bluebell | 0 | 0 | - |
| GRN_sugar | GF | 0 | 0 | - |
| GRN_sugar | DNp02 | 0 | 0 | - |
| GRN_sugar | DNp04 | 0 | 0 | - |
| GRN_sugar | DNp11 | 0 | 0 | - |
| GRN_sugar | MDN | 0 | 0 | - |
| GRN_sugar | DNa01 | 0 | 0 | - |
| GRN_sugar | DNa02 | 0 | 0 | - |
| GRN_sugar | DNp09 | 0 | 0 | - |
| GRN_sugar | MN9 | 0 | 8 | DNge031 (8), CB0573 (5), CB0919 (5) |
| GRN_sugar | DNg13 | 0 | 5 | DNge065 (5) |
| GRN_sugar | DNb05 | 0 | 6 | il3LN6 (6), lLN2F_b (5) |
| GRN_sugar | DNb06 | 0 | 0 | - |
| GRN_sugar | Foxglove | 0 | 33 | CB0499 (33), CB0604 (33), CB1093 (27) |
| GRN_sugar | Bluebell | 0 | 64 | CB0445 (64), AN_GNG_21 (36), CB0366 (32) |
