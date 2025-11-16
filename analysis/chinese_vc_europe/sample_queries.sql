-- Sample SQL Queries for China Capital Flows Analysis
-- Generated: 2025-10-25 15:11:18

-- Flow 1 (Primary Concern) - All Validated

SELECT
    flow_id,
    western_entity_name,
    western_entity_country,
    western_entity_sector,
    chinese_entity_name,
    capital_amount_usd,
    transaction_date
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
ORDER BY transaction_date DESC;
            

-- US vs Europe Flow 1 Comparison

SELECT
    CASE
        WHEN western_entity_country = 'US' THEN 'United States'
        WHEN western_entity_country IN ('GB','DE','FR','IT','ES','NL','BE','AT','SE','DK') THEN 'Europe'
        ELSE 'Other'
    END as region,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
GROUP BY region;
            

-- Temporal Trend (Annual)

SELECT
    strftime('%Y', transaction_date) as year,
    flow_pattern,
    COUNT(*) as count,
    SUM(capital_amount_usd) as total_usd
FROM china_capital_flows_comprehensive
WHERE validation_status = 'VALIDATED'
GROUP BY year, flow_pattern
ORDER BY year DESC, flow_pattern;
            

-- Top Chinese VC Firms (Flow 1)

SELECT
    chinese_entity_name,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital,
    COUNT(DISTINCT western_entity_sector) as sectors_invested
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND validation_status = 'VALIDATED'
GROUP BY chinese_entity_name
ORDER BY investment_count DESC;
            

-- Dual-Use Technology Sectors

SELECT
    western_entity_sector,
    COUNT(*) as investment_count,
    SUM(capital_amount_usd) as total_capital,
    COUNT(DISTINCT chinese_entity_name) as unique_chinese_investors
FROM china_capital_flows_comprehensive
WHERE flow_pattern = 1
AND western_entity_is_dual_use = 1
AND validation_status = 'VALIDATED'
GROUP BY western_entity_sector
ORDER BY investment_count DESC;
            

