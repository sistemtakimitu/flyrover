# Ömer: Gövde, dünya ve gövde-ML sahibi

- **Rol:** Rover uzmanı, simülasyon & yazılım mühendisi
- **Sahip olduğu katmanlar:** L0 (MuJoCo dünyası, robotlar, arazi), L1 (sinek gözü, özellik kodlayıcılar), L4 (rover kontrolcüsü, kol RL becerileri), Gym ortamları ve görev sahneleri, Hat B'de sinek gövdesi (NeuroMechFly)
- **Hakemleri:** Mert (sensör → nöron arayüzü, RL algoritmaları), Yusuf (ortam API'si, tohum havuzları)
- **Yedeği:** Mert
- İlgili kararlar: [0003](../0003-simulasyon-ortami.md) · [0002](../0002-katmanli-mimari.md) · [0005](../0005-ml-stratejisi.md)

---

## Ulaşılması gereken nokta (H28 sonunda)

1. **Görev paketi:** `FlyRover/T1`–`T4` Gymnasium ortamları; her biri için eğitim / doğrulama / sınav tohum havuzları ve domain randomization.
2. **Robotlar:** 4 teker skid-steer rover (opsiyonel olarak 6 teker rocker-bogie) + 5 serbestlik dereceli kol ve paralel kıskaç; kamera, IMU, odometri, eklem enkoderi, temas ve kuvvet sensörleri.
3. **Sinek gözü:** İki geniş açılı kamera → altıgen ommatidia örneklemesi; hem özellik kodlayıcılarına hem FlyVis'e girdi verebiliyor.
4. **Kol becerileri:** MJX'te RL ile eğitilmiş uzan, kavra, kaldır, bırak becerileri; rastgele nesne ve pozlarda **≥ %90 başarı**, L3'ten gelen mod komutuyla çağrılabiliyor.
5. **Rover kontrolcüsü:** (v, ω) komutunu düz ve eğimli arazide kaymayı telafi ederek uygulayan L4 kontrolcüsü.
6. **Hat B (gövde tarafı):** NeuroMechFly yürüme düzeneği; BANC beyin+VNC çıktısını sinek gövdesine bağlayan arayüz.
7. **Görsel çıktı:** Tanıtım ve rapor için video render hattı (kayıtlardan render; simülasyonu yeniden koşturmadan).

---

## Yol haritası

### P0 Temel (H1–H4)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| Mevcut `rover.xml`'i yeni `sim/` yapısına taşı; MuJoCo 3 + MJX kurulumu | Mac'te CPU, sunucuda GPU üzerinde açılıyor |
| **5 DOF kol + paralel kıskaç** MJCF modeli, rover üstüne montaj | Eklem limitleri, kütle ve sürtünme belgelenmiş; kol rover'ı devirmiyor |
| Sensör seti: iki geniş açılı kamera, IMU, odometri, enkoder, temas, bilek kuvveti | `Observation` sözleşmesine uygun |
| **Sinek gözü:** kamera → altıgen ommatidia örneklemesi | Sol/sağ göz ayrı; FlyGym formatıyla uyumlu |
| Gymnasium API iskeleti, `step()` / `reset()`, `info` metrikleri | Duman testi CI'da çalışıyor |
| Prosedürel heightfield arazi v0 | Düz + hafif engebeli |

### P1 Kaçış (H5–H8)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **T1 sahnesi:** tehdit rastgele yön ve hızla yaklaşıyor | Tohum havuzları (Yusuf ile) |
| **Loom özellik kodlayıcı** ommatidia üzerinde (açısal büyüme hızı → LC4, açısal büyüklük → LPLC2, sol/sağ) | Mevcut `LoomingEncoder`'ın renk bağımsız ve **eşiksiz** sürümü (8°/s ve 20° eşikleri kaldırılır; çıktı sürekli ve monoton, A9 testi geçiyor); HAND-MADE etiketli |
| FlyVis girdi formatı | FlyVis ağına ommatidia girdisi verilebiliyor (köprüyü Mert yazar) |
| **L4 rover kontrolcüsü v1**: (v, ω) → teker torkları, kinematik + PID | Düz zeminde komut takibi hatası belgelenmiş |
| T1 mod komutlarını (KAÇ + yön) uygulayan L4 | Mert'in L3 v1'iyle entegre |

### P2 Yaklaş-dur + kol (H9–H14)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **T2 sahnesi:** rastgele konumda hedef kaya, dikkat dağıtıcılar | "1 m önünde durma" metriği `info`'da |
| Küçük hedef özellik kodlayıcı (→ LC10a, LC11) | HAND-MADE etiketli; eşiksiz (A9) |
| **Kol RL becerileri** (MJX, durum tabanlı, PPO/SAC): uzan, kavra, kaldır, bırak | Rastgele nesne ve pozlarda ≥ %90 başarı; MLflow'da kayıtlı |
| Becerilerin parametrik çağrılması: `UZAN(hedef_poz)`, `KAVRA()`, `KALDIR(yükseklik)` | `ModeCommand` → beceri eşlemesi |
| Eğimde rover kontrolcüsü (kayma telafisi) | Eğimli test sahnesinde komut takibi hatası |

### P3 Entegrasyon (H15–H20)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **T3 sahnesi ve uçtan uca entegrasyon**: L3 modları → L4 beceri çağırma | T3 bölümleri uçtan uca koşuyor |
| Nesne pozu algısı (kolun kavraması için; mühendislik algısı) | HAND-MADE etiketli; bilgi güvenlik duvarına uygun (yalnızca L3 parametresi olarak iletiliyor) |
| Becerilerin rover hareket ederken ve eğimde dayanıklılığı | Domain randomization altında başarı oranı |
| **Hat B / B2:** NeuroMechFly yürüme düzeneği; BANC beyin+VNC motor nöron çıktısını sinek gövdesine bağlama | MDN uyarımında gövde hareketinin ölçümü (**GO/NO-GO**, Mert ile) |

### P4 Mars (H21–H28)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **T4 Mars sahnesi:** eğim, kayalık arazi, dikkat dağıtıcılar, görev sırasında gelen tehdit | `info`'da kesinti ve göreve dönüş metrikleri |
| Tam domain randomization (sürtünme, kütle, ışık, renk, kaya şekli) | Ön-kayıtta tanımlı aralıklar |
| Opsiyonel: 6 teker rocker-bogie şasi | Yalnızca zaman kalırsa; ayrı ADR |
| **Video render hattı**: kayıtlardan render, kaynak etiketli ekran yazıları | Synaptera tarzı "neyi kim kontrol ediyor" etiketleri |
| Hat B / B3–B4 (GO ise): beş davranışın gövde ölçümleri; VNC vekili için veri | Mert'e veri seti |

---

## Bağımlılıklar

| Ömer'in ihtiyacı | Kimden | Ne zaman |
|---|---|---|
| CUDA sunucusu, MLflow | Yusuf | P0 ortası |
| Beyin motoru `step()` arayüzü (derlenmiş Brian2) | Mert | H4 |
| `ModeCommand` üreten L3 | Mert | P1'den itibaren |
| Tohum havuzu kilitleme mekanizması | Yusuf | P1 başı |

| Ömer'den beklenen | Kime | Ne zaman |
|---|---|---|
| Dünya v1 + `Observation` + ommatidia | Mert, Yusuf | H3–H4 |
| T1–T4 sahneleri | Mert (modüller), Yusuf (CKS) | Her aşamanın başı |
| Kol becerileri | Mert (L3 UZAN/KAVRA) | P2 sonu |

## Dikkat edilecekler

- **Bilgi güvenlik duvarı.** L4 politikaları kamerayı veya görev kimliğini görmemeli. Ödül tasarımı da görev bilgisini L4'e sızdırmamalı.
- **RL becerilerini beyinden bağımsız eğit.** Becerilerin başarısı beyne bağlı olmamalı; böylece T3'teki başarısızlıklar beyin ve gövde arasında ayrıştırılabilir.
- **Özellik kodlayıcıları renk bağımlı yapma.** Mevcut kırmızı maske Mars zemininde kırılgan; geometri ve hareket tabanlı özellikler tercih edilmeli.
- **Kodlayıcıda karar verme.** "Tehdit var/yok" gibi eşikler L1'de yasak ([0002](../0002-katmanli-mimari.md)); kararı beyin vermeli. Başarı düşükse eşik eklemek yerine sorun raporlanır.
- **Nesne pozu yalnızca L3 üzerinden L4'e gider** ve `HAND-MADE` etiketlidir; kol politikası hangi nesneye uzanacağını kendisi seçmez.
- **Sınav tohumlarına dokunma.** Hata ayıklama eğitim ve doğrulama havuzlarında yapılır.
- **Simülasyon ile beyin arasındaki zaman uyumu.** 20 ms kontrol adımı, 2 ms fizik adımı; render gecikmesi beyin girdisini kaydırmamalı.

## Okuma listesi

- MuJoCo 3 ve MJX belgeleri; MuJoCo Playground
- Wang-Chen et al. 2024, *Nature Methods* 21: NeuroMechFly v2 / FlyGym (göz modeli ve yürüme)
- Brax / MuJoCo Playground PPO ve SAC örnekleri (manipülasyon görevleri)
- Domain randomization (Tobin et al. 2017)
