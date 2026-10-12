# 0002. Katmanlı mimari ve DN seviyesi sınır

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (L2–L3), Ömer (L0, L1, L4), Yusuf (L5)

## Bağlam

Mevcut sistem tek bir döngüden oluşuyor: `kamera → LoomingEncoder → ConnectomeSNN → MotorDecoder → teker`. Katmanlar arasında yazılı bir sözleşme yok, her bileşenin kaynağı (biyolojik mi, elle mi) kayıtlarda ayrılmıyor ve yeni davranışlar eklendikçe çözücü elle yazılmış kurallarla büyüyor.

Synaptera'dan iki mimari ders:
- **Eşikli ayrık karar** (MN9 > 10 Hz) çalıştı; **DN'lerden sürekli analog komut** okumak (DNp15 direksiyonu) çalışmadı.
- Biyolojide DN'ler kasları doğrudan sürmez; VNC'deki motor programlarını **seçer**. Rover'ın tekerleği ve kolu sineğin bacaklarına benzemediği için doğal soyutlama sınırı **DN seviyesidir**.

## Karar

### Katmanlar

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ L5  DEĞERLENDİRME   görevler T1–T4 · kollar (gerçek/shuffled/bypass) · CKS · log │
└──────────────────────────────────────────────────────────────────────────────────┘
 L0 DÜNYA           L1 DUYU                L2 BEYİN ÇEKİRDEĞİ      L3 MOD SEÇİCİ           L4 MOTOR
 MuJoCo/MJX   ──►   göz → ommatidia  ──►   FAFB nöron seviyesi ──► DN hızları → mod   ──►  rover: kinematik
 rover + kol        → VPN hızları          alt ağ (JAX, GPU)       + parametre             kol: RL becerileri
 kamera, IMU,       propriosepsiyon  ──►   modüller                ("VNC yuvası")          (uzan/kavra/kaldır)
 odometri, temas    → AN hızları           tüm-beyin kahini        histerezis, hakemlik
       ▲                                                                                         │
       └──────────────────────────────────── fizik adımı ◄───────────────────────────────────────┘
```

| Katman | Görev | Kaynak etiketi | Sahip |
|---|---|---|---|
| **L0 Dünya** | Fizik, robotlar, arazi, sensörler | — | Ömer |
| **L1 Duyu** | Sensör verisini görsel projeksiyon nöronlarının (VPN: LC4, LPLC2, LC10a, LC11…) ve yükselen nöronların (AN) Poisson hızlarına çevirir | HAND-MADE veya EXTERNAL (FlyVis) | Ömer (göz, özellikler), Mert (FlyVis köprüsü, AN kodlayıcı) |
| **L2 Beyin** | Connectome alt ağı; çıktısı DN popülasyon hızları | BRAIN | Mert |
| **L3 Mod seçici** | DN hızları → `(mod, parametreler)`; eşik, histerezis, kalıcılık, hakemlik. "VNC yuvası": v1 elle, v2 BANC türevi vekil model | HAND-MADE → TRAINED | Mert (Ömer hakem) |
| **L4 Motor** | Mod komutunu teker ve eklem torklarına çevirir | HAND-MADE / TRAINED | Ömer |
| **L5 Değerlendirme** | Görevler, kontrol kolları, CKS, kayıt, doğrulama | — | Yusuf |

### Bilgi güvenlik duvarı

Her katman yalnızca bir üstündeki ve bir altındaki katmanla, aşağıdaki sözleşmeler üzerinden konuşur.

- **L4 politikaları kamera görüntüsünü, tehdit bilgisini veya görev kimliğini göremez.** Bunları yalnızca L3'ün mod komutu üzerinden alır.
- L4'ün alabildiği girdiler: kendi propriosepsiyonu (eklem açıları, teker hızları, IMU) ve L3'ün verdiği parametreler (örneğin hedef yönü, hedef nesne pozu).
- Kolun kavrama için ihtiyaç duyduğu **nesne pozu** L1'de üretilen, **HAND-MADE** etiketli bir mühendislik algısıdır. Hangi nesneye ve ne zaman uzanılacağına L3 (yani beyin) karar verir.

Bu duvar olmazsa ML her işi kendisi öğrenir ve connectome'un katkısı ölçülemez hale gelir.

### Veri sözleşmeleri (taslak)

```python
@dataclass
class Observation:          # L0 → L1
    eye_left: np.ndarray    # ham kamera
    eye_right: np.ndarray
    imu: np.ndarray         # açısal hız, ivme
    wheel_speed: np.ndarray
    arm_q: np.ndarray       # eklem açıları
    contact: dict           # kıskaç / gövde temasları

@dataclass
class SensoryDrive:         # L1 → L2
    rates_hz: dict[str, float]        # nöron grubu → Hz (ör. "LC4_L")
    source: dict[str, str]            # grup → HAND-MADE | EXTERNAL

@dataclass
class DNActivity:           # L2 → L3
    rates_hz: dict[str, np.ndarray]   # DN tipi → nöron başına hız
    t: float

@dataclass
class ModeCommand:          # L3 → L4
    mode: Literal["KAÇ", "YAKLAŞ", "DUR", "KEŞFET", "UZAN", "KAVRA", "BEKLE"]
    params: dict[str, float]          # ör. {"yön": -0.4, "hız": 0.6}
    source: str                       # HAND-MADE | TRAINED

@dataclass
class MotorCommand:         # L4 → L0
    wheel_torque: np.ndarray
    arm_torque: np.ndarray
    gripper: float
    source: str
```

Her alan kayıt dosyasına ayrı ayrı yazılır. Kayıt formatını Yusuf belirler ([0006](0006-repo-kurallari.md)).

### Zamanlama

| Döngü | Adım |
|---|---|
| Fizik (L0) | 2 ms |
| Kontrol döngüsü (L1 → L4) | 20 ms (10 fizik alt adımı) |
| Beyin içi (L2) | dt = 0,1 ms; her kontrol adımında 20 ms simüle edilir |
| L3 okuma filtresi | 1. dereceden alçak geçiren, τ = 50 ms (Synaptera ile aynı mertebe) |

### Değiştirilebilir parçalar

| Yuva | v1 | v2 | v3 (opsiyonel) |
|---|---|---|---|
| Görsel ön işleme (L1) | Özellik kodlayıcı (loom, küçük hedef) | FlyVis | — |
| VNC yuvası (L3) | Elle yazılmış mod seçici | ML ile öğrenilmiş dekoder (DAgger) | Hat B'den BANC türevi vekil model |
| Kol (L4) | IK + elle yörünge | RL beceri kütüphanesi | — |

Sözleşmeler değişmediği sürece yuvanın içi mimariyi yeniden yazmadan değiştirilebilir.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Sınırı VNC / motor nöron seviyesine indirmek | VNC çıktısı sinek bacak kaslarıdır; rover tekerleğine eşlemek için önce sinek gövdesini simüle edip sonra çevirmek gerekir. Bu, Hat B'de araştırma olarak yapılır ([0008](0008-yol-haritasi.md)). |
| DN'lerden sürekli komut okumak (DNp15 tarzı) | Synaptera'da başarısız oldu. Sürekli parametreler (yön, hız) yalnızca simetri testini geçmiş DN çiftlerinden, mod içi parametre olarak okunur. |
| Katmansız, tek döngü (mevcut yapı) | Kaynak ayrımı ve modül değiştirme imkânsızlaşıyor. |

## Sonuçlar

**Olumlu**
- Her bileşenin kaynağı ölçülebilir; CKS hesaplanabilir.
- Ekip katmanlara göre paralel çalışabilir; sözleşmeler entegrasyon riskini azaltır.
- Hat B'nin çıktısı (VNC vekili) ileride yuvaya mimari değişikliği gerektirmeden takılabilir.

**Olumsuz / maliyet**
- Sözleşme ve kayıt altyapısı P0'da ek iş getirir.
- Bilgi güvenlik duvarı, ML performansını bilerek sınırlar. Bu bir tasarım tercihidir.

## İlgili
- [0001 Vizyon](0001-vizyon-ve-basari-olcutu.md) · [0003 Simülasyon](0003-simulasyon-ortami.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md)
