# 0007. Ekip ve görev dağılımı

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip (Mert, Ömer, Yusuf)
- **Revizyon (2026-10-12, inceleme sonrası):** Mert'in L2 sorumluluğu "beyin motorları (derlenmiş Brian2, JAX)" ve shuffled üretici olarak güncellendi.
- **Revizyon 2 (2026-10-12):** Görev dağılımı değişti: Ömer'in ana işi Hat B (BANC + NeuroMechFly) oldu ve L0 dünyasını sürdürüyor; Mert FAFB beyin çekirdeğinin ve **tüm ML'in** sahibi oldu (kol RL becerileri dahil); tarafsızlık için shuffled üretici ve L1 karar-vermezlik testleri Yusuf'a geçti. Hat B artık yan hat değil, ana hatla paralel ikinci hattır.

## Bağlam

Ekip üç kişiden oluşuyor:

| Kişi | Uzmanlık |
|---|---|
| **Mert** | Data scientist & ML engineer |
| **Ömer** | Rover uzmanı, simülasyon & yazılım mühendisi |
| **Yusuf** | Siber güvenlik & full stack mühendisi |

İlk dağılımda Hat B (BANC) haftada en fazla 1 gün ayrılan bir yan hattı ve kol RL becerileri Ömer'deydi. Ekip, Ömer'in BANC hattına, Mert'in FAFB + ML tarafına odaklanmasına karar verdi. Bu, Hat B'yi tam zamanlı bir hatta çevirir ve Mert'in yükünü artırır. Yükü dengelemek için:
- tarafsızlıkla zaten ilişkili işler (shuffled üretici, L1 testleri) Yusuf'a geçer,
- JAX motoru kritik yoldan tamamen çıkar ([0005](0005-ml-stratejisi.md): ince ayarda önce evrim stratejileri),
- Ömer L0 dünyasını sürdürür, çünkü Hat B'deki NeuroMechFly de aynı motorda (MuJoCo) çalışır.

## Karar

### Rol tanımları

| Kişi | Rol | Ana sorumluluk |
|---|---|---|
| **Mert** | **FAFB beyin çekirdeği ve ML sahibi** | Connectome verisi ve nöron seviyesi graf üretici (L2), derlenmiş Brian2 motoru, tüm-beyin kahini, modül kabul testleri, L3 mod seçici, **tüm ML**: L4 kol RL becerileri, L3 öğrenilmiş dekoder, L2 ince ayarı, bypass kolu, VNC vekilinin eğitimi; ML model seçim protokolü ([0009](0009-ml-model-secim-protokolu.md)) |
| **Ömer** | **Hat B ve dünya sahibi** | **Hat B:** BANC verisi, DN'lerin VNC hedefleri, AN seçimi, BANC beyin+VNC modeli, NeuroMechFly sinek gövdesi, GO/NO-GO deneyi, VNC vekili için veri seti. **Dünya:** MuJoCo L0 (rover + kol MJCF, sensörler, arazi), sinek gözü (L1), T1–T4 sahneleri, L4 rover kontrolcüsü |
| **Yusuf** | **Platform, değerlendirme ve dürüstlük sahibi (tarafsız değerlendirici)** | Repo yapısı, CI/CD, güvenlik, CUDA sunucusu, MLflow, kayıt şeması, değerlendirme düzeneği (L5), CKS, `verify.py`, **shuffled graf üretici**, **L1 karar-vermezlik testleri (A9)**, JAX–Brian2 eşdeğerlik düzeneği, dashboard ve beyin aktivitesi görüntüleyici, ön-kayıt süreci, entegrasyon, yayın hazırlığı |

Yusuf'un hiçbir beyin veya ML modülünün sahibi olmaması **bilinçli bir tercihtir**: CKS'yi hesaplayan, sıfır hipotezini (shuffled graf) üreten ve sınav tohumlarını açan kişi, sonucu iyi çıkması gereken modülü yazan kişi olmamalıdır.

### Katman sahipliği

**S** = sahip (yazar, sorumludur) · **H** = hakem (PR onayı zorunlu) · **D** = destek

| Alan | Mert | Ömer | Yusuf |
|---|---|---|---|
| L0 Dünya, robotlar, arazi, görev sahneleri | | **S** | H |
| L1 Göz (ommatidia), özellik kodlayıcılar | H | **S** | H (A9 testleri) |
| L1 FlyVis köprüsü | **S** | H | |
| L1 AN kodlayıcı | **S** | D (BANC'tan AN listesi) | |
| L2 Graf üretici, veri, modüller | **S** | | H |
| L2 Shuffled üretici | H | | **S** |
| L2 Beyin motorları (Brian2; JAX opsiyonel) | **S** | | H (eşdeğerlik düzeneği) |
| L2 Modül kabul testleri | **S** | | H |
| L3 Mod seçici (VNC yuvası) | **S** | H | |
| L4 Rover kontrolcüsü | | **S** | |
| L4 Kol RL becerileri | **S** | H (robot modeli, ödül) | |
| Beyin-ML (dekoder, ince ayar, bypass) | **S** | | H (eşit bütçe) |
| VNC vekili | **S** (model) | **S** (veri) | H |
| Hat B (BANC + NeuroMechFly) | D (FAFB ↔ BANC tip eşlemesi) | **S** | H |
| L5 Değerlendirme, CKS, kayıtlar | D | D | **S** |
| CI/CD, güvenlik, sunucu, MLflow | | | **S** |
| Dashboard, aktivite görüntüleyici | D | D | **S** |
| Ön-kayıtlar | yazar (modüller, ML) | yazar (görevler, Hat B) | **S** (süreç ve onay) |

### İki hat arasındaki sözleşmeler

Hat B ile ana hat iki noktada buluşur; ikisi de **P0'da** yazılı hale getirilir:

| Sözleşme | Üreten | Tüketen | İçerik |
|---|---|---|---|
| **AN listesi** | Ömer | Mert (AN kodlayıcı) | Yürüme durumu ve temas taşıyan AN tipleri; FAFB'deki karşılıkları; rover sensörlerine eşleme önerisi |
| **VNC vekili veri şeması** | Ömer | Mert (vekil model) | Zaman adımı, DN listesi (FAFB tip adlarıyla), gövde kinematiği alanları (v, ω, ön bacak uç noktası), dosya formatı, tohum ve kaynak etiketi |

### Çapraz hakemlik

- Mert'in L2–L3 ve ML PR'larını **Yusuf** (veri bütünlüğü, eşit bütçe, kurallar) veya **Ömer** (ortam ve robot arayüzü) inceler.
- Ömer'in L0–L1–L4 ve Hat B PR'larını **Mert** (sensör → nöron arayüzü, FAFB ↔ BANC eşlemesi) veya **Yusuf** inceler.
- Yusuf'un platform, değerlendirme ve shuffled üretici PR'larını **Mert** ve **Ömer** dönüşümlü inceler.
- Kimse kendi katmanındaki PR'ı tek başına onaylayamaz.

### Yedeklilik (bus factor)

| Alan | Birincil | Yedek |
|---|---|---|
| FAFB beyin çekirdeği (L2–L3) | Mert | Yusuf |
| ML (eğitim hatları) | Mert | Ömer |
| Dünya (L0, L1 göz, L4 rover) | Ömer | Mert |
| Hat B | Ömer | Mert |
| Platform ve değerlendirme (L5, CI) | Yusuf | Ömer |

Yedek kişi, ilgili alanın README'sini okuyup duman testini kendi başına çalıştırabilmelidir. Bu her aşama sonunda bir kez denenir.

### Çalışma ritmi

| Ne | Ne zaman | Sorumlu |
|---|---|---|
| **Entegrasyon demosu:** `main`'deki güncel sistem bir görevde canlı koşturulur | Haftada bir | Yusuf |
| Kısa senkron (engeller, bağımlılıklar, iki hat arasındaki sözleşmeler) | Haftada iki, 15 dk | Herkes |
| Bilim toplantısı: ön-kayıtlar, sonuçlar, CKS, Hat B ilerlemesi | İki haftada bir | Yusuf yönetir |
| Aşama sonu raporu (`docs/reports/`), olumsuz bulgular dahil | Her aşama sonu | Yusuf derler, herkes yazar |
| ADR incelemesi | İhtiyaç oldukça; 48 saat inceleme süresi | Öneren |

### Karar alma

- Katman içi kararlar: katman sahibi verir.
- Katmanlar arası sözleşme değişikliği veya yeni ADR: **en az iki kişinin onayı**.
- Anlaşmazlık: kısa bir ADR taslağı yazılır, seçenekler ve kanıtlar yan yana konur, bilim toplantısında karara bağlanır.

### Mevcut düzenden geçiş

- README ve `.agents/AGENTS.md`'deki beş kişilik branch listesi (`yusuf`, `mert`, `batikan`, `mirac`, `omer`) bu ADR kabul edilince üç kişilik ekibe ve [0006](0006-repo-kurallari.md)'daki konu bazlı branch düzenine göre güncellenir.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Hat B'yi yan hat olarak tutmak (ilk dağılım) | Ekip Ömer'in BANC'a odaklanmasına karar verdi; yarı zamanlı bir hat GO/NO-GO'ya hiç ulaşmayabilirdi |
| Kol RL'ini Ömer'de bırakmak | Ömer'in ana işi Hat B; ML'in tek elde toplanması model seçim protokolünün tutarlı uygulanmasını da kolaylaştırır |
| Shuffled üreticiyi Mert'te bırakmak | Sıfır hipotezini, sonucu iyi çıkması gereken modülün sahibi üretmemeli; Mert'in yükü de azalır |
| Değerlendirmeyi modül sahiplerine bırakmak | Çıkar çatışması; tarafsız bir sahip gerekiyor |

## Sonuçlar

**Olumlu**
- Hat B gerçekten yürütülebilir hale gelir; GO/NO-GO kararı H8'de verilebilir ([0008](0008-yol-haritasi.md)).
- Tüm ML tek bir protokolle ([0009](0009-ml-model-secim-protokolu.md)) ve tek bir sahiple yürür.
- Sıfır hipotezi ve L1 testleri tarafsız kişide.

**Olumsuz / maliyet**
- **Mert'in yükü en fazla.** Önlemler: JAX motoru kritik yolda değil; kol becerileri beyinden bağımsız olduğu için boşluklarda ilerletilebilir; gerekirse P4'teki ince ayar kapsamı daraltılır.
- **Ömer iki işi taşıyor** (Hat B + dünya). Dünya işinin yoğun kısmı P0'dadır; P1'den sonra Ömer'in zamanının büyük kısmı Hat B'ye ayrılır. Görev sahneleri (T1b–T4) için gerekirse Yusuf destek verir.

## İlgili
- [0008 Yol haritası](0008-yol-haritasi.md) · [0009 Model seçim protokolü](0009-ml-model-secim-protokolu.md) · [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md) · [gorevler/yusuf.md](gorevler/yusuf.md)
