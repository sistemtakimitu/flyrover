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

## 3. Git ve Klasör Düzeni
- **Git Flow:** Ana kodlar (Production) `main` branch'inde durur. Buraya *asla* doğrudan commit atılmamalıdır (Başlangıç kurulumu hariç). Geliştirmeler kişisel `feature/isim-gorev` branch'lerinde yapılmalı ve PR açılmalıdır.
- **Modülerlik:** Yapılan değişiklikler projenin profesyonel yapısına (`src/data`, `src/snn`, `tests`, `docs`) uygun olmalı, ana dizine geçici/dağınık dosyalar bırakılmamalıdır. Geçici SNN denemeleri `tests/` altında yapılmalıdır.
