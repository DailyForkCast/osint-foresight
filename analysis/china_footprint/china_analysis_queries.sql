-- China-related vendor search
SELECT * FROM vendor_table
WHERE LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%chinese%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%';

-- Contract analysis by year
SELECT EXTRACT(YEAR FROM contract_date) as year,
       COUNT(*) as contracts,
       SUM(amount) as total_amount
FROM contracts_table
GROUP BY year
ORDER BY year DESC;

-- Foreign entity analysis
SELECT country_code,
       COUNT(*) as entity_count,
       SUM(total_amount) as total_value
FROM international_vendors
WHERE country_code = 'CN'
GROUP BY country_code;
