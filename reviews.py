import db

REVIEW_COLUMNS = (
    "book_reviews.id, book_reviews.user_id, book_reviews.title, "
    "book_reviews.author, book_reviews.review, book_reviews.created_at, "
    "users.username"
)


def _review_filter(query, genre):
    where = []
    params = []
    if query:
        where.append(
            "(book_reviews.title LIKE ? OR book_reviews.author LIKE ?)"
        )
        params += ["%" + query + "%", "%" + query + "%"]
    if genre:
        where.append(
            "book_reviews.id IN "
            "(SELECT review_id FROM review_classes WHERE value = ?)"
        )
        params.append(genre)
    clause = " WHERE " + " AND ".join(where) if where else ""
    return clause, params


def count_reviews(query, genre):
    clause, params = _review_filter(query, genre)
    sql = "SELECT COUNT(*) FROM book_reviews" + clause
    return db.query(sql, params)[0][0]


def get_reviews(query, genre, page, page_size):
    clause, params = _review_filter(query, genre)
    sql = f"""
    SELECT {REVIEW_COLUMNS}
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id{clause}
    ORDER BY book_reviews.id DESC
    LIMIT ? OFFSET ?"""
    return db.query(sql, params + [page_size, page_size * (page - 1)])


def count_reviews_by_user(user_id):
    sql = "SELECT COUNT(*) FROM book_reviews WHERE user_id = ?"
    return db.query(sql, [user_id])[0][0]


def get_reviews_by_user(user_id, page, page_size):
    sql = f"""
    SELECT {REVIEW_COLUMNS}
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.user_id = ?
    ORDER BY book_reviews.id DESC
    LIMIT ? OFFSET ?"""
    return db.query(sql, [user_id, page_size, page_size * (page - 1)])


def get_user_stats(user_id):
    sql = """
    SELECT COUNT(*) AS count,
           DATE(MIN(created_at)) AS first_review,
           DATE(MAX(created_at)) AS last_review
    FROM book_reviews
    WHERE user_id = ?"""
    return db.query(sql, [user_id])[0]


def get_review_by_id(review_id):
    sql = f"""
    SELECT {REVIEW_COLUMNS}
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.id = ?"""
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
