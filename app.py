import math
import re
import secrets
import sqlite3
from urllib.parse import quote

import markupsafe

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session)
from werkzeug.security import check_password_hash, generate_password_hash

import config
from comments import (
    add_comment,
    get_comment,
    get_comments,
    remove_comment,
    update_comment,
)
from reviews import (
    add_review,
    count_reviews,
    count_reviews_by_user,
    delete_review,
    get_all_classes,
    get_review_by_id,
    get_review_classes,
    get_reviews,
    get_reviews_by_user,
    get_user_stats,
    update_review,
)
from users import create_user, get_password_hash, get_user, get_user_id

app = Flask(__name__)
app.secret_key = config.secret_key

PAGE_SIZE = 10


def current_user_id():
    return get_user_id(session["username"])


def page_count_for(total):
    return max(math.ceil(total / PAGE_SIZE), 1)


def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        flash("ERROR: invalid request, please try again")
        return redirect("/")
    return None


def any_blank(*values):
    return any(not value.strip() for value in values)


def comment_error(text):
    if any_blank(text):
        return "ERROR: comment cannot be blank"
    if len(text) > 1000:
        return "ERROR: comment is too long (max 1000 characters)"
    return None


def form_classes():
    all_classes = get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        parts = entry.split(":")
        if len(parts) != 2:
            flash("ERROR: invalid genre selection")
            return []
        class_title, class_value = parts
        if (class_title not in all_classes
                or class_value not in all_classes[class_title]):
            flash("ERROR: invalid genre selection")
            return []
        classes.append((class_title, class_value))
    return classes


@app.errorhandler(403)
def forbidden(error):  # pylint: disable=unused-argument
    flash("ERROR: you are not allowed to do that")
    return redirect("/")


@app.errorhandler(404)
def not_found(error):  # pylint: disable=unused-argument
    flash("ERROR: page not found")
    return redirect("/")


@app.route("/")
def index():
    query = request.args.get("query")
    genre = request.args.get("genre")
    page = request.args.get("page", 1, type=int)

    page_count = page_count_for(count_reviews(query, genre))
    filter_qs = ""
    if query:
        filter_qs += "&query=" + quote(query)
    if genre:
        filter_qs += "&genre=" + quote(genre)
    if page < 1:
        return redirect("/?page=1" + filter_qs)
    if page > page_count:
        return redirect(f"/?page={page_count}{filter_qs}")

    book_reviews = get_reviews(query, genre, page, PAGE_SIZE)
    user_id = current_user_id() if "username" in session else None
    return render_template(
        "index.html",
        query=query,
        genre=genre,
        genres=get_all_classes().get("Genre", []),
        book_reviews=book_reviews,
        user_id=user_id,
        page=page,
        page_count=page_count,
        filter_qs=filter_qs,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    username = request.form.get("username", "")
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")
    filled = {"username": username}

    errors = []
    if len(username) < 3:
        errors.append("ERROR: username must be at least 3 characters")
    if not re.fullmatch(r"[A-Za-z0-9]+", username):
        errors.append("ERROR: username may only contain letters and numbers")
    if len(password1) < 8:
        errors.append("ERROR: password must be at least 8 characters")
    if re.search(r"\s", password1):
        errors.append("ERROR: password must not contain spaces")
    if (not re.search(r"[A-Za-z]", password1)
            or not re.search(r"[0-9]", password1)
            or not re.search(r"[^A-Za-z0-9\s]", password1)):
        errors.append("ERROR: password must contain at least one letter, "
                      "one number and one special character")
    if password1 != password2:
        errors.append("ERROR: passwords do not match")

    if errors:
        for error in errors:
            flash(error)
        return render_template("register.html", filled=filled)

    password_hash = generate_password_hash(password1)

    try:
        create_user(username, password_hash)
    except sqlite3.IntegrityError:
        flash("ERROR: username not available")
        return render_template("register.html", filled=filled)

    flash("Account created")
    return redirect("/")


@app.route("/new_review")
def new_review():
    if "username" not in session:
        return redirect("/")
    return render_template(
        "newreview.html",
        user_id=current_user_id(),
        classes=get_all_classes(),
        filled={},
        selected=[],
    )


@app.route("/user/<int:user_id>")
def user_page(user_id):
    if "username" not in session:
        return redirect("/")
    user = get_user(user_id)
    if not user:
        abort(404)

    page = request.args.get("page", 1, type=int)
    page_count = page_count_for(count_reviews_by_user(user_id))
    if page < 1:
        return redirect(f"/user/{user_id}?page=1")
    if page > page_count:
        return redirect(f"/user/{user_id}?page={page_count}")

    book_reviews = get_reviews_by_user(user_id, page, PAGE_SIZE)
    stats = get_user_stats(user_id)
    is_owner = user["username"] == session["username"]
    return render_template(
        "userpage.html",
        user=user,
        book_reviews=book_reviews,
        stats=stats,
        is_owner=is_owner,
        page=page,
        page_count=page_count,
    )


@app.route("/review/<int:review_id>")
def review_page(review_id):
    if "username" not in session:
        return redirect("/")
    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    return render_template(
        "review.html",
        book_review=book_review,
        review_classes=get_review_classes(review_id),
        comments=get_comments(review_id),
    )


@app.route("/new_comment", methods=["POST"])
def new_comment():
    if "username" not in session:
        return redirect("/")
    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    review_id = request.form.get("review_id", "")
    comment = request.form.get("comment", "")
    if not get_review_by_id(review_id):
        abort(404)

    error = comment_error(comment)
    if error:
        flash(error)
        return redirect(f"/review/{review_id}")

    add_comment(review_id, current_user_id(), comment)
    return redirect(f"/review/{review_id}")


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    if "username" not in session:
        return redirect("/")
    comment = get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["username"] != session["username"]:
        flash("ERROR: you can only change your own comments")
        return redirect(f"/review/{comment['review_id']}")

    if request.method == "GET":
        return render_template("editcomment.html", comment=comment)

    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    new_text = request.form.get("comment", "")
    error = comment_error(new_text)
    if error:
        flash(error)
        return redirect(f"/edit_comment/{comment_id}")

    update_comment(comment_id, new_text)
    return redirect(f"/review/{comment['review_id']}")


@app.route("/confirm_delete_comment/<int:comment_id>")
def confirm_delete_comment(comment_id):
    if "username" not in session:
        return redirect("/")
    comment = get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["username"] != session["username"]:
        flash("ERROR: you can only change your own comments")
        return redirect(f"/review/{comment['review_id']}")
    return render_template("confirmdeletecomment.html", comment=comment)


@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    if "username" not in session:
        return redirect("/")
    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    comment = get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["username"] != session["username"]:
        flash("ERROR: you can only change your own comments")
        return redirect(f"/review/{comment['review_id']}")

    remove_comment(comment_id)
    return redirect(f"/review/{comment['review_id']}")


@app.route("/edit/<int:review_id>")
def edit(review_id):
    book_review = get_review_by_id(review_id)
    if "username" not in session:
        return redirect("/")
    if not book_review:
        flash("Review not found")
        return redirect(f"/user/{current_user_id()}")
    if book_review[0]["username"] != session["username"]:
        flash("ERROR: you can only change your own reviews")
        return redirect(f"/review/{review_id}")
    row = book_review[0]
    review_classes = get_review_classes(review_id)
    selected = [f"{t}:{v}" for t, values in review_classes.items()
                for v in values]
    return render_template(
        "editreview.html",
        book_review=book_review,
        classes=get_all_classes(),
        filled={"title": row["title"], "author": row["author"],
                "review": row["review"]},
        selected=selected,
    )


@app.route("/confirm_delete/<int:review_id>")
def confirm_delete(review_id):
    book_review = get_review_by_id(review_id)
    if "username" not in session:
        return redirect("/")
    if not book_review:
        flash("Review not found")
        return redirect(f"/user/{current_user_id()}")
    if book_review[0]["username"] != session["username"]:
        flash("ERROR: you can only change your own reviews")
        return redirect(f"/review/{review_id}")
    return render_template("confirmdelete.html", book_review=book_review)


@app.route("/add", methods=["POST"])
def add():
    if "username" not in session:
        return redirect("/")
    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    user_id = get_user_id(session["username"])

    title = request.form.get("title", "")
    author = request.form.get("author", "")
    review = request.form.get("review", "")
    classes = form_classes()

    errors = []
    if any_blank(title, author, review):
        errors.append("ERROR: title, author and review cannot be blank")
    if not classes:
        errors.append("ERROR: pick at least one genre")
    if errors:
        for error in errors:
            flash(error)
        return render_template(
            "newreview.html",
            user_id=user_id,
            classes=get_all_classes(),
            filled={"title": title, "author": author, "review": review},
            selected=request.form.getlist("classes"),
        )

    try:
        add_review(user_id, title, author, review, classes)
        flash("Review added successfully!")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not added")
    return redirect(f"/user/{user_id}")


@app.route("/update/<int:review_id>", methods=["POST"])
def update(review_id):
    if "username" not in session:
        return redirect("/")
    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review[0]["username"] != session["username"]:
        flash("ERROR: you can only change your own reviews")
        return redirect(f"/review/{review_id}")

    title = request.form.get("title", "")
    author = request.form.get("author", "")
    review = request.form.get("review", "")
    classes = form_classes()

    errors = []
    if any_blank(title, author, review):
        errors.append("ERROR: title, author and review cannot be blank")
    if not classes:
        errors.append("ERROR: pick at least one genre")
    if errors:
        for error in errors:
            flash(error)
        return render_template(
            "editreview.html",
            book_review=book_review,
            classes=get_all_classes(),
            filled={"title": title, "author": author, "review": review},
            selected=request.form.getlist("classes"),
        )

    try:
        update_review(review_id, title, author, review, classes)
        flash("Review updated successfully!")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not updated")
    return redirect(f"/user/{book_review[0]['user_id']}")


@app.route("/delete/<int:review_id>", methods=["POST"])
def delete(review_id):
    if "username" not in session:
        return redirect("/")
    csrf_redirect = check_csrf()
    if csrf_redirect:
        return csrf_redirect

    book_review = get_review_by_id(review_id)
    if not book_review:
        abort(404)
    if book_review[0]["username"] != session["username"]:
        flash("ERROR: you can only change your own reviews")
        return redirect(f"/review/{review_id}")

    user_id = book_review[0]["user_id"]
    try:
        delete_review(review_id)
        flash("Review deleted successfully!")
    except sqlite3.DatabaseError:
        flash("ERROR: Something went wrong. Review not deleted")
    return redirect(f"/user/{user_id}")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    password_hash = get_password_hash(username)

    if password_hash and check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = get_user_id(username)
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    flash("ERROR: incorrect username or password")
    return redirect("/")


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
        del session["user_id"]
        del session["csrf_token"]
    return redirect("/")


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.template_filter()
def show_preview(content):
    lines = content.split("\n")[:3]
    preview = "\n".join(lines)
    truncated = len(preview) < len(content)
    if len(preview) > 300:
        preview = preview[:300]
        truncated = True
    if truncated:
        preview = preview.rstrip() + " ..."
    return show_lines(preview)
