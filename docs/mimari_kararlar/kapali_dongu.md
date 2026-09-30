# Kapalı Döngü Mimarisi (Simülatör ↔ Sinek Beyni)

Her **20 ms**'de bir şu döngü çalışır:

```
MuJoCo kamerası ─► Kodlayıcı ─► SNN (Brian2, 20 ms) ─► Çözücü ─► Teker hızları
      ▲                                                                 │
      └──────────────────── MuJoCo 20 ms ilerler ◄──────────────────────┘
```

Biyolojik olan kısım **sadece ortadaki SNN**'dir: bağlantılar ve ağırlıklar doğrudan FlyWire'dan gelir, elle ayarlanmaz. Kodlayıcı ve çözücü **mühendislik katmanıdır** — sinekte retina/optik lob ve omurilik eşdeğeri (VNC) olan yerlerin sadeleştirilmiş karşılıklarıdır.

## 1. SNN — `src/snn/network.py`

Shiu et al. 2024 (Nature) tüm-beyin LIF modeli, aynı parametrelerle:

| Parametre | Değer |
|---|---|
| Dinlenme / eşik potansiyeli | −52 mV / −45 mV |
| Membran / sinaps zaman sabiti | 20 ms / 5 ms |
| Refrakter süre, sinaptik gecikme | 2.2 ms, 1.8 ms (dolaylı kenarlarda 3.6 ms) |
| Sinaps başına ağırlık | 0.275 mV |

Her graf düğümü, gerçek sayıda nörondan oluşan bir **popülasyondur** (ör. `LC4_L` = 54 nöron). A → B kenarı, A'nın her nöronunu B'nin her nöronuna `W/N_A` ağırlıkla bağlar: A'nın tamamı ateşlediğinde her B nöronu grafın söylediği kadar sinaps girdisi alır.

**Kalibrasyon yapılmadı**, literatür parametreleriyle çalışıyor. Davranış testleri (`tests/test_snn.py`):
- LC4_L uyarılınca sadece **sol** DNp02/DNp04/GF ateşleniyor; sağ taraf ve direksiyon nöronları sessiz (izolasyon).
- LPLC2 → GF ateşliyor.
- LC10a hangi taraftaysa o taraftaki DNa02 ateşliyor.

## 2. Kodlayıcı — `LoomingEncoder`

Kamera görüntüsünden tehdit (kırmızı nesne) maskelenir. Sol ve sağ görüş alanı için ayrı ayrı:

| Nöron | Ne kodlar | Formül |
|---|---|---|
| `LC4_L/R` | Yaklaşma **hızı** (açısal genişleme, °/s) | `4 Hz × max(dθ/dt − 8°/s, 0)` |
| `LPLC2_L/R` | Yaklaşma **büyüklüğü** (açısal boyut, °), sadece büyürken | `2 Hz × max(θ − 20°, 0)` |

8°/s eşiği gerçek LC4'lerin sadece hızlı genişlemeye yanıt vermesini taklit eder. 0.4 m yarıçaplı, 1.2 m/s ile gelen top için bu eşik ~2.3 m mesafeye karşılık gelir. Büyüme hızı, piksel gürültüsünü azaltmak için son 0.1 s'lik pencereden hesaplanır.

## 3. Çözücü — `MotorDecoder`

| Rover komutu | Nöronlar | Biyolojik karşılık |
|---|---|---|
| Geri | DNp02 + DNp04 + GF + MDN | Geri yönlü kaçış / geri yürüme |
| İleri | BPN tipleri | İleri yürüme ("gaz pedalı") |
| Dönüş | (DNa01 + DNa02)_sol − _sağ | Aynı taraf aktif → o tarafa dön |

**Motor kalıcılığı:** Sinekte DN'ler VNC'deki motor programlarını tetikler; program, DN sustuğu anda bitmez. Bunu taklit etmek için her kanal anında yükselir ve ~0.5 s'de söner. Bu olmadan rover "kaç-dur-kaç" diye titriyordu: geri gidince göreli yaklaşma azalıyor → LC4 susuyor → rover duruyor → top yaklaşıyor.

## Bilinen sınırlar

- Tehdit sadece **renkle** algılanıyor (kırmızı top). Faz 3'te engebeli arazide optik akış tabanlı bir algıya geçmek gerekebilir.
- SNN gerçek zamandan ~7 kat yavaş (Brian2 `numpy` hedefi). 5 s'lik bir senaryo ~40 s sürüyor. Simülasyon adım adım ilerlediği için bu sonucu değiştirmiyor, sadece süreyi uzatıyor.
- Ağırlıkları tüm tip üyelerine eşit dağıtıyoruz (tip içi retinotopi yok). Tehdidin sol/sağ ayrımı için yeterli; daha ince yön bilgisi gerekirse nöron seviyesindeki bağlantılar kullanılmalı.
