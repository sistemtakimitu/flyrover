# FlyRover Yol Haritası

> Son güncelleme: 30.09.2026 · Durum: **Faz 1 tamamlandı**

## Hedef

Meyve sineği (Drosophila) beyninin gerçek bağlantı haritasından (FlyWire connectome) türetilen bir spiking sinir ağının (SNN), 3D simülasyonda:

1. bir rover'ı **sürmesi** (kaçma, hedefe dönme, ilerleme, durma),
2. bir robot **kolu kullanarak cisimleri tutup kaldırması**.

Proje açık kaynak ve **sadece simülasyon** üzerinedir; gerçek donanım hedefi yoktur.

## Strateji: önce tek davranış, uçtan uca

Projenin en büyük riski *"connectome'dan türetilen ağ, rover'ı gerçekten anlamlı biçimde sürebiliyor mu?"* sorusuydu. Bu yüzden tüm nöronlarla aynı anda uğraşmak yerine:

- Önce **tek bir davranışı** (kaçış) kameradan tekerleğe kadar **kapalı döngüde** çalıştırdık.
- Sonra davranışları **birer birer** ekliyoruz; her biri öncekinin altyapısını kullanır.
- **Kol en sona** kalır: rover sürüşü çalışmadan kolu bağlamanın anlamı yok.

Her faz, bir **otomatik test** (`pytest`) ve bir **video** ile biter. Test geçmiyorsa faz bitmemiştir.

## Fazlar

| Faz | Hedef | "Bitti" ölçütü | Durum |
|---|---|---|---|
| **0. Temizlik** | Graf ağırlıklarını düzelt, testleri çalışır hale getir | `pytest` 1 dakikada biter | ✅ |
| **1. Kaçış** | Üstüne gelen topu görünce geri kaç | Beyin açıkken çarpışma yok, kapalıyken var (`tests/test_escape_demo.py`) | ✅ |
| **2. Sürüş** | Hedef kayaya dön (LC10a → DNa02), ilerle (BPN), önünde dur (Foxglove/BRK) | Rover rastgele konumdaki bir kayaya gidip önünde duruyor | ⏳ Sıradaki |
| **3. Mars** | Engebeli arazi, eğimde kaymayı düzelt (VS/HS), pusula ile yönelme (EPG → PFL3) | Eğimli arazide rotadan sapmadan hedefe gidiyor | — |
| **4. Kol** | Hedefte kolu aç (DNp07/DNp10), cismi tut ve kaldır | Rover kayanın önünde durup kaldırıyor | — |

### Faz 1 sonucu

![Kaçış demosu](../assets/escape_demo.gif)

- Rover'ı **sadece** connectome ağı sürüyor; kaçış kuralı elle yazılmadı.
- Top ~1.9 m'ye geldiğinde kaçış başlıyor; beyin kapalıyken top rover'a çarpıyor.
- Kendiliğinden çıkan davranış: rover **mesafeyi koruyor** — top hızlandıkça daha hızlı geri gidiyor (0.8 m/s tehdit → ~0.8 m/s kaçış, 1.2 → ~1.2).

Detaylar: [Kapalı döngü mimarisi](mimari_kararlar/kapali_dongu.md) · [Hücre tipi grafı](mimari_kararlar/hucre_tipi_grafi.md)

## Faz 2 planı (sıradaki)

1. Sahneye bir **hedef kaya** (kırmızıdan farklı renk) ekle.
2. Kodlayıcı: hedefin sol/sağ görüş alanındaki konumu → `LC10a_L` / `LC10a_R` girdisi. Veride LC10a → DNa02 aynı tarafta güçlü (122).
3. **İleri yürüme** için BPN'lere bir "keşfet" komutu (sabit girdi) ver — BPN'lerin görsel girdisi yok, veride de bağlantısız; bu beklenen bir durum (BPN yürüme komut nöronu).
4. **Durma**: hedef yeterince büyüdüğünde (yakınlık) Foxglove/BRK'yi uyar. Foxglove GABAerjik, BPN'yi baskılayıp baskılamadığı veride kontrol edilecek.
5. Kabul testi: 5 farklı hedef konumunun hepsinde rover hedefin 1 m önünde durur.

## Bilerek ertelenenler

| Konu | Neden |
|---|---|
| Kol | Rover sürüşü çalışmadan anlamsız (Faz 4) |
| Yanal kayma / mecanum şasi | Sinekte biyolojik karşılığı yok; skid-steer yeterli |
| Retina, T4/T5 simülasyonu | Görüntü işleme "yaklaşan nesne" sinyalini doğrudan üretiyor; T4/T5 Faz 3'te (optik akış → VS/HS) gerekebilir |
| Öğrenme (STDP) | Projenin değeri gerçek connectome ağırlıklarından geliyor |
| Yeni nöron eklemek | Önce mevcutların doğruluğu (bkz. hücre tipi grafı dokümanındaki denetim) |

## Kod haritası

```
config/cell_types.json        Hangi hücre tipleri, hangi fazda
config/type_graph.json        Hücre tipi seviyesinde graf (SNN bunu kullanır)
config/neurons.json           Tek tek doğrulanmış temsilci nöronlar (tarihsel)
config/connectome_graph.json  Temsilci nöronlar arası graf (tarihsel)
src/data/build_type_graph.py  type_graph.json üretir (token gerektirmez)
src/data/fetch_data.py        connectome_graph.json üretir (CAVE token gerekir)
src/snn/network.py            Adım adım çalışan Brian2 SNN
src/sim/rover.xml             MuJoCo sahnesi
src/sim/env.py                Rover ortamı (teker komutu, kamera)
src/sim/interface.py          Kodlayıcı (kamera → nöron) ve çözücü (nöron → teker)
src/sim/escape_demo.py        Faz 1 kapalı döngü demosu
tests/                        Tüm testler: pytest
```
