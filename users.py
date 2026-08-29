import db


def create_user(username, password_hash):
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])


def get_password_hash(username):
    sql = "SELECT password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0][0] if result else None


def get_user_id(username):
    sql = "SELECT id FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if result:
        return result[0]["id"]
    return None


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None
