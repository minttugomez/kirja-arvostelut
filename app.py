import sqlite3
from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from repositories.user_repository import create_user, get_password_hash, get_user_id
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if len(username) < 3:
        flash("ERROR: username must be at least 3 characters")
        return redirect("/register")
    if len(password1) <8:
        flash("ERROR: password must be at least 8 characters")
        return redirect("/register")
    if password1 != password2:
        flash("ERROR: passwords do not match")
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    try:
        create_user(username, password_hash)
    except sqlite3.IntegrityError:
        flash("ERROR: username not available")
        return redirect("/register")

    flash("Account created")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    password_hash = get_password_hash(username)

    if password_hash and check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        flash("ERROR: incorrect username or password")
        return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
