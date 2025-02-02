from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import sqlite3
app = Flask(__name__)
import random

app.secret_key = 'my_super_secret_key_1234567890'


# استرجاع البيانات من قاعدة البيانات
def fetch_data(query):
    with sqlite3.connect('electricity_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
    return data
from flask import render_template




# التحقق من بيانات تسجيل الدخول
def check_user(username, password):
    conn = sqlite3.connect('electricity_management.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# إضافة مستخدم جديد إلى قاعدة البيانات
def add_user(username, password):
    conn = sqlite3.connect('electricity_management.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


from flask import flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        
        if user:
            session['user'] = username
            return redirect(url_for('chart'))
        else:
            flash('Invalid credentials, try again.', 'error')  # استخدام flash لعرض الرسالة
        
    return render_template('login.html')


# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # تحقق من وجود المستخدم بالفعل
        conn = sqlite3.connect('electricity_management.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return "Username already exists. Please choose another one."
        
        # إضافة المستخدم الجديد
        add_user(username, password)
        return redirect(url_for('login'))

    return render_template('register.html')

# صفحة لوحة التحكم بعد تسجيل الدخول


# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home-arabic'))


def fetch_user_data(username):
    conn = sqlite3.connect('electricity_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    data = cursor.fetchone()
    conn.close()
    return data


@app.route('/chart')
def chart():
    # التحقق من وجود المستخدم في الجلسة
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # استرجاع بيانات من قاعدة البيانات (على سبيل المثال)
    user_data = fetch_user_data(session['user'])  # افترض أن لديك دالة لجلب بيانات المستخدم من قاعدة البيانات
    
    # إرسال البيانات إلى القالب لعرضها

    # استعلام لاسترداد جميع القيم مع استبدال أي قيمة None بـ 0 مباشرة في استهلاك الكهرباء
    day = fetch_data("SELECT COALESCE(consumtion, 0) AS consumtion FROM days_consumtion")
    room_consumption = fetch_data("""
        SELECT room_name, COALESCE(SUM(consumption), 0) AS total_consumption
        FROM (
            SELECT room_name, consumption, date
            FROM daily_consumption
            ORDER BY date DESC
            LIMIT 30
        ) AS limited_data
        GROUP BY room_name
    """)

    room_names = [row[0] for row in room_consumption]  # أسماء الغرف
    consumption_values = [row[1] for row in room_consumption    ]  # قيم الاستهلاك

    # التحقق مما إذا كانت البيانات فارغة أو غير موجودة
    if not day or len(day) == 0:
        return "No data available"  # في حال عدم وجود بيانات نعرض رسالة "لا توجد بيانات"

    # استخراج القيم الخاصة باستهلاك الكهرباء كقائمة
    consumptions = [x[0] for x in day]  # تحويل البيانات إلى قائمة تحتوي فقط على القيم

    # تقسيم القيم إلى مجموعات، كل مجموعة تحتوي على استهلاك 30 يومًا
    monthly_consumption = [
        sum(consumptions[i:i + 30]) for i in range(0, len(consumptions), 30)
    ]

    # الاحتفاظ بأول 12 شهرًا فقط (إذا كان هناك أكثر من 12 شهر)
    monthly_consumption = monthly_consumption[:12]

    # استخراج القيم الخاصة بأول 30 يومًا فقط
    consumptions_30_days = consumptions[:30]

    # تأكد من أن البيانات تحتوي على 30 يومًا فقط، وإذا كانت أقل من 30 يومًا، أضف 0 للقيم المفقودة
    if len(consumptions_30_days) < 30:
        consumptions_30_days += [0] * (30 - len(consumptions_30_days))

    # تخصيص استهلاك الكهرباء على الأجهزة المنزلية المختلفة (نسب الاستهلاك لكل جهاز)
    device_ratios = {
        'Fridge': 0.15,
        'AC': 0.2,
        'Washing Machine': 0.1,
        'Oven': 0.05,
        'Microwave': 0.05,
        'TV': 0.1,
        'Laptop': 0.05,
        'Heater': 0.15,
        'Vacuum Cleaner': 0.02,
        'Dishwasher': 0.05,
        'Fan': 0.03,
        'Water Pump': 0.03,
        'Iron': 0.02,
        'Toaster': 0.01,
        'Light Bulbs': 0.05,
        'Electric Kettle': 0.02,
        'Hair Dryer': 0.01,
        'Home Theater': 0.01,
        'Router': 0.02,
        'Electric Stove': 0.08
    }

    # إنشاء قائمة لتخزين توزيع استهلاك الأجهزة اليومية
    device_distribution = []

    # توزيع استهلاك الكهرباء اليومي على الأجهزة المنزلية خلال أول 30 يومًا
    for daily_consumption in consumptions_30_days:
        device_consumption = {}  # قاموس لتخزين استهلاك كل جهاز في هذا اليوم

        # حساب استهلاك كل جهاز بناءً على النسب المحددة
        for device, ratio in device_ratios.items():
            device_consumption[device] = daily_consumption * ratio

        # إضافة التوزيع إلى قائمة التوزيعات
        device_distribution.append(device_consumption)

    # استعلام لاسترداد استهلاك الكهرباء ليوم واحد (افترض أنه يتم تحديد اليوم الحالي)
    day = fetch_data("SELECT COALESCE(consumtion, 0) AS consumtion FROM days_consumtion ORDER BY date DESC LIMIT 1")

    # التحقق مما إذا كانت البيانات فارغة أو غير موجودة
    if not day or len(day) == 0:
        return "No data available"  # في حال عدم وجود بيانات نعرض رسالة "لا توجد بيانات"

    # استخراج القيمة الخاصة باستهلاك الكهرباء لهذا اليوم
    daily_consumption = day[0][0]  # استهلاك الكهرباء في اليوم الأخير

    # دالة لتوزيع استهلاك الكهرباء على ساعات اليوم
    def distribute_consumption_by_hour(daily_consumption):
        # توزيع استهلاك الكهرباء على ساعات اليوم (24 ساعة)
        hourly_distribution = [0] * 24  # 24 ساعة في اليوم

        # توزيع الاستهلاك بشكل غير متساوٍ مع اختلافات منطقية بين الساعات
        morning_ratio = 0.1  # 6 صباحًا - 12 ظهرًا (أقل استهلاك)
        afternoon_ratio = 0.2  # 12 ظهرًا - 6 مساءً
        evening_ratio = 0.4  # 6 مساءً - 12 منتصف الليل (أعلى استهلاك)
        night_ratio = 0.3  # 12 منتصف الليل - 6 صباحًا (أقل استهلاك)

        # توزيع الاستهلاك على ساعات اليوم مع تباين منطقي بين الساعات
        for hour in range(24):
            if 6 <= hour < 12:  # الصباح
                base_value = daily_consumption * morning_ratio / 6
                # إضافة اختلاف تدريجي بين الساعات
                hourly_distribution[hour] = base_value + random.uniform(-0.02, 0.2) * (hour - 6 + 1)
            elif 12 <= hour < 18:  # الظهيرة
                base_value = daily_consumption * afternoon_ratio / 6
                # إضافة اختلاف تدريجي بين الساعات
                hourly_distribution[hour] = base_value + random.uniform(-0.02, 0.2) * (hour - 12 + 1)
            elif 18 <= hour < 24:  # المساء
                base_value = daily_consumption * evening_ratio / 6
                # إضافة اختلاف تدريجي بين الساعات
                hourly_distribution[hour] = base_value + random.uniform(-0.02, 0.2) * (hour - 18 + 1)
            else:  # الليل
                base_value = daily_consumption * night_ratio / 6
                # إضافة اختلاف تدريجي بين الساعات
                hourly_distribution[hour] = base_value + random.uniform(-0.02, 0.2) * (hour - 0 + 1)

        return hourly_distribution

    # توزيع استهلاك الكهرباء على ساعات اليوم
    hourly_distribution = distribute_consumption_by_hour(daily_consumption)

    # تمرير البيانات إلى القالب dashboard.html لعرضها في المتصفح
    return render_template(
        'dashboard.html',               # اسم القالب الذي سيتم عرضه
        numbers=monthly_consumption,     # استهلاك الكهرباء الشهري للمجموعات
        consumptions=consumptions_30_days,  # استهلاك الكهرباء لأيام 30 الأولى
        daily_distribution=device_distribution,  # توزيع استهلاك الكهرباء اليومي على الأجهزة
        device_ratios=device_ratios,  # نسب استهلاك الأجهزة
        daily_consumption=daily_consumption,  # استهلاك الكهرباء لهذا اليوم
        hourly_distribution=hourly_distribution,
        room_names=room_names,
        consumption_values=consumption_values
    )
    return render_template('dashboard-arabic.html', user=session['user'], data=user_data)




@app.route("/")
def home_arabic():
    return render_template("Home-arabic.html")


@app.route("/home-english")
def home_english():
    return render_template("Home-english.html")


@app.route("/calc-english")
def english():
    return render_template("calc-english.html")


@app.route("/tips-english")
def tips_english():
    return render_template("tips-english.html")



@app.route("/calc-arabic")
def calc_arabic():
    return render_template("calc-arabic.html")



@app.route("/tips-arabic")
def tips_arabic():
    return render_template("tips-arabic.html")



@app.route("/life")
def life():
    return render_template("life.html")







@app.route('/get-day-data/<int:day_id>', methods=['GET'])
def get_day_data(day_id):
    conn = sqlite3.connect('electricity_usage.db')
    cursor = conn.cursor()

    # استعلام لجلب بيانات اليوم بناءً على ID
    cursor.execute("""
        SELECT date, consumption
        FROM usage_data
        WHERE id = ?;
    """, (day_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({'date': row[0], 'consumption': row[1]})
    else:
        return jsonify({'error': 'Day ID not found'}), 404



@app.route('/get-user-details', methods=['GET'])
def get_user_details():
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('electricity_management.db')  # تأكد من أنك تستخدم قاعدة البيانات الصحيحة
    cursor = conn.cursor()

    # استعلام لاسترجاع الاسم والبريد الإلكتروني من قاعدة البيانات
    cursor.execute('SELECT name, email FROM users WHERE id=1')  # قم بتعديل الاستعلام بناءً على جدولك
    user = cursor.fetchone()  # استرجاع البيانات (اسم، بريد إلكتروني)
    conn.close()

    # إذا تم العثور على البيانات، نعيدها بشكل JSON
    if user:
        return jsonify({"name": user[0], "email": user[1]})
    else:
        return jsonify({"error": "لم يتم العثور على بيانات المستخدم"}), 404


























































# وظيفة لجلب البيانات من قاعدة البيانات
def get_latest_data():
    conn = sqlite3.connect('electricity_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT current, timestamp FROM readings ORDER BY id DESC LIMIT 10")  # جلب آخر 10 قراءات
    data = cursor.fetchall()
    conn.close()
    return [{"current": row[0], "timestamp": row[1]} for row in data]

@app.route('/data')
def data():
    data = get_latest_data()
    return jsonify(data)

@app.route('/real_life')
def index():
    return render_template('real_life.html')



if __name__ == '__main__':
    app.run(debug=True)
