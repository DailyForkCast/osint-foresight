
-- GEOGRAPHIC VIEWS EXPORT
-- Generated: 2025-09-24T18:10:18.599791

-- Country Aggregation
CREATE TABLE IF NOT EXISTS geographic_countries (
    country_code CHAR(2),
    data_points INTEGER,
    projects INTEGER,
    funding DECIMAL(15,2),
    PRIMARY KEY (country_code)
);

-- Insert country data (Row count: 41)
INSERT INTO geographic_countries VALUES
('LV', 508, 16, 91046.06),
('CZ', 481, 17, 142232.32),
('HR', 517, 19, 287070.74),
('DK', 495, 17, 95811.25),
('RS', 505, 25, 693749.00),
('BA', 482, 34, 580214.89),
('AT', 451, 17, 598557.05),
('MD', 496, 19, 1102282.57),
('UA', 523, 18, 649707.04),
('IE', 516, 9, 580177.08);

-- EU Buckets
CREATE TABLE IF NOT EXISTS eu_groupings (
    group_name VARCHAR(50),
    country_code CHAR(2),
    PRIMARY KEY (group_name, country_code)
);

-- Insert EU groupings (Row count: 93)
INSERT INTO eu_groupings VALUES ('EU27', 'AT');
INSERT INTO eu_groupings VALUES ('EU27', 'BE');
INSERT INTO eu_groupings VALUES ('EU27', 'BG');
INSERT INTO eu_groupings VALUES ('EU27', 'HR');
INSERT INTO eu_groupings VALUES ('EU27', 'CY');
INSERT INTO eu_groupings VALUES ('EU_Candidates', 'AL');
INSERT INTO eu_groupings VALUES ('EU_Candidates', 'ME');
INSERT INTO eu_groupings VALUES ('EU_Candidates', 'MK');
INSERT INTO eu_groupings VALUES ('EU_Candidates', 'RS');
INSERT INTO eu_groupings VALUES ('EU_Candidates', 'TR');
INSERT INTO eu_groupings VALUES ('EEA', 'AT');
INSERT INTO eu_groupings VALUES ('EEA', 'BE');
INSERT INTO eu_groupings VALUES ('EEA', 'BG');
INSERT INTO eu_groupings VALUES ('EEA', 'HR');
INSERT INTO eu_groupings VALUES ('EEA', 'CY');
INSERT INTO eu_groupings VALUES ('Schengen', 'AT');
INSERT INTO eu_groupings VALUES ('Schengen', 'BE');
INSERT INTO eu_groupings VALUES ('Schengen', 'CZ');
INSERT INTO eu_groupings VALUES ('Schengen', 'DK');
INSERT INTO eu_groupings VALUES ('Schengen', 'EE');

-- Query example: Get EU27 totals
SELECT SUM(data_points) as total_points, SUM(funding) as total_funding
FROM geographic_countries
WHERE country_code IN (SELECT country_code FROM eu_groupings WHERE group_name = 'EU27');
