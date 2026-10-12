# 0010. Nöron seçimi: elle seçilmiş nöronlardan tohum tiplerine

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (hakem: Yusuf)

## Bağlam

Faz 1'de `config/neurons.json`'a 13 grupta **73 nöron** elle eklendi; her biri bir `root_id`. Bu yaklaşımın sorunları:

1. **Tek temsilci nöron devreyi temsil etmez.** Tek bir LC4'ün DNp04'e 24 sinapsı var ve DNp04'ü ateşleyemiyor; 55 LC4'ün toplamı ateşliyor. LPLC2 → GF bağlantısı tek nöron seviyesinde eşik altında kalıyor ([hucre_tipi_grafi.md](../mimari_kararlar/hucre_tipi_grafi.md)).
2. **Seçim hataları:** P9 olarak eklenen 4 nöron 4 farklı tipte çıktı; PFL3'ün `root_id`'si v783'te yok; BPN Tip 2'nin sol ve sağ nöronları farklı tiplerde (SMP459 / SMP460).
3. **Ara nöronlar eksik:** LC10a → DNa02 gibi yollar ancak path-integrated kenarlarla kurulabildi; bu kenarlar artık simülasyonda yasak ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)).
4. **Mod → DN eşlemesi yok:** Yeni L3 kuralı ([0002](0002-katmanli-mimari.md)) her mod için ayrık bir DN popülasyonu istiyor.

Soru "73 nöron yetersiz mi, yenileri mi eklenmeli?" idi. Cevap: **sorun sayı değil, yöntem.** Elle `root_id` eklemek her seferinde aynı seçim yanlılığını yeniden üretir.

## Karar

### 1. Yöntem değişikliği

- Ağa artık **tek tek nöron eklenmez** (kural B8, [0006](0006-repo-kurallari.md)).
- Ağ, **tohum hücre tiplerinden** üretilir: her tohum tipinin FlyWire v783 anotasyonundaki **tüm** nöronları (her iki taraf) alınır.
- Ara nöronlar elle seçilmez; [0004](0004-connectome-noron-ve-sinaps-kurallari.md)'teki **genişletme adımı** (≥ `θ` katkı, en fazla 2 sıçrama) onları veriden bulur.
- `config/neurons.json` ve `config/connectome_graph.json` **v0** (tarihsel) olur; yeni kod bunları okumaz.
- Tohum tipleri `config/modules.yaml` dosyasında tanımlanır (aşağıda şema). Graf üretici yalnızca bu dosyayı okur.
- `docs/neuron_secim_kriterleri.md`'deki 8 adımlı protokol **hücre tipi düzeyinde** uygulanır: tipin adı, süper sınıfı, nörotransmitteri ve **beklenen nöron sayısı** (taraf başına) anotasyonla karşılaştırılır. Graf üretici her tohum tipi için bulunan nöron sayısını raporlar; beklenenden sapma varsa durur.

### 2. Tohum tipleri ve mod popülasyonları

**Girdi tohumları** (L1'den sürülür):

| Tohum tipi | Modül | Not |
|---|---|---|
| LC4 | Kaçış | Yaklaşma hızı; v0'da taraf başına ~50 nöron |
| LPLC2 | Kaçış | Yaklaşma büyüklüğü; taraf başına ~100 nöron |
| LC10a | Hedefe yönelme | Küçük hareketli hedef; taraf başına ~115 nöron. Yalnızca LC10a alt tipi (LC10b–d değil) |
| LC11 | Dur / don | Küçük hedef; v0 tip grafında yoktu, eklendi |
| Labellar şeker GRN'leri | Uzanma kararı | Shiu et al. 2024'te şeker algısı için kullanılan GRN'ler; FlyWire anotasyonundan (gustatory, sugar/water) **her iki taraf**. Girdi eşlemesi "hedef yakın ve ortada" → GRN hızı, `HAND-MADE` ve eşiksiz (A9) |

**Çıktı tohumları ve mod popülasyonları** (L3 bunları okur; her DN tipi en fazla bir modda):

| Mod | DN popülasyonu | Mod içi parametre | Kanıt / risk |
|---|---|---|---|
| **KAÇ** | DNp01 (GF), DNp02, DNp04, DNp11, MDN | Yön: popülasyonun sol–sağ asimetrisi (ayna simetrisi testini geçerse) | LC4/LPLC2 → GF/DNp02/04/11 ölçülmüş ve güçlü; MDN geri yürüme (Bidaye et al.) |
| **YAKLAŞ** | DNae001 (DNa01), DNa02 | Yön: sol–sağ farkı (simetri testi şart) | DNa01/02 dönüşle ilişkili (Rayshubskiy et al.); LC10a → DNa02 yolu **tüm beyinde doğrulanmalı** (H11) |
| **DUR** | DNp09 | — | Donma (Zacarias et al. 2018); DNp09 → DNa02 ölçülmüş |
| **UZAN** | MN9 | — | Synaptera'da çalışan tek BRAIN yolu (şeker GRN → MN9 > 10 Hz). Tip adı (Synaptera'da CB0701, 2 nöron) FlyWire anotasyonu ve Shiu et al. ile teyit edilir |
| **KEŞFET / BEKLE** | — (varsayılan mod) | — | Hiçbir mod `z_min`'i aşmazsa uygulanır; görev başına ön-kayıtta; `HAND-MADE` |

**Yalnızca kaydedilen DN'ler** (hiçbir moda girmez, analiz ve sonraki kararlar için kaydedilir): DNg13, DNb05, DNb06 (dönüşle ilişkili diğer DN'ler), Foxglove (CB0890), Bluebell (DNg60).

Toplam **14 tohum tipi** (5 girdi + 9 çıktı) ve 5 kayıt tipi. Tohum tiplerinin tüm nöronları ve genişletme ile beklenen ağ boyutu birkaç bin nörondur; 73 elle seçilmiş nörondan çok daha büyük, ama tamamı veriden gelir.

### 3. Mevcut 73 nöronun durumu

| Grup (v0) | Nöronlar | Karar | Gerekçe |
|---|---|---|---|
| Tehdit algısı | LC4 ×2, LPLC2 ×2 | **Tohum tipi olarak tutuldu** | Tek temsilci yerine tipin tüm nöronları |
| Hedef takibi | LC10a ×2, LC11 ×2 | **Tohum tipi olarak tutuldu** | Aynı |
| Kaçış DN'leri | GF ×2, DNp02 ×2, DNp04 ×2, DNp11 ×2 | **Tutuldu** (KAÇ) | Ölçülmüş güçlü yollar |
| Kaçış DN'leri | DNp03 ×2, DNb01 ×2, DNa15 ×2 | **Ertelendi** | Sakkad tipi keskin dönüş; T1/T1b sonuçlarına göre (yön seçimi yetersizse) yeniden değerlendirilir. KAÇ popülasyonunu şimdilik küçük ve kanıtı güçlü tutuyoruz |
| Geri yürüme | MDN ×2 | **Tutuldu** (KAÇ) | Tipin tüm nöronları (taraf başına 2) |
| Direksiyon DN'leri | DNa01 ×2, DNa02 ×2 | **Tutuldu** (YAKLAŞ) | — |
| Direksiyon DN'leri | DNb05 ×2, DNb06 ×2, DNg13 ×2 | **Yalnızca kayıt** | Ayrık popülasyon kuralı; dönüş ilişkileri korelasyonel. Kayıtlarda simetri ve seçicilik ölçülür, sonra moda alınması ADR ile tartışılır |
| Durma | DNp09 ×2 | **Tutuldu** (DUR) | — |
| Durma | Foxglove ×2, Bluebell ×2 | **Yalnızca kayıt** | DN değiller ya da v0 grafında neredeyse bağlantısızlar; durma kararı DNp09'dan okunur |
| Durma | BRK ×2 (AN_GNG_53) | **Çıkarıldı** | Yükselen (ascending) nöron; doğal girdisi VNC'de, FAFB'de yok. Hat B'nin AN listesine aday olarak devredildi |
| İleri koşu | BPN ×8 (CL209, SMP459, SMP460, CB4187, SMP461) | **Ertelendi** | Tip adları Bidaye et al. 2020 ile tip düzeyinde doğrulanmadı (Tip 2'de sol/sağ tip uyuşmazlığı); bilinen görsel girdileri yok. İleri hareket şimdilik KEŞFET varsayılan modu (`HAND-MADE`) |
| Takip | P9 ×4 | **Çıkarıldı** | Dört nöron dört farklı tipte; tip düzeyinde yeniden seçilmeden kullanılamaz |
| Hareket algısı | T4a–d, T5a–d (8) | **Çıkarıldı** | Tek nöronlar optik akışı temsil edemez; optik akış gerekirse FlyVis (L1) sağlar |
| Stabilizasyon | VS1–6 | **Ertelendi** | T4'te eğimde kayma telafisi gerekirse FlyVis + HS/VS tipleriyle ayrı ADR |
| Pusula | EPG, PFL3, FC2A/B/C | **Ertelendi** | Uniform LIF ile kararlı halka çekicisi beklenmez; PFL3 `root_id`'si geçersiz. Tip düzeyinde ayrı bir çalışma |
| — | — | **Kullanılmayacak** | DNp07/DNp10 (Synaptera'da seçici değil), uçuş DN'leri DNg02 ve DNp15 |

### 4. `config/modules.yaml` şeması (taslak)

```yaml
version: 1
connectome: {dataset: FAFB, materialization: 783}
expansion: {theta: 0.01, max_hops: 2, min_synapses: 5}     # davranıştan önce sabitlenir
inputs:
  LC4:     {cell_type: LC4,    expected_per_side: [45, 60], module: kacis}
  LPLC2:   {cell_type: LPLC2,  expected_per_side: [90, 115], module: kacis}
  LC10a:   {cell_type: LC10a,  expected_per_side: [100, 130], module: hedef}
  LC11:    {cell_type: LC11,   expected_per_side: null, module: dur}           # ilk koşuda raporlanıp sabitlenir
  GRN_sugar: {annotation: {class: gustatory, sub_class: sugar/water, organ: labellum}, module: uzan}
modes:                                                     # her DN tipi en fazla bir modda
  KAC:    [DNp01, DNp02, DNp04, DNp11, MDN]
  YAKLAS: [DNae001, DNa02]
  DUR:    [DNp09]
  UZAN:   [MN9]                                            # tip adı anotasyonla teyit edilecek
record_only: [DNg13, DNb05, DNb06, CB0890, DNg60]
default_mode: {T1: BEKLE, T1b: BEKLE, T2: KESFET, T3: KESFET, T4: KESFET}
```

Beklenen nöron sayısı aralıkları v0 tip grafındaki sayılardan alınmıştır ve ilk graf üretiminde anotasyonla teyit edilir. `GRN_sugar` için anotasyon alan adları ilk üretimde FlyWire anotasyon dosyasındaki gerçek sütun adlarıyla eşleştirilir.

### 5. Yeni tohum tipi ekleme kuralı

Yeni bir tohum tipi ancak şunlarla eklenir:
1. Bu ADR'ye bir revizyon veya yeni bir ADR: hangi mod veya modül için, hangi literatürle.
2. Tip düzeyinde 8 adımlı protokol (ad, süper sınıf, NT, beklenen sayı).
3. Etkilenen modülün 6 kabul testinin yeniden koşturulması.
4. Davranış sonuçlarına bakarak tohum tipi eklemek yasaktır (A5); ekleme gerekçesi ön-kayıttan önce yazılır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| 73 nörona yenilerini elle eklemek | Seçim yanlılığı ve tek temsilci sorunu büyüyerek devam eder |
| Tip seviyesi grafla devam etmek (v0) | Herkes-herkese bağlantı ve path-integrated kenarlar ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)) |
| Tüm v0 tiplerini tohum yapmak | Pusula, BPN, P9 gibi doğrulanmamış veya kararsız devreler ilk CKS'yi riske atar; ayrık mod kuralıyla da çelişir |
| Tüm beyni simüle etmek | Synaptera: tek karar, yüksek maliyet; tüm beyin yalnızca kahin olarak kullanılır |

## Sonuçlar

**Olumlu**
- Ağ tamamen veriden ve tekrarlanabilir biçimde üretilir; elle seçim yalnızca tip düzeyinde ve gerekçeli.
- Mod popülasyonları ayrık; L3 normalizasyonu ([0002](0002-katmanli-mimari.md)) tanımlanabilir.
- Uzanma kararı, Synaptera'da gerçekten çalıştığı gösterilen tek yola dayanır.

**Olumsuz / maliyet**
- İleri hareket (KEŞFET) ve pusula connectome'dan gelmiyor; bu, sonuç tablolarında `HAND-MADE` olarak görünür.
- LC10a → DNa02 yolunun tüm beyinde geçmeme ihtimali gerçek; geçmezse T2'de YAKLAŞ `engineered` olur.
- LC11 ve GRN tipleri için beklenen nöron sayıları ilk graf üretiminde sabitlenecek.

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md) · [0006 Repo kuralları](0006-repo-kurallari.md) (B6, B8)
- v0: [config/neurons.json](../../config/neurons.json) · [hucre_tipi_grafi.md](../mimari_kararlar/hucre_tipi_grafi.md) · [rover_neurons.md](../mimari_kararlar/rover_neurons.md)
