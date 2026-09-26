# Görsel Algı ve Navigasyon (Perception & Navigation)

Rover'ın sensörlerinden (Kamera/Lidar) gelen verilerin, motor komutlarına dönüşmeden önce işlendiği **Görsel Algı (Optic Lobe)** ve **Navigasyon (Central Complex)** katmanlarının nöronal eşleşmeleri aşağıda derlenmiştir. Bu nöronlar, donanımdan gelen ham veriyi "anlamlı tehdit veya hedef" sinyallerine çevirerek doğrudan motor (DN) nöronlarımızı tetikler.

## 1. Temel Görüntü İşleme Katmanı (Ön İşleme / Pre-processing)

Bu katman olmadan diğer hiçbir üst düzey görsel algı çalışmaz. Kamera görüntüsünden hareket vektörlerinin (optic flow) çıkarıldığı yerdir.

| Görsel Nöron | İşlev | Rover Karşılığı |
|---|---|---|
| **T4 (ON) / T5 (OFF)** | Piksel seviyesinde yön-seçici hareket algılama. Biri aydınlanan, diğeri kararan kenarları tespit eder. | Kameradan gelen ham kareler (frames) arası Optik Akış (Optic Flow) hesaplamasının temel filtresi. |

## 2. Tehlike Tespiti (Threat Detection → Kaçış)

Bu nöronlar, genişleyen (üzerimize gelen) objeleri tespit edip tehlike eşiği aşıldığında kaçış manevralarını tetikler.

| Görsel Nöron | Ne Algılıyor | Bağlandığı Motor Nöron | Rover'daki Anlamı |
|---|---|---|---|
| **LC4** | Yaklaşan objenin **açısal genişleme hızı** (looming speed) | → **GF / DNp01** ve **DNp02/04/11** | Nesnenin yaklaşma hızı yüksekse tetiklenir (Hız eşiği). |
| **LPLC2** | Yaklaşan objenin **açısal büyüklüğü** (looming size) | → **GF / DNp01** | Nesne görüş alanının çoğunu kapladığında tetiklenir (Yakınlık eşiği). |

*(Bağlantı Kanıtı: LC4 ve LPLC2, Kaçış (GF) nöronunun optik lobdan aldığı girdinin %99,4'ünü oluşturur. İkisinin sinyali birleştiğinde (Hız x Büyüklük) ani kaçış refleksi tetiklenir.)*

## 3. Av / Hedef Seçimi ve Takip (Target Selection & Pursuit)

Rover'ın incelemesi gereken bir kaya veya gitmesi gereken bir hedef olduğunda devreye giren dikkat ve takip nöronlarıdır.

| Görsel Nöron | Ne Algılıyor | Bağlandığı Eylem | Rover Karşılığı |
|---|---|---|---|
| **LC10a** | Küçük, hareketli hedef. Takip (pursuit) başladığında bu nöronun sinyal kazancı (gain) artar (hedefe kilitlenme). | Yönlendirme / Dönüş (DNa grubu) | "İlgi objesi tespit edildi" ve "Hedefe kilitlenildi" sinyali (CV Confidence). |
| **LC11** | Çok küçük çevresel hareketler (~2,2° gibi hassas). | → **DNp09** (Donma / Freeze) | Beklenmedik küçük hareketlerde anlık "dur ve bekle" refleksi. |

## 4. Stabilizasyon ve Pusula (İç Navigasyon) - *Kritik Eksik Tamamlandı*

Mars yüzeyinde tekerlek kaymaları veya zemin bozuklukları nedeniyle rotadan sapmaları düzeltmek için biyolojik pusula ve stabilizasyon nöronları kullanılacaktır.

| Nöron Grubu | İşlev | Rover'daki Anlamı |
|---|---|---|
| **HS / VS (Lobula Plate)** | Geniş alan optik akışı okuyarak, canlının kendi hareketi veya dış etkenle sürüklenmesini (slip/drift) algılar. | Optomotor tepki (PID dengeleme). Rover kaydığında zıt yönde düzeltme torku. |
| **E-PG (Ellipsoid Body)** | Sadece dönüş hızını entegre ederek (karanlıkta bile) başın nereye baktığını belirten "İç Pusula" (Ring Attractor). | IMU (Inertial Measurement Unit) entegrasyonu. Mars'ta GPS olmadan yön bulma. |
| **FC2 + PFL3** | İstenen hedef açısını, E-PG'den gelen mevcut yön (heading) ile karşılaştırıp hata payı (error) üzerinden dönüş sinyali üretir. | Hedefe yönelim için kapalı çevrim (closed-loop) direksiyon algoritması. |

## 5. Robot Kol (Arm Sub-graph) İçin Yaklaşma Nöronları

| Nöron | İşlev | Rover Karşılığı |
|---|---|---|
| **DNp07 & DNp10** | Bir yüzeye veya objeye son yaklaşma anında bacakları öne uzatma ("iniş/landing") davranışını tetikler. | Hedefe ulaşıldığında Robot Kolun (Arm Sub-graph) açılması/uzatılması komutu. |

---

*Not: Eğer ileride rover'ın nesneleri rengine (örn. kırmızı Mars taşı vs. gri toprak) göre ayırt etmesi gerekirse, bu yapıya R-tipi (Fotoreseptör) ve renk-karşıtlığı (color-opponent) nöron devreleri de eklenecektir.*
