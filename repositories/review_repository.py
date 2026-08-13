import db

def get_all_reviews():
    sql = """
    SELECT book_reviews.id, book_reviews.title, book_reviews.author,
           book_reviews.review, book_reviews.user_id, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    ORDER BY book_reviews.id DESC
    """
    return db.query(sql)

def get_reviews_by_user(user_id):
    sql = """
    SELECT book_reviews.id, book_reviews.title, book_reviews.author,
           book_reviews.review, book_reviews.user_id, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.user_id = ?
    ORDER BY book_reviews.id DESC
    """
    return db.query(sql, [user_id])

def search(query):
    sql = """
    SELECT book_reviews.id, book_reviews.title, book_reviews.author,
           book_reviews.review, book_reviews.user_id, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.title LIKE ? OR book_reviews.author LIKE ?
    ORDER BY book_reviews.id DESC
    """
    queryphrase = "%" + query + "%"
    return db.query(sql, [queryphrase, queryphrase])

def get_review_by_id(review_id):
    sql = """
    SELECT book_reviews.id, book_reviews.title, book_reviews.author,
           book_reviews.review, book_reviews.user_id, users.username
    FROM book_reviews
    JOIN users ON book_reviews.user_id = users.id
    WHERE book_reviews.id = ?
    """
    result = db.query(sql, [review_id])
    return result[0] if result else None

def add_review(user_id, title, author, review):
    sql = """
    INSERT INTO book_reviews (user_id, title, author, review)
    VALUES (?, ?, ?, ?)
    """
    db.execute(sql, [user_id, title, author, review])

def update_review(review_id, title, author, review):
    sql = """
    UPDATE book_reviews
    SET title = ?, author = ?, review = ?
    WHERE id = ?
    """
    db.execute(sql, [title, author, review, review_id])

def delete_review(review_id):
    sql = "DELETE FROM book_reviews WHERE id = ?"
    db.execute(sql, [review_id])
