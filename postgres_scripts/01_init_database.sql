-- USASpending Database Initialization
-- Run this after PostgreSQL is installed

-- Create database
CREATE DATABASE usaspending
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- Connect to database
\c usaspending;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS rpt;
CREATE SCHEMA IF NOT EXISTS int;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA raw TO postgres;
GRANT ALL ON SCHEMA rpt TO postgres;
GRANT ALL ON SCHEMA int TO postgres;

-- Set search path
SET search_path TO public, raw, rpt, int;

-- Create status table
CREATE TABLE IF NOT EXISTS import_status (
    table_name VARCHAR(255) PRIMARY KEY,
    rows_imported BIGINT,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50)
);

COMMENT ON TABLE import_status IS 'Tracks USASpending data import progress';
