# 0003. Simülasyon ortamı: MuJoCo 3 + MJX, Gymnasium

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ömer (hakem: Mert)
- **Revizyon (2026-10-12, inceleme sonrası):** Beyin motoru satırları [0004](0004-connectome-noron-ve-sinaps-kurallari.md) ile uyumlu hale getirildi (P1–P3 derlenmiş Brian2, sonra JAX).

## Bağlam

Simülasyon ortamı üç farklı iş yükünü taşımak zorunda:
1. **Beyin kapalı döngüde** kamera görüntüsüyle çalışan değerlendirme koşuları (T1–T4). Paralellik düşük, görüntü gerekli.
2. **Kol ve hareket becerileri için RL eğitimi.** Milyonlarca adım, yüksek paralellik; görüntü gerekmez (durum tabanlı).
3. **Hat B:** BANC + NeuroMechFly sinek gövdesi simülasyonu ([0008](0008-yol-haritasi.md)).

Mevcut kod MuJoCo kullanıyor (`src/sim/rover.xml`: düz zemin, 4 teker, mocap tehdit topu). Ekipte macOS kullanan üyeler var.

## Karar

**Fizik motoru:** MuJoCo 3. **GPU paralel RL:** MJX (JAX). **Ortam API'si:** Gymnasium.

Kendi fizik motorumuzu **yazmayız**. "Kendi simülasyon ortamımız" = kendi robot modellerimiz, kendi arazimiz, kendi görevlerimiz ve kendi değerlendirme düzeneğimiz; hepsi MuJoCo üzerinde.

### İş yüküne göre çalışma modu

| İş yükü | Mod | Donanım |
|---|---|---|
| Beyin kapalı döngü değerlendirmesi (T1–T4) | MuJoCo (CPU fizik + render) + beyin motoru (P1–P3: derlenmiş Brian2, CPU; gerekirse JAX, GPU — bkz. [0004](0004-connectome-noron-ve-sinaps-kurallari.md)) | CUDA sunucusu; geliştirme için Mac'te CPU |
| Kol / hareket RL eğitimi | MJX, durum tabanlı, binlerce paralel ortam | CUDA sunucusu |
| Hat B sinek gövdesi | NeuroMechFly (FlyGym, MuJoCo) | CUDA sunucusu |

> Not: MJX'te toplu kamera render'ı sınırlıdır. Bu yüzden görüntü gerektiren koşular paralelleştirilmez; RL becerileri görüntüsüz eğitilir. Toplu görüntü gerekirse (ör. Madrona tabanlı toplu render) ayrı bir ADR ile değerlendirilir.

### Robotlar

| Bileşen | v1 (P0–P2) | v2 (P4) |
|---|---|---|
| Şasi | 4 teker skid-steer (mevcut `rover.xml`'den taşınır) | 6 teker rocker-bogie (opsiyonel) |
| Kol | 5 serbestlik dereceli kol + paralel kıskaç | Aynı; kütle ve sürtünme rastgeleleştirmesi |
| Sensörler | 2 geniş açılı kamera (sol/sağ "göz"), IMU, teker odometrisi, eklem enkoderleri, kıskaç temas + bilek kuvvet sensörü | Aynı |

### Sinek gözü

İki kameranın görüntüsü, FlyGym'deki yaklaşıma benzer biçimde **altıgen ommatidia ızgarasına** örneklenir. Bu format hem elle yazılmış özellik kodlayıcılarına (loom, küçük hedef) hem de FlyVis ağına girdi olabilir. Sol göz → `_L`, sağ göz → `_R` nöron grupları.

### Arazi ve sahneler

- Prosedürel heightfield arazi: düz (T1–T3), eğimli ve kayalık (T4).
- Hedef kayalar, dikkat dağıtıcı nesneler, yaklaşan tehdit nesneleri.
- **Domain randomization:** sürtünme, kütle, ışık, renk, kaya şekli.

### Tohum (seed) havuzları

Her görev için üç ayrı tohum havuzu tanımlanır: **eğitim**, **doğrulama**, **sınav**. Sınav tohumları kilitlidir; yalnızca değerlendirme düzeneği, etiketli bir commit üzerinde ve ön-kayıt dosyası mevcutsa açar ([0006](0006-repo-kurallari.md)).

### Ortam API'si

```python
env = gymnasium.make("FlyRover/T2-ApproachStop-v1", seed_pool="train")
obs, info = env.reset(seed=...)
obs, reward, terminated, truncated, info = env.step(motor_command)
# info: görev metrikleri, çarpışmalar, hedef mesafesi, kaynak etiketleri
```

Beyin, fizik motorunun içinde değil, dışında çalışır. İkisi `step()` arayüzüyle konuşur; motor ileride değişirse beyin tarafı etkilenmez.

## Değerlendirilen seçenekler

| Seçenek | Artısı | Neden seçilmedi |
|---|---|---|
| **MuJoCo + MJX (seçilen)** | NeuroMechFly ile aynı motor; GPU'da paralel RL; iyi temas fiziği; mevcut kod MuJoCo'da | — |
| Isaac Sim / Isaac Lab | Kol ve RL için çok güçlü, fotogerçekçi kamera | NVIDIA GPU gerektirir, macOS'ta çalışmaz; NeuroMechFly ile farklı motor |
| Gazebo (ROS) | Gerçek robot ekosistemi | RL için yavaş; projenin donanım hedefi yok |
| PyBullet / Webots | Kolay başlangıç | PyBullet aktif geliştirilmiyor; Webots'ta RL ölçeklenmesi zayıf |
| Kendi fizik motorumuz | Tam kontrol | Temas/kavrama fiziği yıllar alır; projenin özüyle ilgisiz |

## Sonuçlar

**Olumlu**
- Rover, kol ve Hat B (sinek gövdesi) aynı motorda; bilgi ve kod paylaşılır.
- JAX beyin motoru devreye girdiğinde (P2 sonrası) MJX ile aynı çerçevede olduğu için RL ve beyin aynı GPU'da çalışabilir.

**Olumsuz / maliyet**
- **Paylaşılan bir CUDA sunucusu zorunlu.** Kurulumu ve erişim güvenliği Yusuf'un sorumluluğundadır ([gorevler/yusuf.md](gorevler/yusuf.md)).
- Görüntü tabanlı koşular paralelleşmez; değerlendirme süreleri buna göre planlanır.
- Görsel kalite sınırlıdır. Tanıtım videoları için ayrı bir render hattı gerekebilir (P4).

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0005 ML stratejisi](0005-ml-stratejisi.md) · [gorevler/omer.md](gorevler/omer.md)
