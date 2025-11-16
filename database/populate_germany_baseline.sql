-- Populate Germany Baseline Data
-- Major Acquisitions and Key Events

-- ============================================================================
-- MAJOR ACQUISITIONS (Completed)
-- ============================================================================

-- Kuka AG (2016) - $5B robotics acquisition
INSERT OR REPLACE INTO major_acquisitions
(acquisition_id, country_code, target_company, target_sector, target_technology_area,
 chinese_acquirer, acquirer_type, acquisition_date, announcement_date, deal_value_usd,
 ownership_acquired_percentage, deal_structure, strategic_rationale, technology_acquired,
 market_access_gained, employees_at_acquisition, government_review_process,
 approval_conditions, political_controversy, media_attention_level,
 post_acquisition_performance, source_url)
VALUES
('DE_2016_kuka', 'DE', 'Kuka AG', 'robotics', 'Industrial robotics, AI manufacturing',
 'Midea Group', 'private', '2016-08-08', '2016-05-18', 5000000000,
 94.5, 'full_acquisition', 'Access to Industry 4.0 robotics technology',
 'Advanced industrial robotics, automation systems, AI-powered manufacturing',
 'European automotive and manufacturing sectors', 13300,
 'Controversial in Bundestag, technology transfer concerns',
 'Employment guarantees for German workers', 1, 'high',
 'Retained in Germany, employment guarantees maintained',
 'https://www.reuters.com/article/us-kuka-m-a-midea-group-idUSKCN0Z50WX');

-- Putzmeister (2012) - $525M construction equipment
INSERT OR REPLACE INTO major_acquisitions
(acquisition_id, country_code, target_company, target_sector, target_technology_area,
 chinese_acquirer, acquirer_type, acquisition_date, announcement_date, deal_value_usd,
 ownership_acquired_percentage, deal_structure, strategic_rationale, technology_acquired,
 employees_at_acquisition, political_controversy, media_attention_level,
 post_acquisition_performance, source_url)
VALUES
('DE_2012_putzmeister', 'DE', 'Putzmeister Holding GmbH', 'construction_equipment',
 'Concrete pumping technology', 'Sany Heavy Industry', 'private',
 '2012-01-31', '2012-01-31', 525000000, 100.0, 'full_acquisition',
 'Technology acquisition, post-Fukushima relevance',
 'Large-scale concrete pumping systems used at Fukushima',
 3200, 0, 'medium', 'Operations maintained in Germany',
 'https://www.bbc.com/news/business-16822285');

-- KraussMaffei (2016) - $1B machinery
INSERT OR REPLACE INTO major_acquisitions
(acquisition_id, country_code, target_company, target_sector, target_technology_area,
 chinese_acquirer, acquirer_type, acquisition_date, announcement_date, deal_value_usd,
 ownership_acquired_percentage, deal_structure, strategic_rationale, technology_acquired,
 employees_at_acquisition, political_controversy, media_attention_level, source_url)
VALUES
('DE_2016_kraussmaffei', 'DE', 'KraussMaffei Group', 'machinery',
 'Plastics and rubber processing machinery', 'ChemChina', 'soe',
 '2016-01-15', '2015-09-15', 1000000000, 100.0, 'full_acquisition',
 'Advanced manufacturing technology, plastics processing expertise',
 'Injection molding machines, extrusion technology, reaction process machinery',
 4700, 0, 'medium', 'https://www.kraussmaffei.com/');

-- ============================================================================
-- BILATERAL EVENTS (Blocked deals and controversies)
-- ============================================================================

-- Aixtron blocked (2016) - Semiconductor equipment
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_url, source_type, source_reliability)
VALUES
('DE_2016_aixtron_blocked', 'DE', '2016-10-24', 2016, 'controversy', 'economic',
 'Germany blocks Aixtron acquisition',
 'German government blocked Chinese acquisition of Aixtron SE (semiconductor equipment) for $742M following US national security concerns. Led to tightening of FDI screening rules.',
 1, 'negative', 'Policy shift: Increased FDI scrutiny for strategic technologies',
 'https://www.reuters.com/article/us-aixtron-m-a-china-idUSKBN12N20M',
 'news', 2);

-- 50Hertz blocked (2018) - Energy grid
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_url, source_type, source_reliability)
VALUES
('DE_2018_50hertz_blocked', 'DE', '2018-07-27', 2018, 'policy_shift', 'economic',
 'Germany blocks State Grid from 50Hertz stake',
 'German government via KfW intervened to block State Grid Corporation of China from acquiring 20% stake in 50Hertz electricity transmission operator. Critical infrastructure protection.',
 1, 'negative', 'Government intervention to protect critical energy infrastructure',
 'https://www.reuters.com/article/us-elia-m-a-50hertz-idUSKBN1KI0RD',
 'news', 2);

-- Hamburg Port controversy (2022)
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_url, source_type, source_reliability)
VALUES
('DE_2022_hamburg_port', 'DE', '2022-10-26', 2022, 'controversy', 'economic',
 'Hamburg Port COSCO stake approved with conditions',
 'Chancellor Scholz approved reduced 24.9% COSCO stake in Hamburg container terminal CTT (down from 35% request). Coalition government split: Foreign, Economy, Interior ministries opposed. Significant public controversy.',
 2, 'mixed', 'Compromise solution amid growing China skepticism. Ongoing debate over port security.',
 'https://www.dw.com/en/germany-approves-cosco-stake-in-hamburg-port/a-63569781',
 'news', 2);

-- Diplomatic normalization (1972)
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_type, source_reliability)
VALUES
('DE_1972_normalization', 'DE', '1972-10-11', 1972, 'agreement', 'diplomatic',
 'West Germany-PRC diplomatic normalization',
 'Federal Republic of Germany (West Germany) established diplomatic relations with the People''s Republic of China under Chancellor Willy Brandt.',
 1, 'positive', 'Foundation of Germany-China bilateral relationship',
 'official_statement', 1);

-- Strategic Partnership (2004)
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_type, source_reliability)
VALUES
('DE_2004_strategic_partnership', 'DE', '2004-05-01', 2004, 'agreement', 'diplomatic',
 'Germany-China Strategic Partnership',
 'Germany and China established a strategic partnership during Chancellor Gerhard Schröder''s visit to China.',
 1, 'positive', 'Elevation of bilateral relationship status',
 'official_statement', 1);

-- Comprehensive Strategic Partnership (2014)
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_type, source_reliability)
VALUES
('DE_2014_comprehensive_partnership', 'DE', '2014-03-28', 2014, 'agreement', 'diplomatic',
 'Germany-China Comprehensive Strategic Partnership',
 'Germany and China upgraded to a Comprehensive Strategic Partnership during President Xi Jinping''s state visit to Germany. Chancellor Angela Merkel''s 7th China visit.',
 1, 'positive', 'Peak of Germany-China engagement under Merkel',
 'official_statement', 1);

-- China Strategy 2023
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_year, event_type, event_category,
 event_title, event_description, importance_tier, sentiment, strategic_significance,
 source_url, source_type, source_reliability)
VALUES
('DE_2023_china_strategy', 'DE', '2023-07-13', 2023, 'policy_shift', 'political',
 'Germany publishes China Strategy',
 'German government under Chancellor Scholz published comprehensive China strategy describing China as "partner, competitor, and systemic rival." Marks shift toward more cautious approach.',
 1, 'mixed', 'Major policy realignment: De-risking, reducing dependencies, values-based approach',
 'https://www.auswaertiges-amt.de/en/aussenpolitik/china',
 'official_statement', 1);

-- ============================================================================
-- Summary Statistics
-- ============================================================================

SELECT 'GERMANY BASELINE DATA POPULATED' as status;
SELECT COUNT(*) as acquisitions_count, SUM(deal_value_usd)/1e9 as total_value_billions
FROM major_acquisitions WHERE country_code = 'DE';
SELECT COUNT(*) as events_count FROM bilateral_events WHERE country_code = 'DE';
