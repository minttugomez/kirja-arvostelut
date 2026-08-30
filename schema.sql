CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE book_reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    review TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE review_classes (
    id INTEGER PRIMARY KEY,
    review_id INTEGER REFERENCES book_reviews(id),
    title TEXT,
    value TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES book_reviews(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    comment TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_book_reviews_user_id ON book_reviews (user_id);
CREATE INDEX idx_review_classes_review_id ON review_classes (review_id);
CREATE INDEX idx_review_classes_value ON review_classes (value);
CREATE INDEX idx_comments_review_id ON comments (review_id);
