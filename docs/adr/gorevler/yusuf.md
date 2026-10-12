# Yusuf: Platform, değerlendirme ve dürüstlük sahibi

- **Rol:** Siber güvenlik & full stack mühendisi; ekibin **tarafsız değerlendiricisi**
- **Sahip olduğu alanlar:** Repo yapısı, CI/CD, güvenlik, CUDA sunucusu ve erişimi, deney takibi (MLflow), kayıt şeması, L5 değerlendirme düzeneği, CKS, `verify.py`, ön-kayıt süreci, dashboard ve beyin aktivitesi görüntüleyici, entegrasyon, yayın hazırlığı
- **Hakemleri:** Mert ve Ömer (dönüşümlü)
- **Yedeği:** Ömer
- İlgili kararlar: [0006](../0006-repo-kurallari.md) · [0001](../0001-vizyon-ve-basari-olcutu.md) · [0007](../0007-ekip-ve-gorev-dagilimi.md)

Yusuf'un hiçbir beyin veya ML modülünün sahibi olmaması bilinçli bir tercih: CKS'yi hesaplayan ve sınav tohumlarını açan kişi, sonucu iyi çıkması gereken modülü yazan kişi olmamalı.

---

## Ulaşılması gereken nokta (H28 sonunda)

1. **Tek komutla tekrarlanabilirlik:** Repodaki her sonuç `commit + config + tohum` ile tek komutla yeniden üretilebiliyor; rapordaki her sayı `verify.py` ile kayıtlardan yeniden hesaplanıyor.
2. **Kuralları CI denetliyor:** [0006](../0006-repo-kurallari.md)'daki kuralların otomatikleştirilebilenlerin tamamı CI'da (graf hash'i, kaynak etiketleri, ön-kayıt varlığı, sınav tohumu kilidi, gizli bilgi taraması, duman testi < 5 dk).
3. **Tarafsız değerlendirme düzeneği:** T1–T4 için gerçek / shuffled / bypass kollarını koşturan, CKS'yi bootstrap güven aralığıyla hesaplayan, sınav tohumlarını yalnızca ön-kayıtlı ve etiketli commit'lerde açan sistem.
4. **Güvenli altyapı:** Paylaşılan CUDA sunucusu (anahtar tabanlı erişim, kullanıcı hesapları, iş kuyruğu), MLflow, kayıt deposu; gizli bilgiler repoya hiç girmemiş.
5. **Web arayüzleri:**
   - **Dashboard:** koşular, görevler, kollar, CKS, eğitim eğrileri.
   - **Beyin aktivitesi görüntüleyici:** modül bazında spike aktivitesi, DN hızları ve L3 modları; simülasyon videosuyla zaman senkronlu.
6. **Yayın paketi:** final raporu, hash'li veri paketi, lisans denetimi (CC BY-NC 4.0), otomatik üretilen "neyi kim kontrol ediyor" tablosu.

---

## Yol haritası

### P0 Temel (H1–H4)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **Yeni repo yapısı** ([0006](../0006-repo-kurallari.md)): klasörler, `pyproject.toml`, sürüm sabitli bağımlılıklar (`uv.lock`) | Herkes temiz bir klonla 10 dakikada kurulum yapabiliyor |
| **CI (GitHub Actions):** lint, birim testleri, duman testi | < 5 dk; `main` branch koruması, CODEOWNERS |
| **Güvenlik:** pre-commit (gitleaks, dosya boyutu, ana dizin temizliği), `.env` şablonu, CAVE token yönetimi | Gizli bilgi taraması CI'da; geçmişte sızmış gizli bilgi taraması yapılmış |
| **CUDA sunucusu:** SSH anahtarlı erişim (veya Tailscale), kullanıcı hesapları, iş kuyruğu, disk düzeni | Mert ve Ömer sunucuda GPU'lu bir iş çalıştırabiliyor |
| **MLflow** (self-hosted) | Eğitim başlatıcı commit + config + tohumu otomatik kaydediyor |
| **Kayıt şeması** (`meta.json`, `data.h5`/zarr, `metrics.json`) + doğrulayıcı | Etiketsiz alan → test hatası |
| **Değerlendirme düzeneği iskeleti:** görev × kol × tohum koşturucu | Sahte bir görevle uçtan uca çalışıyor |
| **Ön-kayıt şablonu** ve `docs/prereg/` süreci | Şablon + CI kontrolü (sınav koşusu için ön-kaydın daha eski commit'te olması) |
| JAX–Brian2 **eşdeğerlik test düzeneği** (Mert ile) | Referans uyaran seti; istatistik raporu otomatik |
| Mevcut kodu `v0-faz1-kacis` etiketiyle işaretle | Etiket repoda |

### P1 Kaçış (H5–H8)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **Tohum havuzları ve sınav kilidi** (Ömer ile) | Sınav havuzu yalnızca `--exam` + etiketli commit + ön-kayıt ile açılıyor; her açılış loglanıyor |
| **CKS hesaplama** + bootstrap %95 güven aralığı | Birim testli |
| **`verify.py`**: rapor sayılarını kayıtlardan yeniden hesaplar | CI'da çalışıyor; uyuşmazlıkta hata |
| T1 ön-kayıt sürecinin yönetimi | T1 ön-kaydı sınavdan önce `main`'de |
| **T1 sınavının koşturulması** ve ilk CKS raporu | `docs/reports/P1_T1.md` (olumsuz bulgular bölümü dahil) |
| Bypass kolunun eşit bütçe denetimi (hakem) | İnceleme notu |
| **Dashboard v1** (web) | Koşular, kollar ve CKS listeleniyor |

### P2 Yaklaş-dur + kol (H9–H14)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **Beyin aktivitesi görüntüleyici** (web): modül bazında spike'lar, DN hızları, L3 modları, videoyla senkron | Bir T2 bölümü görüntülenebiliyor |
| Gece testleri: modül kabul testleri, tüm-beyin kahini testleri | Gece CI'ında; sonuçlar dashboard'da |
| **Kaynak etiketi denetleyicisi**: her motor komutunun ve girdinin etiketli olduğunu kayıtlardan doğrular | CI'da |
| T2 ön-kaydı ve sınavı | `docs/reports/P2_T2.md` |
| Hat B hakemliği (B1 raporu) | İnceleme notu |

### P3 Entegrasyon (H15–H20)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| **Entegrasyon sahipliği**: haftalık demonun `main`'den otomatik hazırlanması | Her hafta bir demo kaydı |
| Uçtan uca CI: T3 kısa bölümü her PR'da | < 5 dk duman testi korunuyor |
| **Tekrarlanabilirlik denetimi**: kayıtlı bir koşunun bit-bit (veya ön-kayıtlı tolerans içinde) yeniden üretilmesi | `docs/reports/reproducibility.md` |
| Güvenlik incelemesi: sunucu, erişimler, bağımlılıklar | Bulgular ve düzeltmeler |
| T3 ön-kaydı ve sınavı | `docs/reports/P3_T3.md` |
| Beyin tarafı yedekliği: Mert'in modül kabul testlerini kendi başına koşturabilme | Bir modül testinin Yusuf tarafından tekrarlanması |

### P4 Mars + yayın (H21–H28)
| Görev | Teslim / "bitti" ölçütü |
|---|---|
| T4 ön-kaydı ve sınavı; connectome ince ayarının eşit bütçe denetimi | `docs/reports/P4_T4.md` |
| **Final raporu** (tüm aşamalar, olumsuz bulgular, sınırlamalar) | Her sayı `verify.py` ile doğrulanmış |
| "Neyi kim kontrol ediyor" tablosunun kayıtlardan otomatik üretimi | README'de |
| **Veri paketi**: kayıtlar + SHA-256 listesi + açıklama | Ayrı paylaşım; repoya girmiyor |
| **Lisans denetimi**: FlyWire CC BY-NC, NeuroMechFly, FlyVis ve diğer bağımlılıklar | `THIRD_PARTY.md` |
| Yayın kontrol listesi ve README güncellemesi | — |

---

## Bağımlılıklar

| Yusuf'un ihtiyacı | Kimden | Ne zaman |
|---|---|---|
| Kayıt şemasına uygun çıktı üreten L0–L4 | Ömer, Mert | P1'den itibaren |
| Her görev için bypass kolu | Mert | Sınavdan önce |
| Görev sahneleri ve `info` metrikleri | Ömer | Her aşamanın başı |

| Yusuf'tan beklenen | Kime | Ne zaman |
|---|---|---|
| CI, sunucu, MLflow, kayıt şeması | Herkes | **H2–H3 (en kritik bağımlılık)** |
| Eşdeğerlik test düzeneği | Mert | H3 |
| Değerlendirme düzeneği ve CKS | Herkes | P1 |

## Dikkat edilecekler

- **Tarafsızlık.** Sonuç ne çıkarsa çıksın ön-kayıttaki ölçütle değerlendirilir; "biraz daha ayarlayalım" talepleri sapma kaydına yazılır.
- **P0'da darboğaz olma.** Sunucu ve CI gecikirse herkes bekler; P0'ın ilk iki haftası önceliklidir.
- **Gizli bilgiler.** CAVE token'ları, sunucu anahtarları ve kişisel erişim bilgileri asla repoya veya loglara girmez.
- **Altyapıyı basit tut.** Üç kişilik ekip için Kubernetes vb. gereksiz; tek sunucu + iş kuyruğu + MLflow yeterli.
- **Lisans.** FlyWire türevi her çıktı (kayıtlar, figürler, videolar) CC BY-NC 4.0; ticari kullanım talebi reddedilir.

## Okuma listesi

- Synaptera `README.md` ve `docs/PREREGISTRATION_LOG.md`: etiketleme, ön-kayıt ve `verify_report_final.py` yaklaşımı
- MLflow belgeleri (self-hosted tracking server)
- GitHub Actions, branch koruması, CODEOWNERS
- gitleaks, pre-commit
- Bootstrap güven aralıkları (Efron & Tibshirani)
