# Mimari Karar Kayıtları (ADR)

Bu klasör FlyRover'ın **yeniden tasarımına** ait kararları içerir. Her ADR tek bir kararı; bağlamını, değerlendirilen seçenekleri ve sonuçlarını anlatır.

> **Durum:** Tüm ADR'ler şu an **Önerildi** durumundadır. Ekip toplantısında kabul edilince durumları **Kabul edildi** olarak güncellenir ve `README.md`, `.agents/AGENTS.md` ile `docs/yol_haritasi.md` bu kararlara göre güncellenir.

> **Revizyon (2026-10-12):** 0001–0008 (0003 ve 0007'de yalnızca tutarlılık düzeltmeleri) ve görev belgeleri bir inceleme sonrası güncellendi. Değişikliklerin özeti her ADR'nin başındaki "Revizyon" satırındadır.

> **Revizyon 2 (2026-10-12):** İnceleme düzeltmeleri (shuffled tanımı, L1 kapsamı, L3 normalizasyonu, 50 ms atfı, T1b), yeni görev dağılımı (Ömer: Hat B + dünya; Mert: FAFB + tüm ML; Yusuf: platform + shuffled üretici) ve iki yeni ADR: 0009 (model seçim protokolü), 0010 (tohum tipleri).

## Okuma sırası

| # | Karar | Özet |
|---|---|---|
| [0001](0001-vizyon-ve-basari-olcutu.md) | Vizyon ve başarı ölçütü | Beyin *ne/ne zaman*, ML *nasıl*. Manşet sayı: Connectome Katkı Skoru (CKS). |
| [0002](0002-katmanli-mimari.md) | Katmanlı mimari | L0–L5 katmanları, DN seviyesi sınır, bilgi güvenlik duvarı, karar nerede verilir (L1 eşiksiz, L3 hakemliksiz), veri sözleşmeleri |
| [0003](0003-simulasyon-ortami.md) | Simülasyon ortamı | MuJoCo 3 + MJX, Gymnasium; rover + 5 DOF kol; sinek gözü örneklemesi |
| [0004](0004-connectome-noron-ve-sinaps-kurallari.md) | Connectome, nöron ve sinaps kuralları | FAFB v783 nöron seviyesi alt ağ, kalibrasyon ve shuffled kuralları, derlenmiş Brian2 (JAX opsiyonel), 6 kabul testi |
| [0005](0005-ml-stratejisi.md) | ML stratejisi | Ne eğitilir, ne eğitilmez; shuffled/bypass eşit bütçe |
| [0006](0006-repo-kurallari.md) | Repo kuralları | Bilimsel dürüstlük, connectome, ML ve mühendislik kuralları + CI ile denetim |
| [0007](0007-ekip-ve-gorev-dagilimi.md) | Ekip ve görev dağılımı | 3 kişi, iki hat (FAFB + ML / BANC), katman sahipliği, hatlar arası sözleşmeler |
| [0008](0008-yol-haritasi.md) | Yol haritası | P0–P4 aşamaları, T1b ile ilk anlamlı CKS (H8), Hat B GO/NO-GO (H8), karar noktaları |
| [0009](0009-ml-model-secim-protokolu.md) | ML model seçim protokolü | Dört ML işi için aday listesi, tek metrik, IK/kural baz çizgisi, eşit bütçe, 5 tohum, IQM + güven aralığı |
| [0010](0010-noron-secimi-tohum-tipleri.md) | Nöron seçimi: tohum tipleri | 73 elle seçilmiş nöron yerine 14 tohum tipi + veriden genişletme; mod → DN popülasyonları; çıkarılan ve ertelenen tipler |

## Kişi bazlı hedef ve yol haritaları

| Kişi | Rol | Belge |
|---|---|---|
| Mert | Data scientist & ML engineer · FAFB beyin çekirdeği + tüm ML | [gorevler/mert.md](gorevler/mert.md) |
| Ömer | Rover uzmanı, simülasyon & yazılım mühendisi · Hat B (BANC) + dünya | [gorevler/omer.md](gorevler/omer.md) |
| Yusuf | Siber güvenlik & full stack mühendisi · platform, değerlendirme, shuffled üretici | [gorevler/yusuf.md](gorevler/yusuf.md) |

## Mevcut belgelerle ilişki

- `docs/mimari_kararlar/*` ve `docs/yol_haritasi.md` **Faz 1'in (kaçış demosu) tarihsel kaydı** olarak kalır. Mevcut kod (tip seviyesi graf, Brian2 SNN, `escape_demo.py`) yeni mimaride **v0 / eski referans** olarak korunur ve yeni sistemin karşılaştırma tabanı olur.
- Bu ADR'lerdeki gerekçelerin önemli bir kısmı Synaptera projesinin (FlyWire v783 tüm-beyin modeli + NeuroMechFly uçuşu, ön-kayıtlı olumlu ve olumsuz sonuçlar) bulgularına dayanır.

## Yeni ADR nasıl yazılır

1. Sıradaki numarayla `NNNN-kisa-baslik.md` dosyası aç, aşağıdaki şablonu kullan.
2. Durumu **Önerildi** olarak PR aç. En az **iki** ekip üyesinin onayıyla **Kabul edildi** olur.
3. Kabul edilmiş bir ADR silinmez. Değişirse yeni bir ADR yazılır ve eskisinin durumu **Yerini aldı: NNNN** olur.

```markdown
# NNNN. Başlık

- **Durum:** Önerildi | Kabul edildi | Reddedildi | Yerini aldı: NNNN
- **Tarih:** YYYY-AA-GG
- **Karar sahibi:** ...

## Bağlam
## Karar
## Değerlendirilen seçenekler
## Sonuçlar
## İlgili
```
