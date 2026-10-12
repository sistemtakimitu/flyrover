# 0004. Connectome, nöron ve sinaps kuralları

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (hakem: Yusuf)

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
3. **Genişletme:** Her tohum nöronunun girdi ve çıktı ortaklarından, toplam girdisinin/çıktısının ≥ `θ` kadarını sağlayanlar 2 sıçramaya kadar ağa eklenir. Başlangıç değeri `θ = %1`; değer davranışa bakmadan seçilir ve config'te sabitlenir.
4. Bağlantılar **nöron-nöron** kurulur. Tip seviyesinde herkes-herkese bağlantı **kullanılmaz**.
5. **Path-integrated kenarlar simülasyonda yasaktır.** Yalnızca analiz ve rapor amacıyla hesaplanabilir.
6. **Bağlam girdisi:** Alt ağa alınmayan beyin bölgelerinin etkisi, her nörona kalibre edilmiş Poisson arka plan girdisiyle temsil edilir. Hedef: alt ağdaki taban ateşleme hızları, tüm-beyin kahinindeki taban hızlarla eşleşsin.

Beklenen boyut: birkaç bin nöron.

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

| Modül | Girdi | Çekirdek | Çıktı DN'leri | Risk |
|---|---|---|---|---|
| **Kaçış** | LC4, LPLC2 | — | GF (DNp01), DNp02, DNp04, DNp11, MDN | Düşük: ölçülmüş, güçlü yollar |
| **Hedefe yönelme** | LC10a | ara nöronlar | DNa01, DNa02, DNg13 | **Yüksek:** yol tüm beyinde doğrulanmalı |
| **Dur / don** | LC11, LPLC2 | — | DNp09 | Orta |
| **Uzanma kararı** | "hedef yakın ve ortada" → GRN benzeri girdi | Hortum uzatma (PER) devresi | MN9 benzeri karar nöronu | Orta: Synaptera'da çalışan tek yol, girdi eşlemesi elle |
| **İleri / keşif** | AN (yürüme durumu) | BPN | — | Yüksek: BPN'in bilinen görsel girdisi yok |
| Pusula (EPG → PFL3) | — | merkezi kompleks | — | **Ertelendi:** uniform LIF ile kararlı halka çekicisi beklenmez |

Kullanılmayacaklar: DNp07/DNp10 (Synaptera'da seçici çıkmadı), uçuş DN'leri (DNg02, DNp15).

### Nöron modeli

- **Varsayılan:** Shiu et al. 2024 LIF: v_dinlenme = v_reset = −52 mV, v_eşik = −45 mV, τ_m = 20 ms, τ_syn = 5 ms, refrakter 2,2 ms.
- **Varyantlar** (adaptasyon, literatür işaretleri, eksik NT tahminlerinin tamamlanması) ayrı bayraklarla açılır. Varyantla alınan her sonuç `MODEL_VARIANT` etiketi taşır ve yayınlanmış modelin sonucu yerine geçmez.

### Simülasyon motorları

| Motor | Rol |
|---|---|
| **JAX spiking motoru** (kendi yazılımımız) | Kapalı döngü ve eğitimde kullanılan motor. Seyrek matris, dt = 0,1 ms, GPU. Hedef: birkaç bin nöronlu alt ağda gerçek zamanın ≥ 10 katı. |
| **Brian2 referansı** | JAX motorunun doğruluk referansı |
| **Tüm-beyin kahini** (Brian2, 138.639 nöron, Shiu modeli) | Yalnızca kabul testlerinde |

**Eşdeğerlik koşulu:** JAX motoru, referans uyaran seti üzerinde Brian2 ile istatistiksel olarak eşdeğer olmadan kullanılmaz (popülasyon hızlarında korelasyon ≥ 0,95, nöron başına ortalama hız farkı tolerans içinde, 20 tohum). Kesin eşikler P0 ön-kaydında yazılır.

### Modül kabul testleri

Her modül ağa girmeden önce aşağıdakilerin hepsini geçmelidir. Kesin eşikler her modülün ön-kayıt dosyasında, koşudan önce yazılır.

| # | Test | Ölçüt (örnek) |
|---|---|---|
| 1 | **İzolasyon** | Sol girdi yalnızca sol DN'leri sürer |
| 2 | **Ayna simetrisi** | L/R girdisi değişince çıktı yer değiştirir; tabandaki L–R farkı küçüktür |
| 3 | **Sönüm** | Girdi kesildikten 200 ms sonra modül hızı < 0,1 Hz |
| 4 | **Shuffled null** | Etki, 5 shuffled grafın en büyüğünü aşar |
| 5 | **Tüm beyne transfer** | Aynı girdi tüm-beyin kahininde aynı DN'leri aynı yönde sürer |

Testi geçemeyen modül ya ağa alınmaz ya da açıkça `engineered` etiketiyle alınır ve CKS raporunda belirtilir.

### Eski graf

`config/type_graph.json` ve mevcut Brian2 SNN **v0** olarak korunur. Yeni nöron seviyesi graf, T1'de v0 ile karşılaştırılır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Tüm beyni simüle etmek | Synaptera: tek karar, dakikalar süren koşular, 3,5 GB RAM; RL için kullanılamaz. Kahin olarak tutulur. |
| Tip seviyesi graf (mevcut) | Seçiciliği siliyor; kenarların %72'si doğrusal varsayıma dayanıyor |
| BANC'ı simülasyon tabanı yapmak | Etiketleri daha az olgun, doğrulanmış hazır model yok. Hat B'nin sonucuna göre yeniden değerlendirilir. |
| FAFB + BANC sinaps sayılarını aynı ağda karıştırmak | İki farklı hayvan, farklı ölçek; ayıklanması zor hatalar |

## Sonuçlar

**Olumlu**
- Path-integrated varsayımı ortadan kalkar; sonuçlar tüm beyne daha iyi taşınır.
- Her modülün biyolojik geçerliliği beş testle belgelenir.

**Olumsuz / maliyet**
- Kendi spiking motorumuzu yazmak ve Brian2'ye karşı doğrulamak P0'ın en büyük işidir.
- Tüm-beyin kahini testleri pahalıdır (koşu başına dakikalar); gece testlerinde çalışır.
- Bazı modüllerin (özellikle hedefe yönelme) testi geçememe ihtimali gerçektir. Bu durumda T2 için o modül `engineered` olur ve bu açıkça raporlanır.

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0005 ML stratejisi](0005-ml-stratejisi.md) · [gorevler/mert.md](gorevler/mert.md)
- Mevcut: [docs/mimari_kararlar/hucre_tipi_grafi.md](../mimari_kararlar/hucre_tipi_grafi.md) · [docs/neuron_secim_kriterleri.md](../neuron_secim_kriterleri.md)
