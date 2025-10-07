-- Basic schema for job postings
CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    job_title VARCHAR(512),
    company VARCHAR(512),
    location VARCHAR(512),
    salary_raw TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    salary_currency VARCHAR(16),
    remote BOOLEAN,
    description TEXT,
    requirements TEXT,
    url TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_job_title ON job_postings (job_title);
CREATE INDEX IF NOT EXISTS idx_company ON job_postings (company);
CREATE INDEX IF NOT EXISTS idx_location ON job_postings (location);
