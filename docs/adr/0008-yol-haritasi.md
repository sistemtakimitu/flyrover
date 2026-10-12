# 0008. Yol haritası

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip

## Bağlam

Yeni mimari ([0002](0002-katmanli-mimari.md)) mevcut koddan farklı bir altyapı gerektiriyor: nöron seviyesi graf, JAX motoru, yeni simülasyon ortamı, değerlendirme düzeneği. Synaptera'nın tecrübesi, ölçütleri ve kontrolleri **baştan** kurmanın sonradan eklemekten çok daha ucuz olduğunu gösteriyor. Ekip üç kişi ve yarı zamanlı çalışıyor olabilir; süreler buna göre tahmini verilmiştir.

## Karar

### Aşamalar

Hafta 1 (H1) = 2026-10-19 haftası. Süreler tahminidir; her aşama **"bitti" ölçütü** sağlanınca kapanır, tarih dolunca değil.

| Aşama | Haftalar | Hedef | "Bitti" ölçütü |
|---|---|---|---|
| **P0 Temel** | H1–H4 | Altyapı | Yeni repo yapısı + CI; nöron seviyesi graf üretici; JAX motoru Brian2 eşdeğerliğini geçti; MuJoCo dünyası v1 (rover + kol + iki göz); değerlendirme düzeneği iskeleti; ön-kayıt şablonu |
| **P1 Kaçış (T1)** | H5–H8 | İlk CKS | Kaçış modülü 5 kabul testini geçti; T1 ön-kaydı; gerçek/shuffled/bypass kollarıyla T1 sınavı; **ilk CKS raporu**; v0 (tip grafı) ile karşılaştırma |
| **P2 Yaklaş-dur (T2) + kol** | H9–H14 | Hedef davranışı ve kol becerileri | Hedefe yönelme ve dur modülleri kabul testlerinden geçti (ya da `engineered` olarak raporlandı); T2 CKS; kol becerileri (uzan, kavra, kaldır) beyinden bağımsız olarak ≥ %90 başarı |
| **P3 Entegrasyon (T3)** | H15–H20 | Uçtan uca alma görevi | Uzanma kararı modülü; L3 → L4 beceri çağırma; T3 CKS; öğrenilmiş dekoder (VNC yuvası v2) bypass'a karşı test edildi |
| **P4 Mars + öğrenme (T4)** | H21–H28 | Final sınavı | Eğimli arazi, dikkat dağıtıcılar, görev kesintisi; T4 CKS; connectome ince ayarı (gerçek vs shuffled, eşit bütçe); final raporu |

### Hat B: BANC + sinek gövdesi (paralel araştırma hattı)

| Adım | Haftalar | İçerik | Karar |
|---|---|---|---|
| **B1 Hazırlık** | H9–H11 | BANC verisi; MDN, DNa02, DNp09'un VNC hedefleri; yürüme durumu taşıyan AN adayları (bu liste ana hatta AN kodlayıcıyı da besler) | — |
| **B2 Tek davranış** | H12–H14 | BANC beyin+VNC LIF; MDN uyarılınca NeuroMechFly sinek gövdesinde geri yürüme deseni | **GO / NO-GO** (H14) |
| B3 Beş davranış | H15–H22 | Geri yürüme, dönüş, kaçış, dur, ön bacak uzanma; ön-kayıtlı ölçütler | Yalnızca GO ise |
| B4 VNC vekili | H21–H28 | DN aktivitesi → sinek gövdesi hareketi modeli; VNC yuvasına v3 olarak takılır | Yalnızca GO ise |

**NO-GO durumunda:** Hat B "BANC = bilgi kaynağı" moduna geçer (DN hedefleri ve AN seçimi belgelenir), VNC yuvası v2'de (öğrenilmiş dekoder) kalır. Ana hat bu karardan etkilenmez.

Hat B'ye ayrılan süre sınırlıdır: Mert ve Ömer için haftada en fazla 1'er gün.

### Kişi × aşama özeti

| Aşama | Mert | Ömer | Yusuf |
|---|---|---|---|
| **P0** | Veri indirme + graf üretici; JAX motoru; tüm-beyin kahini | MuJoCo dünyası v1; rover + kol MJCF; iki göz + ommatidia; Gym API | Repo yapısı, CI, güvenlik, CUDA sunucusu, MLflow, kayıt şeması, değerlendirme iskeleti |
| **P1** | Kaçış modülü + kabul testleri; arka plan girdisi kalibrasyonu; L3 v1; T1 bypass | T1 sahnesi; loom özellik kodlayıcı; FlyVis girdi formatı; rover kontrolcüsü | CKS + bootstrap; `verify.py`; T1 ön-kayıt ve rapor hattı; dashboard v1 |
| **P2** | Hedefe yönelme + dur modülleri (tüm-beyin testi); T2 bypass; B1 | T2 sahnesi; kol RL becerileri; eğimde rover kontrolü | Beyin aktivitesi görüntüleyici; gece testleri; etiket denetleyicisi |
| **P3** | Uzanma kararı modülü; öğrenilmiş dekoder; AN kodlayıcı; B2 | T3 entegrasyonu; nesne pozu algısı; B2 NeuroMechFly | Entegrasyon sahibi; uçtan uca CI; tekrarlanabilirlik denetimi; güvenlik incelemesi |
| **P4** | Connectome ince ayarı; VNC vekili (GO ise); final CKS | T4 Mars arazisi; domain randomization; video render hattı | Final rapor; veri paketi; lisans denetimi; yayın |

Ayrıntılı kişisel hedefler ve yol haritaları: [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md) · [gorevler/yusuf.md](gorevler/yusuf.md)

### Kritik bağımlılıklar

```
P0:  Yusuf (CI, sunucu, kayıt şeması) ──► herkes
     Ömer (dünya v1, göz) ──────────────► Mert (L1 → L2 bağlantısı)
     Mert (JAX motoru) ─────────────────► herkes (kapalı döngü)
P1:  Mert (kaçış modülü) + Ömer (T1 sahnesi) ──► Yusuf (T1 CKS)
P2:  Ömer (kol becerileri) ─────────────► P3 entegrasyonu
     Mert (hedef modülü tüm-beyin testi) ──► T2'nin BRAIN mi engineered mı olacağı
P3:  Mert (uzanma kararı) + Ömer (beceriler) ──► T3
```

### Karar noktaları

| Hafta | Karar | Seçenekler |
|---|---|---|
| H4 | JAX motoru eşdeğerliği geçti mi? | Geçti → devam. Geçmedi → P1 Brian2 (Cython) ile yürür, JAX P2'ye kayar. |
| H8 | T1 CKS > 0 mı? | Evet → devam. Hayır → nedenler raporlanır (kodlayıcı mı, alt ağ mı?); T2 tasarımı buna göre gözden geçirilir. |
| H11 | LC10a → DNa02 tüm-beyin testinden geçti mi? | Geçti → T2 hedefe yönelme BRAIN. Geçmedi → `engineered` olarak raporlanır, alternatif yol aranır. |
| H14 | Hat B GO / NO-GO | Bkz. yukarı |
| H20 | Öğrenilmiş dekoder bypass'ı yeniyor mu? | Evet → v2 varsayılan. Hayır → v1 kalır, sonuç raporlanır. |

### Mevcut koddan geçiş

1. Mevcut kod (`src/`, `config/type_graph.json`, testler) etiketli bir commit ile **v0** olarak işaretlenir (ör. `v0-faz1-kacis`).
2. Yeni yapı ([0006](0006-repo-kurallari.md)'daki klasörler) P0'da yanına kurulur. v0, T1'de karşılaştırma kolu olarak kullanılır.
3. P1 sonunda v0 kodu `legacy/` altına taşınır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Mevcut Faz 2 planıyla (tip grafı) devam etmek | Path-integrated varsayımı ve ölçülemeyen katkı sorunu büyüyerek devam eder |
| Önce Hat B'yi tamamlayıp sonra rover'a geçmek | Hat B'nin başarısız olma ihtimali gerçek; rover hiç ilerlemeyebilir. Paralel yürütülür. |
| Kolu en sona bırakmak | Kol becerileri beyinden bağımsız eğitilebilir; P2'de başlamak entegrasyon riskini azaltır |

## Sonuçlar

**Olumlu**
- İlk CKS P1 sonunda (≈ 2 ay) elde edilir; proje erken aşamada gerçek bir sayı üretir.
- Kol, P2'den itibaren paralel ilerler.
- Riskli kararlar (JAX motoru, hedef modülü, Hat B) belirli haftalarda, belirli ölçütlerle verilir.

**Olumsuz / maliyet**
- P0'da görünür bir "yeni demo" çıkmaz; altyapı haftalarıdır.
- Toplam süre (~7 ay) üç kişilik yarı zamanlı ekip için iddialıdır. Aşamalar tarihe göre değil "bitti" ölçütüne göre kapanır; gecikme olursa P4'ün kapsamı (rocker-bogie, ince ayar) daraltılır.

## İlgili
- [0001](0001-vizyon-ve-basari-olcutu.md) – [0007](0007-ekip-ve-gorev-dagilimi.md) · mevcut [docs/yol_haritasi.md](../yol_haritasi.md)
