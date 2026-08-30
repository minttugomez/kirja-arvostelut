import db


def get_all_reviews():
    sql = """
    SELECT book_reviews.*, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id"""
    return db.query(sql)


def search(query):
    sql = """
    SELECT book_reviews.*, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE title LIKE ? OR author LIKE ?"""
    queryphrase = "%" + query + "%"
    return db.query(sql, [queryphrase, queryphrase])


def get_reviews_by_user(user_id):
    sql = """
    SELECT book_reviews.*, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.user_id = ?"""
    return db.query(sql, [user_id])


def get_user_stats(user_id):
    sql = """
    SELECT COUNT(*) AS count,
           DATE(MIN(created_at)) AS first_review,
           DATE(MAX(created_at)) AS last_review
    FROM book_reviews
    WHERE user_id = ?"""
    return db.query(sql, [user_id])[0]


def get_review_by_id(review_id):
    sql = """
    SELECT book_reviews.*, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.id = ?
    """
    return db.query(sql, [review_id])


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    classes = {}
    for row in db.query(sql):
        classes.setdefault(row["title"], []).append(row["value"])
    return classes


def get_review_classes(review_id):
    sql = "SELECT title, value FROM review_classes WHERE review_id = ?"
    classes = {}
    for row in db.query(sql, [review_id]):
        classes.setdefault(row["title"], []).append(row["value"])
    return classes


def add_review(user_id, title, author, review, classes):
    sql = """
    INSERT INTO book_reviews (user_id, title, author, review, created_at)
    VALUES (?, ?, ?, ?, datetime('now')) """
    db.execute(sql, [user_id, title, author, review])
    review_id = db.last_insert_id()

    sql = """
    INSERT INTO review_classes (review_id, title, value)
    VALUES (?, ?, ?)"""
    for class_title, class_value in classes:
        db.execute(sql, [review_id, class_title, class_value])


def update_review(review_id, title, author, review, classes):
    sql = """
    UPDATE book_reviews
    SET title = ?, author = ?, review = ?
    WHERE id = ?
    """
    db.execute(sql, [title, author, review, review_id])

    db.execute("DELETE FROM review_classes WHERE review_id = ?", [review_id])
    sql = """
    INSERT INTO review_classes (review_id, title, value)
    VALUES (?, ?, ?)"""
    for class_title, class_value in classes:
        db.execute(sql, [review_id, class_title, class_value])


def delete_review(review_id):
    db.execute("DELETE FROM review_classes WHERE review_id = ?", [review_id])
    db.execute("DELETE FROM comments WHERE review_id = ?", [review_id])
    db.execute("DELETE FROM book_reviews WHERE id = ?", [review_id])
