# 0005. ML stratejisi: ne eğitilir, ne eğitilmez

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (beyne dokunan ML), Ömer (gövdeye dokunan ML); hakem: Yusuf

## Bağlam

Vizyon ML'e iki rol veriyor: kol ve rover hareketini öğrenmek, ve uzun vadede connectome'un kendisini iyileştirmek. Riskler:
- Synaptera'da DN'lerden eğitilen ridge okuma başarısız oldu: dönüş için çapraz doğrulanmış R² negatif, DN özelliklerinin çoğu sessiz, kapalı döngüde dağılım kayması (covariate shift) ve **bypass kolu gerçek beyin kolu kadar iyi**.
- ML'e çok fazla serbestlik verilirse connectome süs olarak kalır ve CKS anlamsızlaşır.

## Karar

### Sahiplik kuralı

- **Beyne dokunan ML** (L2–L3: ince ayar, öğrenilmiş dekoder, VNC vekili, bypass) → **Mert**
- **Gövdeye dokunan ML** (L4: kol becerileri, hareket kontrolcüsü) → **Ömer**

### Modeller

| # | Model | Katman | Yöntem | Öğrendiği | Etiket | Sahip | Aşama |
|---|---|---|---|---|---|---|---|
| 1 | **Kol becerileri** (uzan, kavra, kaldır, bırak) | L4 | PPO / SAC, MJX'te paralel, durum tabanlı, domain randomization | Hedef poz + propriosepsiyon → eklem torkları | TRAINED | Ömer | P2 |
| 2 | **Rover hareket kontrolcüsü** | L4 | PID → gerekirse RL | (v, ω) → teker torku; eğimde kayma telafisi | HAND-MADE / TRAINED | Ömer | P1–P4 |
| 3 | **Öğrenilmiş dekoder** (VNC yuvası v2) | L3 | DAgger veya RL (ridge ile davranış klonlaması değil) | DN aktivitesi → mod + parametre | TRAINED | Mert | P3 |
| 4 | **Connectome ince ayarı** | L2 | Surrogate-gradient veya evrim stratejileri | **Yalnızca hücre tipi başına kazanç ve eşik** (birkaç yüz parametre) | TRAINED (BRAIN topolojisi) | Mert | P4 |
| 5 | **VNC vekili** (Hat B) | L3 | Denetimli öğrenme | DN aktivitesi → sinek gövdesi hareketi (v, ω, ön bacak uzanması) | TRAINED (biyolojik simülasyon verisi) | Mert | P4, Hat B GO ise |
| 6 | **Bypass** | L1 → L3 | 3 ve 4 ile **aynı bütçe** | L1 özellikleri → L3 modları, beyin olmadan | Yalnızca kontrol kolu | Mert | P1'den itibaren |

### Kırmızı çizgiler

1. **Sinaps başına ağırlık asla eğitilmez.** Eğitilirse elde kalan şey connectome değil, connectome şeklinde başlatılmış rastgele bir ağdır. Eğitilebilir parametreler yalnızca hücre tipi başına skalerlerdir.
2. **Eşit bütçe:** Gerçek connectome'a uygulanan her eğitim ve ayar, aynı bütçeyle shuffled grafa ve bypass koluna da uygulanır. Bütçe = optimizasyon adımı + hiperparametre denemesi + ayar için kullanılan tohum sayısı.
3. **Bypass'ı güçlü kurmak bir yükümlülüktür.** Bypass'ın sahibi (Mert) aynı zamanda gerçek kolun ML sahibidir; bypass'ı zayıf bırakmak CKS'yi şişirir ve hakem incelemesinde reddedilir.
4. **Kamera → motor uçtan uca politika** yalnızca bypass kolu olarak var olur, ürün olarak asla.
5. **Bilgi güvenlik duvarı:** L4 politikaları görev bilgisini yalnızca L3'ün mod komutu üzerinden alır ([0002](0002-katmanli-mimari.md)).
6. **Sınav tohumları** ne eğitimde ne hiperparametre seçiminde kullanılır.

### Araçlar

| İhtiyaç | Seçim |
|---|---|
| Çerçeve | JAX, Flax, Optax |
| RL | Brax / MuJoCo Playground PPO-SAC uygulamaları; gerekirse kendi uygulamamız |
| Deney takibi | MLflow (Yusuf'un kurduğu sunucu); her koşu config + tohum + commit hash'iyle |
| Konfigürasyon | Hydra |

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| DN → komut ridge regresyonu (Synaptera T1) | Başarısız oldu: dağılım kayması, sessiz özellikler |
| Tüm ağırlıkları serbestçe eğitmek | Connectome'un anlamı kalmaz |
| ML kullanmamak | Kol ve sürekli kontrol gerçekleşmez |
| Uçtan uca RL (kamera → motor) | Connectome'un katkısı ölçülemez; yalnızca bypass olarak tutulur |

## Sonuçlar

**Olumlu**
- Kol ve hareket, connectome'un sınırlarından bağımsız olarak çalışır hale gelir.
- Connectome ince ayarının sonucu yorumlanabilir: gerçek ile shuffled arasındaki fark doğrudan topolojinin katkısıdır.

**Olumsuz / maliyet**
- Eşit bütçe kuralı eğitim maliyetini artırır.
- Surrogate-gradient ile SNN eğitimi kararsız olabilir; evrim stratejileri yedek yöntemdir.

## İlgili
- [0001 Vizyon](0001-vizyon-ve-basari-olcutu.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md) · [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md)
