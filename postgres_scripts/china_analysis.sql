-- Find China-related vendors
SELECT vendor_name, vendor_country, contract_value, contract_date
FROM vendors
WHERE LOWER(vendor_country) IN ('china', 'cn', 'prc')
   OR LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%';

-- Analyze contracts by year
SELECT EXTRACT(YEAR FROM contract_date) as year,
       COUNT(*) as num_contracts,
       SUM(contract_value) as total_value,
       AVG(contract_value) as avg_value
FROM contracts
WHERE vendor_country = 'CN'
GROUP BY year
ORDER BY year DESC;

-- High-value foreign contracts
SELECT vendor_name, vendor_country,
       SUM(contract_value) as total_value,
       COUNT(*) as num_contracts
FROM contracts
WHERE vendor_country NOT IN ('US', 'USA')
  AND contract_value > 1000000
GROUP BY vendor_name, vendor_country
ORDER BY total_value DESC
LIMIT 100;
