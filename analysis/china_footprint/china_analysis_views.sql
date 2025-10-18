-- USASpending China Analysis Queries

-- 1. Find all China-related vendors
CREATE VIEW china_vendors AS
SELECT DISTINCT vendor_name, vendor_country, vendor_city
FROM (
    SELECT * FROM vendor_table
    UNION ALL
    SELECT * FROM recipients_table
) vendors
WHERE LOWER(vendor_country) IN ('china', 'cn', 'prc', 'chinese')
   OR LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%'
   OR LOWER(vendor_name) LIKE '%huawei%'
   OR LOWER(vendor_name) LIKE '%zte%';

-- 2. Aggregate spending by year
CREATE VIEW china_spending_by_year AS
SELECT
    EXTRACT(YEAR FROM transaction_date) as year,
    COUNT(*) as transaction_count,
    SUM(transaction_amount) as total_amount,
    AVG(transaction_amount) as avg_amount
FROM transactions
WHERE vendor_id IN (SELECT vendor_id FROM china_vendors)
GROUP BY EXTRACT(YEAR FROM transaction_date)
ORDER BY year DESC;

-- 3. Top China-linked contracts
CREATE VIEW top_china_contracts AS
SELECT
    contract_id,
    vendor_name,
    contract_value,
    contract_date,
    description
FROM contracts
WHERE vendor_name IN (SELECT vendor_name FROM china_vendors)
ORDER BY contract_value DESC
LIMIT 100;

-- Quick test query
SELECT COUNT(*) as china_vendor_count FROM china_vendors;
