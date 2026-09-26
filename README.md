<<<<<<< HEAD
# flyrover
Connectome rover project
=======
# FlyRover 

Bio-Inspired Autonomous Rover (Mars Surface Application) - ITU Sistem Takımı

## Proje Hedefi (Project Goal)
Mars gibi zorlu yüzeylerde otonom olarak hareket edebilen, biyolojik konnektom verilerini (Drosophila melanogaster - meyve sineği) kullanarak karar alan, "Hiyerarşik Gangliyon Mimarisine" sahip bir rover geliştirmek.

## Mimari (Architecture)
- **Sensor/Vision:** Gelen uyaranları (örneğin büyüyen tehlike algısı) Poisson spike'ları olarak kodlar.
- **Merkezi Karar Düğümü (Central Decision Node):** Hangi alt ağın çalışacağına karar veren yönlendirici.
- **Rover Alt Ağı (Locomotion):** Otonom hareket ve kaçınma manevraları.
- **Kol Alt Ağı (Manipulation):** Hedefe ulaşma ve obje manipülasyonu.
(Not: İki alt ağ arasında fonksiyonel çakışmayı önlemek için izole edilmiştir.)

## Çalışma Düzeni & Git Flow (Workflow)
Projeye dahil olan herkesin kendi görevlerine odaklanabilmesi ve kod entegrasyonunun sorunsuz ilerlemesi için **Git Flow** yöntemi kullanılacaktır.

1. `main`: Sadece test edilmiş, kararlı ve çalışan kodları barındırır. Doğrudan commit atılmaz!
2. `develop`: Geliştirme sürecinin ana dalıdır. Tüm feature'lar burada birleşir.
3. `feature/isim-gorev`: Herkes kendi görevi için `develop` branch'inden bir branch açar (Örn: `feature/ahmet-snn-model`, `feature/ayse-api-entegrasyonu`). Görev bitince `develop`'a Pull Request (PR) açılır.

## Görev Dağılımı
*Görev dağılımları ve ilgili `feature` branch'leri ekip toplantısı sonrası buraya eklenecektir.*
