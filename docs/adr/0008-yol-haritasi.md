# 0008. Yol haritası

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip
- **Revizyon (2026-10-12, inceleme sonrası):** JAX motoru P0'ın kritik yolundan çıkarıldı (P1–P3 derlenmiş Brian2 ile yürür, JAX P2'de geliştirilir); T1 için CKS ≈ 0 beklentisi karar noktasına yazıldı; mevcut koddan geçişe v0 belge düzeltmeleri eklendi.

## Bağlam

Yeni mimari ([0002](0002-katmanli-mimari.md)) mevcut koddan farklı bir altyapı gerektiriyor: nöron seviyesi graf, JAX motoru, yeni simülasyon ortamı, değerlendirme düzeneği. Synaptera'nın tecrübesi, ölçütleri ve kontrolleri **baştan** kurmanın sonradan eklemekten çok daha ucuz olduğunu gösteriyor. Ekip üç kişi ve yarı zamanlı çalışıyor olabilir; süreler buna göre tahmini verilmiştir.

## Karar

### Aşamalar

Hafta 1 (H1) = 2026-10-19 haftası. Süreler tahminidir; her aşama **"bitti" ölçütü** sağlanınca kapanır, tarih dolunca değil.

| Aşama | Haftalar | Hedef | "Bitti" ölçütü |
|---|---|---|---|
| **P0 Temel** | H1–H4 | Altyapı | Yeni repo yapısı + CI; nöron seviyesi graf üretici; derlenmiş Brian2 motoru `step()` arayüzüyle çalışıyor ve hızı ölçüldü; MuJoCo dünyası v1 (rover + kol + iki göz); değerlendirme düzeneği iskeleti; ön-kayıt şablonu |
| **P1 Kaçış (T1)** | H5–H8 | İlk CKS | Kaçış modülü 6 kabul testini geçti; L1 eşiksiz kodlayıcı (A9) ve dondurulmuş L3 kuralı (A10) hazır; T1 ön-kaydı; gerçek/shuffled/bypass kollarıyla T1 sınavı; **ilk CKS raporu**; v0 (tip grafı) ile karşılaştırma |
| **P2 Yaklaş-dur (T2) + kol** | H9–H14 | Hedef davranışı ve kol becerileri | Hedefe yönelme ve dur modülleri kabul testlerinden geçti (ya da `engineered` olarak raporlandı); T2 CKS; kol becerileri (uzan, kavra, kaldır) beyinden bağımsız olarak ≥ %90 başarı; JAX motoru Brian2 eşdeğerliğini geçti |
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
| **P0** | Veri indirme + graf üretici; shuffled üretici; derlenmiş Brian2 motoru; tüm-beyin kahini | MuJoCo dünyası v1; rover + kol MJCF; iki göz + ommatidia; Gym API | Repo yapısı, CI, güvenlik, CUDA sunucusu, MLflow, kayıt şeması, değerlendirme iskeleti |
| **P1** | Kaçış modülü + kabul testleri; arka plan girdisi kalibrasyonu; L3 v1; T1 bypass | T1 sahnesi; loom özellik kodlayıcı; FlyVis girdi formatı; rover kontrolcüsü | CKS + bootstrap; `verify.py`; T1 ön-kayıt ve rapor hattı; dashboard v1 |
| **P2** | Hedefe yönelme + dur modülleri (tüm-beyin testi); T2 bypass; JAX motoru + eşdeğerlik; B1 | T2 sahnesi; kol RL becerileri; eğimde rover kontrolü | Beyin aktivitesi görüntüleyici; gece testleri; etiket denetleyicisi |
| **P3** | Uzanma kararı modülü; öğrenilmiş dekoder; AN kodlayıcı; B2 | T3 entegrasyonu; nesne pozu algısı; B2 NeuroMechFly | Entegrasyon sahibi; uçtan uca CI; tekrarlanabilirlik denetimi; güvenlik incelemesi |
| **P4** | Connectome ince ayarı; VNC vekili (GO ise); final CKS | T4 Mars arazisi; domain randomization; video render hattı | Final rapor; veri paketi; lisans denetimi; yayın |

Ayrıntılı kişisel hedefler ve yol haritaları: [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md) · [gorevler/yusuf.md](gorevler/yusuf.md)

### Kritik bağımlılıklar

```
P0:  Yusuf (CI, sunucu, kayıt şeması) ──► herkes
     Ömer (dünya v1, göz) ──────────────► Mert (L1 → L2 bağlantısı)
     Mert (derlenmiş Brian2 motoru) ─────► herkes (kapalı döngü)
P1:  Mert (kaçış modülü) + Ömer (T1 sahnesi) ──► Yusuf (T1 CKS)
P2:  Ömer (kol becerileri) ─────────────► P3 entegrasyonu
     Mert (hedef modülü tüm-beyin testi) ──► T2'nin BRAIN mi engineered mı olacağı
     Mert (JAX motoru, eşdeğerlik) ─────► P3 dekoder eğitimi, P4 ince ayar
P3:  Mert (uzanma kararı) + Ömer (beceriler) ──► T3
```

### Karar noktaları

| Hafta | Karar | Seçenekler |
|---|---|---|
| H4 | Derlenmiş Brian2, T1 sınavını (≥ 20 bölüm × 3 kol × 5 tohum) sunucuda bir gecede bitirebiliyor mu? | Evet → P1 Brian2 ile yürür. Hayır → JAX motoru öne çekilir, P1 en fazla 2 hafta kayar. |
| H8 | T1 üç kolla uçtan uca koştu mu; CKS ne çıktı? | T1 bir aktarım testidir; **CKS ≈ 0 beklenir ve projeyi durdurmaz** ([0001](0001-vizyon-ve-basari-olcutu.md)). CKS < 0 veya gerçek kol başarısızsa nedenler raporlanır (kodlayıcı mı, alt ağ mı, kalibrasyon mu?) ve T2 tasarımı buna göre gözden geçirilir. |
| H11 | LC10a → DNa02 tüm-beyin testinden geçti mi? | Geçti → T2 hedefe yönelme BRAIN. Geçmedi → `engineered` olarak raporlanır, alternatif yol aranır. |
| H14 | Hat B GO / NO-GO | Bkz. yukarı |
| H14 | JAX motoru eşdeğerliği geçti mi? | Geçti → P3 dekoder eğitimi ve P4 ince ayarı JAX ile. Geçmedi → dekoder Brian2 ile DAgger olarak eğitilir; P4 ince ayarı evrim stratejileriyle ve daraltılmış bütçeyle yapılır. |
| H20 | Öğrenilmiş dekoder bypass'ı yeniyor mu? | Evet → v2 varsayılan. Hayır → v1 kalır, sonuç raporlanır. |

### Mevcut koddan geçiş

1. Mevcut kod (`src/`, `config/type_graph.json`, testler) etiketli bir commit ile **v0** olarak işaretlenir (ör. `v0-faz1-kacis`). Aynı adımda v0 belgelerindeki iddialar düzeltilir: README ve `docs/yol_haritasi.md` kaçışın "sadece connectome ile" yapıldığını söylememeli (kodlayıcıdaki eşikler, elle seçilmiş DN → geri eşlemesi ve 0,5 s kalıcılık elle tasarlandı). `tests/test_hierarchical_isolation.py` Shiu parametrelerini kullanmadığı için v0 olarak etiketlenir veya kaldırılır; kök dizindeki `brian2_isolation_test.png` `assets/` altına taşınır ya da silinir.
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
- Riskli kararlar (motor hızı, JAX motoru, hedef modülü, Hat B) belirli haftalarda, belirli ölçütlerle verilir.
- İlk CKS, kendi motorumuzun doğrulanmasını beklemez.

**Olumsuz / maliyet**
- P0'da görünür bir "yeni demo" çıkmaz; altyapı haftalarıdır.
- Toplam süre (~7 ay) üç kişilik yarı zamanlı ekip için iddialıdır. Aşamalar tarihe göre değil "bitti" ölçütüne göre kapanır; gecikme olursa P4'ün kapsamı (rocker-bogie, ince ayar) daraltılır.

## İlgili
- [0001](0001-vizyon-ve-basari-olcutu.md) – [0007](0007-ekip-ve-gorev-dagilimi.md) · mevcut [docs/yol_haritasi.md](../yol_haritasi.md)
