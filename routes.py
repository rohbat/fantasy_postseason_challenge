from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app
from werkzeug.security import check_password_hash, generate_password_hash

from fantasy_postseason_challenge.db import get_db


@app.route("/")
def hello():
    print("Handling request to home page.")
    return "I'm gonna be a football app."

@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        e = None

        if not (username and password):
            e = "username and password required"
        elif db.execute("SELECT * FROM login WHERE username=?", (username,)).fetchone():
            e = f"{username} already exists"

        if not e:
            db.execute(
                "INSERT INTO login (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("login"))
        else:
            flash(e)

    return render_template("register.html")

@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        e = None
        user = db.execute("SELECT * FROM login WHERE username=?", (username,)).fetchone()

        if not (username and password):
            e = "username and password required"
        elif not user:
            e = f"{username} does not exist"
        elif not check_password_hash(user["password"], password):
            e = "incorrect password"

        if not e:
            session.clear()
            session["user_id"] = user["user_id"]
            return redirect(url_for("hello"))
        else:
            flash(e)

    return render_template("login.html")
