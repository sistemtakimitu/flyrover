# 0004. Connectome, nöron ve sinaps kuralları

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (hakem: Yusuf); shuffled üretici: Yusuf (hakem: Mert)
- **Revizyon (2026-10-12, inceleme sonrası):** Arka plan girdisi kalibrasyonu ön-kayıtlı, davranıştan bağımsız ve her kola ayrı uygulanan bir prosedür olarak tanımlandı; shuffled graf üretimi tanımlandı; kabul testlerine lezyon testi eklendi; P1 için varsayılan motor Brian2 (derlenmiş) oldu, JAX motoru ihtiyaç doğduğunda devreye giren bir hızlandırıcıya dönüştü.
- **Revizyon 2 (2026-10-12):** Shuffled değiş tokuşu ağırlık aralığı içine alındı (dereceler tam, sinaps toplamları yaklaşık); davranış modülleri tablosu [0010](0010-noron-secimi-tohum-tipleri.md)'daki tohum tipi kararıyla değiştirildi; shuffled üreticinin sahipliği tarafsızlık için Yusuf'a geçti.

## Bağlam

Mevcut graf (`config/type_graph.json`) 50 düğüm ve 609 nörondan oluşuyor. Her düğüm bir hücre tipi popülasyonu; A → B kenarı A'nın her nöronunu B'nin her nöronuna bağlıyor (herkes-herkese). 135 kenarın **97'si (%72) "path-integrated"**: çok adımlı yollar doğrusal bir varsayımla tek kenara indirgenmiş. Bu yaklaşım:
- tip içi seçiciliği ve retinotopiyi siliyor,
- ara nöronların eşik davranışını yok sayıyor (bir yol gerçek ağda iletmeyebilir),
- kritik Faz 2 yolu LC10a → DNa02'yi (123) tamamen bu varsayıma dayandırıyor.

Synaptera'dan dersler: alt ağda çalışan bir devre tüm beyinde susabilir; yoğun tekrarlı devreler kalıcı duruma kilitlenebilir; işaret tahminleri hatalı olabilir; tek taraflı taban aktivitesi sürekli okumayı bozar.

## Karar

### Veri kaynakları

| Kaynak | Rol | Sürüm / not |
|---|---|---|
| **FAFB / FlyWire** | Simülasyon tabanı (beyin) | **v783 sabit**, SHA-256 ile doğrulanır |
| Schlegel et al. 2024 anotasyonları | Hücre tipi, taraf, nörotransmitter | Sabit commit |
| **BANC** | DN'lerin VNC hedefleri, AN seçimi, Hat B | Yalnızca bilgi kaynağı; sinaps sayıları FAFB ile **aynı ağda karıştırılmaz** |
| MANC | BANC'ın VNC tarafına çapraz kontrol | — |
| FlyVis | Görsel ön işleme | Önceden eğitilmiş ağırlıklar |

Veri dosyaları repoya konmaz; indirme scripti hash'leri doğrular. FlyWire CC BY-NC 4.0'dır.

### Graf kurulumu (nöron seviyesi)

1. **Tohum tipleri** davranış modüllerinden seçilir (aşağıdaki tablo).
2. Tohum tiplerinin **tüm nöronları** gerçek kimlikleriyle alınır (`root_id`).
3. **Genişletme:** Bir nöronun toplam girdisinin (çıktısının) ≥ `θ` kadarını sağlayan ve ≥ 5 sinapslı ortakları 2 sıçramaya kadar ağa eklenir. Başlangıç değeri `θ = %1`; değer davranışa bakmadan seçilir ve config'te sabitlenir. **Yön (2026-10-12 netleştirme):** girdi tohumlarından yalnızca çıkış yönünde, mod ve kayıt tohumlarından yalnızca giriş yönünde genişletilir (`direction: directed`). Girdilerin yukarı akışı (optik lob) L1'in işidir; DN'lerin aşağı akışı (VNC) FAFB'de yoktur. Çift yönlü genişletme ~39 bin nöron (25 bini optik lob), yönlü genişletme ~9,3 bin nöron verir ([p0_graf_v1.md](../reports/p0_graf_v1.md)). Toplam girdi/çıktı, eşiksiz tüm sinapslarla hesaplanır.
4. Bağlantılar **nöron-nöron** kurulur. Tip seviyesinde herkes-herkese bağlantı **kullanılmaz**.
5. **Path-integrated kenarlar simülasyonda yasaktır.** Yalnızca analiz ve rapor amacıyla hesaplanabilir.
6. **Bağlam girdisi:** Alt ağa alınmayan beyin bölgelerinin etkisi, her nörona kalibre edilmiş Poisson arka plan girdisiyle temsil edilir. Hedef: alt ağdaki taban ateşleme hızları, tüm-beyin kahinindeki taban hızlarla eşleşsin.

Beklenen boyut: birkaç bin nöron (v1: 9.304 nöron, 291.383 kenar).

### Arka plan girdisi kalibrasyonu

Kalibrasyon bir **ayar adımıdır** ve CKS'yi doğrudan etkiler. Bu yüzden:

- **Prosedür ön-kayıtta sabitlenir:** hedef büyüklük (hücre tipi başına taban hızı), serbest parametreler (hücre tipi başına tek bir arka plan hızı; nöron başına parametre yok), optimizasyon yöntemi, adım sayısı ve tolerans.
- **Yalnızca uyaransız taban aktivitesi kullanılır.** Görev koşuları, davranış metrikleri ve uyaranlı tepkiler kalibrasyonda kullanılmaz.
- **Her kola ayrı ve aynı bütçeyle uygulanır.** Her shuffled graf kendi kalibrasyonunu aynı prosedürle alır; bütçe [0005](0005-ml-stratejisi.md)'teki eşit bütçe kuralına dahildir.
- Kalibre edilen değerler config'te `tuned_on: baseline` ile işaretlenir ve graf manifestine yazılır.
- Kalibrasyon toleransa ulaşamazsa sonuç raporlanır; tolerans gevşetilmez.

### Shuffled graf üretimi

[0001](0001-vizyon-ve-basari-olcutu.md)'deki tanım nöron seviyesinde şöyle uygulanır:
- Genişletilmiş alt ağ (adım 1–3) **gerçek graf üzerinde** bir kez kurulur; shuffled graflar bu alt ağın kenarlarından üretilir.
- Kenarlar **aynı işaret sınıfı ve aynı ağırlık aralığı** içinde çift-kenar değiş tokuşuyla karıştırılır; ağırlık kenarla birlikte taşınır. Ağırlık aralıkları sinaps sayısının log ölçekli aralıklarıdır (başlangıç önerisi: 5–7, 8–11, 12–19, 20–39, 40–79, ≥ 80); aralıklar ilk shuffled koşudan önce ön-kayda yazılır.
- **Neden aralık:** A→B (w₁) ve C→D (w₂) değiş tokuş edilip ağırlık kenarla taşınırsa A ve C'nin çıkış toplamı korunur, ama w₁ ≠ w₂ ise B ve D'nin giriş toplamı değişir. Dereceler ve iki yöndeki sinaps toplamları ağırlıklar farklıyken aynı anda tam korunamaz. Aralık içi değiş tokuş dereceleri **tam**, sinaps toplamlarını **yaklaşık** korur.
- Değiş tokuş sayısı kenar sayısının en az 10 katıdır.
- Üretici, birim testleriyle gelir: giriş/çıkış dereceleri **birebir** aynı; nöron başına giriş/çıkış sinaps toplamlarının göreli sapması ön-kayıtlı toleransın altında (sapma dağılımı raporlanır); işaret sınıfı başına kenar sayısı aynı; girdi ve çıktı nöronlarının kimliği aynı. Her shuffled graf kendi tohumu ve hash'iyle manifestte yer alır.

### Sinapslar

```
w_ij = işaret(i) × sinaps_sayısı(i → j) × w_syn        (w_syn = 0,275 mV, Shiu et al. 2024)
```

| Kural | Değer |
|---|---|
| Eşik | Nöron çifti başına ≥ 5 sinaps (FlyWire standardı) |
| İşaret | ACh → +1; GABA, Glu → −1 (Shiu ile aynı). Tahmin güveni kaydedilir. |
| İşaret düzeltmesi | Yalnızca `connectome/sign_overrides.yaml`; her satırda kaynak makale ve hakem onayı |
| Gecikme | 1,8 ms |
| Kenar kaynağı | `measured` veya `engineered` |
| Engineered kenar | Yalnızca `connectome/engineered_edges.yaml`; gerekçe + hakem onayı; mümkün olduğunca az |
| Elle düzenleme | **Yasak.** Graf yalnızca kodla üretilir; manifest (parametreler + girdi hash'leri + çıktı hash'i) commit edilir. |

### Davranış modülleri

Tohum tipleri, mod → DN popülasyonu eşlemesi, çıkarılan ve ertelenen tipler [0010](0010-noron-secimi-tohum-tipleri.md)'da karara bağlanmıştır. Özet:

| Modül | Girdi tohumları | Çıktı (mod popülasyonu) | Risk |
|---|---|---|---|
| **Kaçış** | LC4, LPLC2 | KAÇ: DNp01 (GF), DNp02, DNp04, DNp11, MDN | Düşük: ölçülmüş, güçlü yollar |
| **Hedefe yönelme** | LC10a | YAKLAŞ: DNae001 (DNa01), DNa02 | **Yüksek:** yol tüm beyinde doğrulanmalı |
| **Dur / don** | LC11 | DUR: DNp09 | Orta |
| **Uzanma kararı** | Labellar şeker GRN'leri ("hedef yakın ve ortada" → GRN, HAND-MADE) | UZAN: MN9 | Orta: Synaptera'da çalışan tek yol; girdi eşlemesi elle |

Ara nöronlar elle seçilmez; genişletme adımıyla (adım 3) veriden gelir. Kullanılmayacaklar: DNp07/DNp10 (Synaptera'da seçici çıkmadı), uçuş DN'leri (DNg02, DNp15). Pusula (EPG → PFL3) ve ileri yürüme (BPN, P9) ertelendi.

### Nöron modeli

- **Varsayılan:** Shiu et al. 2024 LIF: v_dinlenme = v_reset = −52 mV, v_eşik = −45 mV, τ_m = 20 ms, τ_syn = 5 ms, refrakter 2,2 ms.
- **Varyantlar** (adaptasyon, literatür işaretleri, eksik NT tahminlerinin tamamlanması) ayrı bayraklarla açılır. Varyantla alınan her sonuç `MODEL_VARIANT` etiketi taşır ve yayınlanmış modelin sonucu yerine geçmez.

### Simülasyon motorları

| Motor | Rol |
|---|---|
| **Brian2, derlenmiş hedef** (`cython` veya `cpp_standalone`) | **P1–P3 varsayılan motoru.** Kapalı döngü değerlendirmesi (T1–T3). Nöron seviyesi seyrek bağlantı, dt = 0,1 ms. `ConnectomeSNN.step()` arayüzü korunur. |
| **JAX spiking motoru** (kendi yazılımımız) | **Opsiyonel hızlandırıcı.** Yalnızca Brian2'nin yetmediği yüksek paralellik işlerinde: RL ile L3 dekoder eğitimi, surrogate-gradient ince ayar. İnce ayarın ilk yöntemi evrim stratejileri olduğu ve Brian2 ile çalıştığı için ([0005](0005-ml-stratejisi.md)) JAX motoru kritik yolda değildir; ihtiyacı [0009](0009-ml-model-secim-protokolu.md)'daki ölçümlerle belirlenir. Seyrek matris, GPU. Hedef: birkaç bin nöronlu alt ağda gerçek zamanın ≥ 10 katı. |
| **Tüm-beyin kahini** (Brian2, 138.639 nöron, Shiu modeli) | Yalnızca kabul testlerinde |

**Neden bu sıra:** Bugünkü yavaşlığın ana nedeni motor değil, `numpy` hedefi ve tip seviyesindeki herkes-herkese bağlantılar. Birkaç bin nöronluk seyrek bir alt ağ derlenmiş Brian2'de değerlendirme koşuları için yeterince hızlı olmalıdır. Bu, P0'daki en büyük riski (kendi motorumuzu yazmak) ilk CKS'nin kritik yolundan çıkarır. P0'da derlenmiş Brian2'nin hızı ölçülür; T1 sınavı (≥ 20 bölüm × 3 kol × 5 tohum) sunucuda bir gecede bitmiyorsa JAX motoru öne çekilir.

**Eşdeğerlik koşulu:** JAX motoru, referans uyaran seti üzerinde Brian2 ile istatistiksel olarak eşdeğer olmadan kullanılmaz (popülasyon hızlarında korelasyon ≥ 0,95, nöron başına ortalama hız farkı tolerans içinde, 20 tohum). Kesin eşikler, JAX motorunun ön-kaydında, ilk karşılaştırma koşusundan önce yazılır.

### Modül kabul testleri

Her modül ağa girmeden önce aşağıdakilerin hepsini geçmelidir. Kesin eşikler her modülün ön-kayıt dosyasında, koşudan önce yazılır.

| # | Test | Ölçüt (örnek) |
|---|---|---|
| 1 | **İzolasyon** | Sol girdi yalnızca sol DN'leri sürer |
| 2 | **Ayna simetrisi** | L/R girdisi değişince çıktı yer değiştirir; tabandaki L–R farkı küçüktür |
| 3 | **Sönüm** | Girdi kesildikten 200 ms sonra modül hızı < 0,1 Hz |
| 4 | **Shuffled null** | Etki, 5 shuffled grafın (derece korumalı, kendi kalibrasyonuyla) en büyüğünü aşar |
| 5 | **Tüm beyne transfer** | Aynı girdi tüm-beyin kahininde aynı DN'leri aynı yönde sürer |
| 6 | **Lezyon** | Modülün iddia edilen yolundaki ara nöronlar susturulunca (ör. LC4 → DNp04 yolundaki doğrudan kenarlar) DN tepkisi ön-kayıtlı oranda düşer; başka bir yoldan gelen etki raporlanır |

Testi geçemeyen modül ya ağa alınmaz ya da açıkça `engineered` etiketiyle alınır ve CKS raporunda belirtilir.

Test 2 (ayna simetrisi) ve tabandaki L–R farkı, sürekli bir parametrenin (yön, hız) okunabilmesi için **ön koşuldur** ([0002](0002-katmanli-mimari.md)). Tabanda tek taraflı aktivite gösteren DN çiftleri (Synaptera'daki DNp15 gibi) yalnızca ayrık mod seçiminde kullanılabilir.

### Eski graf

`config/type_graph.json` ve mevcut Brian2 SNN **v0** olarak korunur. Yeni nöron seviyesi graf, T1'de v0 ile karşılaştırılır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Tüm beyni simüle etmek | Synaptera: tek karar, dakikalar süren koşular, 3,5 GB RAM; RL için kullanılamaz. Kahin olarak tutulur. |
| Tip seviyesi graf (mevcut) | Seçiciliği siliyor; kenarların %72'si doğrusal varsayıma dayanıyor |
| BANC'ı simülasyon tabanı yapmak | Etiketleri daha az olgun, doğrulanmış hazır model yok. Hat B'nin sonucuna göre yeniden değerlendirilir. |
| FAFB + BANC sinaps sayılarını aynı ağda karıştırmak | İki farklı hayvan, farklı ölçek; ayıklanması zor hatalar |
| P0'da JAX motorunu kritik yola koymak | İlk CKS'yi kendi motorumuzun doğrulanmasına bağlar; derlenmiş Brian2 değerlendirme için muhtemelen yeterli. JAX, paralellik gerçekten gerektiğinde devreye girer. |
| Kalibrasyonu yalnızca gerçek grafa yapmak | Shuffled graf kalibre edilmemiş taban aktivitesiyle dezavantajlı başlar ve CKS şişer. |

## Sonuçlar

**Olumlu**
- Path-integrated varsayımı ortadan kalkar; sonuçlar tüm beyne daha iyi taşınır.
- Her modülün biyolojik geçerliliği altı testle belgelenir.
- İlk CKS, kendi motorumuzun doğrulanmasını beklemez.

**Olumsuz / maliyet**
- Kendi spiking motorumuzu yazmak ve Brian2'ye karşı doğrulamak hâlâ büyük bir iştir; P2'ye kayar ve P4'teki ince ayar buna bağlıdır.
- Her shuffled graf için ayrı kalibrasyon, hesaplama maliyetini artırır.
- Tüm-beyin kahini testleri pahalıdır (koşu başına dakikalar); gece testlerinde çalışır.
- Bazı modüllerin (özellikle hedefe yönelme) testi geçememe ihtimali gerçektir. Bu durumda T2 için o modül `engineered` olur ve bu açıkça raporlanır.

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0005 ML stratejisi](0005-ml-stratejisi.md) · [gorevler/mert.md](gorevler/mert.md)
- Mevcut: [docs/mimari_kararlar/hucre_tipi_grafi.md](../mimari_kararlar/hucre_tipi_grafi.md) · [docs/neuron_secim_kriterleri.md](../neuron_secim_kriterleri.md)
