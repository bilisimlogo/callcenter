import sqlite3

# Veritabanı bağlantısı oluştur
conn = sqlite3.connect("call_center.db")
cursor = conn.cursor()

# Yeni kullanıcı ekle
username = 'admin'
password = 'admin'

cursor.execute(
    'INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
conn.commit()

# Veritabanı bağlantısını kapat
conn.close()
