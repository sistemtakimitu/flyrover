# P0: Graf v1 (FAFB v783)

> Bu dosya `python -m connectome.build_graph` ile üretilir; elle düzenlenmez.

- **graph_id:** `fafb783-c2d5a878c336`
- **SHA-256:** `c2d5a878c3367184ca6993838a161ddfb150a0b7af0d84f42012343f563eda82`
- **Nöron:** 9304 · **kenar:** 291383 · **sinaps:** 5925498
- **Parametreler:** θ = 0.01, max_hops = 2, min_synapses = 5, direction = directed, w_syn = 0.275 mV

## Tohumlar

| tohum | rol | sol | sag | durum |
|---|---|---|---|---|
| LC4 | input | 54 | 50 | OK |
| LPLC2 | input | 108 | 102 | OK |
| LC10a | input | 115 | 119 | OK |
| LC11 | input | 66 | 61 | OK |
| GRN_sugar | input | 33 | 24 | OK |
| GF | mode | 1 | 1 | OK |
| DNp02 | mode | 1 | 1 | OK |
| DNp04 | mode | 1 | 1 | OK |
| DNp11 | mode | 1 | 1 | OK |
| MDN | mode | 2 | 2 | OK |
| DNa01 | mode | 1 | 1 | OK |
| DNa02 | mode | 1 | 1 | OK |
| DNp09 | mode | 1 | 1 | OK |
| MN9 | mode | 1 | 1 | OK |
| DNg13 | record | 1 | 1 | OK |
| DNb05 | record | 1 | 1 | OK |
| DNb06 | record | 1 | 1 | OK |
| Foxglove | record | 1 | 1 | OK |
| Bluebell | record | 1 | 1 | OK |

## Ağın bileşimi

| origin | noron |
|---|---|
| backward | 2471 |
| backward+forward | 1356 |
| forward | 4715 |
| seed | 762 |

| hop | noron |
|---|---|
| 0 | 762 |
| 1 | 1536 |
| 2 | 7006 |

| super_class | noron |
|---|---|
| central | 4754 |
| visual_projection | 1904 |
| optic | 1218 |
| descending | 550 |
| sensory | 347 |
| ascending | 344 |
| visual_centrifugal | 112 |
| motor | 53 |
| sensory_ascending | 22 |

## En sık ara tipler (tohum olmayan)

| ara tip | noron |
|---|---|
| LC17 | 146 |
| LC10d | 118 |
| Pm08 | 110 |
| (tipsiz) | 104 |
| LPLC4 | 98 |
| Li17 | 89 |
| Pm03 | 87 |
| Pm01 | 65 |
| LC9 | 65 |
| Li10 | 54 |
| LMa1 | 54 |
| LPLC1 | 53 |
| LC13 | 48 |
| Li05 | 48 |
| LPC1 | 44 |
| LC10b | 35 |
| LC14a1 | 30 |
| LMa2 | 30 |
| LT52 | 29 |
| PVLP004,PVLP005 | 29 |
| LLPt | 29 |
| LMa5 | 26 |
| Pm06 | 25 |
| Pm05 | 25 |
| TmY14 | 25 |

## Nörotransmitter ve işaret

Modülatör NT'ler (dopamin, serotonin, oktopamin) +1 alır (v0 ile aynı); `synapse_avg` = anotasyonda top_nt yok, sinaps düzeyi NT ortalamasından.

| nt | nt_source | sign | noron |
|---|---|---|---|
| acetylcholine | annotation | 1 | 5422 |
| dopamine | annotation | 1 | 44 |
| gaba | annotation | -1 | 2250 |
| glutamate | annotation | -1 | 1454 |
| octopamine | annotation | 1 | 14 |
| serotonin | annotation | 1 | 120 |

| sign | kenar | sinaps |
|---|---|---|
| -1 | 130832 | 2855471 |
| 1 | 160551 | 3070027 |

## Girdi → mod erişilebilirliği (alt ağ içinde)

- **bulusma:** girdinin ileri genişletmesi ile hedefin geri genişletmesinin ortak nöron sayısı.
- **en_kisa / en_kisa_uyarici:** alt ağda en kısa yol (sıçrama); ikincisi yalnızca uyarıcı kenarlarla.
- **guclu_yol_darbogaz / guclu_yol:** en fazla 4 sıçramalık (ileri + geri genişletme derinliği) yollar içinde en zayıf kenarı en güçlü olan yol; darboğaz o kenarın sinaps sayısı, yol tip adlarıyla. İşaret gözetmez.

Yol varlığı davranış demek değildir; asıl test kabul testleri ve tüm-beyin kahinidir.

| girdi | hedef | bulusma | en_kisa | en_kisa_uyarici | guclu_yol_darbogaz | guclu_yol |
|---|---|---|---|---|---|---|
| LC4 | GF | 77 | 1 | 1 | 42 | LC4 → DNp04 → PVLP122b → DNp01 |
| LC4 | DNp02 | 56 | 1 | 1 | 37 | LC4 → DNp04 → PVLP010 → DNp02 |
| LC4 | DNp04 | 61 | 1 | 1 | 42 | LC4 → DNp04 |
| LC4 | DNp11 | 60 | 1 | 1 | 42 | LC4 → DNp04 → PVLP122a → PVLP015 → DNp11 |
| LC4 | MDN | 35 | 2 | 2 | 28 | LC4 → PVLP024 → PVLP141 → DNpe023 → MDN |
| LC4 | DNa01 | 65 | 2 | 3 | 25 | LC4 → DNp04 → DNpe045 → CB0556 → DNae001 |
| LC4 | DNa02 | 86 | 2 | 2 | 42 | LC4 → DNp04 → DNp35 → CB0527 → DNa02 |
| LC4 | DNp09 | 71 | 2 | 2 | 42 | LC4 → DNp04 → AVLP077 → PVLP150 → DNp09 |
| LC4 | MN9 | 19 | 3 | 3 | 42 | LC4 → DNp04 → DNg108 → CB0701 |
| LC4 | DNg13 | 84 | 2 | 2 | 42 | LC4 → DNp04 → DNge119 → DNg97 → DNg13 |
| LC4 | DNb05 | 10 | 2 | 2 | 37 | LC4 → DNp04 → CL140 → DNbe007 → DNb05 |
| LC4 | DNb06 | 37 | 3 | 3 | 42 | LC4 → DNp04 → PVLP010 → CB0478 → DNb06 |
| LC4 | Foxglove | 12 | 3 | 3 | 20 | LC4 → LTe18 → DNpe027 → CB0429 → CB0890 |
| LC4 | Bluebell | 22 | 3 | 3 | 21 | LC4 → DNp04 → DNge119 → CB0036 → DNg60 |
| LPLC2 | GF | 104 | 1 | 1 | 61 | LPLC2 → PVLP011 → PVLP151 → DNp01 |
| LPLC2 | DNp02 | 63 | 2 | 2 | 43 | LPLC2 → PVLP011 → PVLP076 → PVLP010 → DNp02 |
| LPLC2 | DNp04 | 57 | 1 | 1 | 56 | LPLC2 → PVLP011 → PVLP015 → PVLP130 → DNp04 |
| LPLC2 | DNp11 | 59 | 2 | 2 | 78 | LPLC2 → PVLP011 → PVLP015 → PVLP022 → DNp11 |
| LPLC2 | MDN | 56 | 2 | 2 | 30 | LPLC2 → PVLP069 → AVLP573 → CL322 → MDN |
| LPLC2 | DNa01 | 106 | 2 | 2 | 25 | LPLC2 → DNp04 → DNpe045 → CB0556 → DNae001 |
| LPLC2 | DNa02 | 123 | 2 | 2 | 78 | LPLC2 → PVLP011 → PVLP015 → PVLP141 → DNa02 |
| LPLC2 | DNp09 | 91 | 1 | 1 | 72 | LPLC2 → PVLP011 → PLP018 → DNp09 |
| LPLC2 | MN9 | 28 | 3 | 3 | 33 | LPLC2 → PVLP069 → CL213 → DNg108 → CB0701 |
| LPLC2 | DNg13 | 124 | 2 | 2 | 30 | LPLC2 → PVLP011 → PLP249 → LAL016 → DNg13 |
| LPLC2 | DNb05 | 29 | 2 | 2 | 62 | LPLC2 → PVLP011 → PLP035 → PLP092 → DNb05 |
| LPLC2 | DNb06 | 54 | 3 | 3 | 27 | LPLC2 → DNp04 → PVLP010 → CB0478 → DNb06 |
| LPLC2 | Foxglove | 24 | 2 | 2 | 24 | LPLC2 → LHAD1g1 → DNp71 → DNd05 → CB0890 |
| LPLC2 | Bluebell | 43 | 3 | 3 | 21 | LPLC2 → AVLP531 → CL214 → CB0585 → DNg60 |
| LC10a | GF | 30 | 3 | 3 | 48 | LC10a → AOTU014 → DNge043 → CB0010 → DNp01 |
| LC10a | DNp02 | 19 | 3 | 3 | 34 | LC10a → AOTU014 → DNge043 → CB0010 → DNp02 |
| LC10a | DNp04 | 41 | 3 | 3 | 25 | LC10a → AOTU019 → PVLP060 → PVLP130 → DNp04 |
| LC10a | DNp11 | 63 | 2 | 2 | 55 | LC10a → AOTU014 → cL20 → DNp11 |
| LC10a | MDN | 103 | 2 | 2 | 55 | LC10a → AOTU019 → DNa03 → DNpe023 → MDN |
| LC10a | DNa01 | 202 | 2 | 2 | 60 | LC10a → AOTU019 → LAL046 → LAL126 → DNae001 |
| LC10a | DNa02 | 211 | 2 | 2 | 65 | LC10a → AOTU014 → IB018 → AOTU019 → DNa02 |
| LC10a | DNp09 | 57 | 2 | 2 | 33 | LC10a → AOTU019 → LT82b → PLP018 → DNp09 |
| LC10a | MN9 | 23 | 3 | 4 | 59 | LC10a → AOTU014 → DNde002 → CB0047 → CB0701 |
| LC10a | DNg13 | 207 | 2 | 2 | 60 | LC10a → AOTU019 → DNa03 → LAL073 → DNg13 |
| LC10a | DNb05 | 30 | 2 | 2 | 60 | LC10a → AOTU019 → PS232 → PLP060 → DNb05 |
| LC10a | DNb06 | 92 | 2 | 2 | 65 | LC10a → AOTU014 → PS300 → DNb06 |
| LC10a | Foxglove | 21 | 3 | 3 | 38 | LC10a → AOTU019 → LAL119 → CB0190 → CB0890 |
| LC10a | Bluebell | 41 | 3 | 3 | 51 | LC10a → AOTU014 → DNge043 → CB0287 → DNg60 |
| LC11 | GF | 63 | 2 | 3 | 52 | LC11 → CB0732 → AVLP442 → DNp70 → DNp01 |
| LC11 | DNp02 | 14 | 2 | 3 | 42 | LC11 → CB0732 → AVLP442 → PVLP010 → DNp02 |
| LC11 | DNp04 | 23 | 2 | 2 | 44 | LC11 → CB0732 → PVLP061 → PVLP130 → DNp04 |
| LC11 | DNp11 | 33 | 2 | 2 | 45 | LC11 → CB0732 → AVLP498 → PVLP015 → DNp11 |
| LC11 | MDN | 29 | 3 | 3 | 30 | LC11 → DNp35 → VES041 → LAL040 → MDN |
| LC11 | DNa01 | 45 | 3 | 3 | 30 | LC11 → DNp35 → VES041 → LAL014 → DNae001 |
| LC11 | DNa02 | 54 | 3 | 3 | 39 | LC11 → PVLP002 → AVLP080 → PVLP141 → DNa02 |
| LC11 | DNp09 | 78 | 2 | 2 | 58 | LC11 → AVLP282 → AVLP435b → CB2458 → DNp09 |
| LC11 | MN9 | 8 | 3 | 4 | 30 | LC11 → DNp35 → DNg108 → CB0701 |
| LC11 | DNg13 | 46 | 2 | 2 | 30 | LC11 → DNp35 → CB0527 → PS018b → DNg13 |
| LC11 | DNb05 | 19 | 2 | 2 | 28 | LC11 → PVLP002 → PLP093 → PLP034 → DNb05 |
| LC11 | DNb06 | 15 | 2 | 2 | 30 | LC11 → DNp35 → VES041 → AOTU023 → DNb06 |
| LC11 | Foxglove | 1 | 3 | 3 | 30 | LC11 → DNp35 → VES041 → LAL119 → CB0890 |
| LC11 | Bluebell | 9 | 3 | 3 | 28 | LC11 → DNp35 → VES041 → LAL119 → DNg60 |
| GRN_sugar | GF | 7 | 3 | 3 | 40 | LB3b → AN_GNG_21 → CB0568 → DNpe042 → DNp01 |
| GRN_sugar | DNp02 | 4 | 3 | 3 | 18 | LB3c → CB0062 → DNg104 → LHAD1g1 → DNp02 |
| GRN_sugar | DNp04 | 0 | 3 | 3 | 18 | LB3b → AN_GNG_68 → VESa1_P02 → PVLP151 → DNp04 |
| GRN_sugar | DNp11 | 2 | 3 | 4 | 16 | LB3b → il3LN6 → MZ_lv2PN → LTe20 → DNp11 |
| GRN_sugar | MDN | 6 | 3 | 3 | 34 | LB3b → AN_GNG_21 → CB0698 → DNpe023 → MDN |
| GRN_sugar | DNa01 | 23 | 3 | 3 | 18 | LB3b → AN_GNG_21 → CB0698 → LAL013 → DNae001 |
| GRN_sugar | DNa02 | 9 | 3 | 3 | 46 | LB3b → AN_GNG_21 → DNge101 → DNg75 → DNa02 |
| GRN_sugar | DNp09 | 5 | 3 | 3 | 23 | LB3b → AN_GNG_68 → VESa1_P02 → AVLP437 → DNp09 |
| GRN_sugar | MN9 | 196 | 2 | 2 | 50 | LB3c → CB0616 → DNge080 → CB0701 |
| GRN_sugar | DNg13 | 42 | 2 | 3 | 40 | LB3b → CB0366 → CB0177 → CB0021 → DNg13 |
| GRN_sugar | DNb05 | 7 | 2 | 2 | 32 | LB3b → AN_GNG_68 → VESa1_P02 → PLP096 → DNb05 |
| GRN_sugar | DNb06 | 10 | 3 | 4 | 18 | LB3c → CB0616 → DNge059 → CB0358 → DNb06 |
| GRN_sugar | Foxglove | 179 | 2 | 2 | 44 | LB3b → AN_GNG_21 → CB0872 → CB0177 → CB0890 |
| GRN_sugar | Bluebell | 197 | 2 | 2 | 46 | LB3b → AN_GNG_21 → CB0872 → DNg60 |
