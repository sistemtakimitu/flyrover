# Mert: FAFB beyin çekirdeği ve ML sahibi

- **Rol:** Data scientist & ML engineer
- **Sahip olduğu alanlar:** L2 (FAFB verisi, nöron seviyesi graf üretici, derlenmiş Brian2 motoru, tüm-beyin kahini, modül kabul testleri), L3 (mod seçici / VNC yuvası), **tüm ML** (L4 kol RL becerileri, L3 öğrenilmiş dekoder, L2 ince ayarı, bypass kolu, VNC vekili modeli), ML model seçim protokolü
- **Hakemleri:** Yusuf (veri bütünlüğü, eşit bütçe, kurallar), Ömer (robot modeli, ödül tasarımı, L1/L3 arayüzü)
- **Yedeği:** Yusuf (beyin), Ömer (ML hatları)
- İlgili kararlar: [0004](../0004-connectome-noron-ve-sinaps-kurallari.md) · [0005](../0005-ml-stratejisi.md) · [0009](../0009-ml-model-secim-protokolu.md) · [0010](../0010-noron-secimi-tohum-tipleri.md) · [0002](../0002-katmanli-mimari.md)
- **Revizyon 2 (2026-10-12):** Görev dağılımı değişti ([0007](../0007-ekip-ve-gorev-dagilimi.md)): kol RL becerileri Mert'e geçti, shuffled üretici Yusuf'a geçti, BANC analizi Ömer'e geçti; JAX motoru opsiyonel oldu; nöron seçimi tohum tiplerine taşındı ([0010](../0010-noron-secimi-tohum-tipleri.md)).

---

## Ulaşılması gereken nokta (H28 sonunda)

1. **Doğrulanmış bir beyin çekirdeği:** [0010](../0010-noron-secimi-tohum-tipleri.md)'daki 14 tohum tipinden, FAFB v783 üzerinde nöron seviyesinde ve veriden genişletilerek kurulan alt ağ; 4 modül (kaçış, hedefe yönelme, dur, uzanma kararı). Her modülün 6 kabul testi sonucu belgelenmiş: geçenler BRAIN, geçemeyenler `engineered` olarak raporlanmış.
2. **Yeterince hızlı motor:** Derlenmiş Brian2 motoru değerlendirme ve ES ince ayar koşularını taşıyor. JAX motoru yalnızca ölçümler gerektirirse yazılmış ve eşdeğerliği kanıtlanmış.
3. **Ölçülmüş katkı:** T1, T1b, T2, T3, T4 için gerçek / shuffled / bypass sonuçları ve **CKS** (Yusuf'un düzeneğiyle). Bypass her görevde gerçek kolla aynı aday listesi ve bütçeyle kurulmuş.
4. **Kol becerileri:** Uzan, kavra, kaldır, bırak; doğrulama tohumlarında, domain randomization altında **≥ %90 başarı**; model [0009](../0009-ml-model-secim-protokolu.md)'a göre seçilmiş (IK baz çizgisi dahil). UZAN modu bu zinciri başlatıyor.
5. **VNC yuvası:** v1 (sabit kural) ve v2 (öğrenilmiş dekoder, DAgger öncelikli) çalışıyor; v2'nin bypass'a karşı sonucu raporlanmış.
6. **Connectome ince ayarı:** Hücre tipi başına kazanç ve eşik; **önce CMA-ES**; gerçek ve shuffled eşit bütçeyle karşılaştırılmış.
7. **VNC vekili (Hat B GO ise):** Ömer'in verisiyle eğitilmiş, doğrusal / MLP / GRU arasından protokolle seçilmiş, yuvaya v3 olarak takılmış.

---

## Başlangıç: ilk 2 hafta (H1–H2)

Sıra önemli: önce veri ve tekrarlanabilirlik, sonra graf, sonra motor. ML hattı H3'te başlar.

| # | İş | Çıktı |
|---|---|---|
| 1 | **Ortam:** Python 3.11, Brian2 (derlenmiş hedef: önce `cython`, sonra `cpp_standalone` denemesi), pandas, pyarrow; sürümler sabit | `requirements` güncellemesi (Yusuf'un `uv.lock` yapısına uygun) |
| 2 | **Veri:** `src/data/build_type_graph.py`'nin indirdiği FlyWire v783 bağlantı tablosu (Zenodo, ~880 MB) ve Schlegel et al. anotasyonları; **SHA-256 hash'leri** kaydedilir | `data/cache/` (gitignore) + hash tablosu |
| 3 | **Anotasyon keşfi:** 14 tohum tipinin taraf başına nöron sayısı, NT dağılımı; şeker GRN'leri ve MN9 için doğru anotasyon alanları | `docs/reports/p0_tohum_tipleri.md`: beklenen vs bulunan sayı tablosu |
| 4 | **`config/modules.yaml`** ([0010](../0010-noron-secimi-tohum-tipleri.md) §4) | Dosya + şema doğrulayıcı |
| 5 | **Graf üretici v1** (`connectome/build_graph.py`): tohum tipleri → tüm nöronlar → `θ` eşikli 2 sıçrama genişletme → nöron-nöron kenarlar (≥ 5 sinaps), işaretler, manifest | Aynı girdiyle aynı hash; birim testleri; **ilk rapor:** nöron sayısı, kenar sayısı, modül başına ara nöron sayısı |
| 6 | **v0 ile karşılaştırma:** v0 tip grafındaki her path-integrated kenar (ör. LC10a → DNa02, 123) için yeni grafta gerçek 1–2 sıçramalı yollar var mı? | Rapor tablosu. **Bu, H11 kararının erken bir göstergesidir.** |

## Yol haritası

### P0 Temel (H1–H4)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Yukarıdaki 1–6 | Graf üretici v1 ve rapor `main`'de |
| `sign_overrides.yaml` ve `engineered_edges.yaml` şemaları | Boş ama doğrulanan dosyalar; yükleyici path-integrated kenarı reddediyor |
| **Derlenmiş Brian2 motoru** (nöron seviyesi seyrek bağlantı, `step(inputs, 20 ms)`, mevcut `ConnectomeSNN` arayüzü) | Hız ölçümü: kontrol adımı başına süre, gerçek zamana oran (**H4 karar noktası**) |
| Tüm-beyin kahini (Shiu modeli, Brian2, sunucuda) | Tek komutla bir uyaran için tüm-beyin DN yanıtı |
| **ML hattı doğrulaması** ([0009](../0009-ml-model-secim-protokolu.md) başlangıç sırası 1): MJX'te tek bir "uzan" becerisi, IK baz çizgisi + PPO, 5 tohum, MLflow, IQM raporu | Uçtan uca çalışan hat (**H4 karar noktası**) |
| `docs/prereg/ml/kol_becerileri.md` ön-kaydı | `main`'de, ilk tam eğitimden önce |

### P1 Kaçış (H5–H8)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Kaçış modülü (LC4, LPLC2 → KAÇ popülasyonu) | Graf manifestinde modül tanımı |
| Arka plan girdisi kalibrasyonu (ön-kayıtlı; yalnızca uyaransız taban; her shuffled grafa ayrı) | Taban hızları kahinle tolerans içinde; bütçe üç kolda eşit |
| Kaçış modülü **6 kabul testi** | Test raporu; ön-kayıtlı eşikler |
| **L3 v1**: filtre (τ = 50 ms) → z-skoru normalizasyonu → argmax → histerezis; `z_min`, varsayılan mod | Ön-kayıtta dondurulmuş; Ömer onayı |
| **T1 ve T1b bypass kolları** (aday ailesi gerçek kolla aynı) | Hakem (Yusuf) onayı |
| v0 (tip grafı) ile karşılaştırma | T1 raporunda ayrı satır |
| Kol becerileri: uzan, kavra, kaldır, bırak eğitimleri (arka planda) | MLflow kayıtları |

### P2 Yaklaş-dur + kol (H9–H14)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Hedefe yönelme modülü (LC10a → … → YAKLAŞ) | Modül tanımı; genişletmenin bulduğu ara nöronlar raporlanmış |
| **LC10a → DNa02 tüm-beyin testi** | **H11 karar noktası:** BRAIN mı `engineered` mı |
| Dur modülü (LC11 → DUR) | 6 kabul testi |
| T2 bypass | Hakem onayı |
| **Kol becerileri seçimi** ([0009](../0009-ml-model-secim-protokolu.md) iş 1) | **H14:** ön-kayıtlı kurala göre seçim, tüm adaylar raporlanmış |

### P3 Entegrasyon (H15–H20)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Uzanma kararı modülü (şeker GRN'leri → MN9 → UZAN) | 6 kabul testi; girdi eşlemesi `HAND-MADE` ve eşiksiz (A9) |
| UZAN → L4 beceri zinciri (uzan → kavra → kaldır) | Hakemliğin L2'den gelip gelmediği ölçülmüş; `L3-öncelik` karşılaştırma kolu ayrı raporlanmış |
| **AN kodlayıcı** (Ömer'in AN listesiyle) | `SensoryDrive` sözleşmesine uygun |
| **Öğrenilmiş dekoder** ([0009](../0009-ml-model-secim-protokolu.md) iş 2; DAgger öncelikli) | Üç kola aynı prosedür; **H20 karar noktası** |

### P4 Mars + öğrenme (H21–H28)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **İnce ayar** ([0009](../0009-ml-model-secim-protokolu.md) iş 3): CMA-ES, tip başına kazanç/eşik | Gerçek vs shuffled, eşit bütçe; **H22 karar noktası** (JAX gerekli mi) |
| T4 için modüllerin eğimli arazi ve kesinti altında testi | T4 CKS (Yusuf ile) |
| VNC vekili ([0009](../0009-ml-model-secim-protokolu.md) iş 4; Hat B GO ise) | Yuvaya v3; bypass'a karşı test |
| Final rapor: beyin ve ML bölümleri | Olumsuz bulgular dahil |

---

## Bağımlılıklar

| Mert'in ihtiyacı | Kimden | Ne zaman |
|---|---|---|
| CUDA sunucusu, MLflow, kayıt şeması | Yusuf | H2–H3 |
| Shuffled üretici | Yusuf | P0 sonu |
| Kol MJCF modeli (MJX'te çalışır) | Ömer | H3 |
| Ommatidia çıktısı, eşiksiz loom kodlayıcı | Ömer | P0 sonu / P1 başı |
| AN listesi, VNC vekili veri şeması | Ömer (B1) | H4 |
| T1–T4 sahneleri ve tohum havuzları | Ömer + Yusuf | Her aşamanın başı |

| Mert'ten beklenen | Kime | Ne zaman |
|---|---|---|
| Graf üretici v1 + manifest | Yusuf (shuffled üretici bunun üzerinde çalışır) | H2–H3 |
| Derlenmiş Brian2 motoru ve `step()` | Herkes | H4 |
| `ModeCommand` üreten L3 | Ömer (L4 rover) | P1 |
| Bypass kolları | Yusuf (CKS) | Her sınavdan önce |
| Kol becerileri | T3 entegrasyonu | P2 sonu |

## Dikkat edilecekler

- **Bypass'ı güçlü kur.** CKS'yi şişirecek en kolay hata zayıf bir bypass; gerçek kolla aynı aday listesi ve arama bütçesi.
- **Davranışa bakarak ayar yok.** `θ`, kalibrasyon, `z_min`, τ gibi sabitler davranıştan önce seçilir; ayarlananlar `tuned_on:` ile işaretlenir. Tohum tipi eklemek de buna dahil (A5).
- **Hakemliği L3'e koyma.** L3 yalnızca normalizasyon + argmax + histerezis.
- **Sürekli DN okumasına güvenme.** Yön parametresi yalnızca simetri testini ve taban kalibrasyonunu geçen popülasyonlardan.
- **Model seçimini sınav tohumlarında yapma**, tek "en iyi koşu" raporlama; IQM + güven aralığı.
- **ES önce, JAX sonra.** JAX motorunu yalnızca ölçüm gerektirirse yaz.
- **Tekrarlı devrelerde sönüm testi.** Kilitlenen bir devre tüm sistemi kalıcı bir moda sokabilir.

## Okuma listesi

- Shiu et al. 2024, *Nature* 634: tüm-beyin LIF modeli (ve github.com/philshiu/Drosophila_brain_model)
- Dorkenwald et al. 2024 ve Schlegel et al. 2024, *Nature* 634: FlyWire connectome ve anotasyonlar
- Synaptera `REPORT.md`: §2.1 (model), §3.2 (DNp15), §3.7 (koku kilitlenmesi), §3.8 (görsel DN taraması), §3.9b (eğitilmiş okuma); `flight/vnc_bridge.py` (okuma filtresi, MN9 eşiği)
- Agarwal et al. 2021, NeurIPS: "Deep RL at the Edge of the Statistical Precipice" (IQM, rliable)
- Ross, Gordon & Bagnell 2011: DAgger
- Hansen 2016: "The CMA Evolution Strategy: A Tutorial"; Salimans et al. 2017: OpenAI-ES
- MuJoCo Playground / Brax PPO örnekleri (manipülasyon)
