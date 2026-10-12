# Mert: Beyin ve beyin-ML sahibi

- **Rol:** Data scientist & ML engineer
- **Sahip olduğu katmanlar:** L2 (connectome, JAX motoru, modüller), L3 (mod seçici / VNC yuvası), beyne dokunan tüm ML, bypass kolu, Hat B veri tarafı
- **Hakemleri:** Yusuf (veri bütünlüğü, kurallar, eşit bütçe), Ömer (L1/L3 arayüz uyumu)
- **Yedeği:** Yusuf
- İlgili kararlar: [0004](../0004-connectome-noron-ve-sinaps-kurallari.md) · [0005](../0005-ml-stratejisi.md) · [0002](../0002-katmanli-mimari.md)

---

## Ulaşılması gereken nokta (H28 sonunda)

1. **Doğrulanmış bir beyin çekirdeği:** FAFB v783'ten nöron seviyesinde kurulan, en az **4 davranış modülünden** oluşan alt ağ (kaçış, hedefe yönelme, dur/don, uzanma kararı). Her modülün 5 kabul testi sonucu belgelenmiş: geçen modüller BRAIN, geçemeyenler `engineered` olarak raporlanmış.
2. **Hızlı ve doğru bir motor:** JAX spiking motoru, Brian2 ile istatistiksel olarak eşdeğer ve birkaç bin nöronluk alt ağı GPU'da **gerçek zamanın ≥ 10 katı** hızda çalıştırıyor.
3. **Ölçülmüş katkı:** T1–T4'ün her biri için gerçek / shuffled / bypass kollarının sonuçları ve **CKS** (Yusuf'un düzeneğiyle). Bypass her görevde güçlü kurulmuş ve hakem incelemesinden geçmiş.
4. **VNC yuvası:** v1 (elle) ve v2 (öğrenilmiş dekoder) çalışır durumda; v2'nin bypass'a karşı sonucu raporlanmış.
5. **Connectome ince ayarı:** Hücre tipi başına kazanç ve eşiklerin eğitildiği deney; gerçek ve shuffled graf eşit bütçeyle karşılaştırılmış.
6. **Hat B (veri tarafı):** BANC'tan DN hedefleri ve AN listesi belgelenmiş; GO kararı verildiyse VNC vekili v3 olarak yuvaya takılmış.

---

## Yol haritası

### P0 Temel (H1–H4)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| FAFB v783 + anotasyon indirme scriptini yeni yapıya taşı | Tüm dosyalar SHA-256 ile doğrulanıyor; CI'da hash testi |
| **Nöron seviyesi graf üretici** (`connectome/build_graph.py`): tohum tipleri → nöronlar → `θ` eşikli 2 sıçrama genişletme → nöron-nöron kenarlar | Manifest (parametreler, girdi hash'leri, çıktı hash'i); aynı girdiyle aynı hash; birim testleri |
| `sign_overrides.yaml` ve `engineered_edges.yaml` şemaları | Boş ama doğrulanan dosyalar; yükleyici path-integrated kenarı reddediyor |
| **JAX spiking motoru v0** (LIF, seyrek bağlantı, Poisson girdi, `step(inputs, 20 ms)`) | Mevcut `ConnectomeSNN` ile aynı arayüz |
| Brian2 eşdeğerlik testi (Yusuf'un test düzeneğiyle) | Referans uyaran setinde ön-kayıtlı eşdeğerlik ölçütleri sağlandı (**H4 karar noktası**) |
| Tüm-beyin kahini: Shiu modeli Brian2'de, sunucuda | Tek komutla bir uyaran için tüm-beyin DN yanıtı alınabiliyor |

### P1 Kaçış (H5–H8)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Kaçış modülü (LC4, LPLC2 → GF, DNp02/04/11, MDN) nöron seviyesinde | Graf manifestinde modül tanımı |
| Arka plan girdisi kalibrasyonu | Alt ağ taban hızları tüm-beyin kahinindeki taban hızlarla ön-kayıtlı tolerans içinde |
| Kaçış modülü **5 kabul testi** | Test raporu; ön-kayıtlı eşikler |
| **L3 mod seçici v1**: DN → {KAÇ, BEKLE} + yön; eşik, histerezis, kalıcılık | `ModeCommand` sözleşmesine uygun; Ömer'in onayı |
| **T1 bypass kolu**: loom özellikleri → KAÇ kuralı, aynı ayar bütçesi | Hakem (Yusuf) onayı |
| v0 (tip grafı) ile yeni graf karşılaştırması | T1 raporunda ayrı satır |

### P2 Yaklaş-dur (H9–H14)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Hedefe yönelme modülü (LC10a → … → DNa01/02, DNg13) | Modül tanımı |
| **LC10a → DNa02 tüm-beyin testi** | **H11 karar noktası:** BRAIN mı `engineered` mı |
| Dur/don modülü (LC11, LPLC2 → DNp09) | 5 kabul testi |
| L3 v1'e YAKLAŞ, DUR, KEŞFET modları; direksiyon parametresi yalnızca simetri testini geçen DN çiftlerinden | Taban kalibrasyonlu, ayna simetrisi testli |
| T2 bypass kolu | Hakem onayı |
| **Hat B / B1:** BANC'ta MDN, DNa02, DNp09'un VNC hedefleri; yürüme durumu taşıyan AN adayları | `docs/reports/banc_b1.md` |

### P3 Entegrasyon (H15–H20)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Uzanma kararı modülü (PER devresi; "hedef yakın ve ortada" → GRN benzeri girdi) | 5 kabul testi; girdi eşlemesi HAND-MADE etiketli |
| L3'e UZAN, KAVRA modları ve hakemlik (KAÇ > DUR > UZAN > YAKLAŞ > KEŞFET) | Hakemliğin connectome'da kendiliğinden olup olmadığının ölçümü raporlanmış |
| **AN kodlayıcı**: rover odometrisi ve temas → B1'de seçilen AN grupları | `SensoryDrive` sözleşmesine uygun |
| **Öğrenilmiş dekoder (VNC yuvası v2)**: DAgger veya RL | Bypass'a karşı sonuç (**H20 karar noktası**) |
| **Hat B / B2:** Ömer ile BANC beyin+VNC → NeuroMechFly MDN geri yürüme | **H14 GO/NO-GO** kararı (B2 başlangıcı P2 sonu) |

### P4 Mars + öğrenme (H21–H28)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **Connectome ince ayarı**: tip başına kazanç/eşik; surrogate-gradient, yedek olarak evrim stratejileri | Gerçek vs shuffled, eşit bütçe; MLflow'da üç kol yan yana |
| T4 için modüllerin eğimli arazi ve kesinti altında testi | T4 CKS (Yusuf ile) |
| Hat B / B4 (GO ise): VNC vekili | VNC yuvası v3, bypass'a karşı test edilmiş |
| Final rapor: beyin bölümü | Olumsuz bulgular dahil |

---

## Bağımlılıklar

| Mert'in ihtiyacı | Kimden | Ne zaman |
|---|---|---|
| CUDA sunucusu, MLflow, kayıt şeması, eşdeğerlik test düzeneği | Yusuf | P0 ortası |
| Ommatidia formatında göz çıktısı, loom özellikleri | Ömer | P0 sonu / P1 başı |
| T1–T4 sahneleri ve tohum havuzları | Ömer + Yusuf | Her aşamanın başı |

| Mert'ten beklenen | Kime | Ne zaman |
|---|---|---|
| JAX motoru ve `step()` arayüzü | Herkes | H4 |
| `ModeCommand` üreten L3 | Ömer (L4) | P1 |
| Bypass kolları | Yusuf (CKS) | Her görev sınavından önce |

## Dikkat edilecekler

- **Bypass'ı güçlü kur.** CKS'yi şişirecek en kolay hata zayıf bir bypass'tır; hakem incelemesinde ilk bakılacak yer burası.
- **Davranışa bakarak eşik ayarlama.** `θ`, arka plan girdisi, L3 eşikleri gibi sabitler davranıştan önce seçilir; ayarlananlar `tuned_on:` ile işaretlenir.
- **Sürekli DN okumasına güvenme.** DNp15 dersi: sol/sağ taban kalibrasyonu ve ayna simetrisi testi olmadan analog parametre okunmaz.
- **Hat B'ye haftada en fazla 1 gün.** Ana hat önceliklidir.
- **Tekrarlı devrelerde sönüm testi.** Kilitlenen bir devre tüm sistemi kalıcı bir moda sokabilir.

## Okuma listesi

- Shiu et al. 2024, *Nature* 634: tüm-beyin LIF modeli
- Dorkenwald et al. 2024 ve Schlegel et al. 2024, *Nature* 634: FlyWire connectome ve anotasyonlar
- Lappalainen et al. 2024, *Nature* 634: FlyVis, connectome kısıtlı görsel model
- Synaptera `REPORT.md`: özellikle §3.2 (DNp15), §3.7 (koku kilitlenmesi), §3.8 (görsel DN taraması), §3.9b (eğitilmiş okuma)
- Surrogate-gradient SNN eğitimi (Neftci, Mostafa & Zenke 2019)
