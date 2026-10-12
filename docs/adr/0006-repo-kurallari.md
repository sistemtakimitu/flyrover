# 0006. Repo kuralları ve denetimi

- **Durum:** Önerildi
- **Tarih:** 2026-10-12
- **Karar sahibi:** Yusuf (hakem: Mert, Ömer)
- **Revizyon (2026-10-12, inceleme sonrası):** Katman kararlarını (L1 eşiksiz, L3 dondurulmuş kural) ve kol eşitliğini denetleyen kurallar (A9–A11), shuffled üretici kuralı (B7) eklendi; kabul testi sayısı altıya çıktı.

## Bağlam

`.agents/AGENTS.md` bugün veri sürümü, kenar etiketleri, branch düzeni ve test kurallarını içeriyor. Yeni mimari bunlara ek olarak bilimsel dürüstlük (kaynak etiketi, ön-kayıt, kontrol kolları) ve ML kuralları gerektiriyor. Synaptera'nın en güçlü yanı kuralları **otomatik olarak denetlemesiydi**: rapordaki her sayı bir script tarafından kayıtlardan yeniden hesaplanıyordu.

Kural yazmak yetmez; mümkün olan her kural **CI tarafından denetlenmelidir**.

## Karar

Aşağıdaki kurallar kabul edildikten sonra `.agents/AGENTS.md` ve `CONTRIBUTING.md`'ye taşınır.

### A. Bilimsel dürüstlük

| # | Kural | Denetim |
|---|---|---|
| A1 | **Kaynak etiketi:** Her girdi ve motor komutu BRAIN / HAND-MADE / TRAINED / REFLEX / EXTERNAL etiketlerinden birini taşır ve ayrı ayrı loglanır. | Kayıt şeması doğrulayıcısı; etiketsiz alan → test hatası |
| A2 | **Kontrolsüz iddia yok:** "Beyin X'i yapıyor" yalnızca gerçek / shuffled / bypass karşılaştırmasıyla yazılabilir. | PR şablonu kontrol listesi; rapor scripti üç kolu birlikte üretir |
| A3 | **Ön-kayıt:** Başarı ölçütleri koşudan önce `docs/prereg/` altına PR ile commit edilir. Sonuç görüldükten sonra ölçüt değişmez; sapmalar tarihli olarak `docs/prereg/SAPMALAR.md`'ye yazılır. | Değerlendirme düzeneği, sınav koşusu için ön-kayıt dosyasının daha eski bir commit'te var olmasını şart koşar |
| A4 | **Sınav tohumları kilitli:** Ayar, eğitim ve hata ayıklama sınav tohumlarıyla yapılmaz. | Sınav havuzu yalnızca `--exam` bayrağı + etiketli commit + ön-kayıt ile açılır; her açılış loglanır |
| A5 | **Sabitler davranıştan önce seçilir.** Davranışa bakılarak ayarlanan sabit config'te `tuned_on:` alanıyla işaretlenir. | Config şeması |
| A6 | **Olumsuz sonuçlar** aynı ağırlıkla raporlanır. | Aşama sonu rapor şablonu "olumsuz bulgular" bölümünü zorunlu kılar |
| A7 | **Rakamlar elle yazılmaz:** Rapordaki her sayı `eval/verify.py` tarafından kayıtlardan yeniden hesaplanır. | CI'da `verify.py` |
| A8 | Raporlanan her sonuç **en az 5 tohumla** verilir; tümü raporlanır. | Rapor scripti |
| A9 | **L1 karar vermez:** L1 çıktıları sürekli ve monotondur; görev kararını veren eşik yoktur ([0002](0002-katmanli-mimari.md)). | Referans uyaran taramasıyla birim testi; L1 config'indeki her sabit gerekçe alanı taşır |
| A10 | **L3 kuralı dondurulur:** L3 kural dosyası ön-kayıt commit'inden sonra değişmez; öncelik tablosu yalnızca `L3-öncelik` etiketli karşılaştırma kolunda bulunur. | Değerlendirme düzeneği L3 dosyasının hash'ini ön-kayıttakiyle karşılaştırır |
| A11 | **Kollar yalnızca L2'de farklıdır:** Gerçek, shuffled ve bypass koşularında L0, L1, L3, L4 config hash'leri aynıdır. | Değerlendirme düzeneği `meta.json`'daki hash'leri karşılaştırır; fark varsa CKS hesaplanmaz |

### B. Connectome

| # | Kural | Denetim |
|---|---|---|
| B1 | FlyWire sürümü **v783** sabittir; tüm veri dosyaları SHA-256 ile doğrulanır. | `fetch` scripti; CI hash kontrolü |
| B2 | Graf yalnızca kodla üretilir; **elle düzenlenmez**. Graf kodu ve üretilen graf (manifest + hash) **aynı PR'da** olur. | CI grafı yeniden üretir ve hash'i karşılaştırır |
| B3 | Engineered kenarlar ve işaret düzeltmeleri yalnızca kendi YAML dosyalarında, kaynak ve hakem onayıyla eklenir. | CODEOWNERS: bu dosyalar için iki onay |
| B4 | Path-integrated kenarlar simülasyonda kullanılmaz. | Graf yükleyici reddeder |
| B5 | Yeni modül, 6 kabul testini geçmeden `main`'e girmez ([0004](0004-connectome-noron-ve-sinaps-kurallari.md)). | Kabul testleri gece CI'ında |
| B7 | Shuffled graflar yalnızca derece korumalı üreticiyle (işaret sınıfı içinde çift-kenar değiş tokuşu) üretilir; tohum ve hash manifestte yer alır. | Üreticinin birim testleri giriş/çıkış derecelerini ve sinaps toplamlarını doğrular |
| B6 | Yeni nöron tipi aramada `docs/neuron_secim_kriterleri.md`'deki 8 adımlı protokol uygulanır. | PR şablonu |

### C. ML

| # | Kural | Denetim |
|---|---|---|
| C1 | Connectome üzerinde eğitilebilir parametreler yalnızca hücre tipi başına skalerlerdir. | Eğitim kodu parametre sayısını ve türünü loglar; sınır aşılırsa hata |
| C2 | Gerçek, shuffled ve bypass kollarına eşit eğitim/ayar bütçesi. | MLflow'da üç kolun bütçeleri yan yana raporlanır |
| C3 | L4 politikaları L3 dışında görev bilgisi alamaz. | Gözlem şeması testi |
| C4 | Her eğitim koşusu config, tohum ve commit hash'iyle MLflow'a kaydedilir. | Eğitim başlatıcı |

### D. Mühendislik ve güvenlik

| # | Kural | Denetim |
|---|---|---|
| D1 | `main` her zaman uçtan uca çalışır. Duman testi CI'da < 5 dk; uzun testler gece. | GitHub Actions + branch koruması |
| D2 | `main`'e doğrudan commit yok; PR + en az bir onay. **İnceleyen, kodu yazanla farklı katmandan olur.** | Branch koruması, CODEOWNERS |
| D3 | Branch adı `<kişi>/<konu>` (ör. `mert/graph-builder`); PR'lar merge commit ile birleştirilir. | — |
| D4 | Mimari kararlar ADR olarak yazılır. | — |
| D5 | Yapay zekâ ile yazılan kod testsiz merge edilmez; yapay zekâ ile üretilen sayılar elle rapora yazılmaz. | PR şablonu |
| D6 | Gizli bilgiler (CAVE token, sunucu anahtarları) repoya girmez; `.env` + gizli bilgi taraması. | pre-commit + CI'da gitleaks |
| D7 | Veri dosyaları, büyük kayıtlar ve videolar repoya girmez (`.gitignore`); paylaşım sunucu üzerinden. | pre-commit dosya boyutu kontrolü |
| D8 | Ana dizine geçici dosya bırakılmaz; çıktılar `runs/` (gitignore) altına. | pre-commit |
| D9 | Bağımlılıklar sürüm sabitli (`requirements.lock` / `uv.lock`). | CI |
| D10 | Lisans: proje ticari değildir; FlyWire türevi tüm çıktılar CC BY-NC 4.0. | Yayın kontrol listesi |

### Kayıt formatı

Her koşu `runs/<tarih>_<görev>_<kol>_<tohum>/` altında:
- `meta.json`: commit, config, graf hash'i, tohum, kol, kaynak etiketleri
- `data.h5` veya `zarr`: zaman serileri (gözlem, sürüş hızları, DN hızları, mod, motor komutları; her biri etiketli)
- `metrics.json`: görev metrikleri

Şemayı Yusuf tanımlar ve doğrulayıcısını yazar.

## Değerlendirilen seçenekler

| Seçenek | Neden seçilmedi |
|---|---|
| Kuralları yalnızca belgede tutmak | Takip edilmez; Synaptera'nın gücü otomatik denetimdi |
| Harici ön-kayıt (OSF) | İleride değerlendirilebilir; şimdilik repo içi ön-kayıt + commit geçmişi yeterli. Synaptera'daki gibi repo içi ön-kaydın bağımsız kanıt olmadığı raporlarda belirtilir. |
| Kişisel uzun ömürlü branch'ler (mevcut düzen) | Uzun ömürlü branch'ler çakışma üretiyor; konu bazlı kısa ömürlü branch'lere geçilir |

## Sonuçlar

**Olumlu**
- Kurallar insan disiplinine değil CI'a dayanır.
- Her sonuç tek komutla yeniden üretilebilir.

**Olumsuz / maliyet**
- P0'da CI, şema ve doğrulayıcı altyapısı kurulmalı (Yusuf'un P0 işinin büyük kısmı).
- Bazı kurallar (eşit bütçe, güçlü bypass) tam otomatikleştirilemez; hakem incelemesine dayanır.

## İlgili
- [0007 Ekip](0007-ekip-ve-gorev-dagilimi.md) · [gorevler/yusuf.md](gorevler/yusuf.md) · mevcut [.agents/AGENTS.md](../../.agents/AGENTS.md)
