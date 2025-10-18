-- China Analysis Views for USASpending Data

-- View 1: China-related vendors
CREATE OR REPLACE VIEW china_vendors AS
SELECT DISTINCT
    recipient_name as vendor_name,
    recipient_country_code as country,
    recipient_state_code as state,
    COUNT(*) as contract_count,
    SUM(total_obligation_amount) as total_amount,
    MIN(action_date) as first_contract,
    MAX(action_date) as last_contract
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(recipient_name) LIKE '%chinese%'
   OR LOWER(recipient_name) LIKE '%huawei%'
   OR LOWER(recipient_name) LIKE '%zte%'
   OR LOWER(recipient_name) LIKE '%lenovo%'
   OR LOWER(recipient_name) LIKE '%dji%'
GROUP BY recipient_name, recipient_country_code, recipient_state_code;

-- View 2: Agencies with China exposure
CREATE OR REPLACE VIEW agency_china_exposure AS
SELECT
    awarding_agency_name as agency,
    COUNT(DISTINCT contract_award_unique_key) as china_contracts,
    SUM(total_obligation_amount) as total_china_spending,
    COUNT(DISTINCT recipient_name) as unique_china_vendors,
    MAX(action_date) as latest_china_contract
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(product_or_service_description) LIKE '%made in china%'
GROUP BY awarding_agency_name
ORDER BY total_china_spending DESC;

-- View 3: Critical products from China
CREATE OR REPLACE VIEW critical_china_products AS
SELECT
    product_or_service_code as psc_code,
    naics_code,
    product_or_service_description as description,
    COUNT(*) as contract_count,
    SUM(total_obligation_amount) as total_value,
    STRING_AGG(DISTINCT recipient_name, '; ') as vendors
FROM public.contracts
WHERE (LOWER(product_or_service_description) LIKE '%made in china%'
   OR LOWER(recipient_country_code) IN ('cn', 'china', 'prc'))
   AND (
       product_or_service_code LIKE '58%' -- Communication equipment
       OR product_or_service_code LIKE '59%' -- Electrical equipment
       OR product_or_service_code LIKE '70%' -- IT equipment
       OR naics_code LIKE '334%' -- Computer/Electronic manufacturing
   )
GROUP BY product_or_service_code, naics_code, product_or_service_description
ORDER BY total_value DESC;

-- View 4: China spending timeline
CREATE OR REPLACE VIEW china_spending_timeline AS
SELECT
    DATE_TRUNC('month', action_date) as month,
    COUNT(*) as contracts,
    SUM(total_obligation_amount) as amount,
    COUNT(DISTINCT recipient_name) as unique_vendors,
    COUNT(DISTINCT awarding_agency_name) as unique_agencies
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(product_or_service_description) LIKE '%china%'
GROUP BY DATE_TRUNC('month', action_date)
ORDER BY month DESC;
