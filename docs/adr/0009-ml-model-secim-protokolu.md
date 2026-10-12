# 0009. ML model seçim protokolü

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Mert (hakem: Yusuf)

## Bağlam

"Hangi model daha iyi?" sorusu tek başına tanımsızdır. Projede birbirinden bağımsız **dört ML işi** var ve her birinde "daha iyi"nin anlamı farklı ([0005](0005-ml-stratejisi.md)):

| İş | "Daha iyi" ne demek |
|---|---|
| L4 kol becerileri | Rastgeleleştirilmiş nesne ve pozlarda daha yüksek başarı, aynı hesaplama bütçesiyle |
| L3 öğrenilmiş dekoder | Kapalı döngüde daha yüksek görev başarısı; ama sonuç CKS ile okunur, çünkü aynı seçim üç kola da uygulanır |
| L2 connectome ince ayarı | Gerçek ve shuffled arasındaki farkın büyüklüğü (topolojinin katkısı) |
| VNC vekili | Ayrılmış sinek gövdesi verisinde daha düşük tahmin hatası, sonra kapalı döngüde tutarlılık |

RL'de az tohumla, eşit olmayan bütçeyle ve tek bir "en iyi koşu" ile model seçmek yanıltıcı sonuçlar verir. Synaptera'daki eğitilmiş okuma denemesi de seçim kuralını önceden yazmanın değerini gösterdi: ridge ızgarası ve λ seçim kuralı sabit olduğu için olumsuz sonuç tartışmasız raporlanabildi.

## Karar

### Genel kurallar (her ML işi için)

1. **Ön-kayıt:** Her seçim için `docs/prereg/ml/<iş>.md` dosyası, ilk aday eğitilmeden önce `main`'e girer. İçeriği: aday listesi, birincil metrik, ikincil metrikler, bütçe, tohumlar, karar kuralı.
2. **Tek birincil metrik.** İkincil metrikler raporlanır ama seçimi belirlemez.
3. **Klasik baz çizgisi zorunlu.** Her işte ML'siz bir baz çizgi vardır ve ML adayı onu yenemezse baz çizgi seçilir.
4. **Eşit bütçe:** Her aday aynı ortam adımı **ve** aynı GPU saati sınırıyla eğitilir; hiperparametre araması her aday için aynı deneme sayısıyla (başlangıç önerisi: 16 deneme, rastgele arama) yapılır.
5. **Tohumlar:** Her aday en az **5 eğitim tohumuyla** eğitilir. Seçim yalnızca **doğrulama** tohumlarında yapılır; sınav tohumları seçimde kullanılmaz (A4).
6. **İstatistik:** Sonuçlar tohumlar arası **IQM** (çeyrekler arası ortalama) ve **bootstrap %95 güven aralığı** ile raporlanır (rliable yaklaşımı). Tek bir "en iyi koşu" raporlanmaz.
7. **Karar kuralı:** En yüksek IQM'li aday seçilir; güven aralıkları en basit adayınkiyle örtüşüyorsa **daha basit aday** seçilir (basitlik sırası ön-kayıtta yazılır).
8. **Hepsi raporlanır:** Seçilmeyen ve başarısız olan adaylar da `docs/reports/ml/` altında raporlanır.
9. **Kayıt:** Her koşu MLflow'da `<iş>/<aday>/<tohum>` adlandırmasıyla, config + commit hash'iyle (C4).

### İş bazlı protokol

| İş | Adaylar (basitlik sırasıyla) | Birincil metrik | Ortam / veri | Not |
|---|---|---|---|---|
| **1. L4 kol becerileri** | (a) IK + elle kavrama yörüngesi, (b) PPO, (c) SAC | Doğrulama tohumlarında, domain randomization altında beceri başarı oranı | MJX, durum tabanlı, binlerce paralel ortam | PPO MJX'in paralelliğiyle en uyumlu aday; SAC daha az örnekle öğrenir ama paralelleşmesi zayıf. Bütçe GPU saatiyle eşitlenir. |
| **2. L3 öğrenilmiş dekoder** | (a) v1 sabit kural, (b) davranış klonlama (MLP), (c) DAgger, (d) PPO (DN girdili) | Kapalı döngüde doğrulama görev başarısı | Brian2 ile kapalı döngü; öğretmen = simülatör durumunu okuyan elle yazılmış politika (`HAND-MADE`, yalnızca etiket üretir) | (b) Synaptera'daki gibi dağılım kaymasıyla çökebilir; bunu göstermek de sonuçtur. (c) RL'e göre çok daha az beyin koşusu gerektirdiği için ilk ciddi aday. **Seçim prosedürü gerçek, shuffled ve bypass kollarına ayrı ayrı ve aynen uygulanır**; sonuç CKS ile okunur. |
| **3. L2 ince ayar** | (a) ince ayarsız, (b) CMA-ES, (c) OpenAI-ES, (d) surrogate-gradient (yalnızca JAX eşdeğerliği geçtiyse) | Doğrulama görev başarısı; okunan sonuç gerçek − shuffled farkı | Eğitilebilir parametre: yalnızca hücre tipi başına kazanç ve eşik (C1) | Birkaç yüz parametrede ES gradyansız ve Brian2 ile doğrudan çalışır; JAX motoruna bağımlılık yoktur. Gerçek ve her shuffled graf aynı değerlendirme bütçesini alır. |
| **4. VNC vekili** (Hat B GO ise) | (a) doğrusal, (b) MLP, (c) GRU | Ayrılmış NeuroMechFly koşularında (v, ω, ön bacak uç noktası) tahmininde R² | Ömer'in B4 veri seti ([0007](0007-ekip-ve-gorev-dagilimi.md) veri şeması) | Ayrılmış veri **koşu bazında** ayrılır (aynı koşudan pencereler eğitim ve teste bölünmez). Seçilen model sonra kapalı döngüde test edilir. |
| **5. Bypass** | İlgili işte gerçek kol için seçilen aday ailesi | — | Aynı L1 çıktısı → DN biçimi → aynı L3 | Gerçek kolla aynı aday listesi ve aynı arama bütçesi; en iyisi bypass olarak kullanılır (zayıf bypass CKS'yi şişirir). |

### Başlangıç sırası

1. **P0 (H3–H4): ML hattının doğrulanması.** İş 1'in küçük bir sürümü: tek bir "uzan" becerisi, IK baz çizgisi ve PPO, 5 tohum. Amaç model seçmek değil; MJX + MLflow + tohum havuzları + IQM raporunun uçtan uca çalıştığını göstermek.
2. **P1–P2: İş 1'in tamamı** (uzan, kavra, kaldır, bırak) ve H14'te seçim.
3. **P1: İş 5** (T1/T1b bypass), **P2:** T2 bypass.
4. **P3: İş 2** (dekoder).
5. **P4: İş 3** (ince ayar) ve Hat B GO ise **İş 4**.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Her iş için "bilinen en iyi" algoritmayı doğrudan seçmek | Projedeki kısıtlar (bilgi güvenlik duvarı, eşit bütçe, Brian2 hızı) standart kıyaslamalardan farklı; seçim kendi ortamımızda ölçülmeli |
| Ortalama ± standart sapma ile raporlamak | Az tohumda aykırı koşulara duyarlı; IQM + bootstrap daha güvenilir |
| Sınav tohumlarında seçim yapmak | Sınav performansını şişirir; A4'e aykırı |
| Dekoder seçimini yalnızca gerçek kolda yapmak | Seçim avantajı yalnızca gerçek kola gider; CKS şişer |

## Sonuçlar

**Olumlu**
- Model seçimi tartışma değil, ön-kayıtlı bir kural sonucu olur.
- Olumsuz sonuçlar (örneğin RL'in IK'yi yenememesi, dekoderin bypass'ı yenememesi) aynı ciddiyetle raporlanabilir.
- ES'in ilk yöntem olması JAX motorunu kritik yoldan çıkarır.

**Olumsuz / maliyet**
- 5 tohum × birden fazla aday × hiperparametre araması hesaplama maliyetini artırır; P0'da ölçülen hızlara göre bütçeler ön-kayıtta gerçekçi tutulur.
- Dekoder seçiminin üç kola ayrı ayrı uygulanması, P3'ün en pahalı işidir.

## İlgili
- [0005 ML stratejisi](0005-ml-stratejisi.md) · [0006 Repo kuralları](0006-repo-kurallari.md) (A4, C1–C5) · [gorevler/mert.md](gorevler/mert.md)
- Agarwal et al. 2021, "Deep Reinforcement Learning at the Edge of the Statistical Precipice" (IQM ve rliable)
