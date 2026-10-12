# 0010. Nöron seçimi: elle seçilmiş nöronlardan tohum tiplerine

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (hakem: Yusuf)
- **Revizyon 1 (2026-10-12):** Anotasyon keşfi ([p0_tohum_tipleri.md](../reports/p0_tohum_tipleri.md)) sonrası tip adları ve şeker GRN tanımı netleşti: MN9 = CB0701, DNa01 = DNae001, şeker GRN = LB3c + LB3b (su hariç); şema `seeds` yapısına geçti; beklenen sayılar sabitlendi.

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
| Labellar şeker GRN'leri | Uzanma kararı | FlyWire anotasyonunda `cell_class: gustatory`, `cell_sub_class: sugar` (LB3c) + `sugar/low_salt` (LB3b), MxLbN siniri, **her iki taraf** (33 sol, 24 sağ). Su GRN'leri (LB3a) dahil değil. Shiu et al. 2024'ün 21 nöronluk listesi v783'te karışık çıkıyor (LB3c 9, LB3b 2, LB3d tuz 5, LB4b 4, 1 bulunamadı; hepsi sol); bu liste yalnızca tüm-beyin kahininde Shiu sonucunu tekrarlamak için kullanılır. Girdi eşlemesi "hedef yakın ve ortada" → GRN hızı, `HAND-MADE` ve eşiksiz (A9) |

**Çıktı tohumları ve mod popülasyonları** (L3 bunları okur; her DN tipi en fazla bir modda):

| Mod | DN popülasyonu | Mod içi parametre | Kanıt / risk |
|---|---|---|---|
| **KAÇ** | DNp01 (GF), DNp02, DNp04, DNp11, MDN | Yön: popülasyonun sol–sağ asimetrisi (ayna simetrisi testini geçerse) | LC4/LPLC2 → GF/DNp02/04/11 ölçülmüş ve güçlü; MDN geri yürüme (Bidaye et al.) |
| **YAKLAŞ** | DNa01 (FlyWire `cell_type: DNae001`), DNa02 | Yön: sol–sağ farkı (simetri testi şart) | DNa01/02 dönüşle ilişkili (Rayshubskiy et al.). Hemibrain/Namiki DNa01'in FlyWire karşılığı DNae001'dir (`hemibrain_type`); FlyWire'daki `DNa01` adlı tip ayrı bir nörondur (hemibrain VES006) ve kullanılmaz. LC10a → DNa02 2 sıçramada güçlü (AOTU019, AOTU025), yine de **tüm beyinde doğrulanmalı** (H11) |
| **DUR** | DNp09 | — | Donma (Zacarias et al. 2018); DNp09 → DNa02 ölçülmüş |
| **UZAN** | MN9 (FlyWire `cell_type: CB0701`) | — | Synaptera'da çalışan tek BRAIN yolu (şeker GRN → MN9 > 10 Hz). **Teyit edildi:** Shiu et al.'ın MN9 kimliği (720575940660219265) CB0701'in sağ nöronu; tip `ingestion_motor_neuron`, taraf başına 1. Şeker GRN → MN9 2 sıçramada zayıf (en iyi ara tip 8 sinaps); genişletmenin iki ucu buluşuyor mu graf üreticide ölçülür |
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

### 4. `config/modules.yaml` şeması

Geçerli dosya: [config/modules.yaml](../../config/modules.yaml); doğrulayıcı `connectome/modules.py`. Her tohum `seeds` altında tek bir kayıttır:

```yaml
seeds:
  LC10a:     {role: input, module: hedef, cell_type: LC10a,   expected_per_side: [100, 130]}
  GRN_sugar: {role: input, module: uzan,  expected_per_side: [20, 40],
              annotation: {cell_class: gustatory, cell_sub_class: [sugar, sugar/low_salt]}}
  DNa01:     {role: mode,  mode: YAKLAS,  cell_type: DNae001, expected_per_side: [1, 1]}
  MN9:       {role: mode,  mode: UZAN,    cell_type: CB0701,  expected_per_side: [1, 1]}
  DNg13:     {role: record,               cell_type: DNg13,   expected_per_side: [1, 1]}
```

- Seçici ya `cell_type` ya da `annotation` (sütun → değer veya değer listesi); ikisi birden olamaz.
- Aynı seçici iki tohumda kullanılamaz: bu, mod popülasyonlarının ayrıklığını ([0002](0002-katmanli-mimari.md)) dosya düzeyinde garanti eder.
- `expected_per_side`: sol ve sağ sayının her biri aralıkta olmalı; değilse graf üretimi durur. Aralıklar ilk keşif raporunda sabitlendi (davranışa bakılmadan).
- Tohum adı (ör. `DNa01`, `MN9`) literatürdeki addır; `cell_type` FlyWire v783 anotasyonundaki addır.

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
- FlyWire tip adları literatürden farklı olabiliyor (DNa01 → DNae001, MN9 → CB0701); keşif raporu her üretimde ad çakışmalarını listeler.
- Bazı tohumların NT tahmini zayıf (GF: karışık, güven 0,29; şeker GRN ortalama 0,47; MN9 0,45); işaret düzeltmeleri `sign_overrides.yaml` ile kaynaklı yapılır ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)).

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0004 Connectome](0004-connectome-noron-ve-sinaps-kurallari.md) · [0006 Repo kuralları](0006-repo-kurallari.md) (B6, B8)
- v0: [config/neurons.json](../../config/neurons.json) · [hucre_tipi_grafi.md](../mimari_kararlar/hucre_tipi_grafi.md) · [rover_neurons.md](../mimari_kararlar/rover_neurons.md)
