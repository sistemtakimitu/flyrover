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
| cython | persistent | 0.2 | 0.3 |
| cython | per_run | 0.2 | 0.2 |
| numpy | persistent | 0.1 | 0.2 |
| numpy | per_run | 0.1 | 0.2 |

## Adım süresi

| kod üretimi | mod | senaryo | adım (ms) | medyan duvar (ms) | RTF | aktif nöron |
|---|---|---|---|---|---|---|
| cython | persistent | sessiz | 10 | 2.0 | 5.10 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 10 | 2.0 | 4.94 | 397 |
| cython | persistent | tüm girdiler 100 Hz | 10 | 2.1 | 4.74 | 1645 |
| cython | persistent | sessiz | 20 | 4.2 | 4.82 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 20 | 4.1 | 4.89 | 473 |
| cython | persistent | tüm girdiler 100 Hz | 20 | 4.2 | 4.78 | 1666 |
| cython | persistent | sessiz | 50 | 9.5 | 5.25 | 0 |
| cython | persistent | LC4 iki taraf 100 Hz | 50 | 9.7 | 5.16 | 500 |
| cython | persistent | tüm girdiler 100 Hz | 50 | 10.1 | 4.97 | 1693 |
| cython | per_run | sessiz | 10 | 24.9 | 0.40 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 10 | 25.1 | 0.40 | 397 |
| cython | per_run | tüm girdiler 100 Hz | 10 | 25.1 | 0.40 | 1645 |
| cython | per_run | sessiz | 20 | 26.6 | 0.75 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 20 | 26.7 | 0.75 | 473 |
| cython | per_run | tüm girdiler 100 Hz | 20 | 27.1 | 0.74 | 1666 |
| cython | per_run | sessiz | 50 | 31.5 | 1.59 | 0 |
| cython | per_run | LC4 iki taraf 100 Hz | 50 | 31.8 | 1.57 | 500 |
| cython | per_run | tüm girdiler 100 Hz | 50 | 32.2 | 1.55 | 1693 |
| numpy | persistent | sessiz | 10 | 5.5 | 1.83 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 10 | 6.2 | 1.62 | 397 |
| numpy | persistent | tüm girdiler 100 Hz | 10 | 6.7 | 1.49 | 1645 |
| numpy | persistent | sessiz | 20 | 10.9 | 1.83 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 20 | 12.1 | 1.65 | 473 |
| numpy | persistent | tüm girdiler 100 Hz | 20 | 13.2 | 1.51 | 1666 |
| numpy | persistent | sessiz | 50 | 26.4 | 1.89 | 0 |
| numpy | persistent | LC4 iki taraf 100 Hz | 50 | 30.1 | 1.66 | 500 |
| numpy | persistent | tüm girdiler 100 Hz | 50 | 32.7 | 1.53 | 1693 |
| numpy | per_run | sessiz | 10 | 26.0 | 0.38 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 10 | 26.6 | 0.38 | 397 |
| numpy | per_run | tüm girdiler 100 Hz | 10 | 27.2 | 0.37 | 1645 |
| numpy | per_run | sessiz | 20 | 30.9 | 0.65 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 20 | 32.4 | 0.62 | 473 |
| numpy | per_run | tüm girdiler 100 Hz | 20 | 33.5 | 0.60 | 1666 |
| numpy | per_run | sessiz | 50 | 47.4 | 1.06 | 0 |
| numpy | per_run | LC4 iki taraf 100 Hz | 50 | 50.4 | 0.99 | 500 |
| numpy | per_run | tüm girdiler 100 Hz | 50 | 53.6 | 0.93 | 1693 |

## Duman testi: mod DN hızları (Hz, sol–sağ ortalaması; cython persistent, 20 ms adım, tohum 0)

Kalibrasyonsuz, arka plan girdisiz; kabul testi değildir. Yalnızca ağın sessiz kalmadığını ve kalıcı duruma kilitlenmediğini gösterir.

| senaryo | GF | DNp02 | DNp04 | DNp11 | MDN | DNa01 | DNa02 | DNp09 | MN9 |
|---|---|---|---|---|---|---|---|---|---|
| sessiz | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| LC4 iki taraf 100 Hz | 72.0 | 195.0 | 290.0 | 166.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| tüm girdiler 100 Hz | 166.0 | 167.0 | 298.0 | 91.0 | 0.0 | 0.0 | 25.0 | 3.0 | 318.0 |
