# 0005. ML stratejisi: ne eğitilir, ne eğitilmez

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (tüm ML); hakem: Yusuf (eşit bütçe), Ömer (kol becerileri ve ortam arayüzü)
- **Revizyon (2026-10-12, inceleme sonrası):** Eşit bütçe kuralı arka plan kalibrasyonunu ve L3 kuralının seçimini kapsayacak şekilde genişletildi; bypass'ın çıktı biçimi [0001](0001-vizyon-ve-basari-olcutu.md) ile uyumlu hale getirildi; Synaptera atfı düzeltildi.
- **Revizyon 2 (2026-10-12):** Tüm ML Mert'e geçti (Ömer Hat B'ye, bkz. [0007](0007-ekip-ve-gorev-dagilimi.md)); connectome ince ayarında evrim stratejileri **ilk yöntem** oldu; model seçimi [0009](0009-ml-model-secim-protokolu.md)'daki protokole bağlandı.

## Bağlam

Vizyon ML'e iki rol veriyor: kol ve rover hareketini öğrenmek, ve uzun vadede connectome'un kendisini iyileştirmek. Riskler:
- Synaptera'da DN'lerden eğitilen ridge okuma ilk denemede başarısız oldu (üç kolda da 0/4): dönüş için çapraz doğrulanmış R² negatif, DN özelliklerinin çoğu sessiz, kapalı döngüde dağılım kayması (covariate shift) ve **gerçek beyin kolu shuffled ve bypass kollarından daha iyi değildi** (itki ve yunuslama için bypass'ın R²'si daha yüksekti).
- ML'e çok fazla serbestlik verilirse connectome süs olarak kalır ve CKS anlamsızlaşır.

## Karar

### Sahiplik kuralı

- **Tüm ML** (L2 ince ayar, L3 öğrenilmiş dekoder, L4 kol becerileri, VNC vekili, bypass) → **Mert**
- **Rover hareket kontrolcüsü** (L4, kinematik + PID; RL gerekirse Mert ile) → **Ömer**
- Hangi modelin seçileceği yalnızca [0009](0009-ml-model-secim-protokolu.md)'daki protokolle belirlenir.

### Modeller

| # | Model | Katman | Yöntem | Öğrendiği | Etiket | Sahip | Aşama |
|---|---|---|---|---|---|---|---|
| 1 | **Kol becerileri** (uzan, kavra, kaldır, bırak) | L4 | PPO / SAC, MJX'te paralel, durum tabanlı, domain randomization | Hedef poz + propriosepsiyon → eklem torkları | TRAINED | Mert | P0 sonu – P2 |
| 2 | **Rover hareket kontrolcüsü** | L4 | PID → gerekirse RL | (v, ω) → teker torku; eğimde kayma telafisi | HAND-MADE / TRAINED | Ömer | P1–P4 |
| 3 | **Öğrenilmiş dekoder** (VNC yuvası v2) | L3 | DAgger veya RL (ridge ile davranış klonlaması değil) | DN aktivitesi → mod + parametre | TRAINED | Mert | P3 |
| 4 | **Connectome ince ayarı** | L2 | **Önce evrim stratejileri** (CMA-ES): gradyan gerektirmez, doğrudan Brian2 ile çalışır. Surrogate-gradient yalnızca ES tıkanırsa ve JAX motoru eşdeğerliği geçmişse | **Yalnızca hücre tipi başına kazanç ve eşik** (birkaç yüz parametre) | TRAINED (BRAIN topolojisi) | Mert | P4 |
| 5 | **VNC vekili** (Hat B) | L3 | Denetimli öğrenme | DN aktivitesi → sinek gövdesi hareketi (v, ω, ön bacak uzanması) | TRAINED (biyolojik simülasyon verisi) | Mert | P4, Hat B GO ise |
| 6 | **Bypass** | L1 → L3 | 3 ve 4 ile **aynı bütçe** | L1 özellikleri → DN aktivitesi biçiminde çıktı → aynı L3 kuralı, beyin olmadan | Yalnızca kontrol kolu | Mert | P1'den itibaren |

### Kırmızı çizgiler

1. **Sinaps başına ağırlık asla eğitilmez.** Eğitilirse elde kalan şey connectome değil, connectome şeklinde başlatılmış rastgele bir ağdır. Eğitilebilir parametreler yalnızca hücre tipi başına skalerlerdir.
2. **Eşit bütçe:** Gerçek connectome'a uygulanan her eğitim ve ayar, aynı bütçeyle shuffled grafa ve bypass koluna da uygulanır. Bütçe = optimizasyon adımı + hiperparametre denemesi + ayar için kullanılan tohum sayısı. **Arka plan girdisi kalibrasyonu ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)) ve L3 kuralındaki serbest sabitlerin (popülasyon tanımı, filtre, histerezis) seçimi de bu bütçeye dahildir.** L3 sabitleri gerçek kolun sonuçlarına bakılarak seçilemez; ya ön-kayıtta sabitlenir ya da her kol için aynı prosedürle ayrı ayrı seçilir.
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
- Evrim stratejileri, parametre sayısı birkaç yüzü aşarsa yavaşlar; bu sınır, tip başına skaler kuralıyla (C1) zaten korunur. Surrogate-gradient ile SNN eğitimi kararsız olabilir; bu yüzden ikinci sıradadır.

## İlgili
- [0001 Vizyon](0001-vizyon-ve-basari-olcutu.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md) · [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md)
