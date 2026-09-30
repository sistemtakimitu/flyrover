# Hücre Tipi Seviyesinde Connectome Grafı

## Neden tek nöron değil de hücre tipi?

İlk yaklaşımda her hücre tipi **tek bir temsilci nöronla** modellendi (`config/neurons.json`). Bu, gerçek devreyi büyük ölçüde kaybettiriyordu:

- DNp04'e yaklaşık **55 LC4** birden bağlı. Tek bir LC4'ün DNp04'e 24 sinapsı var; biyolojik parametrelerle bu, DNp04'ü **ateşleyemiyor**. 55'inin toplamı (1064 sinaps) ise kolayca ateşliyor.
- Literatürde GF'nin ana girdisi olan **LPLC2 → GF** bağlantısı, tek LPLC2'nin GF'ye 5'ten az sinapsı olduğu için gürültü eşiğinde **tamamen kayboluyordu**. Tip seviyesinde: 539 sinaps/GF.
- 73 nöronun 21'i hiçbir şeye bağlı değildi.

Bu yüzden `config/type_graph.json` üretildi: her düğüm bir **(hücre tipi, taraf)** çiftidir ve o tipin **tüm** nöronlarını kapsar (ör. `LC4_L` = sol yarıdaki 54 LC4).

## Veri kaynakları (açık, token gerektirmez)

| Veri | Kaynak |
|---|---|
| Bağlantı tablosu (FAFB v783, 16.8M satır) | Dorkenwald et al. 2024, Zenodo [10676866](https://zenodo.org/records/10676866) |
| Hücre tipi, taraf, nörotransmitter etiketleri | Schlegel et al. 2024, [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations) |

`src/data/build_type_graph.py` ikisini de `data/cache/` altına indirir (~880 MB, bir kez) ve grafı **~20 saniyede** yerel olarak hesaplar. Böylece ekipteki herkes aynı grafı üretebilir.

## Ağırlıklar

Birim: **hedef tipin bir nöronunun aldığı ortalama sinaps sayısı.**

- **measured** (doğrudan): `W(A→B) = işaret(A) · Σ sinaps(A→B) / N_B`
- **path-integrated** (A → ara nöron k → B): `W(A→B) = Σ_k işaret(A)·işaret(k) · (S_Ak / girdi_k) · S_kB / N_B`
  A, k'nin toplam girdisinin `S_Ak / girdi_k` kadarını sağlar; k'nin B'ye verdiği sinapsların o kadarı A'ya yazılır. Böylece dolaylı bağlantılar doğrudanlarla aynı ölçektedir.

Filtreler (FlyWire standardı): nöron çifti başına **≥ 5 sinaps**; tip seviyesinde **|W| ≥ 1**.

**İşaret:** ACh uyarıcı (+1); GABA ve glutamat baskılayıcı (−1, Shiu et al. 2024 ile aynı). Bir tipin işareti, üyelerinin **çoğunluk** nörotransmitteridir; `known_nt` (deneysel olarak bilinen) tahmine göre önceliklidir. Bu, tek nöron tahmin hatalarını düzeltir — örneğin sağ GF'nin tahmini "glutamat" ama GF'nin kolinerjik olduğu biliniyor.

## Sonuç (Faz 1 + 2 tipleri: 50 düğüm, 609 nöron)

Literatürdeki devreler veride açıkça görülüyor:

| Devre | Bağlantı | Ağırlık |
|---|---|---|
| Kaçış (yaklaşma hızı) | LC4 → DNp04 / DNp02 / DNp11 / GF | 1064 / 499 / 544 / 329 (sol) |
| Kaçış (yaklaşma büyüklüğü) | LPLC2 → GF / DNp04 | 539 / 506 (sağ) |
| Hedefe dönüş | LC10a_L → DNa02_L (aynı taraf, dolaylı) | 123 |
| Donma → dönüş | DNp09 → DNa02 | 24–31 |

BPN tipleri bağlantısız: BPN'lerin görsel girdisi yok, bu beklenen bir durum. Faz 2'de "yürü" komutu olarak doğrudan uyarılacaklar.

## `config/neurons.json` denetimi

72/73 nöron resmi FlyWire etiketleriyle eşleşti ve **tüm sol/sağ çiftleri gerçekten iki farklı yarıda.** Düzeltilmesi gerekenler:

| Nöron | Sorun |
|---|---|
| **P9** (aSP9_1/2, pSP9_1/2) | Dört nöron dört **farklı** tipte (CB2793, LHAV2b2a, CB2973 [GABA], LHAV4a4 [glutamat]); sol/sağ çifti değiller. P9 seçimi 8 adımlı protokolle yeniden yapılmalı. |
| **BPN Type 2** | Sol SMP459, sağ SMP460 — farklı tipler. Hangisinin BPN olduğu makaleden teyit edilmeli (şimdilik ikisi de grafta). |
| **PFL3** | Root ID v783 etiketlerinde yok ve hiç sinapsı yok → ID eski/parça. Yeniden aranmalı. |
| **GF_2** | Nöron seviyesindeki grafta (`connectome_graph.json`) glutamat → **baskılayıcı** görünüyor; yanlış. Tip grafında düzeltildi. |

Resmi tip adları: DNa01 = `DNae001`, Foxglove = `CB0890`, Bluebell = `DNg60`, BRK = `AN_GNG_53` (bir *ascending* nöron, DN değil).
