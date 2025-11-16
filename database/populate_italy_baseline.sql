-- ============================================================================
-- ITALY BASELINE DATA WITH MULTI-SOURCE CITATIONS
-- ============================================================================
-- Italy-China relations: 1970 normalization, 2019 BRI join (G7 first), 2023 BRI exit
-- Major acquisition: Pirelli ($7.7B, 2015)
-- ============================================================================

-- Add Pir

elli acquisition (major_acquisitions does not use verification_status)
INSERT OR REPLACE INTO major_acquisitions
(acquisition_id, country_code, target_company, target_sector, target_technology_area,
 chinese_acquirer, acquirer_type, acquisition_date, announcement_date, deal_value_usd,
 ownership_acquired_percentage, deal_structure, strategic_rationale, technology_acquired,
 market_access_gained, employees_at_acquisition, government_review_process,
 approval_conditions, political_controversy, media_attention_level,
 post_acquisition_performance, source_url)
VALUES
('IT_2015_pirelli', 'IT', 'Pirelli & C. S.p.A.', 'automotive_tires',
 'Premium tire manufacturing, high-performance tire technology',
 'ChemChina (China National Chemical Corporation)', 'state_owned',
 '2015-11-23', '2015-03-23', 7700000000, 65.0, 'majority_acquisition',
 'Access to premium tire technology and global automotive supply chains',
 'Premium tire manufacturing technology, racing tire expertise',
 'European automotive sector, luxury and performance car manufacturers',
 30000, 'Limited review, approved without major conditions',
 'None', 0, 'high',
 'Remained independent brand, maintained operations in Italy',
 'https://www.reuters.com/article/us-pirelli-m-a-chemchina-idUSKBN0TC1JQ20151123');

-- Add bilateral events (check schema for this table too)
INSERT OR REPLACE INTO bilateral_events
(event_id, country_code, event_date, event_title, event_type, event_category,
 event_significance, participants, event_description, event_outcomes,
 geopolitical_context, media_coverage, source_type, source_url)
VALUES
('IT_1970_normalization', 'IT', '1970-11-06',
 'Italy-PRC Diplomatic Normalization',
 'diplomatic', 'diplomatic_relations', 'major',
 'Italian Government, People''s Republic of China',
 'Italy recognizes the People''s Republic of China and establishes diplomatic relations',
 'Establishment of embassies in Rome and Beijing',
 'Part of broader Western European recognition of PRC in early 1970s',
 'high', 'official_statement',
 'https://www.esteri.it/mae/en/sala_stampa/archivionotizie/approfondimenti/2020/11/rapporti-bilaterali-italia-cina.html'),

('IT_2004_strategic_partnership', 'IT', '2004-05-08',
 'Italy-China Comprehensive Strategic Partnership',
 'diplomatic', 'strategic_partnership', 'major',
 'Italian PM Silvio Berlusconi, Chinese Premier Wen Jiabao',
 'Italy and China elevate bilateral relationship to Comprehensive Strategic Partnership',
 'Enhanced cooperation in trade, investment, culture, science and technology',
 NULL, 'high', 'news',
 'http://www.chinadaily.com.cn/english/doc/2004-05/08/content_327893.htm'),

('IT_2019_bri_mou', 'IT', '2019-03-23',
 'Italy Signs Belt and Road Initiative MoU',
 'economic', 'bri_agreement', 'critical',
 'Italian PM Giuseppe Conte, Chinese President Xi Jinping',
 'Italy becomes first G7 country to officially join China''s Belt and Road Initiative',
 '29 bilateral cooperation agreements worth €2.5 billion signed',
 'Major controversy within EU and NATO allies, concerns about Chinese influence',
 'critical', 'official_statement',
 'http://www.governo.it/it/articolo/italia-cina-firmato-il-memorandum-sulla-belt-and-road-initiative/11720'),

('IT_2023_bri_withdrawal', 'IT', '2023-12-06',
 'Italy Withdraws from Belt and Road Initiative',
 'economic', 'bri_withdrawal', 'major',
 'Italian PM Giorgia Meloni',
 'Italy officially withdraws from China''s Belt and Road Initiative after 4 years',
 'Italy becomes first country to exit BRI after joining; signals shift in relations',
 'Reflects growing Western concerns about BRI, alignment with EU and US positions',
 'high', 'news',
 'https://www.reuters.com/world/italy-officially-quits-chinas-belt-road-initiative-2023-12-06/');

SELECT 'ITALY BASELINE DATA INSERTED' as status;
