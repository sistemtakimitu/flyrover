# P0: v0 tip grafı ↔ graf v1 karşılaştırması

> Bu dosya `python -m connectome.compare_v0` ile üretilir; elle düzenlenmez.

- **v1:** `fafb783-c2d5a878c336` (9304 nöron, 291383 kenar)
- **v0:** `config/type_graph.json`; ağırlık birimi hedef nöron başına (eşdeğer) sinaps.
- **tüm beyin (v1 işaret):** v0 formülü, ara nöron k tüm FAFB'den, işaretler v1 kuralıyla (nöron başına `top_nt`). v0 tip çoğunluğu + `known_nt` kullanıyordu; v0 ile fark bu kuraldan gelir.
- **v1 alt ağ:** aynı formül, k yalnızca v1 grafından. **kapsama** = v1 alt ağ / tüm beyin.
- **≤2 en güçlü yol:** v1'de en fazla 2 sıçramalık yollar içinde en zayıf kenarı en güçlü olan (darboğaz sinaps).

Yol varlığı davranış demek değildir; LC10a → DNa02 için asıl test H11 tüm-beyin testidir.

## Özet

| tür | durum | kenar |
|---|---|---|
| measured | uyumlu | 38 |
| path-integrated | uyumlu | 93 |
| path-integrated | v1 dışında (tip ertelendi/çıkarıldı) | 2 |
| path-integrated | İŞARET FARKLI | 2 |

Path-integrated kenarlarda kapsama: medyan 100%, en düşük -14%, en yüksek 140% (95 kenar).

## Tüm kenarlar (önce path-integrated, |v0 ağırlık| sırasıyla)

| v0 kenar | tür | v0 | tüm beyin (v1 işaret) | v1 alt ağ | kapsama | işaret v0/tüm/v1 | en kısa | ≤2 en güçlü yol | durum |
|---|---|---|---|---|---|---|---|---|---|
| LC10a_L → DNa02_L | path-integrated | 122.8 | 116.3 | 116.3 | 100% | +/+/+ | 2.0 | LC10a → AOTU025 → DNa02 (55) | uyumlu |
| LC10a_R → DNa02_R | path-integrated | 106.2 | 106.2 | 106.2 | 100% | +/+/+ | 2.0 | LC10a → AOTU025 → DNa02 (55) | uyumlu |
| LC10a_R → DNb01_R | path-integrated | 41.1 | 41.1 | 41.1 | 100% | +/+/+ | 2.0 | LC10a → AOTU027 → DNb01 (33) | uyumlu |
| LC10a_L → DNb01_L | path-integrated | 39.3 | 38.5 | 38.5 | 100% | +/+/+ | 2.0 | LC10a → CB0007 → DNb01 (27) | uyumlu |
| LC10a_R → DNb01_L | path-integrated | 36.6 | 36.6 | 36.6 | 100% | +/+/+ | 2.0 | LC10a → CB1080 → DNb01 (27) | uyumlu |
| LC10a_L → DNb01_R | path-integrated | 35.0 | 35.1 | 35.1 | 100% | +/+/+ | 2.0 | LC10a → CB2070 → DNb01 (27) | uyumlu |
| LC10a_L → DNa15_R | path-integrated | -28.0 | -26.9 | -26.9 | 100% | −/−/− | 2.0 | LC10a → AOTU019 → DNa15 (56) | uyumlu |
| LC10a_R → DNa02_L | path-integrated | 24.3 | 24.3 | 24.3 | 100% | +/+/+ | 2.0 | LC10a → AOTU019 → DNa02 (60) | uyumlu |
| LC4_L → DNp11_R | path-integrated | -22.3 | -22.3 | -22.3 | 100% | −/−/− | 2.0 | LC4 → PVLP024 → DNp11 (28) | uyumlu |
| LPLC2_R → DNb05_R | path-integrated | 22.0 | 22.0 | 21.4 | 97% | +/+/+ | 2.0 | LPLC2 → LPLC4 → DNb05 (21) | uyumlu |
| LC10a_L → DNa15_L | path-integrated | 21.9 | 20.8 | 20.8 | 100% | +/+/+ | 2.0 | LC10a → AOTU025 → DNa15 (23) | uyumlu |
| LC10a_R → DNa15_R | path-integrated | 17.4 | 17.4 | 17.4 | 100% | +/+/+ | 2.0 | LC10a → LAL027 → DNa15 (24) | uyumlu |
| LC4_R → DNp04_L | path-integrated | -16.8 | -16.8 | -16.8 | 100% | −/−/− | 2.0 | LC4 → PVLP024 → DNp04 (21) | uyumlu |
| LC10a_R → DNg13_L | path-integrated | 16.6 | 16.6 | 16.6 | 100% | +/+/+ | 2.0 | LC10a → CB1080 → DNg13 (22) | uyumlu |
| LC10a_R → DNa15_L | path-integrated | -16.1 | -16.1 | -16.1 | 100% | −/−/− | 2.0 | LC10a → AOTU019 → DNa15 (60) | uyumlu |
| LPLC2_L → DNb05_L | path-integrated | 15.9 | 15.9 | 15.6 | 98% | +/+/+ | 2.0 | LPLC2 → PVLP076 → DNb05 (19) | uyumlu |
| LC10a_L → DNb06_R | path-integrated | 14.9 | 14.1 | 14.1 | 100% | +/+/+ | 2.0 | LC10a → AOTU023 → DNb06 (55) | uyumlu |
| LC4_L → DNp04_R | path-integrated | -14.5 | -14.5 | -14.5 | 100% | −/−/− | 2.0 | LC4 → PVLP130 → DNp04 (18) | uyumlu |
| LC10a_R → DNg13_R | path-integrated | 12.5 | 12.5 | 12.5 | 100% | +/+/+ | 2.0 | LC10a → CB0007 → DNg13 (16) | uyumlu |
| LC10a_L → DNg13_R | path-integrated | 12.4 | 12.5 | 12.5 | 100% | +/+/+ | 2.0 | LC10a → CB1080 → DNg13 (23) | uyumlu |
| LPLC2_L → GF_R | path-integrated | 12.2 | 12.2 | 12.2 | 100% | +/+/+ | 2.0 | LPLC2 → PVLP151 → DNp01 (18) | uyumlu |
| LPLC2_R → GF_L | path-integrated | 11.2 | 11.2 | 11.2 | 100% | +/+/+ | 2.0 | LPLC2 → PVLP151 → DNp01 (18) | uyumlu |
| LC10a_L → DNb06_L | path-integrated | 10.9 | 10.2 | 10.2 | 100% | +/+/+ | 2.0 | LC10a → AOTU023 → DNb06 (40) | uyumlu |
| LC10a_L → DNg13_L | path-integrated | 10.8 | 10.8 | 10.8 | 100% | +/+/+ | 2.0 | LC10a → CB0007 → DNg13 (18) | uyumlu |
| LC4_R → DNp03_L | path-integrated | -10.3 | -10.3 | -10.3 | 100% | −/−/− | 2.0 | LC4 → PVLP024 → DNp03 (16) | uyumlu |
| LC10a_L → DNa01_L | path-integrated | 8.8 | 8.4 | 8.4 | 100% | +/+/+ | 2.0 | LC10a → LAL027 → DNae001 (13) | uyumlu |
| LC10a_R → DNa01_R | path-integrated | 8.0 | 8.0 | 8.0 | 100% | +/+/+ | 2.0 | LC10a → AOTU015b → DNae001 (12) | uyumlu |
| LC4_R → DNp11_L | path-integrated | -7.2 | -7.2 | -7.2 | 100% | −/−/− | 2.0 | LC4 → PVLP022 → DNp11 (21) | uyumlu |
| LC10a_R → DNb06_L | path-integrated | 6.6 | 6.6 | 6.6 | 100% | +/+/+ | 2.0 | LC10a → AOTU023 → DNb06 (22) | uyumlu |
| LC10a_R → DNb06_R | path-integrated | 6.3 | 6.3 | 6.3 | 100% | +/+/+ | 2.0 | LC10a → AOTU023 → DNb06 (21) | uyumlu |
| LC4_L → DNp02_R | path-integrated | -6.1 | -6.1 | -6.1 | 100% | −/−/− | 2.0 | LC4 → PVLP130 → DNp02 (15) | uyumlu |
| LPLC2_L → DNp03_L | path-integrated | 4.6 | 4.6 | 4.5 | 99% | +/+/+ | 2.0 | LPLC2 → LPLC4 → DNp03 (17) | uyumlu |
| LC4_L → DNa02_R | path-integrated | 4.2 | 4.2 | 4.2 | 100% | +/+/+ | 2.0 | LC4 → PVLP141 → DNa02 (18) | uyumlu |
| LC10a_L → MDN_R | path-integrated | -3.9 | -3.7 | -3.7 | 100% | −/−/− | 2.0 | LC10a → AOTU019 → MDN (41) | uyumlu |
| LC4_R → DNp02_L | path-integrated | -3.9 | -3.9 | -3.9 | 100% | −/−/− | 2.0 | LC4 → PVLP130 → DNp02 (15) | uyumlu |
| DNp11_L → DNb06_L | path-integrated | -3.8 | -3.8 | -3.8 | 100% | −/−/− | 2.0 | DNp11 → CB0358 → DNb06 (39) | uyumlu |
| LC4_R → DNa02_L | path-integrated | 3.8 | 3.8 | 3.8 | 100% | +/+/+ | 2.0 | LC4 → PVLP141 → DNa02 (15) | uyumlu |
| DNp04_R → GF_R | path-integrated | -3.7 | -3.7 | -3.4 | 91% | −/−/− | 2.0 | DNp04 → PVLP010 → DNp01 (137) | uyumlu |
| DNp11_R → DNb06_R | path-integrated | -3.7 | -3.7 | -3.7 | 100% | −/−/− | 2.0 | DNp11 → CB0358 → DNb06 (32) | uyumlu |
| LPLC2_L → DNp04_R | path-integrated | -2.9 | -2.9 | -2.9 | 100% | −/−/− | 2.0 | LPLC2 → PVLP130 → DNp04 (18) | uyumlu |
| DNb01_L → DNa02_R | path-integrated | 2.8 | 2.8 | 2.9 | 104% | +/+/+ | 2.0 | DNb01 → DNa03 → DNa02 (106) | uyumlu |
| LPLC2_L → DNp02_L | path-integrated | -2.7 | -2.7 | -2.7 | 100% | −/−/− | 2.0 | LPLC2 → DNg40 → DNp02 (21) | uyumlu |
| LPLC2_L → DNp11_L | path-integrated | -2.7 | -2.7 | -2.7 | 100% | −/−/− | 2.0 | LPLC2 → LHAD1g1 → DNp11 (13) | uyumlu |
| DNb01_L → DNa15_L | path-integrated | 2.6 | 2.6 | 0.8 | 31% | +/+/+ | 2.0 | DNb01 → CB0164 → DNa15 (41) | uyumlu |
| DNb05_L → GF_L | path-integrated | -2.6 | -2.6 | -2.6 | 100% | −/−/− | 2.0 | DNb05 → CB0010 → DNp01 (97) | uyumlu |
| DNb05_R → GF_R | path-integrated | -2.5 | -2.5 | -2.5 | 100% | −/−/− | 2.0 | DNb05 → CB0010 → DNp01 (86) | uyumlu |
| DNp09_R → DNa15_R | path-integrated | -2.5 | -2.5 | -1.4 | 56% | −/−/− | 2.0 | DNp09 → CB0527 → DNa15 (62) | uyumlu |
| LPLC2_R → DNp03_L | path-integrated | 2.4 | 2.4 | 2.4 | 100% | +/+/+ | 2.0 | LPLC2 → PVLP151 → DNp03 (10) | uyumlu |
| DNp09_L → DNa15_L | path-integrated | -2.3 | -2.3 | -2.6 | 111% | −/−/− | 2.0 | DNp09 → CB0527 → DNa15 (69) | uyumlu |
| BRK_R → BRK_L | path-integrated | -2.2 | - | - | - | - | - | - | v1 dışında (tip ertelendi/çıkarıldı) |
| DNb01_L → DNb01_R | path-integrated | -2.2 | -2.2 | 0.2 | -10% | −/−/+ | 2.0 | DNb01 → CB0312 → DNb01 (57) | İŞARET FARKLI |
| DNb01_R → DNa15_R | path-integrated | 2.2 | 2.2 | -0.3 | -13% | +/+/− | 2.0 | DNb01 → PS232 → DNa15 (16) | İŞARET FARKLI |
| DNp04_L → GF_L | path-integrated | -2.2 | -2.2 | -2.0 | 92% | −/−/− | 2.0 | DNp04 → PVLP010 → DNp01 (113) | uyumlu |
| DNp11_R → MDN_L | path-integrated | -2.1 | -2.1 | -2.1 | 100% | −/−/− | 2.0 | DNp11 → CB0095 → MDN (14) | uyumlu |
| LC4_L → GF_R | path-integrated | 2.1 | 2.1 | 2.1 | 100% | +/+/+ | 2.0 | LC4 → AMMC-A1 → DNp01 (12) | uyumlu |
| DNb01_R → DNb01_L | path-integrated | -2.0 | -2.0 | -0.8 | 40% | −/−/− | 2.0 | DNb01 → LAL046 → DNb01 (40) | uyumlu |
| LC10a_L → LC10a_R | path-integrated | -2.0 | -2.0 | -2.0 | 100% | −/−/− | 2.0 | LC10a → TuTuAa → LC10a (15) | uyumlu |
| LPLC2_L → DNp02_R | path-integrated | -2.0 | -2.0 | -2.0 | 100% | −/−/− | 2.0 | LPLC2 → PVLP130 → DNp02 (15) | uyumlu |
| LPLC2_R → DNp02_L | path-integrated | -2.0 | -2.0 | -2.0 | 100% | −/−/− | 2.0 | LPLC2 → PVLP130 → DNp02 (15) | uyumlu |
| LPLC2_R → DNp04_L | path-integrated | 2.0 | 2.0 | 2.0 | 100% | +/+/+ | 2.0 | LPLC2 → PVLP151 → DNp04 (18) | uyumlu |
| MDN_L → MDN_R | path-integrated | 2.0 | 2.0 | 2.0 | 100% | +/+/+ | 2.0 | MDN → CB0543 → MDN (20) | uyumlu |
| DNp11_R → DNb06_L | path-integrated | -1.9 | -1.9 | -1.9 | 100% | −/−/− | 2.0 | DNp11 → CB0358 → DNb06 (32) | uyumlu |
| DNp11_R → MDN_R | path-integrated | -1.9 | -1.9 | -1.9 | 100% | −/−/− | 2.0 | DNp11 → CB0095 → MDN (14) | uyumlu |
| Foxglove_R → DNg13_R | path-integrated | -1.9 | -1.9 | -1.9 | 100% | −/−/− | 2.0 | CB0890 → CB0409 → DNg13 (36) | uyumlu |
| LC10a_R → LC10a_L | path-integrated | -1.9 | -1.9 | -1.9 | 100% | −/−/− | 2.0 | LC10a → TuTuAa → LC10a (15) | uyumlu |
| LC4_L → DNb05_R | path-integrated | -1.9 | -1.8 | -1.8 | 100% | −/−/− | 2.0 | LC4 → PVLP021 → DNb05 (7) | uyumlu |
| Foxglove_L → Bluebell_L | path-integrated | 1.8 | 1.8 | 1.8 | 100% | +/+/+ | 2.0 | CB0890 → CB0069 → DNg60 (25) | uyumlu |
| MDN_L → DNa02_R | path-integrated | -1.8 | -1.8 | -1.8 | 100% | −/−/− | 2.0 | MDN → CB0172 → DNa02 (32) | uyumlu |
| DNp09_L → DNa02_R | path-integrated | -1.7 | -1.7 | -1.7 | 100% | −/−/− | 2.0 | DNp09 → CB0527 → DNa02 (47) | uyumlu |
| DNp11_L → DNb06_R | path-integrated | -1.7 | -1.7 | -1.7 | 100% | −/−/− | 2.0 | DNp11 → CB0358 → DNb06 (28) | uyumlu |
| DNa02_R → DNb01_R | path-integrated | -1.6 | -1.6 | -1.6 | 100% | −/−/− | 2.0 | DNa02 → PS137 → DNb01 (47) | uyumlu |
| DNb05_R → DNb01_R | path-integrated | -1.6 | -1.6 | -0.2 | 11% | −/−/− | 2.0 | DNb05 → CB0049 → DNb01 (6) | uyumlu |
| DNb05_R → GF_L | path-integrated | -1.6 | -1.6 | -1.6 | 100% | −/−/− | 2.0 | DNb05 → CB0010 → DNp01 (60) | uyumlu |
| DNp09_R → DNa02_L | path-integrated | -1.6 | -1.6 | -1.7 | 108% | −/−/− | 2.0 | DNp09 → CB0527 → DNa02 (62) | uyumlu |
| DNp11_L → MDN_R | path-integrated | -1.6 | -1.6 | -1.6 | 100% | −/−/− | 2.0 | DNp11 → CB0095 → MDN (19) | uyumlu |
| DNp09_L → DNb06_R | path-integrated | -1.5 | -1.5 | -1.5 | 100% | −/−/− | 2.0 | DNp09 → CB0358 → DNb06 (13) | uyumlu |
| Foxglove_R → Bluebell_L | path-integrated | 1.5 | 1.5 | 1.5 | 100% | +/+/+ | 2.0 | CB0890 → CB0069 → DNg60 (25) | uyumlu |
| LC10a_L → DNa02_R | path-integrated | 1.5 | 1.9 | 1.9 | 100% | +/+/+ | 2.0 | LC10a → AOTU019 → DNa02 (56) | uyumlu |
| Bluebell_R → DNa02_L | path-integrated | -1.4 | -1.4 | -1.4 | 100% | −/−/− | 2.0 | DNg60 → DNg75 → DNa02 (55) | uyumlu |
| DNp09_L → DNa15_R | path-integrated | -1.4 | -1.3 | -1.3 | 100% | −/−/− | 2.0 | DNp09 → CB0527 → DNa15 (69) | uyumlu |
| DNp09_L → GF_L | path-integrated | -1.4 | -1.4 | -1.4 | 100% | −/−/− | 2.0 | DNp09 → CB0397 → DNp01 (18) | uyumlu |
| DNp09_R → DNa15_L | path-integrated | -1.4 | -1.4 | -1.3 | 96% | −/−/− | 2.0 | DNp09 → CB0527 → DNa15 (62) | uyumlu |
| DNp11_L → MDN_L | path-integrated | -1.4 | -1.4 | -1.4 | 100% | −/−/− | 2.0 | DNp11 → CB0095 → MDN (19) | uyumlu |
| MDN_L → DNa02_L | path-integrated | -1.4 | -1.4 | -1.4 | 100% | −/−/− | 2.0 | MDN → CB0543 → DNa02 (26) | uyumlu |
| BPN_T2a_L → DNa15_R | path-integrated | 1.3 | - | - | - | - | - | - | v1 dışında (tip ertelendi/çıkarıldı) |
| Foxglove_R → DNg13_L | path-integrated | -1.3 | -1.3 | -1.3 | 100% | −/−/− | 2.0 | CB0890 → DNg97 → DNg13 (36) | uyumlu |
| LC10a_R → MDN_R | path-integrated | -1.3 | -1.3 | -1.3 | 100% | −/−/− | 2.0 | LC10a → AOTU019 → MDN (19) | uyumlu |
| LC4_L → DNa15_L | path-integrated | -1.3 | -1.3 | -1.3 | 100% | −/−/− | 2.0 | LC4 → PLP029 → DNa15 (10) | uyumlu |
| DNa15_R → DNa02_R | path-integrated | -1.2 | -1.2 | -1.4 | 109% | −/−/− | 2.0 | DNa15 → PS059 → DNa02 (26) | uyumlu |
| LC10a_L → MDN_L | path-integrated | -1.2 | -1.1 | -1.1 | 100% | −/−/− | 2.0 | LC10a → AOTU019 → MDN (26) | uyumlu |
| LC10a_R → DNa01_L | path-integrated | 1.2 | 1.2 | 1.2 | 100% | +/+/+ | 2.0 | LC10a → AOTU019 → DNae001 (6) | uyumlu |
| DNp04_L → DNp03_L | path-integrated | -1.1 | -1.1 | -1.1 | 100% | −/−/− | 2.0 | DNp04 → LHAD1g1 → DNp03 (13) | uyumlu |
| DNp04_R → DNp02_R | path-integrated | -1.1 | -1.1 | -1.1 | 103% | −/−/− | 2.0 | DNp04 → PVLP010 → DNp02 (48) | uyumlu |
| DNp09_L → DNp02_L | path-integrated | -1.1 | -1.1 | -1.1 | 100% | −/−/− | 2.0 | DNp09 → CB0397 → DNp02 (15) | uyumlu |
| DNb01_R → DNa02_L | path-integrated | 1.0 | 1.0 | 1.4 | 142% | +/+/+ | 2.0 | DNb01 → DNa03 → DNa02 (102) | uyumlu |
| LPLC2_R → Foxglove_R | path-integrated | 1.0 | 1.0 | 1.0 | 100% | +/+/+ | 2.0 | LPLC2 → DNpe025 → CB0890 (13) | uyumlu |
| MDN_R → DNa02_L | path-integrated | -1.0 | -1.0 | -1.0 | 100% | −/−/− | 2.0 | MDN → CB0172 → DNa02 (37) | uyumlu |
| LC4_L → DNp04_L | measured | 1064.0 | 1064.0 | 1064.0 | 100% | +/+/+ | 1.0 | LC4 → DNp04 (42) | uyumlu |
| LC4_R → DNp04_R | measured | 786.0 | 786.0 | 786.0 | 100% | +/+/+ | 1.0 | LC4 → DNp04 (37) | uyumlu |
| LC4_L → DNp11_L | measured | 544.0 | 544.0 | 544.0 | 100% | +/+/+ | 1.0 | LC4 → DNp11 (37) | uyumlu |
| LPLC2_R → GF_R | measured | 539.0 | 539.0 | 539.0 | 100% | +/+/+ | 1.0 | LPLC2 → DNp103 → DNp01 (24) | uyumlu |
| LPLC2_R → DNp04_R | measured | 506.0 | 506.0 | 506.0 | 100% | +/+/+ | 1.0 | LPLC2 → DNp04 (27) | uyumlu |
| LPLC2_L → DNp04_L | measured | 501.0 | 501.0 | 501.0 | 100% | +/+/+ | 1.0 | LPLC2 → DNp04 (15) | uyumlu |
| LC4_L → DNp02_L | measured | 499.0 | 499.0 | 499.0 | 100% | +/+/+ | 1.0 | LC4 → DNp02 (27) | uyumlu |
| LC4_R → DNp02_R | measured | 463.0 | 463.0 | 463.0 | 100% | +/+/+ | 1.0 | LC4 → DNp02 (19) | uyumlu |
| LC4_R → GF_R | measured | 428.0 | 428.0 | 428.0 | 100% | +/+/+ | 1.0 | LC4 → PVLP024 → DNp01 (24) | uyumlu |
| LC4_L → GF_L | measured | 329.0 | 329.0 | 329.0 | 100% | +/+/+ | 1.0 | LC4 → PVLP024 → DNp01 (27) | uyumlu |
| LC4_L → DNp03_L | measured | 317.0 | 317.0 | 317.0 | 100% | +/+/+ | 1.0 | LC4 → DNp03 (18) | uyumlu |
| LC4_R → DNp11_R | measured | 316.0 | 316.0 | 316.0 | 100% | +/+/+ | 1.0 | LC4 → DNp11 (23) | uyumlu |
| LPLC2_L → GF_L | measured | 305.0 | 305.0 | 305.0 | 100% | +/+/+ | 1.0 | LPLC2 → LHAD1g1 → DNp01 (24) | uyumlu |
| DNp09_R → DNa02_R | measured | 31.0 | 31.0 | 31.0 | 100% | +/+/+ | 1.0 | DNp09 → DNg75 → DNa02 (67) | uyumlu |
| DNp09_L → DNa02_L | measured | 24.0 | 24.0 | 24.0 | 100% | +/+/+ | 1.0 | DNp09 → CB0527 → DNa02 (67) | uyumlu |
| DNb01_R → DNa15_L | measured | -19.0 | -19.0 | -19.0 | 100% | −/−/− | 1.0 | DNb01 → DNa03 → DNa15 (102) | uyumlu |
| DNp03_L → DNb01_R | measured | 18.0 | 18.0 | 18.0 | 100% | +/+/+ | 1.0 | DNp03 → DNb01 (18) | uyumlu |
| DNa01_R → Bluebell_R | measured | 17.0 | 17.0 | 17.0 | 100% | +/+/+ | 1.0 | DNae001 → CB0781 → DNg60 (46) | uyumlu |
| DNa01_L → DNg13_L | measured | 14.0 | 14.0 | 14.0 | 100% | +/+/+ | 1.0 | DNae001 → DNg13 (14) | uyumlu |
| DNb01_L → DNa15_R | measured | -12.0 | -12.0 | -12.0 | 100% | −/−/− | 1.0 | DNb01 → DNa03 → DNa15 (106) | uyumlu |
| LPLC2_L → DNp09_L | measured | 11.0 | 11.0 | 11.0 | 100% | +/+/+ | 1.0 | LPLC2 → AVLP531 → DNp09 (21) | uyumlu |
| DNp09_L → DNa01_L | measured | 10.0 | 10.0 | 10.0 | 100% | +/+/+ | 1.0 | DNp09 → CB0556 → DNae001 (20) | uyumlu |
| DNp03_L → DNa15_R | measured | 9.0 | 9.0 | 9.0 | 100% | +/+/+ | 1.0 | DNp03 → PS100 → DNa15 (24) | uyumlu |
| Bluebell_L → DNa02_R | measured | -8.0 | -8.0 | -8.0 | 100% | −/−/− | 1.0 | DNg60 → DNg75 → DNa02 (70) | uyumlu |
| DNp11_L → DNp03_L | measured | 8.0 | 8.0 | 8.0 | 100% | +/+/+ | 1.0 | DNp11 → PS181 → DNp03 (10) | uyumlu |
| DNa01_L → Bluebell_L | measured | 7.0 | 7.0 | 7.0 | 100% | +/+/+ | 1.0 | DNae001 → CB0781 → DNg60 (32) | uyumlu |
| DNa01_R → DNa02_R | measured | 7.0 | 7.0 | 7.0 | 100% | +/+/+ | 1.0 | DNae001 → DNg75 → DNa02 (24) | uyumlu |
| DNa01_R → DNg13_R | measured | 7.0 | 7.0 | 7.0 | 100% | +/+/+ | 1.0 | DNae001 → DNa11 → DNg13 (13) | uyumlu |
| DNa02_R → DNa15_R | measured | 7.0 | 7.0 | 7.0 | 100% | +/+/+ | 1.0 | DNa02 → PS100 → DNa15 (39) | uyumlu |
| DNp09_R → DNa01_R | measured | 7.0 | 7.0 | 7.0 | 100% | +/+/+ | 1.0 | DNp09 → CB0556 → DNae001 (30) | uyumlu |
| DNa01_L → DNa02_L | measured | 6.0 | 6.0 | 6.0 | 100% | +/+/+ | 1.0 | DNae001 → DNg75 → DNa02 (18) | uyumlu |
| DNa02_L → DNa01_L | measured | 6.0 | 6.0 | 6.0 | 100% | +/+/+ | 1.0 | DNa02 → PS059 → DNae001 (16) | uyumlu |
| DNa02_L → DNa15_L | measured | 5.0 | 5.0 | 5.0 | 100% | +/+/+ | 1.0 | DNa02 → PS100 → DNa15 (33) | uyumlu |
| DNa15_L → DNb01_L | measured | 5.0 | 5.0 | 5.0 | 100% | +/+/+ | 1.0 | DNa15 → PS274 → DNb01 (15) | uyumlu |
| Foxglove_L → DNg13_R | measured | -5.0 | -5.0 | -5.0 | 100% | −/−/− | 1.0 | CB0890 → CB0409 → DNg13 (36) | uyumlu |
| LPLC2_R → DNp09_R | measured | 5.0 | 5.0 | 5.0 | 100% | +/+/+ | 1.0 | LPLC2 → AVLP531 → DNp09 (17) | uyumlu |
| LPLC2_R → LC4_R | measured | 2.4 | 2.4 | 2.4 | 100% | +/+/+ | 1.0 | LPLC2 → LC4 (13) | uyumlu |
| LPLC2_L → LC4_L | measured | 1.6 | 1.6 | 1.6 | 100% | +/+/+ | 1.0 | LPLC2 → LC4 (10) | uyumlu |
