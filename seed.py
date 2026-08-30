import random
import sqlite3

from werkzeug.security import generate_password_hash

USER_COUNT = 1000
REVIEW_COUNT = 100000
COMMENT_COUNT = 1000000

GENRES = ["Fantasy", "Science Fiction", "Mystery", "Thriller", "Romance",
          "Horror", "Historical Fiction", "Non-fiction", "Biography",
          "Young Adult", "Poetry", "Other"]

con = sqlite3.connect("database.db")
con.execute("PRAGMA foreign_keys = OFF")

for table in ["comments", "review_classes", "book_reviews", "users"]:
    con.execute("DELETE FROM " + table)

password_hash = generate_password_hash("password")
con.executemany(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    [("user" + str(i), password_hash) for i in range(1, USER_COUNT + 1)])

con.executemany(
    """INSERT INTO book_reviews (user_id, title, author, review, created_at)
       VALUES (?, ?, ?, ?, datetime('now'))""",
    [(random.randint(1, USER_COUNT), "Book " + str(i),
      "Author " + str(i % 500), "Review text number " + str(i))
     for i in range(1, REVIEW_COUNT + 1)])

con.executemany(
    "INSERT INTO review_classes (review_id, title, value) "
    "VALUES (?, 'Genre', ?)",
    [(review_id, random.choice(GENRES))
     for review_id in range(1, REVIEW_COUNT + 1)
     for _ in range(random.randint(1, 3))])

con.executemany(
    """INSERT INTO comments (review_id, user_id, comment, created_at)
       VALUES (?, ?, ?, datetime('now'))""",
    [(random.randint(1, REVIEW_COUNT), random.randint(1, USER_COUNT),
      "Comment number " + str(i))
     for i in range(1, COMMENT_COUNT + 1)])

con.commit()
con.close()
