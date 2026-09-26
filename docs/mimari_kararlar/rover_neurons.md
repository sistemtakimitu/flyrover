# Rover Nöron - Aksiyon Eşleştirmeleri (Mimari Kararlar)

Omnidirectional bir şasi için gereken temel hareket serbestlik dereceleri (DOF) ile connectome literatüründe **doğrudan doğrulanmış** en iyi nöron eşleşmeleri aşağıda derlenmiştir. Biyolojik karşılığı bulunmayan veya zayıf kanıtlı durumlar açıkça belirtilmiş olup, bu kısımların mühendislik yaklaşımlarıyla (uydurma eşleşmeler yapılmadan) çözülmesi planlanmaktadır.

## 1. Doğrusal Hareket (Translation)

| Rover Hareketi | Nöron | Kanıt / Not |
|---|---|---|
| **Düz ileri (sabit hız)** | **BPN (Bolt Protocerebral Neurons)** | Hızlı, uzun süreli, dümdüz ileri yürüyüşü tetikleyen tek merkezi beyin nöron tipi budur; adı Usain Bolt'tan gelir ve yürüme hızını kademeli (graded) olarak kontrol eder — yani "gaz pedalı" tam olarak bu nörona ait. |
| **İleri + hedefe kilitlenerek hafif dönüş** | **P9** | P9, ipsilateral dönüş bileşenli ileri yürüyüşü tetikler; kur yapma sırasında bir erkeğin dişiyi takip etmesi için gereklidir — yani "hedefi takip ederek ilerleme" moduna karşılık gelir. |
| **Düz geri (sabit hız)** | **MDN (simetrik aktivasyon)** | Dört MDN'nin simetrik uyarımı düz geri yürüme, asimetrik uyarımı ise geri dönüşle sonuçlanır. |
| **Geri + dönüş** | **MDN (asimetrik)** veya **MooSEZ nöronları** | MooSEZ, MDN'ye monosinaptik bağlı SEZ kökenli bir nöron çifti; simetrik aktivasyonda düz geri yürüme, asimetrik aktivasyonda geri dönüş üretir — MDN'nin geri yürüyüş devresine giriş sağlayan üst-kademe bir alternatif. |
| **Yanal kayma (strafe)** | ⚠️ **Doğrudan biyolojik karşılık yok** | Sinekler mecanum tekerlekli bir robot gibi rotasyonsuz yanal kayma yapmaz. Buna denk gelen tek bir komut nöronu tespit edilememiştir. Bu hareket mühendislik katmanında (örn. sol/sağ DN sinyallerini rover'ın omnidirectional teker kinematiğine özel bir dönüşüm matrisiyle karıştırarak) türetilecektir. |

## 2. Dönüş (Rotation / Yaw)

| Rover Hareketi | Nöron | Kanıt / Not |
|---|---|---|
| **Yerinde dönüş (nokta dönüşü)** | **DNa01, DNa02, DNb05, DNb06, DNg13** (asimetrik) | Bu beş DN tipinin sağ-sol aktivite farkı, vücudun rotasyonel hızıyla doğrusal korelasyon gösterir. Dördü aynı yönlü (ipsiversive), DNb06 ise ters yönlü (contraversive) dönüşle ilişkilidir. "Sol taraf aktif = sağa dön" mantığıyla PID benzeri sürekli direksiyon sinyali üretir. |
| **Sürekli rota düzeltmesi (ince manevra)** | Aynı DN seti (özellikle **DNa02 + DNg13**) | Bu ikisi en güçlü korelasyonu gösterir ve farklı bacak hareketlerine ayrı ayrı etki eder — iki kanallı bir direksiyon kontrolcüsü (fine/coarse steering) olarak ayrıştırılabilir. |
| **Ani/keskin kaçınma dönüşü (saccade)** | **DNb01** (+ **DNa15**), hub olarak **DNp03** | DNp03, görsel yaklaşma (looming) sinyalini alıp DNb01 ve DNa15'e aktararak ani kaçınma dönüşlerini (saccade) tetikleyen bir merkez görevi görür — "tehdit anında sert manevra" komutu olarak modellenecektir. |

## 3. Hız Modülasyonu / Durma

| Rover Hareketi | Nöron | Kanıt / Not |
|---|---|---|
| **Hızlanma / ivmelenme** | **BPN** (graded kontrol) | BPN aktivasyon seviyesi arttıkça yürüme hızı kademeli olarak artar — analog bir "throttle" sinyali gibi kullanılabilir. |
| **Yumuşak durma (sadece ileri hareketi kes)** | **Foxglove (FG)** | İleri yürüyüşü baskılayan GABAerjik bir "walk-OFF" nöronu; dönüşü etkilemez. |
| **Yumuşak durma (sadece dönüşü kes)** | **Bluebell (BB)** | Dönüşü baskılayan GABAerjik nöron; ileri hareketi etkilemez. FG ve BB birlikte, "sadece direksiyonu kilitle" veya "sadece ileri gidişi durdur" gibi ayrık komutlar için ideal bir çifttir. |
| **Acil/tam fren (tüm komutları geçersiz kıl)** | **Brake (BRK)** | Hem ileri hem geri hem dönüş komutlarını tamamen bastırır ve eklem direncini artırarak fiziksel bir kilitlenme etkisi yaratır — motorlara aktif frenleme/tork direnci uygulamak için idealdir. |
| **Tehdide bağlı donma (freeze)** | **DNp09** | Yürüme hızı düşükken tehdit algılandığında donma olasılığı artar; DNp09 bu seçimi yöneten kritik nörondur. *(Not: DNp09, P9 ile aynı anatomik nöron olabilir ve bağlama göre ya donma ya da ileri+dönüşle takip davranışı üretir).* |

## 4. Kaçış / Sıçrama (Acil Manevra Sınıfı)

| Rover Hareketi | Nöron | Kanıt / Not |
|---|---|---|
| **Yönsüz, en hızlı panik kaçışı** | **GF = DNp01 (Giant Fiber)** | Sinekteki en kalın/hızlı ileten nöron; yön belirlemeden ani, kısa süreli kalkış/sıçrama tetikler. |
| **Yönlü ileri kaçış sıçraması** | **DNp11** | Aktivasyonu doğrudan ileri yönlü sıçrama/kalkışa yol açar. |
| **Yönlü, kontrollü geri kaçış** | **DNp02 + DNp04 (birlikte)** | Bu ikisinin ortak aktivasyonu, GF'ninkinden daha yavaş ama yön kontrollü bir geri sıçrama üretir — rover'da "engelden uzaklaşarak geri çekil" komutu için MDN'den daha "acil" bir alternatif. |

---

## 🏗️ 4 Katmanlı Komut Mimarisi Önerisi

Omnidirectional şasi tasarımı için aşağıdaki 4 katmanlı komut mimarisi planlanmıştır:
1. **Taşıma katmanı:** BPN (ileri) / MDN (geri) / P9 (ileri+takip)
2. **Direksiyon katmanı:** DNa01 / DNa02 / DNb05 / DNb06 / DNg13'ün asimetrik kombinasyonu (sürekli yaw sinyali)
3. **Durdurma katmanı:** FG/BB (yumuşak, seçici) → BRK (sert, tam) → DNp09 (bağlamsal donma)
4. **Acil katman:** GF (yönsüz panik) / DNp11 / DNp02+DNp04 (yönlü kaçış)

*(Not: Yanal strafe için connectome'da gerçek bir eşleşme olmadığı için, bu hareket ya mekanik/kinematik katmanda çözülecek ya da DNa/DNb/DNg dönüş sinyalleri rover'ın teker geometrisine özgü bir dönüşüm matrisiyle yorumlanarak uygulanacaktır. Bu, biyolojik bir eşleşme değil mühendislik katmanı çözümüdür.)*
