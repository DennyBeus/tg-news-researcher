CREATE TABLE IF NOT EXISTS news (
    id              SERIAL PRIMARY KEY,
    text            TEXT NOT NULL,
    date            TIMESTAMP NOT NULL,
    views           INTEGER,
    reactions_count INTEGER,
    link            VARCHAR(255) NOT NULL,
    source_channel  VARCHAR(255),
    created_at      TIMESTAMP DEFAULT NOW()
);
