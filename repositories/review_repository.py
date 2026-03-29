import db

def get_all_reviews():
    sql = "SELECT * FROM bookreviews"
    return db.query(sql)
