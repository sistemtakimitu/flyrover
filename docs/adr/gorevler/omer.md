# Ömer: Hat B ve dünya sahibi

- **Rol:** Rover uzmanı, simülasyon & yazılım mühendisi
- **Sahip olduğu alanlar:** **Hat B** (BANC verisi, BANC beyin+VNC modeli, NeuroMechFly sinek gövdesi, GO/NO-GO deneyi, AN listesi, VNC vekili veri seti); **dünya** (L0 MuJoCo: rover + kol MJCF, sensörler, arazi; L1 sinek gözü ve özellik kodlayıcılar; T1–T4 görev sahneleri; L4 rover kontrolcüsü)
- **Hakemleri:** Mert (sensör → nöron arayüzü, FAFB ↔ BANC tip eşlemesi), Yusuf (ortam API'si, tohum havuzları, A9 testleri)
- **Yedeği:** Mert
- İlgili kararlar: [0003](../0003-simulasyon-ortami.md) · [0007](../0007-ekip-ve-gorev-dagilimi.md) · [0008](../0008-yol-haritasi.md) · [0002](../0002-katmanli-mimari.md)
- **Revizyon 2 (2026-10-12):** Görev dağılımı değişti ([0007](../0007-ekip-ve-gorev-dagilimi.md)): Hat B ana iş oldu ve H1'de başlıyor (GO/NO-GO H8); kol RL becerileri Mert'e geçti; dünya işinin yoğun kısmı P0'da.

---

## Ulaşılması gereken nokta (H28 sonunda)

**Hat B**
1. **BANC bilgi paketi:** MDN, DNa02, DNp09 ve diğer mod DN'lerinin VNC hedefleri; FAFB ↔ BANC tip eşlemesi ve farkları; lisans ve kullanım koşulları belgelenmiş.
2. **AN listesi:** Yürüme durumu ve temas taşıyan yükselen nöronlar; FAFB'deki karşılıkları; rover sensörlerine eşleme önerisi (Mert'in AN kodlayıcısı için).
3. **GO/NO-GO sonucu (H8):** BANC beyin+VNC LIF modeli + NeuroMechFly gövdesi; MDN uyarımında geri yürüme deseni ön-kayıtlı ölçütle test edilmiş. Sonuç olumlu da olumsuz da raporlanmış.
4. **GO ise:** Beş davranış (geri yürüme, dönüş, kaçış, dur, ön bacak uzanma) ön-kayıtlı ölçütlerle test edilmiş; **VNC vekili veri seti** şemaya uygun olarak Mert'e teslim edilmiş.

**Dünya**
5. **Görev paketi:** `FlyRover/T1`, `T1b`, `T2`, `T3`, `T4` Gymnasium ortamları; eğitim / doğrulama / sınav tohum havuzları (Yusuf ile) ve domain randomization.
6. **Robotlar ve sensörler:** 4 teker skid-steer rover + 5 DOF kol ve paralel kıskaç (MJX'te çalışır); kamera, IMU, odometri, eklem enkoderi, temas ve kuvvet.
7. **Sinek gözü ve L1:** İki kamera → altıgen ommatidia; eşiksiz loom ve küçük hedef kodlayıcıları (A9).
8. **Rover kontrolcüsü:** (v, ω) komutunu düz ve eğimli arazide uygulayan L4.

---

## Başlangıç: ilk 2 hafta (H1–H2)

| # | İş | Çıktı |
|---|---|---|
| 1 | **BANC erişimi ve lisans:** veri kaynağı, sürüm, kullanım koşulları; repoya veri girmez | `docs/reports/banc_b1.md` ilk bölüm |
| 2 | **NeuroMechFly / FlyGym kurulumu:** yürüme örneğinin sunucuda çalışması | Çalışan örnek, sürümler sabit |
| 3 | **Dünya v1 iskeleti:** mevcut `rover.xml` yeni `sim/` yapısında; kol MJCF taslağı (Mert'in ML hattı H3'te buna ihtiyaç duyuyor) | MJX'te açılan rover + kol |
| 4 | **İki sözleşmenin taslağı** ([0007](../0007-ekip-ve-gorev-dagilimi.md)): AN listesi formatı ve VNC vekili veri şeması | Mert ile birlikte yazılmış taslaklar |

## Yol haritası

### P0 (H1–H4): Dünya v1 + B1
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Rover + **5 DOF kol + kıskaç** MJCF; MJX uyumu | Eklem limitleri, kütle, sürtünme belgelenmiş; Mert'in "uzan" görevi bu modelle çalışıyor |
| Sensör seti ve `Observation` sözleşmesi | Duman testi CI'da |
| **Sinek gözü:** kamera → altıgen ommatidia | Sol/sağ ayrı; FlyGym formatıyla uyumlu |
| Gymnasium API iskeleti, heightfield arazi v0 | `reset/step/info` çalışıyor |
| **B1:** MDN, DNa02, DNp09 VNC hedefleri; AN adayları; iki sözleşme | `docs/reports/banc_b1.md`; sözleşmeler `main`'de (H4) |
| **B2 ön-kaydı:** "MDN uyarımında geri yürüme" ölçütü | `docs/prereg/hatb_b2.md`, B2 koşularından önce |

### P1 (H5–H8): B2 + T1/T1b
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **B2:** BANC beyin+VNC LIF modeli; MDN uyarımı → NeuroMechFly gövdesi | **GO / NO-GO (H8)**, rapor olumsuz bulgular dahil |
| T1 ve T1b sahneleri (tek tehdit; iki tehdit / tehdit + dikkat dağıtıcı) | Tohum havuzları (Yusuf ile) |
| Eşiksiz loom kodlayıcı (LC4: genişleme hızı, LPLC2: açısal boyut; renk bağımsız) | A9 testi geçiyor (Yusuf) |
| L4 rover kontrolcüsü v1 (kinematik + PID) | Düz zeminde komut takibi hatası belgelenmiş |

### P2 (H9–H14): B3 + T2
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **B3** (GO ise): dönüş (DNa02), kaçış, dur (DNp09), ön bacak uzanma | Her biri için ön-kayıtlı ölçüt ve sonuç |
| T2 sahnesi; küçük hedef kodlayıcı (LC10a, LC11; literatürden ayar eğrisi) | A9 testi; "1 m önünde durma" metriği |
| Eğimde rover kontrolcüsü | Eğimli sahnede komut takibi |
| **NO-GO ise:** BANC bilgi paketi raporu; zaman T2–T4 sahnelerine ve kol ortamına kayar | Rapor |

### P3 (H15–H20): B3–B4 + T3
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **B4** (GO ise): DN aktivitesi → gövde hareketi veri seti | Şemaya uygun; koşu bazında eğitim/test ayrımı yapılabilir |
| T3 sahnesi; nesne pozu algısı (`HAND-MADE`, yalnızca L3 üzerinden L4'e) | T3 bölümleri uçtan uca koşuyor |

### P4 (H21–H28): B5 + T4
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **B5:** Hat B final raporu; FAFB ↔ BANC farkları | Olumsuz bulgular dahil |
| T4 Mars sahnesi: eğim, kayalar, dikkat dağıtıcılar, görev kesintisi | `info`'da kesinti ve göreve dönüş metrikleri |
| Domain randomization; opsiyonel rocker-bogie (ayrı ADR) | Ön-kayıtta tanımlı aralıklar |

---

## Bağımlılıklar

| Ömer'in ihtiyacı | Kimden | Ne zaman |
|---|---|---|
| CUDA sunucusu | Yusuf | H2–H3 |
| FAFB tip adları ve mod DN listesi ([0010](../0010-noron-secimi-tohum-tipleri.md)) | Mert | H1 (hazır) |
| Beyin motoru `step()` (T1 entegrasyonu) | Mert | H4 |
| Tohum havuzu kilidi, A9 testleri | Yusuf | P1 başı |

| Ömer'den beklenen | Kime | Ne zaman |
|---|---|---|
| Kol MJCF (MJX uyumlu) | Mert (ML hattı) | **H3** |
| Dünya v1 + `Observation` + ommatidia | Mert, Yusuf | H4 |
| AN listesi + VNC vekili veri şeması | Mert | H4 |
| GO/NO-GO kararı | Ekip | H8 |
| VNC vekili veri seti (GO ise) | Mert | P3 sonu |

## Dikkat edilecekler

- **İki hattı dengele.** Dünya işinin yoğun kısmı P0'da; kol MJCF H3'te Mert'in kritik yolunda. P1'den sonra zamanın çoğu Hat B'ye.
- **B2'yi ön-kayıtla yap.** "Geri yürüme deseni" ölçütü (yön, ritim, bacak koordinasyonu) koşulardan önce yazılmalı; Synaptera'nın tek "çalışan" kararının da elle bir tetikleyiciye dayandığını unutma.
- **FAFB ve BANC sinaps sayılarını aynı ağda karıştırma** ([0004](../0004-connectome-noron-ve-sinaps-kurallari.md)); karşılaştırmalar tip düzeyinde.
- **Kodlayıcıda karar verme** (A9); seçicilik eğrileri literatürden, kaynaklı.
- **Bilgi güvenlik duvarı:** L4 kamerayı ve görev kimliğini görmez; nesne pozu yalnızca L3 üzerinden.
- **Sınav tohumlarına dokunma.**

## Okuma listesi

- BANC yayını ve veri sayfası (lisans ve kullanım koşulları dahil)
- Wang-Chen et al. 2024, *Nature Methods* 21: NeuroMechFly v2 / FlyGym (yürüme, göz modeli)
- Bidaye et al. 2014, *Science*: MDN ve geri yürüme
- Cheong et al. 2024 / MANC DN tiplemesi (DN'lerin VNC hedefleri)
- MuJoCo 3, MJX ve MuJoCo Playground belgeleri
