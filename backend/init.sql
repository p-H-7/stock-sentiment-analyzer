-- This file will run when the database is first created
CREATE DATABASE sentiment_db;
\c sentiment_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sentiment_db TO postgres;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";