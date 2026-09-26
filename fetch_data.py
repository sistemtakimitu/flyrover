from caveclient import CAVEclient

# Doğru ve herkese açık veritabanına bağlanıyoruz
client = CAVEclient('flywire_fafb_public')

# Mevcut veri tablolarının listesini çekelim
tables = client.materialize.get_tables()

print("Bağlantı Başarılı! Mevcut Tablo Sayısı:", len(tables))
print("Tablo İsimlerinden Bazıları:")
for table in tables[:15]:
    print("-", table)
    