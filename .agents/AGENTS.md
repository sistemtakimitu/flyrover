# FlyRover - Yapay Zeka Ajanları (AI Agents) İçin Proje Kuralları

Bu dosya, FlyRover projesinde çalışacak tüm AI Asistanlarının (Antigravity vb.) ve takım üyelerinin projeye kod yazarken veya veri çekerken uyması gereken **kesin** kuralları içerir. Lütfen herhangi bir kod değişikliği yapmadan önce bu kuralları okuyun.

## 1. Veri Çekme (Data Fetching) ve CAVEclient Kuralları
- **Versiyon Sabitleme (Kritik):** CAVEclient (FlyWire FAFB) üzerinden yapılan tüm materialization ve query işlemleri KESİNLİKLE **`version=783`** parametresi ile sabitlenmelidir. (Örn: `client.materialize.version = 783`). Bu, projenin tekrarlanabilirliği (NASA standardı) için şarttır. Dinamik veya versiyonsuz sorgu atmak yasaktır.
- **Nöron Seçimi:** Yeni bir nöron Root ID'si aranacağı zaman mutlaka `docs/neuron_secim_kriterleri.md` dosyasındaki 8 adımlı protokol izlenmelidir. Metin araması yapıp çıkan ilk ID koda eklenemez.
- **Ara Nöron Tespiti:** T4 ve LC4 gibi uzak hücreler arasında doğrudan sinaps yoksa, uydurma köprüler kurmak yerine *Multi-hop path integration* (kısa yol / dolaylı sinaps hesaplama) mantığı kullanılmalıdır.

## 2. Connectome Graf (SNN) Kuralları
`config/connectome_graph.json` dosyasına eklenecek olan her bir sinaps (edge) kesinlikle aşağıdaki 3 etiketten (edge_type) birine sahip olmalıdır:
- `"measured"`: CAVEclient'tan doğrudan çekilmiş %100 gerçek, tek sıçramalı sinapslar.
- `"path-integrated"`: Gerçek veriden elde edilmiş ancak ara nöronlar üzerinden hesaplanmış (multi-hop) dolaylı bağlantılar.
- `"engineered"`: Biyolojik veride bulunamayıp mühendislik kararı ile manuel atanan ağırlıklar. (Bu etiket mümkün olduğunca az kullanılmalıdır).

Aynı kural `config/type_graph.json` (hücre tipi seviyesi) için de geçerlidir. Bu dosya elle düzenlenmez; `src/data/build_type_graph.py` ile üretilir, hangi tiplerin gireceği `config/cell_types.json`'da tanımlanır. Graf üreten koddaki değişiklik ile üretilen graf **aynı PR'da** olmalıdır.

## 3. Git ve Klasör Düzeni
- **Branch düzeni:** Herkes kendi isimli branch'inde (`yusuf`, `mert`, ...) çalışır ve `main`'e Pull Request açar. `main`'e doğrudan commit atılmaz. PR merge edilince kişisel branch `main` ile güncellenir. PR'lar "merge commit" ile birleştirilir (squash değil; uzun ömürlü kişisel branch'lerde tekrar çakışma çıkarır).
- **Testler:** PR açmadan önce `pytest tests` geçmelidir. Yeni bir davranış eklendiğinde onu doğrulayan bir test de eklenir (bkz. `tests/test_snn.py`, `tests/test_escape_demo.py`).
- **Modülerlik:** Değişiklikler proje yapısına uygun olmalı: `src/data` (veri), `src/snn` (sinir ağı), `src/sim` (MuJoCo simülasyonu ve kodlayıcı/çözücü), `tests`, `docs`. Ana dizine geçici dosya bırakılmaz. `tests/` altındaki dosyalar pytest testi olmalıdır; çalıştırılabilir demolar `src/` altına konur.
- **Faz disiplini:** Çalışmalar `docs/yol_haritasi.md`'deki aktif faza odaklanır. Aktif fazın dışındaki nöron/özellik eklemeleri önce yol haritasına yazılır.
