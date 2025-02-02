import sqlite3

# إنشاء قاعدة البيانات وجداول المستخدمين
def create_db():
    conn = sqlite3.connect('electricity_management.db')  # الاتصال بقاعدة البيانات
    cursor = conn.cursor()

    # إنشاء جدول المستخدمين إذا لم يكن موجودًا
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # إضافة المستخدم الافتراضي "admin" إذا لم يكن موجودًا
    cursor.execute("SELECT * FROM users WHERE username = 'admin';")
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '2025');")
        print("تم إضافة المستخدم الافتراضي 'admin' بنجاح.")
    
    conn.commit()  # حفظ التغييرات
    conn.close()  # إغلاق الاتصال

# التحقق من وجود الجدول
def check_table():
    conn = sqlite3.connect('electricity_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    result = cursor.fetchone()

    if result:
        print("الجدول موجود.")
    else:
        print("الجدول غير موجود.")
    conn.close()

if __name__ == "__main__":
    create_db()  # إنشاء القاعدة والجدول
    check_table()  # التحقق من وجود الجدول
