# 0008. Yol haritası

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip
- **Revizyon (2026-10-12, inceleme sonrası):** JAX motoru P0'ın kritik yolundan çıkarıldı (P1–P3 derlenmiş Brian2 ile yürür, JAX P2'de geliştirilir); T1 için CKS ≈ 0 beklentisi karar noktasına yazıldı; mevcut koddan geçişe v0 belge düzeltmeleri eklendi.
- **Revizyon 2 (2026-10-12):** Yeni görev dağılımına göre ([0007](0007-ekip-ve-gorev-dagilimi.md)) Hat B tam zamanlı ve H1'de başlıyor, GO/NO-GO H8'e çekildi; P1'e ilk anlamlı CKS için T1b eklendi; kol becerileri P0 sonunda ML hattının ilk işi olarak başlıyor; JAX motoru opsiyonel oldu; v0 temizliği bu revizyonda yapıldı.

## Bağlam

Yeni mimari ([0002](0002-katmanli-mimari.md)) mevcut koddan farklı bir altyapı gerektiriyor: nöron seviyesi graf, derlenmiş Brian2 motoru, yeni simülasyon ortamı, değerlendirme düzeneği. Synaptera'nın tecrübesi, ölçütleri ve kontrolleri **baştan** kurmanın sonradan eklemekten çok daha ucuz olduğunu gösteriyor. Ekip üç kişi ve yarı zamanlı çalışıyor olabilir; süreler buna göre tahmini verilmiştir.

Proje iki paralel hatta yürür:
- **Ana hat (FAFB + ML + rover):** Mert (beyin, ML), Yusuf (platform, değerlendirme), Ömer (dünya, P0 ağırlıklı).
- **Hat B (BANC + sinek gövdesi):** Ömer.

## Karar

### Ana hat aşamaları

Hafta 1 (H1) = 2026-10-19 haftası. Süreler tahminidir; her aşama **"bitti" ölçütü** sağlanınca kapanır, tarih dolunca değil.

| Aşama | Haftalar | Hedef | "Bitti" ölçütü |
|---|---|---|---|
| **P0 Temel** | H1–H4 | Altyapı | Yeni repo yapısı + CI; `config/modules.yaml` ve nöron seviyesi graf üretici ([0010](0010-noron-secimi-tohum-tipleri.md)); shuffled üretici; derlenmiş Brian2 motoru `step()` arayüzüyle çalışıyor ve hızı ölçüldü; MuJoCo dünyası v1 (rover + kol + iki göz); değerlendirme düzeneği iskeleti; ön-kayıt şablonu; **ML hattı doğrulandı** (kol "uzan" görevinde IK baz çizgisi + PPO, [0009](0009-ml-model-secim-protokolu.md)) |
| **P1 Kaçış (T1, T1b)** | H5–H8 | İlk anlamlı CKS | Kaçış modülü 6 kabul testini geçti; eşiksiz L1 (A9) ve dondurulmuş L3 (A10); T1 ve T1b ön-kayıtları; üç kolla sınav; **T1 CKS (aktarım testi) ve T1b CKS (ilk anlamlı sayı)**; v0 (tip grafı) ile karşılaştırma |
| **P2 Yaklaş-dur (T2) + kol** | H9–H14 | Hedef davranışı ve kol becerileri | Hedefe yönelme ve dur modülleri kabul testlerinden geçti (ya da `engineered` olarak raporlandı); T2 CKS; kol becerileri (uzan, kavra, kaldır) beyinden bağımsız ≥ %90 başarı, model seçimi [0009](0009-ml-model-secim-protokolu.md)'a göre yapıldı |
| **P3 Entegrasyon (T3)** | H15–H20 | Uçtan uca alma görevi | Uzanma kararı modülü; UZAN → L4 beceri zinciri; T3 CKS; öğrenilmiş dekoder (VNC yuvası v2) bypass'a karşı test edildi; AN kodlayıcı (Hat B'nin AN listesiyle) |
| **P4 Mars + öğrenme (T4)** | H21–H28 | Final sınavı | Eğimli arazi, dikkat dağıtıcılar, görev kesintisi; T4 CKS; connectome ince ayarı (önce evrim stratejileri; gerçek vs shuffled, eşit bütçe); VNC vekili (Hat B GO ise) yuvaya takıldı; final raporu |

### Hat B: BANC + sinek gövdesi (Ömer, tam zamanlı)

| Adım | Haftalar | İçerik | Karar |
|---|---|---|---|
| **B1 Hazırlık** | H1–H4 | BANC verisi ve lisans kontrolü; NeuroMechFly yürüme kurulumu; MDN, DNa02, DNp09'un VNC hedefleri; yürüme durumu ve temas taşıyan AN adayları; **AN listesi** ve **VNC vekili veri şeması** sözleşmeleri ([0007](0007-ekip-ve-gorev-dagilimi.md)) | — |
| **B2 Tek davranış** | H5–H8 | BANC beyin+VNC LIF; MDN uyarılınca NeuroMechFly gövdesinde geri yürüme deseni; ön-kayıtlı ölçüt | **GO / NO-GO (H8)** |
| B3 Beş davranış | H9–H18 | Geri yürüme, dönüş (DNa02), kaçış, dur (DNp09), ön bacak uzanma; ön-kayıtlı ölçütler | Yalnızca GO ise |
| B4 VNC vekili verisi | H15–H22 | DN aktivitesi → gövde hareketi veri seti (şemaya uygun); Mert vekil modeli eğitir ([0009](0009-ml-model-secim-protokolu.md)) | Yalnızca GO ise |
| B5 Rapor | H23–H28 | Hat B sonuçları (olumlu ve olumsuz); FAFB ile BANC arasında tip eşlemesi ve farklar | — |

**NO-GO durumunda:** Hat B "BANC = bilgi kaynağı" moduna geçer (DN hedefleri, AN seçimi ve neden çalışmadığı raporlanır); Ömer'in zamanı T2–T4 sahnelerine, rover kontrolcüsüne ve gerekirse kol becerilerinin ortam tarafına kayar. VNC yuvası v2'de (öğrenilmiş dekoder) kalır. Ana hat bu karardan etkilenmez.

### Kişi × aşama özeti

| Aşama | Mert (FAFB + ML) | Ömer (Hat B + dünya) | Yusuf (platform + değerlendirme) |
|---|---|---|---|
| **P0** | Veri indirme; `modules.yaml` + graf üretici; derlenmiş Brian2; tüm-beyin kahini; ML hattı (kol "uzan" IK vs PPO); [0009](0009-ml-model-secim-protokolu.md) ön-kaydı | MuJoCo dünyası v1; rover + kol MJCF; iki göz + ommatidia; Gym API; **B1** | Repo yapısı, CI, güvenlik, CUDA sunucusu, MLflow, kayıt şeması, değerlendirme iskeleti; **shuffled üretici** |
| **P1** | Kaçış modülü + 6 kabul testi; arka plan kalibrasyonu; L3 v1; T1/T1b bypass | T1/T1b sahneleri; eşiksiz loom kodlayıcı; rover kontrolcüsü v1; **B2 (GO/NO-GO H8)** | CKS + bootstrap; `verify.py`; A9 testleri; T1/T1b ön-kayıt ve rapor; dashboard v1 |
| **P2** | Hedefe yönelme + dur modülleri (tüm-beyin testi); T2 bypass; **kol becerileri** (uzan, kavra, kaldır) | T2 sahnesi; küçük hedef kodlayıcı; **B3** | Beyin aktivitesi görüntüleyici; gece testleri; etiket denetleyicisi; T2 sınavı |
| **P3** | Uzanma kararı modülü; öğrenilmiş dekoder; AN kodlayıcı; beceri zincirinin entegrasyonu | T3 sahnesi; nesne pozu algısı; **B3–B4** | Entegrasyon sahibi; uçtan uca CI; tekrarlanabilirlik denetimi; T3 sınavı |
| **P4** | ES ile ince ayar; VNC vekili (GO ise); final CKS | T4 Mars arazisi; domain randomization; **B4–B5** | Final rapor; veri paketi; lisans denetimi; yayın |

Ayrıntılı kişisel hedefler ve yol haritaları: [gorevler/mert.md](gorevler/mert.md) · [gorevler/omer.md](gorevler/omer.md) · [gorevler/yusuf.md](gorevler/yusuf.md)

### Kritik bağımlılıklar

```
P0:  Yusuf (CI, sunucu, MLflow, kayıt şeması) ──► herkes
     Ömer (dünya v1, kol MJCF, göz) ──────────► Mert (L1 → L2, kol becerileri)
     Mert (graf + derlenmiş Brian2) ──────────► herkes (kapalı döngü)
     Yusuf (shuffled üretici) ────────────────► P1 kontrol kolu
     Ömer (B1 sözleşmeleri) ──────────────────► Mert (AN kodlayıcı P3, VNC vekili P4)
P1:  Mert (kaçış modülü) + Ömer (T1/T1b sahneleri) ──► Yusuf (CKS)
P2:  Mert (hedef modülü tüm-beyin testi) ──► T2'nin BRAIN mi engineered mı olacağı
     Mert (kol becerileri) ──────────────────► P3 entegrasyonu
P3:  Mert (uzanma kararı + beceriler) + Ömer (T3 sahnesi) ──► T3
P4:  Ömer (B4 verisi, GO ise) ───────────────► Mert (VNC vekili)
```

### Karar noktaları

| Hafta | Karar | Seçenekler |
|---|---|---|
| H4 | Derlenmiş Brian2, T1 sınavını (≥ 20 bölüm × 3 kol × 5 tohum) sunucuda bir gecede bitirebiliyor mu? | Evet → devam. Hayır → önce derleme hedefi (`cpp_standalone`) ve paralel koşu sayısı gözden geçirilir; yetmezse JAX motoru öne çekilir, P1 en fazla 2 hafta kayar. `θ` davranış görülmeden değiştirilmez. |
| H4 | ML hattı uçtan uca çalışıyor mu (kol "uzan": IK + PPO, 5 tohum, MLflow)? | Evet → P2 kol becerileri bu hatla. Hayır → P1 boyunca altyapı düzeltilir. |
| H8 | T1 ve T1b üç kolla koştu mu; CKS ne çıktı? | T1'de CKS ≈ 0 beklenir. **T1b ilk anlamlı sayıdır:** CKS > 0 → devam; ≤ 0 → nedenler raporlanır (kodlayıcı mı, alt ağ mı, kalibrasyon mu, L3 normalizasyonu mu?) ve T2 tasarımı buna göre gözden geçirilir. Proje durmaz. |
| H8 | Hat B GO / NO-GO | Bkz. yukarı |
| H11 | LC10a → DNa02 tüm-beyin testinden geçti mi? | Geçti → T2 hedefe yönelme BRAIN. Geçmedi → `engineered` olarak raporlanır, genişletilmiş ağda alternatif yol aranır. |
| H14 | Kol becerilerinde hangi model? | [0009](0009-ml-model-secim-protokolu.md)'daki ön-kayıtlı kurala göre (IK baz çizgisi, PPO, SAC). |
| H20 | Öğrenilmiş dekoder bypass'ı yeniyor mu? | Evet → v2 varsayılan. Hayır → v1 kalır, sonuç raporlanır. |
| H22 | ES ince ayarı tıkandı mı ve JAX gerekli mi? | Hayır → ES ile devam. Evet ve JAX eşdeğerliği geçtiyse → surrogate-gradient denenir; geçmediyse ince ayar ES sonucuyla raporlanır. |

### Mevcut koddan geçiş

1. Mevcut kod (`src/`, `config/type_graph.json`, `config/neurons.json`, `config/connectome_graph.json`, testler) etiketli bir commit ile **v0** olarak işaretlenir (`v0-faz1-kacis`). v0 belgelerindeki iddialar düzeltilir: README ve `docs/yol_haritasi.md` kaçışın "sadece connectome ile" yapıldığını söylememeli (kodlayıcıdaki eşikler, elle seçilmiş DN → geri eşlemesi ve 0,5 s kalıcılık elle tasarlandı). `tests/test_hierarchical_isolation.py` Shiu parametrelerini kullanmadığı için v0 olarak etiketlenir veya kaldırılır.
2. Kök dizindeki `brian2_isolation_test.png` `assets/v0/` altına taşındı (Revizyon 2).
3. Yeni yapı ([0006](0006-repo-kurallari.md)'daki klasörler) P0'da yanına kurulur. v0, T1'de karşılaştırma kolu olarak kullanılır.
4. P1 sonunda v0 kodu `legacy/` altına taşınır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Mevcut Faz 2 planıyla (tip grafı) devam etmek | Path-integrated varsayımı ve ölçülemeyen katkı sorunu büyüyerek devam eder |
| Önce Hat B'yi tamamlayıp sonra rover'a geçmek | Hat B'nin başarısız olma ihtimali gerçek; rover hiç ilerlemeyebilir. Paralel yürütülür. |
| Hat B'yi yarı zamanlı tutmak (ilk plan) | Ekip Ömer'in BANC'a odaklanmasına karar verdi; GO/NO-GO H14 yerine H8'de verilebilir |
| İlk anlamlı CKS'yi T2'ye bırakmak | H14'e kadar connectome katkısına dair hiçbir sayı olmazdı; T1b aynı altyapıyla H8'de bir sayı üretir |
| Kolu en sona bırakmak | Kol becerileri beyinden bağımsız eğitilebilir; erken başlamak ML hattını da doğrular |

## Sonuçlar

**Olumlu**
- İlk anlamlı CKS P1 sonunda (≈ 2 ay, T1b).
- Hat B'nin GO/NO-GO kararı H8'de; NO-GO olsa bile Ömer'in zamanı ana hatta kayar.
- ML hattı P0'da doğrulanır; P2'deki kol becerileri altyapı sorunlarıyla gecikmez.
- JAX motoru kritik yolda değil.

**Olumsuz / maliyet**
- P0'da görünür bir "yeni demo" çıkmaz; altyapı haftalarıdır.
- Toplam süre (~7 ay) üç kişilik yarı zamanlı ekip için iddialıdır. Aşamalar tarihe göre değil "bitti" ölçütüne göre kapanır; gecikme olursa P4'ün kapsamı (rocker-bogie, ince ayar) daraltılır.

## İlgili
- [0001](0001-vizyon-ve-basari-olcutu.md) – [0007](0007-ekip-ve-gorev-dagilimi.md) · [0009](0009-ml-model-secim-protokolu.md) · [0010](0010-noron-secimi-tohum-tipleri.md) · mevcut [docs/yol_haritasi.md](../yol_haritasi.md)
