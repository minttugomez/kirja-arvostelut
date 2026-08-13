import secrets
import sqlite3
from flask import Flask, abort, flash, redirect, render_template, request, session
from repositories.user_repository import create_user, check_login
from repositories.review_repository import (
    get_all_reviews, get_reviews_by_user, get_review_by_id,
    add_review, update_review, delete_review, search
)
import config

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.errorhandler(403)
def forbidden(error):
    return redirect("/")

@app.route("/")
def index():
    query = request.args.get("query")
    book_reviews = search(query) if query else get_all_reviews()
    return render_template("index.html", query=query, book_reviews=book_reviews)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if len(username) < 3 or len(username) > 50:
        flash("ERROR: username must be between 3 and 50 characters", "error")
        return redirect("/register")
    if len(password1) < 8 or len(password1) > 100:
        flash("ERROR: password must be between 8 and 100 characters", "error")
        return redirect("/register")
    if password1 != password2:
        flash("ERROR: passwords do not match", "error")
        return redirect("/register")

    try:
        create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("ERROR: username not available", "error")
        return redirect("/register")

    flash("Account created", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user_id = check_login(username, password)
    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        flash("ERROR: incorrect username or password", "error")
        return redirect("/login")

@app.route("/logout")
def logout():
    require_login()
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/newreview")
def newreview():
    require_login()
    return render_template("newreview.html")

@app.route("/add", methods=["POST"])
def add():
    require_login()
    check_csrf()

    title = request.form["title"]
    author = request.form["author"]
    review = request.form["review"]
    if not title or len(title) > 100:
        abort(403)
    if not author or len(author) > 100:
        abort(403)
    if not review or len(review) > 5000:
        abort(403)

    add_review(session["user_id"], title, author, review)
    flash("Review added successfully!", "success")
    return redirect("/yourpage")

@app.route("/yourpage")
def yourpage():
    require_login()
    book_reviews = get_reviews_by_user(session["user_id"])
    return render_template("yourpage.html", book_reviews=book_reviews)

@app.route("/edit/<int:review_id>")
def edit(review_id):
    require_login()
    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review["user_id"] != session["user_id"]:
        abort(403)
    return render_template("editreview.html", book_review=book_review)

@app.route("/update/<int:review_id>", methods=["POST"])
def update(review_id):
    require_login()
    check_csrf()

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    author = request.form["author"]
    review = request.form["review"]
    if not title or len(title) > 100:
        abort(403)
    if not author or len(author) > 100:
        abort(403)
    if not review or len(review) > 5000:
        abort(403)

    update_review(review_id, title, author, review)
    flash("Review updated successfully!", "success")
    return redirect("/yourpage")

@app.route("/confirmdelete/<int:review_id>")
def confirmdelete(review_id):
    require_login()
    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review["user_id"] != session["user_id"]:
        abort(403)
    return render_template("confirmdelete.html", book_review=book_review)

@app.route("/delete/<int:review_id>", methods=["POST"])
def delete(review_id):
    require_login()
    check_csrf()

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review["user_id"] != session["user_id"]:
        abort(403)

    if "continue" in request.form:
        delete_review(review_id)
        flash("Review deleted successfully!", "success")

    return redirect("/yourpage")
