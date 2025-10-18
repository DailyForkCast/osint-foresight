-- Import USASpending .dat files
-- Run this after database initialization

-- Import example for a single table
-- Adjust paths as needed

\COPY contracts FROM 'F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/contracts.dat'
WITH (FORMAT text, DELIMITER E'\t', NULL '\N', ESCAPE '\', QUOTE E'\b', ENCODING 'UTF8');

-- Track import
INSERT INTO import_status (table_name, rows_imported, status)
SELECT 'contracts', COUNT(*), 'completed'
FROM contracts;

-- Repeat for other tables as needed
