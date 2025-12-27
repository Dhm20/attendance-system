from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("attendance.db")

with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        company_code TEXT
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        time TEXT
    )
    """)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/attendance")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        company_code = request.form["company_code"]

        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password, company_code) VALUES (?, ?, ?, ?)",
            (name, email, password, company_code)
        )
        db.commit()
        return redirect("/")

    return render_template("register.html")

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user_id" not in session:
        return redirect("/")

    message = ""
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        action = request.form["action"]
        db = get_db()
        db.execute(
            "INSERT INTO attendance (user_id, action, time) VALUES (?, ?, ?)",
            (session["user_id"], action, time_now)
        )
        db.commit()
        message = f"تم تسجيل {action} بنجاح"

    return render_template("attendance.html", time=time_now, message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
