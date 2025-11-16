-- BCI Cross-Domain Alert Queries
-- Purpose: Detect high-value intelligence through technology convergence
-- Created: 2025-10-26
-- Database: osint_master.db

-- ============================================================================
-- CRITICAL PRIORITY ALERTS
-- ============================================================================

-- Alert 1: BCI + Optogenetics + Chinese/PLA Affiliation
-- Rationale: Enables precise neural control, dual-use for cognitive manipulation
-- Risk Level: CRITICAL
SELECT
    'CRITICAL: BCI+Optogenetics+China' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    CASE
        WHEN oa.institutions LIKE '%PLA%' OR
             oa.institutions LIKE '%People''s Liberation Army%' OR
             oa.institutions LIKE '%Military Medical%' OR
             oa.institutions LIKE '%Academy of Military%'
        THEN 'PLA_AFFILIATED'
        ELSE 'CIVILIAN'
    END AS institution_type,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%optogenetic%' OR
      oa.abstract LIKE '%optogenetic%' OR
      oa.title LIKE '%channelrhodopsin%' OR
      oa.abstract LIKE '%channelrhodopsin%' OR
      oa.title LIKE '%light-activated neuron%' OR
      oa.abstract LIKE '%light-activated neuron%'
  )
ORDER BY
    CASE WHEN oa.institutions LIKE '%PLA%' THEN 0 ELSE 1 END,
    oa.publication_date DESC;

-- Alert 2: Neural Swarm Control (BCI + Multi-Agent + China)
-- Rationale: China leads in both BCI and drone swarms, convergence = military capability
-- Risk Level: CRITICAL
SELECT
    'CRITICAL: Neural_Swarm_Control' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%swarm%' OR
      oa.abstract LIKE '%swarm%' OR
      oa.title LIKE '%multi-agent%' OR
      oa.abstract LIKE '%multi-agent%' OR
      oa.title LIKE '%multi-robot%' OR
      oa.abstract LIKE '%multi-robot%' OR
      oa.title LIKE '%UAV%' OR
      oa.abstract LIKE '%drone%'
  )
ORDER BY oa.publication_date DESC;

-- Alert 3: Focused Ultrasound + BCI (Non-Invasive Neuromodulation)
-- Rationale: Chinese research explosion 2020-2025, enables remote neural control
-- Risk Level: CRITICAL
SELECT
    'CRITICAL: FUS+BCI+China' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count,
    CASE
        WHEN oa.title LIKE '%cognitive%' OR oa.abstract LIKE '%cognitive enhancement%' THEN 'ENHANCEMENT_FOCUS'
        WHEN oa.title LIKE '%military%' OR oa.title LIKE '%defense%' THEN 'MILITARY_FOCUS'
        ELSE 'MEDICAL_FOCUS'
    END AS application_area
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%focused ultrasound%' OR
      oa.abstract LIKE '%focused ultrasound%' OR
      oa.title LIKE '%tFUS%' OR
      oa.title LIKE '%ultrasound neuromodulation%' OR
      oa.abstract LIKE '%ultrasound neuromodulation%'
  )
ORDER BY oa.publication_date DESC;

-- Alert 4: Graphene Electrodes (Advanced BCI Hardware)
-- Rationale: Enables higher-performance BCIs, China strong in graphene research
-- Risk Level: HIGH
SELECT
    'HIGH: Graphene_BCI_Electrodes' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%graphene electrode%' OR
      oa.abstract LIKE '%graphene electrode%' OR
      oa.title LIKE '%graphene neural%' OR
      oa.abstract LIKE '%graphene neural interface%' OR
      oa.title LIKE '%carbon nanotube electrode%' OR
      oa.abstract LIKE '%carbon nanotube electrode%'
  )
ORDER BY oa.publication_date DESC;

-- ============================================================================
-- HIGH PRIORITY ALERTS
-- ============================================================================

-- Alert 5: Neural Dust / Ultrasound-Powered Implants
-- Rationale: US-dominated, watch for Chinese catch-up efforts
-- Risk Level: HIGH
SELECT
    'HIGH: Neural_Dust_China' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%neural dust%' OR
      oa.abstract LIKE '%neural dust%' OR
      oa.title LIKE '%ultrasound-powered%' OR
      oa.abstract LIKE '%ultrasound-powered implant%' OR
      oa.title LIKE '%neurograins%' OR
      oa.abstract LIKE '%wireless neural sensor%'
  )
ORDER BY oa.publication_date DESC;

-- Alert 6: Brain-to-Brain Interface
-- Rationale: Synthetic telepathy for military coordination
-- Risk Level: HIGH
SELECT
    'HIGH: Brain_to_Brain_Interface' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%brain-to-brain%' OR
      oa.abstract LIKE '%brain-to-brain%' OR
      oa.title LIKE '%brain to brain%' OR
      oa.title LIKE '%synthetic telepathy%' OR
      oa.abstract LIKE '%direct brain communication%'
  )
ORDER BY oa.publication_date DESC;

-- Alert 7: Neural Authentication / Brainwave Biometrics
-- Rationale: Dual-use for secure authentication + mass surveillance
-- Risk Level: HIGH
SELECT
    'HIGH: Neural_Authentication_China' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    oa.doi,
    oa.cited_by_count,
    CASE
        WHEN oa.institutions LIKE '%security%' OR
             oa.institutions LIKE '%police%' OR
             oa.institutions LIKE '%surveillance%'
        THEN 'SECURITY_AGENCY'
        ELSE 'RESEARCH_INSTITUTION'
    END AS institution_type
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.title LIKE '%brainwave biometric%' OR
      oa.abstract LIKE '%brainwave biometric%' OR
      oa.title LIKE '%neural authentication%' OR
      oa.abstract LIKE '%eeg authentication%' OR
      oa.title LIKE '%brain-based authentication%'
  )
ORDER BY oa.publication_date DESC;

-- ============================================================================
-- TECHNOLOGY CONVERGENCE DETECTION
-- ============================================================================

-- Alert 8: Multiple Ecosystem Technologies in Single Paper
-- Rationale: Papers combining 2+ ecosystem technologies indicate advanced capability
-- Risk Level: VARIABLE (HIGH if 3+, MEDIUM if 2)
SELECT
    CASE
        WHEN convergence_count >= 3 THEN 'HIGH: Multi-Technology_Convergence'
        ELSE 'MEDIUM: Dual-Technology_Convergence'
    END AS alert_type,
    work_id,
    title,
    publication_date,
    authors,
    institutions,
    countries,
    technologies_detected,
    convergence_count,
    doi
FROM (
    SELECT
        oa.id AS work_id,
        oa.title,
        oa.publication_date,
        oa.authors,
        oa.institutions,
        oa.countries,
        oa.doi,
        GROUP_CONCAT(DISTINCT tech_type, ', ') AS technologies_detected,
        COUNT(DISTINCT tech_type) AS convergence_count
    FROM openalex_works oa
    CROSS JOIN (
        SELECT 'Optogenetics' AS tech_type, 'optogenetic' AS keyword
        UNION ALL SELECT 'Optogenetics', 'channelrhodopsin'
        UNION ALL SELECT 'Neural_Dust', 'neural dust'
        UNION ALL SELECT 'Neural_Dust', 'neurograins'
        UNION ALL SELECT 'FUS', 'focused ultrasound'
        UNION ALL SELECT 'FUS', 'ultrasound neuromodulation'
        UNION ALL SELECT 'Graphene', 'graphene electrode'
        UNION ALL SELECT 'Graphene', 'graphene neural'
        UNION ALL SELECT 'Brain-to-Brain', 'brain-to-brain'
        UNION ALL SELECT 'Brain-to-Brain', 'synthetic telepathy'
        UNION ALL SELECT 'Neural_Swarm', 'swarm' || ' control'
        UNION ALL SELECT 'Neural_Swarm', 'multi-agent'
        UNION ALL SELECT 'TMS_tDCS', 'transcranial magnetic'
        UNION ALL SELECT 'TMS_tDCS', 'tDCS'
        UNION ALL SELECT 'Neural_Auth', 'brainwave biometric'
        UNION ALL SELECT 'Cognitive_Enhancement', 'nootropic'
    ) AS tech_keywords
    WHERE oa.technology_domain = 'Brain_Computer_Interface'
      AND oa.countries LIKE '%CN%'
      AND (oa.title LIKE '%' || tech_keywords.keyword || '%' OR
           oa.abstract LIKE '%' || tech_keywords.keyword || '%')
    GROUP BY oa.id, oa.title, oa.publication_date, oa.authors, oa.institutions, oa.countries, oa.doi
    HAVING COUNT(DISTINCT tech_type) >= 2
)
ORDER BY convergence_count DESC, publication_date DESC;

-- ============================================================================
-- EU-CHINA COLLABORATION ALERTS
-- ============================================================================

-- Alert 9: EU-China BCI Ecosystem Collaborations
-- Rationale: Technology transfer risk via academic collaboration
-- Risk Level: MEDIUM-HIGH (depends on technology)
SELECT
    'COLLAB: EU-China_BCI_Ecosystem' AS alert_type,
    oa.id AS work_id,
    oa.title,
    oa.publication_date,
    oa.authors,
    oa.institutions,
    oa.countries,
    CASE
        WHEN oa.title LIKE '%optogenetic%' THEN 'Optogenetics'
        WHEN oa.title LIKE '%focused ultrasound%' THEN 'FUS'
        WHEN oa.title LIKE '%graphene%' THEN 'Graphene'
        WHEN oa.title LIKE '%swarm%' THEN 'Neural_Swarm'
        ELSE 'BCI_General'
    END AS technology_area,
    oa.doi,
    oa.cited_by_count
FROM openalex_works oa
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND oa.countries LIKE '%CN%'
  AND (
      oa.countries LIKE '%DE%' OR  -- Germany
      oa.countries LIKE '%FR%' OR  -- France
      oa.countries LIKE '%GB%' OR  -- UK
      oa.countries LIKE '%AT%' OR  -- Austria (Graz BCI hub)
      oa.countries LIKE '%NL%' OR  -- Netherlands
      oa.countries LIKE '%ES%' OR  -- Spain
      oa.countries LIKE '%IT%' OR  -- Italy
      oa.countries LIKE '%SE%' OR  -- Sweden
      oa.countries LIKE '%CH%'     -- Switzerland
  )
ORDER BY oa.publication_date DESC;

-- ============================================================================
-- TEMPORAL TREND ANALYSIS
-- ============================================================================

-- Alert 10: Rapid Growth Detection (Year-over-Year Surge)
-- Rationale: Sudden increase in publications indicates strategic priority
-- Risk Level: MEDIUM (indicator of emerging focus)
SELECT
    'TREND: Rapid_Growth_Detection' AS alert_type,
    tech_area,
    year,
    paper_count,
    LAG(paper_count, 1) OVER (PARTITION BY tech_area ORDER BY year) AS prev_year_count,
    CASE
        WHEN LAG(paper_count, 1) OVER (PARTITION BY tech_area ORDER BY year) > 0
        THEN ROUND(100.0 * (paper_count - LAG(paper_count, 1) OVER (PARTITION BY tech_area ORDER BY year)) /
                   LAG(paper_count, 1) OVER (PARTITION BY tech_area ORDER BY year), 1)
        ELSE NULL
    END AS yoy_growth_percent
FROM (
    SELECT
        CASE
            WHEN title LIKE '%optogenetic%' OR abstract LIKE '%optogenetic%' THEN 'Optogenetics'
            WHEN title LIKE '%focused ultrasound%' OR abstract LIKE '%ultrasound neuromodulation%' THEN 'FUS'
            WHEN title LIKE '%graphene electrode%' OR abstract LIKE '%graphene neural%' THEN 'Graphene'
            WHEN title LIKE '%neural dust%' OR title LIKE '%neurograins%' THEN 'Neural_Dust'
            WHEN title LIKE '%swarm%' AND abstract LIKE '%brain%' THEN 'Neural_Swarm'
            WHEN title LIKE '%brain-to-brain%' THEN 'Brain-to-Brain'
            ELSE 'Other_BCI'
        END AS tech_area,
        CAST(strftime('%Y', publication_date) AS INTEGER) AS year,
        COUNT(*) AS paper_count
    FROM openalex_works
    WHERE technology_domain = 'Brain_Computer_Interface'
      AND countries LIKE '%CN%'
      AND publication_date >= '2015-01-01'
    GROUP BY tech_area, year
)
WHERE paper_count IS NOT NULL
ORDER BY tech_area, year DESC;

-- ============================================================================
-- PATENT-RESEARCH CROSS-REFERENCE
-- ============================================================================

-- Alert 11: BCI Research → Chinese Patent Timeline
-- Rationale: Did Chinese companies patent shortly after EU researchers published?
-- Risk Level: HIGH (evidence of technology transfer)
-- NOTE: Requires patents_bilateral table to be populated
SELECT
    'TRANSFER: Research_to_Patent' AS alert_type,
    oa.title AS research_paper,
    oa.publication_date AS research_date,
    oa.authors AS researchers,
    oa.institutions AS research_institution,
    p.patent_number,
    p.filing_date AS patent_date,
    p.assignee_name AS chinese_assignee,
    ROUND(JULIANDAY(p.filing_date) - JULIANDAY(oa.publication_date)) AS days_difference
FROM openalex_works oa
JOIN patents_bilateral p ON p.assignee_country = 'CN'
WHERE oa.technology_domain = 'Brain_Computer_Interface'
  AND (oa.countries LIKE '%EU%' OR oa.countries LIKE '%US%')
  AND p.filing_date > oa.publication_date
  AND p.filing_date <= DATE(oa.publication_date, '+2 years')  -- Patent within 2 years of publication
  AND (
      p.title LIKE '%brain%computer%' OR
      p.abstract LIKE '%neural interface%' OR
      p.abstract LIKE '%brain signal%'
  )
ORDER BY days_difference ASC;

-- ============================================================================
-- USAGE INSTRUCTIONS
-- ============================================================================

-- To run all CRITICAL alerts in sequence:
-- .mode column
-- .headers on
-- .output bci_critical_alerts.txt
-- [Execute Alert 1]
-- [Execute Alert 2]
-- [Execute Alert 3]
-- [Execute Alert 4]
-- .output stdout

-- To export results to CSV:
-- .mode csv
-- .output alert_1_optogenetics.csv
-- [Execute Alert 1]
-- .output stdout

-- To create monitoring dashboard:
-- Run all queries monthly and compare results
-- Flag: New CRITICAL alerts, YoY growth >50%, EU-China collaborations increasing

-- ============================================================================
-- SUMMARY STATISTICS QUERY
-- ============================================================================

-- Summary: BCI Ecosystem Activity Overview
SELECT
    'SUMMARY' AS report_type,
    COUNT(*) AS total_bci_papers,
    SUM(CASE WHEN countries LIKE '%CN%' THEN 1 ELSE 0 END) AS chinese_papers,
    SUM(CASE WHEN countries LIKE '%CN%' AND publication_date >= DATE('now', '-1 year') THEN 1 ELSE 0 END) AS chinese_papers_last_year,
    SUM(CASE WHEN (title LIKE '%optogenetic%' OR abstract LIKE '%optogenetic%') AND countries LIKE '%CN%' THEN 1 ELSE 0 END) AS optogenetics_papers,
    SUM(CASE WHEN (title LIKE '%focused ultrasound%' OR abstract LIKE '%ultrasound neuromodulation%') AND countries LIKE '%CN%' THEN 1 ELSE 0 END) AS fus_papers,
    SUM(CASE WHEN (title LIKE '%graphene electrode%' OR abstract LIKE '%graphene neural%') AND countries LIKE '%CN%' THEN 1 ELSE 0 END) AS graphene_papers,
    SUM(CASE WHEN (title LIKE '%swarm%' AND abstract LIKE '%brain%') AND countries LIKE '%CN%' THEN 1 ELSE 0 END) AS neural_swarm_papers
FROM openalex_works
WHERE technology_domain = 'Brain_Computer_Interface';
