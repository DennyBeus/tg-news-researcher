CREATE TABLE IF NOT EXISTS channels (
    id         SERIAL PRIMARY KEY,
    url        VARCHAR(255) NOT NULL UNIQUE,
    name       VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
