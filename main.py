from flask import Flask, render_template, request, redirect, session, url_for
import os
import json

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"  # แก้เป็นคีย์ของคุณเมื่อใช้งานจริง

# -------------------------
# users stored in users.txt
# format per line: username,password
# -------------------------
def load_users():
    users = {}
    if os.path.exists("users.txt"):
        with open("users.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    username, password = parts
                    users[username] = password
    return users

def save_user(username, password):
    # append new user as "username,password\n"
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"{username},{password}\n")

# -------------------------
# per-user notes stored in <username>_notes.txt
# each line is a note
# -------------------------
def notes_filename(username):
    # simple sanitize: remove slashes
    safe = username.replace("/", "_").replace("\\", "_")
    return f"{safe}_notes.txt"
    
def load_notes(username):
    fn = notes_filename(username)
    if not os.path.exists(fn):
        return []
    try:
        with open(fn, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    
def save_notes(username, notes):
    fn = notes_filename(username)
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_notes(username)
    return render_template("index.html", username=username, notes=notes)

@app.route("/add", methods=["POST"])
def add_note():
    if "username" not in session:
        return redirect(url_for("login"))
    note = request.form.get("note", "").strip()
    if note:
        username = session["username"]
        notes = load_notes(username)
        notes.append(note)
        save_notes(username, notes)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>")
def delete(index):
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_notes(username)
    if 0 <= index < len(notes):
        notes.pop(index)
        save_notes(username, notes)
    # after deletion go to history
    return redirect(url_for("history"))

@app.route("/history")
def history():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_notes(username)
    return render_template("history.html", username=username, notes=notes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not username or not password:
            return render_template("register.html", error="กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
        if username in users:
            return render_template("register.html", error="ชื่อผู้ใช้นี้มีอยู่แล้ว")
        if password != confirm:
            return render_template("register.html", error="รหัสผ่านไม่ตรงกัน")
        # save user
        save_user(username, password)
        # create empty note file (optional)
        save_notes(username, [])
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Replit usually provides its own port; keep debug True for dev
    app.run(host="0.0.0.0", port=81, debug=True)