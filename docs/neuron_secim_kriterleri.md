# FlyWire Nöron Seçim Kriterleri (Data Extraction Protocol)

FlyWire Codex üzerinde "gerçek" kilit nöronları (BPN, MDN vb.) ararken yüzlerce hatalı veya benzer isimli fragmanla karşılaşabiliriz. En doğru nöronların (Root ID) tespit edilip `config/neurons.json` dosyasına eklenmesi için takımca aşağıdaki **6 Adımlı Teyit Protokolü** uygulanacaktır:

## 1. Community Label'da Doğrudan Atıf Ara
En güvenilir sinyal: "(Bidaye et al., 2020)" gibi orijinal makaleye referans veren etiketler (örn. "Type 1 BPN (Bolt Protocerebral Neuron)") gerçek, doğrulanmış nöronlardır.
* **Uyarı:** "BPN like neuron" etiketi teyit edilmemiş bir benzerlik iddiasıdır. "major BPN output" veya "orphan-BPN-output" ise BPN'nin kendisi değil, onun çıkış verdiği hücrelerdir — bunları eleyin.

## 2. Flow ve Super Class Alanını Kontrol Et
Nöronun biyolojik rolüne göre Flow ve Super Class uyumlu olmalıdır. Örneğin gerçek BPN, orta beyinde yerel bir ara nörondur; inen (descending) bir nöron değildir. 
* Bu yüzden BPN ararken Flow = `intrinsic` ve Super Class = `central` olmalıdır. 
* Eğer Flow = `efferent` / Super Class = `descending` görüyorsanız (GNG.75/DNg55 örneğinde olduğu gibi), o satır BPN değil, BPN'den sinyal alan bir inen (DN) nörondur.

## 3. Hemilineage Kümelenmesine Bak
Orijinal çalışmalarda belirli komut hücreleri tek bir gelişimsel hattan (hemilineage) gelir. 
* Codex'te gördüğünüz hemilineage etiketi (örn. "SMPpm1") atıflı nöron adaylarında tekrar ediyorsa, bu kümeleme ek bir doğrulama sinyalidir. 
* Farklı bir hemilineage'de o nöronun ismi geçen bir etiket şüpheyle karşılanmalıdır.

## 4. Predicted NT Type'ı (Nörotransmitter) Karşılaştır
Nöronun fonksiyonu ile salgıladığı kimyasal (Nörotransmitter) uyuşmalıdır. 
* Örn: BPN'ler uyarıcı/aktive edici bir rol oynar; kolinerjik (ACH) olmaları bu rolle tutarlıdır. 
* GABA (inhibitör) olarak işaretlenmiş bir satır (örneğin GNG.75) muhtemelen hedeflenen nöronun kendisi değil, devredeki farklı işlevli bir komşu hücredir.

## 5. Beklenen Hücre Sayısıyla Kıyasla
Literatürdeki hücre sayılarıyla Codex sonuçları uyuşmalıdır.
* Örn: Bidaye ve ark. (2020), BPN'yi hemisfer başına yaklaşık 8-10 hücrelik bir küme olarak tanımlıyor. Yani tek bir beyinde toplam (sol+sağ) yaklaşık 16-20 gerçek BPN beklemeliyiz. 
* Eğer arama sonucu 87 eşleşme veriyorsa; geri kalanlar benzer-şekilli hücreler, mirror twin kopyaları veya farklı connectome setlerindeki aynı hücrenin tekrarlarıdır (bunlar elenmelidir).

## 6. Kriterleri Geçenleri Dışa Aktar (Export)
Yukarıdaki 5 kriteri başarıyla geçen satırları (atıflı etiket + intrinsic/central + tutarlı hemilineage + uyumlu NT + makul sayı) işaretleyip Codex üzerinden **"Copy IDs"** veya **"CSV"** ile dışa aktarın. 

Bu dışa aktarılan liste, elle seçilmiş ama katı literatür kriterleri bazında doğrulanmış **nihai Root ID listemiz** olacaktır.
