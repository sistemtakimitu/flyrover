# P0: Brian2 motoru hız ölçümü (graf v1)

> Bu dosya `python src/snn/bench_fafb.py` ile üretilir; elle düzenlenmez.

- **Graf:** `fafb783-c2d5a878c336`
- **Makine:** macOS-26.6.2-arm64-arm-64bit, arm64, Python 3.12.14
- **Ölçüm:** her senaryo × adım süresi için 1 ısınma + 25 adım, medyan duvar saati. RTF = simüle süre / duvar saati (≥ 1: gerçek zamandan hızlı).
- **Modlar:** `per_run` her adımda bir `net.run()` (Brian2 her çağrıda ~25 ms sabit maliyet öder); `persistent` tek uzun `run()` + adım başına `NetworkOperation` (aynı tohumla aynı spike'lar, birim testli).
- **cpp_standalone ölçülmedi:** her `run()` çağrısında baştan başlar; kapalı döngüde adım adım kullanılamaz. Yalnızca toplu, çevrimdışı koşular (tüm-beyin kahini) içindir.

## Kurulum

| kod üretimi | mod | ağ kurulumu (s, en kötü) | ilk adım, derleme dahil (s) |
|---|---|---|---|
| cython | persistent | 0.2 | 5.8 |
| cython | per_run | 0.2 | 0.1 |
| numpy | persistent | 0.1 | 0.1 |
| numpy | per_run | 0.1 | 0.1 |

## Adım süresi

| kod üretimi | mod | senaryo | adım (ms) | medyan duvar (ms) | RTF | aktif nöron |
|---|---|---|---|---|---|---|
| cython | persistent | sessiz | 10 | 2.9 | 3.41 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 10 | 2.4 | 4.10 | 282 |
| cython | persistent | tüm girdiler 100 Hz | 10 | 2.6 | 3.89 | 1777 |
| cython | persistent | sessiz | 20 | 4.7 | 4.25 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 20 | 4.8 | 4.18 | 312 |
| cython | persistent | tüm girdiler 100 Hz | 20 | 5.0 | 4.01 | 1810 |
| cython | persistent | sessiz | 50 | 11.4 | 4.40 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 50 | 11.5 | 4.36 | 336 |
| cython | persistent | tüm girdiler 100 Hz | 50 | 12.0 | 4.15 | 1848 |
| cython | per_run | sessiz | 10 | 25.3 | 0.39 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 10 | 25.6 | 0.39 | 282 |
| cython | per_run | tüm girdiler 100 Hz | 10 | 25.8 | 0.39 | 1777 |
| cython | per_run | sessiz | 20 | 27.4 | 0.73 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 20 | 27.8 | 0.72 | 312 |
| cython | per_run | tüm girdiler 100 Hz | 20 | 28.1 | 0.71 | 1810 |
| cython | per_run | sessiz | 50 | 33.6 | 1.49 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 50 | 34.1 | 1.47 | 336 |
| cython | per_run | tüm girdiler 100 Hz | 50 | 34.7 | 1.44 | 1848 |
| numpy | persistent | sessiz | 10 | 7.1 | 1.41 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 10 | 7.8 | 1.28 | 282 |
| numpy | persistent | tüm girdiler 100 Hz | 10 | 8.5 | 1.17 | 1777 |
| numpy | persistent | sessiz | 20 | 14.1 | 1.42 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 20 | 15.5 | 1.29 | 312 |
| numpy | persistent | tüm girdiler 100 Hz | 20 | 16.9 | 1.18 | 1810 |
| numpy | persistent | sessiz | 50 | 35.1 | 1.42 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 50 | 38.6 | 1.29 | 336 |
| numpy | persistent | tüm girdiler 100 Hz | 50 | 42.8 | 1.17 | 1848 |
| numpy | per_run | sessiz | 10 | 30.4 | 0.33 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 10 | 30.0 | 0.33 | 282 |
| numpy | per_run | tüm girdiler 100 Hz | 10 | 32.7 | 0.31 | 1777 |
| numpy | per_run | sessiz | 20 | 36.9 | 0.54 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 20 | 36.7 | 0.55 | 312 |
| numpy | per_run | tüm girdiler 100 Hz | 20 | 38.6 | 0.52 | 1810 |
| numpy | per_run | sessiz | 50 | 55.4 | 0.90 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 50 | 59.4 | 0.84 | 336 |
| numpy | per_run | tüm girdiler 100 Hz | 50 | 62.9 | 0.79 | 1848 |

## Duman testi: mod DN hızları (Hz, sol–sağ ortalaması; cython persistent, 20 ms adım, tohum 0)

Kalibrasyonsuz, arka plan girdisiz; kabul testi değildir. Yalnızca ağın sessiz kalmadığını ve kalıcı duruma kilitlenmediğini gösterir.

| senaryo | GF | DNp02 | DNp04 | DNp11 | MDN | DNa01 | DNa02 | DNp09 | MN9 |
|---|---|---|---|---|---|---|---|---|---|
| sessiz | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| LC4 iki taraf 100 Hz | 87.0 | 115.0 | 154.0 | 96.0 | 0.0 | 0.0 | 5.0 | 0.0 | 0.0 |
| tüm girdiler 100 Hz | 143.0 | 102.0 | 180.0 | 82.0 | 0.0 | 0.0 | 26.0 | 0.0 | 43.0 |
