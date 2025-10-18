
-- TEMPORAL VIEWS EXPORT
-- Generated: 2025-09-24T18:10:18.599791

-- Monthly Aggregation
CREATE TABLE IF NOT EXISTS temporal_monthly (
    year_month VARCHAR(7),
    record_count INTEGER,
    PRIMARY KEY (year_month)
);

-- Insert monthly data (Row count: 179)
INSERT INTO temporal_monthly VALUES
('1882-01', 1),
('1968-01', 1),
('1970-01', 2),
('1971-01', 1),
('1972-01', 2),
('1973-01', 1),
('1975-01', 3),
('1976-01', 2),
('1977-01', 2),
('1978-01', 6);

-- Yearly Aggregation
CREATE TABLE IF NOT EXISTS temporal_yearly (
    year INTEGER,
    record_count INTEGER,
    PRIMARY KEY (year)
);

-- Insert yearly data (Row count: 55)
INSERT INTO temporal_yearly VALUES
('1882', 1),
('1968', 1),
('1970', 2),
('1971', 1),
('1972', 2),
('1973', 1),
('1975', 3),
('1976', 2),
('1977', 2),
('1978', 6);

-- Query example: Get trend over time
SELECT year, SUM(record_count) as total
FROM temporal_yearly
WHERE year BETWEEN 2015 AND 2024
GROUP BY year
ORDER BY year;
