-- PostgreSQL Configuration for Large USASpending Import (655 GB)
-- Run this before importing the massive data files

-- Increase memory settings for bulk operations
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';

-- Optimize for bulk loading
ALTER SYSTEM SET checkpoint_segments = 100;
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Disable autovacuum during import
ALTER SYSTEM SET autovacuum = off;

-- Increase timeout for long operations
ALTER SYSTEM SET statement_timeout = 0;
ALTER SYSTEM SET lock_timeout = 0;

-- Logging settings
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_duration = on;

-- Apply settings (requires restart)
SELECT pg_reload_conf();

-- Show current settings
SELECT name, setting, unit, source
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem', 'autovacuum')
ORDER BY name;
