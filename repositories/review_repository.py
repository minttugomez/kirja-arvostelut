import db

def get_all_reviews():
    sql = """
    SELECT bookreviews.*, users.username
    FROM bookreviews
    JOIN users ON bookreviews.user_id = users.id"""
    return db.query(sql)

def add_review(user_id, title, author, review):
    sql = """
    INSERT INTO bookreviews (user_id, title, author, review)
    VALUES (?, ?, ?, ?) """
    db.execute(sql, [user_id, title, author, review])
