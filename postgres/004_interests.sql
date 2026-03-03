CREATE TABLE IF NOT EXISTS interests (
    id         SERIAL PRIMARY KEY,
    text       TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
