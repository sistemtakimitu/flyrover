# 0001. Vizyon ve başarı ölçütü

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Ekip (Mert, Ömer, Yusuf)
- **Revizyon (2026-10-12, inceleme sonrası):** Shuffled kontrolü giriş ve çıkış derecesini koruyacak şekilde tanımlandı; bypass'ın girdi ve çıktı sınırları netleştirildi; T1'in ne ölçtüğü ve "karar nerede verilir" kuralı eklendi; Synaptera'ya yapılan atıflar düzeltildi.
- **Revizyon 2 (2026-10-12):** Shuffled tanımı uygulanabilir hale getirildi (değiş tokuş ağırlık aralığı içinde; dereceler tam, sinaps toplamları yaklaşık korunur); bilgi birleştirme gerektiren T1b görevi eklendi; beyin kararları [0010](0010-noron-secimi-tohum-tipleri.md)'daki mod listesine göre güncellendi (KAVRA ayrı bir beyin kararı değil, UZAN'ın L4 beceri zinciri).

## Bağlam

FlyRover'ın ilk hedefi "sinek connectome'undan türetilen bir SNN'in rover'ı sürmesi ve robot kolla cisim kaldırması" idi. Faz 1 (kaçış) çalıştı, ancak iki sorun görünür hale geldi:

1. **Katkı ölçülmüyor.** Faz 1 testinde kontrol durumu "beyin kapalı = rover hareketsiz". LC4 hızını doğrudan geri vitese bağlayan herhangi bir kural da bu testi geçerdi. Kodlayıcı (tehdit algısı) ve çözücü (kazançlar, 0,5 s kalıcılık) elle yazılmış; aradaki 609 nöronluk alt ağın katkısı ayrıca ölçülmüyor.
2. **Synaptera'nın bulguları.** FlyWire v783 tüm-beyin modelini (Shiu et al. 2024) NeuroMechFly gövdesine bağlayan ön-kayıtlı çalışmada beyinden gelen **tek** davranışsal karar beslenme kararıydı (eşikli MN9 okuması; tetikleyicisi elle tasarlanmıştı). Açık döngü görsel DN taramasında 21 testten yalnızca biri geçti (DNp15, sapma yönü) ve o da sabit bir tek taraflı taban aktivitesi taşıyordu; kapalı döngüde kullanılabilir bir direksiyon sinyali vermedi. İtki DN'i (DNg02) sessiz kaldı, yaklaşma (loom) takip testlerinin 0/20'si geçti. DN'lerden eğitilen doğrusal okuma ilk denemede başarısız oldu (dönüş için çapraz doğrulanmış R² negatif) ve gerçek beyin kolu, shuffled ve beyni atlayan "bypass" kollarından daha iyi değildi.

Buradan çıkan ders: connectome **kısa, güçlü, ölçülmüş yollarda ayrık kararlar** için bilgi taşıyor; **tüm beyni kontrolcü olarak kullanmak** bugünkü modellerle çalışmıyor. "Sinek beyni rover'ı sürüyor" iddiası ise test edilemez.

## Karar

### Vizyon

> **Kararlarını sinek connectome'unun verdiği, hareketlerini makine öğrenmesinin öğrendiği bir rover + robot kol. Connectome'un katkısı her görevde sayıyla ölçülür.**

- **Beyin (connectome):** *ne* yapılacağına ve *ne zaman* yapılacağına karar verir: KAÇ, YAKLAŞ, DUR, UZAN. Hiçbir mod seçilmediğinde görev başına ön-kayıtta tanımlı varsayılan mod (BEKLE veya KEŞFET) uygulanır ([0010](0010-noron-secimi-tohum-tipleri.md)).
- **ML ve klasik kontrol:** bu kararın *nasıl* uygulanacağını öğrenir: teker torkları, kol yörüngesi, kavrama kuvveti. UZAN kararı L4'te uzan → kavra → kaldır beceri zincirini başlatır.

### Manşet ölçüt: Connectome Katkı Skoru (CKS)

Her benchmark görevi `T` için, kilitli **sınav tohumları** üzerinde (en az 20 bölüm, episode) üç kol koşturulur:

| Kol | Tanım |
|---|---|
| **Gerçek** | FAFB v783'ten kurulan alt ağ |
| **Shuffled** | Derece korunarak karıştırılmış alt ağ (5 farklı tohum). Kenarlar yalnızca **aynı işaret sınıfı ve aynı ağırlık aralığı içinde** çift-kenar değiş tokuşuyla (A→B, C→D ⇒ A→D, C→B) karıştırılır; ağırlık kenarla birlikte taşınır. Böylece her nöronun **giriş ve çıkış derecesi tam**, giriş/çıkış sinaps toplamı **yaklaşık** korunur (sapma ön-kayıtlı toleransla raporlanır; ağırlıklar farklıyken iki toplam aynı anda tam korunamaz). Öz-bağlantı ve çift kenar oluşturan değiş tokuşlar reddedilir. Girdi (L1'den sürülen) ve çıktı (L3'e okunan) nöronların kimliği korunur. |
| **Bypass** | Gerçek kolla **aynı L1 çıktısı** → beyinsiz bir eşleme (kural veya küçük MLP) → **DN aktivitesi biçiminde** bir çıktı → **aynı L3 kuralı**. Böylece üç kol yalnızca L2'de farklıdır. **Gerçek kolla aynı ayar/eğitim bütçesi.** |

Üç kolda L0, L1, L3 ve L4 **bayt düzeyinde aynı** config ile çalışır; yalnızca L2 değişir. Kol farkı başka bir katmandan geliyorsa CKS geçersizdir.

```
CKS(T) = S_gerçek − max(S_shuffled, S_bypass)
```

`S` = görev başarı oranı. CKS için bootstrap ile %95 güven aralığı raporlanır. **"Connectome katkı veriyor"** cümlesi yalnızca güven aralığının alt sınırı > 0 ise kurulabilir.

CKS ≤ 0 çıkması da bir sonuçtur ve aynı ağırlıkla raporlanır (bkz. [0006](0006-repo-kurallari.md)).

### Benchmark görevleri

| Görev | Tanım | Beyinden beklenen karar |
|---|---|---|
| **T1 Kaçış** | Rastgele yönden yaklaşan nesneden kaç | KAÇ + yön |
| **T1b Çift tehdit** | İki yönden, farklı hızlarda aynı anda yaklaşan iki nesne; ya da tehdit + yaklaşmayan bir dikkat dağıtıcı | KAÇ + doğru yön (iki girdinin birleştirilmesi) |
| **T2 Yaklaş-dur** | Rastgele konumdaki hedef kayaya git, 1 m önünde dur | YAKLAŞ, DUR |
| **T3 Al** | T2 + kayayı kolla kavra ve kaldır | + UZAN (kavra ve kaldır L4 beceri zinciri) |
| **T4 Mars** | Eğimli arazide T3; dikkat dağıtıcılar ve görev sırasında gelen tehdit | Hakemlik: tehdit → KAÇ, sonra göreve dönüş |

T4 projenin final sınavıdır. Davranışlar arası hakemliği connectome'un kendisi yapabiliyorsa, projenin en güçlü bilimsel sonucu bu olur. Bu iddia ancak hakemlik L3'te kodlanmamışsa kurulabilir ([0002](0002-katmanli-mimari.md), "Karar nerede verilir").

### Görevlerin ne ölçtüğü

- **T1 öncelikle bir aktarım testidir.** Yaklaşan nesne bilgisi L1'de zaten çıkarıldığı için güçlü bir bypass T1'i kolayca çözebilir. T1'de CKS ≈ 0 beklenen ve kabul edilebilir bir sonuçtur; T1'in asıl amacı altyapıyı ve üç kolu uçtan uca doğrulamaktır.
- **T1b ilk anlamlı CKS'dir.** Beynin iki tehdidi birleştirip doğru yönü seçmesi gerekir; bu, bypass'ın tek bir özellikten okuyamayacağı bir karardır. T1 ile aynı sahne ve modülü kullandığı için P1'de (H8) koşturulur; anlamlı ilk sayı T2'yi (H14) beklemez.
- **CKS > 0 ancak beynin birden fazla girdiyi birleştirmesi gereken görevlerde anlamlıdır:** sol/sağ tehdit ayrımı, aynı anda tehdit ve hedef, görev kesintisi ve göreve dönüş (T2–T4). Her görevin ön-kaydı, beynin hangi birleştirmeyi yapması gerektiğini yazar.
- L1 çıktısında görev kararını veren bir eşik varsa (ör. "tehdit var/yok"), o görevde CKS raporlanmaz; önce L1 düzeltilir ([0002](0002-katmanli-mimari.md)).

### Kapsam dışı (bilerek)

- Gerçek donanım. Proje yalnızca simülasyondur.
- Tüm beyni doğrudan kontrolcü olarak kullanmak. Tüm beyin yalnızca **doğrulama kahini** olarak kullanılır (bkz. [0004](0004-connectome-noron-ve-sinaps-kurallari.md)).
- Uçuş. Rover yerde gider; biyolojik karşılık **yürüme** devreleridir.
- Ticari kullanım. FlyWire verisi CC BY-NC 4.0'dır.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| "Sinek beyni rover'ı uçtan uca sürer" | Test edilemez. Synaptera tüm-beyin kontrolünün bugünkü modellerle çalışmadığını gösterdi. |
| Shuffled: yalnızca postsinaptik hedefi permüte etmek | Giriş derecesi dağılımını bozar; bazı nöronlar aşırı girdi alır, bazıları hiç almaz. Fark topolojiden değil derece dağılımından gelebilir. |
| Bypass'ın L3'ü atlayıp doğrudan mod üretmesi | Kollar iki katmanda birden farklı olur; CKS'nin kaynağı ayrıştırılamaz. |
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
