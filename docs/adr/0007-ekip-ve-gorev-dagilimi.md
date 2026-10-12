# 0007. Ekip ve görev dağılımı

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip (Mert, Ömer, Yusuf)

## Bağlam

Ekip üç kişiden oluşuyor:

| Kişi | Uzmanlık |
|---|---|
| **Mert** | Data scientist & ML engineer |
| **Ömer** | Rover uzmanı, simülasyon & yazılım mühendisi |
| **Yusuf** | Siber güvenlik & full stack mühendisi |

Üç kişilik bir ekipte riskler: tek bir kişiye bağımlı katmanlar, entegrasyonun sona kalması, ve modülü yazan kişinin kendi sonucunu değerlendirmesi (çıkar çatışması).

## Karar

### Rol tanımları

| Kişi | Rol | Ana sorumluluk |
|---|---|---|
| **Mert** | **Beyin ve beyin-ML sahibi** | Connectome verisi ve graf üretici (L2), JAX spiking motoru, modül kabul testleri, L3 mod seçici, beyne dokunan tüm ML (dekoder, ince ayar, VNC vekili, **bypass kolu**), BANC analizi |
| **Ömer** | **Gövde, dünya ve gövde-ML sahibi** | MuJoCo dünyası (L0), rover + kol modelleri, sinek gözü ve özellik kodlayıcıları (L1), L4 kontrolcüleri, kol RL becerileri, Gym ortamları ve görev sahneleri, Hat B'de NeuroMechFly |
| **Yusuf** | **Platform, değerlendirme ve dürüstlük sahibi (tarafsız değerlendirici)** | Repo yapısı, CI/CD, güvenlik, CUDA sunucusu, deney takibi, kayıt şeması, değerlendirme düzeneği (L5), CKS, `verify.py`, dashboard ve beyin aktivitesi görüntüleyici, ön-kayıt süreci, entegrasyon, yayın hazırlığı |

Yusuf'un hiçbir beyin veya ML modülünün sahibi olmaması **bilinçli bir tercihtir**: CKS'yi hesaplayan ve sınav tohumlarını açan kişi, sonucu iyi çıkması gereken modülü yazan kişi olmamalıdır.

### Katman sahipliği

**S** = sahip (yazar, sorumludur) · **H** = hakem (PR onayı zorunlu) · **D** = destek

| Alan | Mert | Ömer | Yusuf |
|---|---|---|---|
| L0 Dünya, robotlar, arazi | | **S** | H |
| L1 Göz, özellik kodlayıcılar | D | **S** | |
| L1 FlyVis köprüsü, AN kodlayıcı | **S** | H | |
| L2 Graf üretici, veri | **S** | | H |
| L2 JAX motoru | **S** | | H (eşdeğerlik testi düzeneği) |
| L2 Modül kabul testleri | **S** | | H |
| L3 Mod seçici (VNC yuvası) | **S** | H | |
| L4 Rover kontrolcüsü | | **S** | |
| L4 Kol RL becerileri | D (RL algoritmaları) | **S** | |
| Beyin-ML (dekoder, ince ayar, bypass) | **S** | | H (eşit bütçe denetimi) |
| L5 Değerlendirme, CKS, kayıtlar | D | D | **S** |
| CI/CD, güvenlik, sunucu, MLflow | | | **S** |
| Dashboard, aktivite görüntüleyici | D | D | **S** |
| Ön-kayıtlar | yazar (kendi modülleri) | yazar (kendi görevleri) | **S** (süreç ve onay) |
| Hat B (BANC + NeuroMechFly) | **S** (veri, beyin+VNC) | **S** (sinek gövdesi) | H |

### Çapraz hakemlik

- Mert'in L2–L3 PR'larını **Yusuf** (veri bütünlüğü, kurallar) veya **Ömer** (arayüz uyumu) inceler.
- Ömer'in L0–L1–L4 PR'larını **Mert** (sensör → nöron arayüzü) veya **Yusuf** inceler.
- Yusuf'un platform ve değerlendirme PR'larını **Mert** ve **Ömer** dönüşümlü inceler.
- Kimse kendi katmanındaki PR'ı tek başına onaylayamaz.

### Yedeklilik (bus factor)

| Alan | Birincil | Yedek |
|---|---|---|
| Beyin (L2–L3) | Mert | Yusuf |
| Dünya ve kol (L0, L1, L4) | Ömer | Mert |
| Platform ve değerlendirme (L5, CI) | Yusuf | Ömer |

Yedek kişi, ilgili alanın README'sini okuyup duman testini kendi başına çalıştırabilmelidir. Bu her aşama sonunda bir kez denenir.

### Çalışma ritmi

| Ne | Ne zaman | Sorumlu |
|---|---|---|
| **Entegrasyon demosu:** `main`'deki güncel sistem bir görevde canlı koşturulur | Haftada bir | Yusuf |
| Kısa senkron (engeller, bağımlılıklar) | Haftada iki, 15 dk | Herkes |
| Bilim toplantısı: ön-kayıtlar, sonuçlar, CKS | İki haftada bir | Yusuf yönetir |
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
| Herkesin her şeye dokunması | Üç kişide sahipsiz alanlar ve çakışmalar oluşur |
| ML'in tamamını Mert'e vermek | Kol RL'i robot modeline, ödül tasarımına ve simülasyona sıkı bağlı; Ömer'in alanında daha verimli |
| Değerlendirmeyi modül sahiplerine bırakmak | Çıkar çatışması; Synaptera'nın etiketleme ve ön-kayıt disiplini tarafsız bir sahip gerektiriyor |

## Sonuçlar

**Olumlu**
- Her katmanın tek bir sahibi ve bir hakemi var.
- Değerlendirme tarafsız; CKS'ye güvenilebilir.
- Yusuf'un güvenlik ve full stack yetkinliği, projenin en zayıf iki yanını (tekrarlanabilirlik ve altyapı) kapatıyor.

**Olumsuz / maliyet**
- Mert'in yükü en fazla. P2–P3'te Hat B başlayınca Mert'in Hat B payı sınırlı tutulmalı (haftada en fazla 1 gün); gerekirse Hat B ertelenir.
- Yusuf'un işi P0'da yoğun, P2'den sonra daha çok entegrasyon ve değerlendirme. Bu dönemde Yusuf beyin tarafına yedek olarak hazırlanır.

## İlgili
- [0008 Yol haritası](0008-yol-haritasi.md) · [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md) · [gorevler/yusuf.md](gorevler/yusuf.md)
