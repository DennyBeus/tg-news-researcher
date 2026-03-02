CREATE TABLE IF NOT EXISTS user_state (
    user_id    BIGINT PRIMARY KEY,
    state      VARCHAR(100) NOT NULL,
    data       TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);
