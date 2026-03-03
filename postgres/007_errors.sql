CREATE TABLE IF NOT EXISTS errors (
    id            SERIAL PRIMARY KEY,
    workflow_name VARCHAR(255),
    node_name     VARCHAR(255),
    message       TEXT,
    is_sent       BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT NOW()
);
