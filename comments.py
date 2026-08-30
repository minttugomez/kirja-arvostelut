import db


def get_comments(review_id):
    sql = """
    SELECT comments.id, comments.comment, comments.created_at,
           comments.user_id, users.username
    FROM comments
    JOIN users ON comments.user_id = users.id
    WHERE comments.review_id = ?
    ORDER BY comments.id"""
    return db.query(sql, [review_id])


def get_comment(comment_id):
    sql = """
    SELECT comments.id, comments.review_id, comments.user_id,
           comments.comment, comments.created_at, users.username
    FROM comments
    JOIN users ON comments.user_id = users.id
    WHERE comments.id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None


def add_comment(review_id, user_id, comment):
    sql = """
    INSERT INTO comments (review_id, user_id, comment, created_at)
    VALUES (?, ?, ?, datetime('now'))"""
    db.execute(sql, [review_id, user_id, comment])


def update_comment(comment_id, comment):
    sql = "UPDATE comments SET comment = ? WHERE id = ?"
    db.execute(sql, [comment, comment_id])


def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])
