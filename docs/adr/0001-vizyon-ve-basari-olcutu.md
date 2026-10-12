# 0001. Vizyon ve başarı ölçütü

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip (Mert, Ömer, Yusuf)

## Bağlam

FlyRover'ın ilk hedefi "sinek connectome'undan türetilen bir SNN'in rover'ı sürmesi ve robot kolla cisim kaldırması" idi. Faz 1 (kaçış) çalıştı, ancak iki sorun görünür hale geldi:

1. **Katkı ölçülmüyor.** Faz 1 testinde kontrol durumu "beyin kapalı = rover hareketsiz". LC4 hızını doğrudan geri vitese bağlayan herhangi bir kural da bu testi geçerdi. Kodlayıcı (tehdit algısı) ve çözücü (kazançlar, 0,5 s kalıcılık) elle yazılmış; aradaki 609 nöronluk alt ağın katkısı ayrıca ölçülmüyor.
2. **Synaptera'nın bulguları.** FlyWire v783 tüm-beyin modelini (Shiu et al. 2024) NeuroMechFly gövdesine bağlayan ön-kayıtlı çalışmada beyinden gelen **tek** davranışsal karar beslenme kararıydı (eşikli MN9 okuması). Sürekli direksiyon okuması (DNp15) doğrulamayı geçemedi, itki DN'i (DNg02) sessiz kaldı, yaklaşma (loom) testlerinin 0/20'si geçti, DN'lerden eğitilen ridge okuma başarısız oldu ve beyni atlayan "bypass" kolu gerçek beyin kolu kadar iyi sonuç verdi.

Buradan çıkan ders: connectome **kısa, güçlü, ölçülmüş yollarda ayrık kararlar** için bilgi taşıyor; **tüm beyni kontrolcü olarak kullanmak** bugünkü modellerle çalışmıyor. "Sinek beyni rover'ı sürüyor" iddiası ise test edilemez.

## Karar

### Vizyon

> **Kararlarını sinek connectome'unun verdiği, hareketlerini makine öğrenmesinin öğrendiği bir rover + robot kol. Connectome'un katkısı her görevde sayıyla ölçülür.**

- **Beyin (connectome):** *ne* yapılacağına ve *ne zaman* yapılacağına karar verir: KAÇ, YAKLAŞ, DUR, KEŞFET, UZAN, KAVRA.
- **ML ve klasik kontrol:** bu kararın *nasıl* uygulanacağını öğrenir: teker torkları, kol yörüngesi, kavrama kuvveti.

### Manşet ölçüt: Connectome Katkı Skoru (CKS)

Her benchmark görevi `T` için, kilitli **sınav tohumları** üzerinde (en az 20 bölüm, episode) üç kol koşturulur:

| Kol | Tanım |
|---|---|
| **Gerçek** | FAFB v783'ten kurulan alt ağ |
| **Shuffled** | Derece korunarak karıştırılmış alt ağ: presinaptik nöron, ağırlık ve işaret korunur, postsinaptik hedef alt ağ içinde permüte edilir (5 farklı permütasyon) |
| **Bypass** | Aynı L1 özellikleri → beyinsiz bir eşleme (kural veya küçük MLP) → aynı L3 modları. **Gerçek kolla aynı ayar/eğitim bütçesi.** |

```
CKS(T) = S_gerçek − max(S_shuffled, S_bypass)
```

`S` = görev başarı oranı. CKS için bootstrap ile %95 güven aralığı raporlanır. **"Connectome katkı veriyor"** cümlesi yalnızca güven aralığının alt sınırı > 0 ise kurulabilir.

CKS ≤ 0 çıkması da bir sonuçtur ve aynı ağırlıkla raporlanır (bkz. [0006](0006-repo-kurallari.md)).

### Benchmark görevleri

| Görev | Tanım | Beyinden beklenen karar |
|---|---|---|
| **T1 Kaçış** | Rastgele yönden yaklaşan nesneden kaç | KAÇ + yön |
| **T2 Yaklaş-dur** | Rastgele konumdaki hedef kayaya git, 1 m önünde dur | YAKLAŞ, DUR |
| **T3 Al** | T2 + kayayı kolla kavra ve kaldır | + UZAN, KAVRA |
| **T4 Mars** | Eğimli arazide T3; dikkat dağıtıcılar ve görev sırasında gelen tehdit | Hakemlik: tehdit → KAÇ, sonra göreve dönüş |

T4 projenin final sınavıdır. Davranışlar arası hakemliği connectome'un kendisi yapabiliyorsa, projenin en güçlü bilimsel sonucu bu olur.

### Kapsam dışı (bilerek)

- Gerçek donanım. Proje yalnızca simülasyondur.
- Tüm beyni doğrudan kontrolcü olarak kullanmak. Tüm beyin yalnızca **doğrulama kahini** olarak kullanılır (bkz. [0004](0004-connectome-noron-ve-sinaps-kurallari.md)).
- Uçuş. Rover yerde gider; biyolojik karşılık **yürüme** devreleridir.
- Ticari kullanım. FlyWire verisi CC BY-NC 4.0'dır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| "Sinek beyni rover'ı uçtan uca sürer" | Test edilemez. Synaptera tüm-beyin kontrolünün bugünkü modellerle çalışmadığını gösterdi. |
| Yalnızca seçilmiş nöronlar, ML yok | Sürekli kontrol ve kol için biyolojik devre yok; kol hiç gerçekleşmez. |
| Uçtan uca ML (kamera → motor) | Connectome'un rolü kalmaz. Bu seçenek yalnızca **bypass kontrol kolu** olarak var olur. |

## Sonuçlar

**Olumlu**
- Her iddia sayıyla desteklenir; proje bilimsel olarak savunulabilir hale gelir.
- Olumsuz bir sonuç da (CKS ≈ 0) yayınlanabilir ve değerlidir.
- Kol, connectome'da karşılığı olmasa bile vizyonun parçası olur: kararı beyinden, hareketi ML'den gelir.

**Olumsuz / maliyet**
- Her görev için üç kol koşturmak hesaplama maliyetini yaklaşık üç katına çıkarır.
- Bypass kolunu güçlü kurmak ek iş gerektirir. Zayıf bir bypass CKS'yi şişirir; bu yüzden bypass'ı ML sahibi kurar ve güçlü kurmakla yükümlüdür ([0005](0005-ml-stratejisi.md)).

## İlgili
- [0002 Katmanlı mimari](0002-katmanli-mimari.md) · [0005 ML stratejisi](0005-ml-stratejisi.md) · [0006 Repo kuralları](0006-repo-kurallari.md)
