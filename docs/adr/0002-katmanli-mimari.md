# 0002. Katmanlı mimari ve DN seviyesi sınır

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (L2–L3, L4 kol becerileri), Ömer (L0, L1 göz, L4 rover kontrolcüsü), Yusuf (L5)
- **Revizyon (2026-10-12, inceleme sonrası):** "Karar nerede verilir" bölümü eklendi (L1 karar vermez, L3 hakemlik yapmaz); nesne pozunun L1 → L4 akışı adıyla tanımlandı; VNC yuvası sürümleri tutarlı hale getirildi; L3 filtresi ve beyin motoru satırları düzeltildi.
- **Revizyon 2 (2026-10-12):** L1 kuralı "görevden bağımsız ve sürekli" olarak düzeltildi (monotonluk yalnızca büyüklük özelliklerinde); L3 kuralına normalizasyon, varsayılan mod eşiği ve ayrık DN popülasyonları eklendi; Synaptera okuma filtresi atfı düzeltildi (50 ms); mod listesi [0010](0010-noron-secimi-tohum-tipleri.md) ile hizalandı; sahiplik [0007](0007-ekip-ve-gorev-dagilimi.md) ile hizalandı.

## Bağlam

Mevcut sistem tek bir döngüden oluşuyor: `kamera → LoomingEncoder → ConnectomeSNN → MotorDecoder → teker`. Katmanlar arasında yazılı bir sözleşme yok, her bileşenin kaynağı (biyolojik mi, elle mi) kayıtlarda ayrılmıyor ve yeni davranışlar eklendikçe çözücü elle yazılmış kurallarla büyüyor.

Synaptera'dan iki mimari ders:
- **Eşikli ayrık karar** (MN9 > 10 Hz) çalıştı; **DN'lerden sürekli analog komut** okumak çalışmadı (DNp15 açık döngüde yön seçiciydi ama sabit tek taraflı taban aktivitesi yüzünden kapalı döngüde kullanılabilir bir direksiyon sinyali vermedi).
- Biyolojide DN'ler kasları doğrudan sürmez; VNC'deki motor programlarını **seçer**. Rover'ın tekerleği ve kolu sineğin bacaklarına benzemediği için doğal soyutlama sınırı **DN seviyesidir**.

## Karar

### Katmanlar

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ L5  DEĞERLENDİRME   görevler T1–T4 · kollar (gerçek/shuffled/bypass) · CKS · log │
└──────────────────────────────────────────────────────────────────────────────────┘
 L0 DÜNYA           L1 DUYU                L2 BEYİN ÇEKİRDEĞİ      L3 MOD SEÇİCİ           L4 MOTOR
 MuJoCo/MJX   ──►   göz → ommatidia  ──►   FAFB nöron seviyesi ──► DN hızları → mod   ──►  rover: kinematik
 rover + kol        → VPN hızları          alt ağ (Brian2 → JAX)   + parametre             kol: RL becerileri
 kamera, IMU,       propriosepsiyon  ──►   modüller                ("VNC yuvası")          (uzan/kavra/kaldır)
 odometri, temas    → AN hızları           tüm-beyin kahini        sabit kural, histerezis
       ▲                                                                                         │
       └──────────────────────────────────── fizik adımı ◄───────────────────────────────────────┘
```

| Katman | Görev | Kaynak etiketi | Sahip |
|---|---|---|---|
| **L0 Dünya** | Fizik, robotlar, arazi, sensörler | — | Ömer |
| **L1 Duyu** | Sensör verisini görsel projeksiyon nöronlarının (VPN: LC4, LPLC2, LC10a, LC11…) ve yükselen nöronların (AN) Poisson hızlarına çevirir. **Eşiksiz, sürekli özellik üretir; karar vermez.** | HAND-MADE veya EXTERNAL (FlyVis) | Ömer (göz, özellikler), Mert (FlyVis köprüsü, AN kodlayıcı) |
| **L2 Beyin** | Connectome alt ağı; çıktısı DN popülasyon hızları. **Görev kararları ve davranışlar arası öncelik burada oluşur.** | BRAIN | Mert |
| **L3 Mod seçici** | DN hızları → `(mod, parametreler)`; ön-kayıtta dondurulmuş **sabit kural** (filtre, argmax, histerezis, en kısa süre). Öncelik tablosu yok. "VNC yuvası": v1 elle, v2 öğrenilmiş dekoder, v3 BANC türevi vekil model | HAND-MADE → TRAINED | Mert (Ömer hakem) |
| **L4 Motor** | Mod komutunu teker ve eklem torklarına çevirir | HAND-MADE / TRAINED | Ömer (rover kontrolcüsü), Mert (kol RL becerileri) |
| **L5 Değerlendirme** | Görevler, kontrol kolları, CKS, kayıt, doğrulama | — | Yusuf |

### Bilgi güvenlik duvarı

Her katman yalnızca bir üstündeki ve bir altındaki katmanla, aşağıdaki sözleşmeler üzerinden konuşur.

- **L4 politikaları kamera görüntüsünü, tehdit bilgisini veya görev kimliğini göremez.** Bunları yalnızca L3'ün mod komutu üzerinden alır.
- L4'ün alabildiği girdiler: kendi propriosepsiyonu (eklem açıları, teker hızları, IMU) ve L3'ün verdiği parametreler (örneğin hedef yönü, hedef nesne pozu).
- Kolun kavrama için ihtiyaç duyduğu **nesne pozu** L1'de üretilen, **HAND-MADE** etiketli bir mühendislik algısıdır. Bu, "yalnızca komşu katman" kuralının **tek istisnasıdır** ve şöyle akar: L1 her aday nesne için bir poz üretir → L3 bunları değiştirmeden taşır → L3, L2'nin seçtiği nesnenin pozunu (ör. sol/sağ hedef popülasyonundan hangisi baskınsa) `ModeCommand.params` içinde L4'e verir. **Hangi nesneye ve ne zaman uzanılacağına L2 (beyin) karar verir;** L3 yalnızca bu seçimi uygular. Poz alanı kayıtta `HAND-MADE` olarak işaretlenir.

Bu duvar olmazsa ML her işi kendisi öğrenir ve connectome'un katkısı ölçülemez hale gelir.

### Karar nerede verilir

CKS'nin anlamlı olması için görev kararı **yalnızca L2'de** verilmelidir. Komşu katmanlar kararı önceden veremez ya da sonradan düzeltemez.

**L1 kuralı: karar vermez.**
- L1 çıktıları uyaranın **görevden bağımsız ve sürekli** fonksiyonlarıdır. "Tehdit var/yok" gibi görev kararını veren eşikler L1'de **yasaktır**.
- **Büyüklük özellikleri** (açısal genişleme hızı, açısal boyut) uyaran büyüklüğüne göre **monoton** olmalıdır. **Seçicilik özellikleri** monoton olmak zorunda değildir: LC10a ve LC11 gibi küçük hedef nöronları belirli bir hedef boyutunda tepe yapar, görüş alanındaki konum ayar eğrisi (tuning curve) biçimindedir. Bu eğrilerin biçimi literatürden alınır, kaynağıyla L1 config'ine yazılır ve görev davranışına bakılarak ayarlanmaz.
- İzin verilenler: fiziksel doygunluk (`max_rate`), sensör gürültüsünü bastıran ve görevden bağımsız sabit bir taban (ör. piksel gürültüsü), birim dönüşümleri. Her biri L1 config'inde gerekçesiyle yazılır.
- Nesne tespiti (ör. renk maskesi) bir mühendislik algısıdır ve `HAND-MADE` etiketlidir; ama tespitin çıktısı karar değil, sürekli bir özellik olmalıdır.
- Mevcut `LoomingEncoder`'daki 8°/s ve 20° eşikleri bu kurala aykırıdır; yeni L1'de kaldırılır (v0'da tarihsel kayıt olarak kalır).

**L3 kuralı: hakemlik yapmaz.**
- L3'ün kuralı ön-kayıtta dondurulur ve üç kolda aynıdır: her mod için önceden tanımlı bir DN popülasyonu → alçak geçiren filtre → normalizasyon → en yüksek skorlu mod seçilir (argmax) → histerezis ve en kısa mod süresi. Hiçbir mod skoru diğerinden ek bir katsayı almaz.
- **Normalizasyon gizli bir öncelik tablosudur;** bu yüzden sabittir: her mod skoru, o popülasyonun nöron başına ortalama hızının, **o kolun kendi** uyaransız taban kalibrasyonundaki ortalama ve standart sapmasına göre z-skorudur. Popülasyon büyüklüğü, taban hızı ve tepe hızı farkları böylece aynı ölçeğe gelir; başka bir ağırlık kullanılmaz.
- **Varsayılan mod:** Hiçbir mod skoru ön-kayıtlı `z_min` eşiğini aşmıyorsa görev başına ön-kayıtta tanımlı varsayılan mod uygulanır (T1/T1b: BEKLE; T2–T4: KEŞFET). `z_min` ve varsayılan mod üç kolda aynıdır ve `HAND-MADE` olarak etiketlenir.
- **Ayrık popülasyonlar:** Bir DN tipi en fazla bir modun popülasyonunda yer alır. Mod → DN eşlemesi [0010](0010-noron-secimi-tohum-tipleri.md)'da tanımlıdır; değişikliği ADR gerektirir.
- Modlar arası **öncelik tablosu** (ör. KAÇ > DUR > UZAN) L3'te **kullanılmaz**. Öncelik varsa L2'den, yani DN popülasyonları arasındaki baskılamadan ve aktivite farkından gelmelidir.
- Elle yazılmış bir öncelik tablosu yalnızca ayrı ve etiketli bir karşılaştırma kolu (`L3-öncelik`, HAND-MADE) olarak çalıştırılabilir; ana sonucun yerine geçmez.
- Sürekli parametreler (yön, hız) yalnızca ayna simetrisi testini ve taban kalibrasyonunu geçmiş DN çiftlerinden, mod içi parametre olarak okunur ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)).

**Denetim:** L1 için birim testi, referans uyaran taramasında çıktının sürekli olduğunu, büyüklük özelliklerinin monoton olduğunu ve seçicilik özelliklerinin config'teki ayar eğrisiyle eşleştiğini doğrular. L3 kural dosyası ön-kayıt commit'inden sonra değişirse değerlendirme düzeneği sınav koşusunu reddeder ([0006](0006-repo-kurallari.md)).

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
    mode: Literal["KAÇ", "YAKLAŞ", "DUR", "UZAN", "KEŞFET", "BEKLE"]   # KEŞFET/BEKLE: varsayılan modlar
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
| L3 okuma filtresi | 1. dereceden alçak geçiren; τ ön-kayıtta sabitlenir (başlangıç önerisi 50 ms; Synaptera'nın VNC köprüsündeki okuma filtresiyle aynı: `READOUT_TAU = 0.050`) |
| Beyin gecikmesi | Bir kontrol adımı (20 ms): adım *k*'deki L1 girdisi, en erken adım *k+1*'deki motor komutunu etkiler. Gecikme üç kolda aynıdır. |

### Değiştirilebilir parçalar

| Yuva | v1 | v2 | v3 (opsiyonel) |
|---|---|---|---|
| Görsel ön işleme (L1) | Özellik kodlayıcı (loom, küçük hedef) | FlyVis | — |
| VNC yuvası (L3) | Elle yazılmış sabit kural (argmax + histerezis) | ML ile öğrenilmiş dekoder (DAgger) | Hat B'den BANC türevi vekil model |
| Kol (L4) | IK + elle yörünge | RL beceri kütüphanesi | — |

Sözleşmeler değişmediği sürece yuvanın içi mimariyi yeniden yazmadan değiştirilebilir. L3'ün v2 veya v3 sürümü kullanıldığında, aynı eğitim prosedürü ve bütçe gerçek, shuffled ve bypass kollarının her birine ayrı ayrı uygulanır ([0005](0005-ml-stratejisi.md)).

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Sınırı VNC / motor nöron seviyesine indirmek | VNC çıktısı sinek bacak kaslarıdır; rover tekerleğine eşlemek için önce sinek gövdesini simüle edip sonra çevirmek gerekir. Bu, Hat B'de araştırma olarak yapılır ([0008](0008-yol-haritasi.md)). |
| DN'lerden sürekli komut okumak (DNp15 tarzı) | Synaptera'da başarısız oldu. Sürekli parametreler (yön, hız) yalnızca simetri testini geçmiş DN çiftlerinden, mod içi parametre olarak okunur. |
| Katmansız, tek döngü (mevcut yapı) | Kaynak ayrımı ve modül değiştirme imkânsızlaşıyor. |
| Hakemliği L3'te öncelik tablosuyla yapmak | T4'ün ana sorusu ("hakemliği connectome mu yapıyor?") cevaplanamaz hale gelir; yalnızca etiketli karşılaştırma kolu olarak tutulur. |
| L1'de eşikli tehdit/hedef tespiti | Kararı beyinden önce verir; bypass görevi kolayca çözer ve CKS ölçtüğünü sandığı şeyi ölçmez. |

## Sonuçlar

**Olumlu**
- Her bileşenin kaynağı ölçülebilir; CKS hesaplanabilir.
- Ekip katmanlara göre paralel çalışabilir; sözleşmeler entegrasyon riskini azaltır.
- Hat B'nin çıktısı (VNC vekili) ileride yuvaya mimari değişikliği gerektirmeden takılabilir.

**Olumsuz / maliyet**
- Sözleşme ve kayıt altyapısı P0'da ek iş getirir.
- Bilgi güvenlik duvarı, ML performansını bilerek sınırlar. Bu bir tasarım tercihidir.
- Eşiksiz L1 ve hakemliksiz L3 ile ilk görevlerde başarı oranı düşebilir. Bu, sonucun beyne atfedilebilmesinin bedelidir; başarıyı artırmak için L1 veya L3'e karar eklemek yerine sorun raporlanır.

## İlgili
- [0001 Vizyon](0001-vizyon-ve-basari-olcutu.md) · [0003 Simülasyon](0003-simulasyon-ortami.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md)
