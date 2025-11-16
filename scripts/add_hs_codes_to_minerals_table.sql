-- Add HS Code Columns to semiconductor_critical_minerals Table
-- Date: 2025-11-10
-- Purpose: Integrate HS code mappings for trade flow analysis
-- Source: semiconductor_critical_minerals_hs_mapping.json

-- Step 1: Add new columns for HS codes
ALTER TABLE semiconductor_critical_minerals ADD COLUMN hs_codes_primary TEXT;
ALTER TABLE semiconductor_critical_minerals ADD COLUMN hs_codes_all TEXT;
ALTER TABLE semiconductor_critical_minerals ADD COLUMN hs_code_count INTEGER DEFAULT 0;
ALTER TABLE semiconductor_critical_minerals ADD COLUMN trade_classification TEXT;
ALTER TABLE semiconductor_critical_minerals ADD COLUMN export_controls TEXT;

-- Step 2: Update each mineral with HS code mappings

-- Silicon (id=1): Ultra-pure silicon for wafer substrates
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280461',
    hs_codes_all = '280461,280469,381800',
    hs_code_count = 3,
    trade_classification = 'Primary material / Processed substrate',
    export_controls = 'China export licensing 2023'
WHERE id = 1;

-- Gallium (id=2): GaN power devices, RF amplifiers
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280450',
    hs_codes_all = '280450,381800,285000',
    hs_code_count = 3,
    trade_classification = 'Critical mineral - China export ban Aug 2023',
    export_controls = 'China export ban Aug 2023, US monitoring'
WHERE id = 2;

-- Germanium (id=3): SiGe transistors, infrared optics
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280490',
    hs_codes_all = '280490,381800',
    hs_code_count = 2,
    trade_classification = 'Critical mineral - China export ban Aug 2023',
    export_controls = 'China export ban Aug 2023'
WHERE id = 3;

-- Rare Earth Elements (id=4): Magnets, phosphors, polishing
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280530',
    hs_codes_all = '280530,284610,284690',
    hs_code_count = 3,
    trade_classification = 'Critical minerals - Strategic stockpile',
    export_controls = 'US stockpile material, China export licensing'
WHERE id = 4;

-- Neon Gas (id=5): Excimer lasers for lithography
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280429',
    hs_codes_all = '280429',
    hs_code_count = 1,
    trade_classification = 'Critical gas - Semiconductor manufacturing essential',
    export_controls = 'No formal controls, but supply shock risk (Ukraine war 2022)'
WHERE id = 5;

-- Argon, Xenon, Krypton (id=6): Plasma etching, ion implantation
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '280421',
    hs_codes_all = '280421,280429',
    hs_code_count = 2,
    trade_classification = 'Industrial gases - Widely available',
    export_controls = 'None'
WHERE id = 6;

-- Fluorine Compounds (id=7): Etching, cleaning, CVD
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '281111',
    hs_codes_all = '281111,281290',
    hs_code_count = 2,
    trade_classification = 'Hazardous chemicals - Export controlled',
    export_controls = 'Hazmat regulations, Japan-Korea trade restrictions precedent'
WHERE id = 7;

-- Tungsten (id=8): Interconnects, vias, gate electrodes
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '810194',
    hs_codes_all = '260110,810194,284920',
    hs_code_count = 3,
    trade_classification = 'Strategic metal - China processing dominance',
    export_controls = 'Monitoring for potential future controls'
WHERE id = 8;

-- Cobalt (id=9): Copper barrier layers, advanced interconnects
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '810520',
    hs_codes_all = '260500,810520,282200',
    hs_code_count = 3,
    trade_classification = 'Critical mineral - Conflict mineral (DRC)',
    export_controls = 'Dodd-Frank conflict mineral reporting, China refining dominance'
WHERE id = 9;

-- Tantalum (id=10): Capacitors, barrier layers
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '810320',
    hs_codes_all = '261590,810320',
    hs_code_count = 2,
    trade_classification = 'Conflict mineral - RMI certification common',
    export_controls = 'Dodd-Frank conflict mineral, military export controls'
WHERE id = 10;

-- Indium (id=11): ITO, solders, compound semiconductors
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '811292',
    hs_codes_all = '811292,381800',
    hs_code_count = 2,
    trade_classification = 'Critical mineral - Byproduct dependency',
    export_controls = 'China dominance monitoring'
WHERE id = 11;

-- Hafnium (id=12): High-k dielectrics, gate oxides
UPDATE semiconductor_critical_minerals
SET hs_codes_primary = '811292',
    hs_codes_all = '811292,284990',
    hs_code_count = 2,
    trade_classification = 'CRITICAL - Essential for <22nm nodes',
    export_controls = 'BIS ECCN 1C235 (nuclear dual-use)'
WHERE id = 12;

-- Step 3: Verification query
SELECT
    id,
    mineral_name,
    hs_codes_primary,
    hs_code_count,
    supply_chain_risk,
    china_market_share,
    export_controls
FROM semiconductor_critical_minerals
ORDER BY id;

-- Step 4: Create indexed view for trade analysis
CREATE VIEW IF NOT EXISTS semiconductor_minerals_trade_ready AS
SELECT
    scm.id,
    scm.mineral_name,
    scm.primary_use,
    scm.supply_chain_risk,
    scm.china_market_share,
    scm.strategic_importance,
    scm.hs_codes_primary,
    scm.hs_codes_all,
    scm.hs_code_count,
    scm.export_controls,
    -- Split HS codes into individual rows for joining with trade data
    value as hs_code_individual
FROM semiconductor_critical_minerals scm,
     json_each('["' || REPLACE(scm.hs_codes_all, ',', '","') || '"]');

-- Usage example: Join with trade data
-- SELECT scm.mineral_name, td.reporter_country, td.partner_country, SUM(td.trade_value)
-- FROM semiconductor_minerals_trade_ready scm
-- JOIN comtrade_data td ON scm.hs_code_individual = td.commodity_code
-- WHERE td.partner_country = 'CN' AND td.year = 2024
-- GROUP BY scm.mineral_name, td.reporter_country
-- ORDER BY SUM(td.trade_value) DESC;

COMMIT;
