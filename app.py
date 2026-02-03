from flask import Flask, render_template, redirect, request, url_for,jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from genai_helper import ai_reply
from intent import detect_intent


app = Flask(__name__)
app.secret_key = "myapp"

# ---------------- MYSQL CONFIG ----------------
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "Kgkite@123"
app.config['MYSQL_DB'] = "parking"

mysql = MySQL(app)

# ---------------- HOME ----------------
@app.route('/')
def start():
    alerts = fetch_alerts()
    return render_template("index.html", alerts=alerts)

@app.route('/home')
def home():
    return render_template("index.html")

# ---------------- CONTACT ----------------
@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/data', methods=['POST'])
def data():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO message(name,email,mess) VALUES (%s,%s,%s)",(name, email, message)
    )
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home'))

# ---------------- AUTH ----------------
@app.route('/login')
def login():
    return render_template("login.html")   # renamed from "sign up.html"

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    phno = request.form['phno']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM login WHERE username=%s AND phno=%s AND password=%s",
        (username, phno, password)
    )
    user = cur.fetchone()
    cur.close()

    if user:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    phno = request.form['phno']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO login(username,phno,password) VALUES (%s,%s,%s)",
        (username, phno, password)
    )
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("home"))

# ---------------- PLACES ----------------
@app.route('/places')
def places():
    return render_template("places.html")

@app.route('/prozone')
def prozone():
    return render_template("booking.html", location="Prozone Mall")

@app.route('/brookfields')
def brookfields():
    return render_template("booking.html", location="Brookfields Mall")

@app.route('/fun')
def fun():
    return render_template("booking.html", location="Fun Republic Mall")

@app.route('/kg')
def kg():
    return render_template("booking.html", location="KG Hospital")

@app.route('/kmch')
def kmch():
    return render_template("booking.html", location="KMCH Hospital")

@app.route('/psg')
def psg():
    return render_template("booking.html", location="PSG Hospital")

# ---------------- BOOKING ----------------
@app.route('/book', methods=['POST'])
def book():
    slot = request.form['slot']
    subslot = request.form['subslot']
    time = request.form['time']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO book(slot, subslot, book_time) VALUES (%s,%s,%s)",
        (slot, subslot, time)
    )
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("qr"))

# ---------------- QR ----------------
@app.route('/qr')
def qr():
    return render_template("qr.html")

# ---------------- ENTRY / EXIT ----------------
@app.route('/entryexit')
def entryexit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entryexit")
    logs = cur.fetchall()
    cur.close()

    return render_template(
        'entry.html',
        logs=[{'numplate': l[0], 'entry_time': l[1], 'exit_time': l[2]} for l in logs]
    )

@app.route('/entry', methods=['POST'])
def entry():
    numplate = request.form['numplate']
    entry_time = datetime.now()

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO entryexit (numplate, entry_time) VALUES (%s,%s)",
        (numplate, entry_time)
    )
    mysql.connection.commit()
    cur.close()

    return redirect('/entryexit')

@app.route('/exit', methods=['POST'])
def exit():
    numplate = request.form['numplate']
    exit_time = datetime.now()

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE entryexit SET exit_time=%s WHERE numplate=%s AND exit_time IS NULL",
        (exit_time, numplate)
    )
    mysql.connection.commit()
    cur.close()

    return redirect('/entryexit')

# ---------------- ALERT SYSTEM ----------------
def fetch_alerts():
    alerts = []
    cur = mysql.connection.cursor()

    cur.execute("SELECT slot, subslot, book_time FROM book")
    bookings = cur.fetchall()
    cur.close()

    now = datetime.now()

    for slot, subslot, t in bookings:
        booking_time = datetime.strptime(str(t), "%H:%M:%S")
        if now.hour == booking_time.hour and 0 <= booking_time.minute - now.minute <= 10:
            alerts.append(
                f"🚨 Slot {slot}-{subslot} booked at {t}"
            )

    return alerts

@app.route("/chat-ui")
def chat_ui():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"reply": "⚠️ Please type something."})

        cur = mysql.connection.cursor()

        # ---- LIVE DATA ----
        cur.execute("SELECT COUNT(*) FROM book")
        booked = cur.fetchone()[0]
        total_slots = 100
        available = total_slots - booked

        hour = datetime.now().hour
        rush = "High" if (9 <= hour <= 11 or 16 <= hour <= 18) else "Low"

        charges = "₹20 per hour"
        admin = "Parking is managed by the Admin Office."

        cur.close()

        # ---- SMART CONTEXT ----
        context = f"""
Live Parking Information:
- Available slots: {available}
- Total slots: {total_slots}
- Parking charges: {charges}
- Current rush level: {rush}
- Admin info: {admin}

Rules:
- Answer naturally like a real assistant
- If the question is unrelated, politely guide the user
- Do not mention internal system data unless needed
"""

        reply = ai_reply(context, message)

        print(f"[GEMINI][DYNAMIC] User: {message} | Reply: {reply}")

        return jsonify({"reply": reply})

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"reply": "⚠️ Server error. Please try again."})

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
