from multiprocessing import Process
import os

def run_read_data():
    os.system('python read_data.py')  # تشغيل ملف read_data.py

def run_app():
    os.system('python app.py')  # تشغيل ملف app.py

if __name__ == "__main__":
    p1 = Process(target=run_read_data)
    p2 = Process(target=run_app)
    
    p1.start()  # بدء تشغيل read_data.py
    p2.start()  # بدء تشغيل app.py
    
    p1.join()  # الانتظار حتى ينتهي p1
    p2.join()  # الانتظار حتى ينتهي p2
