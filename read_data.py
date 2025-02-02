import serial
import sqlite3
import time
from datetime import datetime
import contextlib

# مدير السياق لإدارة اتصال قاعدة البيانات
@contextlib.contextmanager
def managed_database_connection():
    conn = sqlite3.connect('electricity_management.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS readings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            current FLOAT,
                            timestamp TEXT)''')
        conn.commit()
        yield conn, cursor
    finally:
        conn.close()

# الدالة لقراءة البيانات من Arduino وتخزينها في قاعدة البيانات
def read_and_store_data(ser, cursor, conn):
    while True:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data.replace('.', '', 1).isdigit():
                current = float(data)
                current_time = datetime.now().strftime('%H:%M:%S')
                cursor.execute("INSERT INTO readings (current, timestamp) VALUES (?, ?)", (current, current_time))
                conn.commit()
                print(f"تم إدخال التيار: {current} أمبير، الوقت: {current_time}")
            else:
                print(f"بيانات غير صالحة: {data}")
        except Exception as e:
            print(f"خطأ: {e}")
        time.sleep(1)  # تأخير لثانية قبل القراءة التالية

# الكود الرئيسي لتشغيل البرنامج
if __name__ == "__main__":
    try:
        with serial.Serial('COM7', 9600, timeout=1) as ser, managed_database_connection() as (conn, cursor):
            read_and_store_data(ser, cursor, conn)
    except serial.SerialException as e:
        print(f"خطأ في الاتصال التسلسلي: {e}")
    except KeyboardInterrupt:
        print("تم إيقاف البرنامج من قبل المستخدم.")
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")
    finally:
        print("تم إغلاق قاعدة البيانات.")
