import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
from reviews import (
    add_review,
    delete_review,
    get_all_reviews,
    get_review_by_id,
    get_reviews_by_user,
    get_user_stats,
    search,
    update_review,
)
from users import create_user, get_password_hash, get_user, get_user_id

app = Flask(__name__)
app.secret_key = config.secret_key


def current_user_id():
    return get_user_id(session["username"])


@app.errorhandler(403)
def forbidden(error):
    return redirect("/")


@app.route("/")
def index():
    query = request.args.get("query")
    book_reviews = search(query) if query else get_all_reviews() or []
    user_id = current_user_id() if "username" in session else None
    return render_template(
        "index.html", query=query, book_reviews=book_reviews, user_id=user_id
    )


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/new_review")
def new_review():
    if "username" not in session:
        return redirect("/")
    return render_template("newreview.html", user_id=current_user_id())


@app.route("/user/<int:user_id>")
def user_page(user_id):
    if "username" not in session:
        return redirect("/")
    user = get_user(user_id)
    if not user:
        abort(404)
    book_reviews = get_reviews_by_user(user_id) or []
    stats = get_user_stats(user_id)
    is_owner = user["username"] == session["username"]
    return render_template(
        "userpage.html",
        user=user,
        book_reviews=book_reviews,
        stats=stats,
        is_owner=is_owner,
    )


@app.route("/edit/<int:review_id>")
def edit(review_id):
    book_review = get_review_by_id(review_id)
    if "username" not in session:
        return redirect("/")
    if not book_review:
        flash("Review not found")
        return redirect(f"/user/{current_user_id()}")
    if book_review[0]["username"] != session["username"]:
        abort(403)
    return render_template("editreview.html", book_review=book_review)


@app.route("/confirm_delete/<int:review_id>")
def confirm_delete(review_id):
    book_review = get_review_by_id(review_id)
    if "username" not in session:
        return redirect("/")
    if not book_review:
        flash("Review not found")
        return redirect(f"/user/{current_user_id()}")
    if book_review[0]["username"] != session["username"]:
        abort(403)
    return render_template("confirmdelete.html", book_review=book_review)


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if len(username) < 3:
        flash("ERROR: username must be at least 3 characters")
        return redirect("/register")
    if len(password1) < 8:
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


@app.route("/add", methods=["POST"])
def add():
    if "username" not in session:
        return redirect("/")

    user_id = get_user_id(session["username"])

    title = request.form["title"]
    author = request.form["author"]
    review = request.form["review"]

    try:
        add_review(user_id, title, author, review)
        flash("Review added successfully!")
        return redirect(f"/user/{user_id}")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not added")


@app.route("/update/<int:review_id>", methods=["POST"])
def update(review_id):
    if "username" not in session:
        return redirect("/")

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review[0]["username"] != session["username"]:
        abort(403)

    title = request.form['title']
    author = request.form['author']
    review = request.form['review']

    try:
        update_review(review_id, title, author, review)
        flash("Review updated successfully!")
        return redirect(f"/user/{book_review[0]['user_id']}")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not updated")


@app.route("/delete/<int:review_id>", methods=["POST"])
def delete(review_id):
    if "username" not in session:
        return redirect("/")

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review[0]["username"] != session["username"]:
        abort(403)

    try:
        delete_review(review_id)
        flash("Review deleted successfully!")
        return redirect(f"/user/{book_review[0]['user_id']}")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not deleted")


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
    if "username" in session:
        del session["username"]
        return redirect("/")
