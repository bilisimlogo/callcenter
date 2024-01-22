import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect("call_center.db")
cursor = conn.cursor()

# Kullanıcılar tablosunu oluştur
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

# Müşteri sorunları tablosunu oluştur
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_issues (
        id INTEGER PRIMARY KEY,
        customer_name TEXT,
        issue_date TEXT,
        program_name TEXT,
        customer_email TEXT,
        customer_phone TEXT,
        issue_detail TEXT
    )
''')

# Örnek kullanıcıları ekleyelim
cursor.execute(
    'INSERT INTO users (username, password) VALUES (?, ?)',
    ('admin', 'admin')
)
cursor.execute(
    'INSERT INTO users (username, password) VALUES (?, ?)',
    ('user1', 'password1')
)

# Veritabanı değişikliklerini kaydet
conn.commit()

# Veritabanı bağlantısını kapat
conn.close()
