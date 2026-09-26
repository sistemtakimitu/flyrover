# FlyWire Nöron Seçim Kriterleri (Genel Data Extraction Protocol)

FlyWire Codex üzerinde "gerçek" kilit nöronları ararken yüzlerce hatalı veya benzer isimli fragmanla karşılaşabiliriz. En doğru nöronların (Root ID) tespit edilip projeye dahil edilmesi için takımca aşağıdaki **8 Adımlı Genel Teyit Protokolü** uygulanacaktır:

## 1. Sistematik İsimle Ara, Betimleyici İsimle Değil
Aramaya, literatürdeki resmi/sistematik ismi yazın ("DNa02", "LC4", "MDN", "GF" gibi) — "kaçış nöronu" veya "dönüş nöronu" gibi betimleyici bir terimle değil. Codex, hücre-tipi kodlarını hassas indeksliyor; gevşek bir metin araması Community Label içinde o kelime geçen alakasız hücreleri de getirir.

## 2. Community Label'da Kaynak Makaleye Atıf Ara
En güçlü doğrulama sinyali budur: etiket doğrudan orijinal karakterizasyon makalesine (yazar + yıl) atıf veriyorsa (örn. "(Bidaye et al., 2020)", "(Namiki et al., 2018)", "(Card & Dickinson, 2008)") bu gerçek, teyit edilmiş eşleşmedir. "-like", "-similar", "candidate", "X output", "X input", "orphan-X" gibi ek ibareler taşıyan etiketler o nöronun KENDİSİ değil, ona benzeyen veya bağlantılı komşu bir hücredir — eleyin.

## 3. Beklenen Flow / Super Class Değerini Önceden Bilip Sonra Doğrulayın
Codex'e bakmadan ÖNCE, makaleden bu nöronun hangi kategoride olması gerektiğini çıkarın:
* İnen/motor bir komut nöronu ise **Flow="efferent"**, **Super Class="descending"** beklenir (MDN, GF, DNa02, DNp09 gibi).
* Orta beyinde yerel bir ara nöron ise **Flow="intrinsic"**, **Super Class="central"** beklenir (BPN, E-PG gibi).
* Görsel algı nöronu ise **Super Class="visual projection"** beklenir (LC4, LC10a, LPLC2 gibi).

Codex'teki değer bu beklentiyle uyuşmuyorsa, yanlış/komşu bir hücreyi bulmuşsunuzdur.

## 4. Anatomik "Parmak İzini" Doğrulayın
Nöron kategorisine göre farklı bir sabit anatomik işarete bakın: merkezi ara nöronlarda Hemilineage (gelişimsel köken kümesi), inen nöronlarda Nerve alanı (örn. cervical connective/CV, beyinden VNC'ye çıkış yolu), görsel projeksiyon nöronlarında ise optik glomerulus/tabaka bilgisi. Adaylarınızın hepsinde bu işaret tutarlıysa, bu ek bir doğrulamadır; farklıysa muhtemelen farklı bir alt-tip karışmıştır.

## 5. Nörotransmitter Tipini Davranışsal Rolle Kıyaslayın
Predicted NT Type sütununu, o nöronun bilinen işlevine göre kontrol edin: bir eylemi TETİKLEYEN nöronlar genelde kolinerjik (ACH) veya glutamaterjik olma eğilimindedir, bir eylemi BASTIRAN/durduran nöronlar (FG, BB, BRK gibi) genelde GABAerjik'tir. Beklenenle ters bir NT tipi görürseniz, bu satırı şüpheyle karşılayın.

## 6. Beklenen Hücre Sayısıyla Kıyaslayın
Orijinal makaledeki hücre sayısını arama sonucu sayısıyla karşılaştırın — bu nörona göre ÇOK değişir: GF hemisfer başına tek, benzersiz bir hücredir; MDN ~2/hemisfer (toplam 4); BPN ~8-10/hemisfer; LC10a ~100/hemisfer; T4/T5 ise her biri ~750 görsel kolonda tekrarlanan devasa bir populasyondur. Aramadan önce bu sayıyı makaleden not edin; sonuç sayısı bu aralıktan çok sapıyorsa arama ya çok geniş ya çok dar demektir.

## 7. Doğru Connectome Veri Setini Kontrol Edin
FAFB/FlyWire sadece BEYNİ (+ optik loblar) kapsar; inen nöronların beyindeki dendritleri burada görünür ama bacak/kanat motor devrelerine giden çıkış sinapsları omurga eşdeğeri olan VNC'de yer alır ve ayrı bir veri setinde (MANC) bulunur. Eyleminiz doğrudan bacak/kanat motor seviyesindeyse (örn. yürüme paternini üreten devre), sadece FAFB'de değil MANC'ta da o hücre tipini aramanız gerekebilir. Codex'teki "instances in BANC/FAFB/MANC/..." satırları aynı hücre tipinin farklı veri setlerindeki karşılıklarına atlamanızı sağlar.

## 8. Kriterleri Geçenleri Kaydedin ve Proje Tablosuna İşleyin
Yukarıdaki 7 kriteri geçen satırları Copy IDs/CSV ile dışa aktarın ve "eylem → nöron tipi → Codex ID → veri seti" formatında tek bir proje tablosunda toplayın (örn: `config/neurons.json`). Böylece her yeni nöron için bu süreci sıfırdan tekrar etmek yerine, ekip bu tabloya doğrudan başvurabilir.
