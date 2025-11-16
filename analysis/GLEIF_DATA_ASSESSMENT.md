# GLEIF Data Assessment

## Date: 2025-10-11

## Currently Downloaded Files (F:/GLEIF)

### Core Entity and Relationship Data (Complete)
1. **LEI Level 2 Golden Copy** - 895MB (lei2-golden-copy.json.zip)
   - Primary entity records with legal names, addresses, entity categories
   - Registration status and managing LOU information

2. **Relationship Record (RR) Golden Copy** - 32MB (rr-golden-copy.json.zip)
   - Direct and ultimate parent relationships
   - Corporate ownership structures
   - Available in JSON and XML formats

3. **Reporting Exceptions (REPEX) Golden Copy** - 55MB (repex-golden-copy.json.zip)
   - Entities that cannot report parent relationships (legal/regulatory reasons)

4. **Delta Files (Last Month)** - 50MB total
   - Recent changes and updates for lei2, rr, repex

### Cross-Reference Mapping Files (Complete)
5. **ISIN-to-LEI Mapping** - 26MB
   - Links securities (ISIN codes) to legal entities (LEI)
   - Critical for investment/portfolio analysis

6. **BIC-to-LEI Mapping** - ~360KB (multiple dates)
   - Links bank identifier codes to LEI
   - Essential for financial institution analysis

7. **QCC-to-LEI Mapping** - 29MB (2 files)
   - Links Chinese company codes (QCC) to LEI
   - **HIGHLY RELEVANT** for China analysis

8. **OpenCorporates-to-LEI Mapping** - 23MB
   - Links OpenCorporates company IDs to LEI
   - Enables cross-referencing with company registers

## Missing Files (Recommended for Download)

### Priority 1: High Value for Analysis
- **MIC-to-LEI Relationship File**
  - Market Identifier Code mappings
  - Use case: Identify which entities operate trading venues/exchanges
  - Strategic value: Track exchange ownership and market infrastructure control

### Priority 2: Optional Enhancement
- **S&P Capital IQ Company ID-to-LEI Relationship**
  - Links S&P financial intelligence data to LEI
  - Use case: Enhanced financial institution analysis
  - Note: May require S&P subscription to fully utilize

## Data Coverage Assessment

### What We Have: EXCELLENT
- ✅ Complete global entity registry (LEI Level 2)
- ✅ Full corporate ownership network (RR golden copy)
- ✅ Reporting exceptions coverage (REPEX)
- ✅ Securities-to-entity mapping (ISIN)
- ✅ Banking institution mapping (BIC)
- ✅ **Chinese company registry links (QCC)** - critical for PRC analysis
- ✅ Global company register integration (OpenCorporates)

### What This Enables
1. **Phase 6 International Links**: Complete corporate ownership network analysis
2. **Cross-border entity tracking**: Follow parent-subsidiary relationships globally
3. **China-specific analysis**: QCC mapping enables direct Chinese company identification
4. **Financial institution mapping**: BIC enables bank relationship tracking
5. **Investment tracking**: ISIN enables portfolio and securities holder analysis

## Processing Priority

### Immediate Processing (High Impact)
1. **LEI Level 2 entities** - Foundation for all other analysis
2. **RR Relationships** - Enables ownership network analysis
3. **QCC-LEI mapping** - Critical for China entity identification

### Secondary Processing (Supporting Data)
4. **ISIN-LEI mapping** - Investment tracking
5. **BIC-LEI mapping** - Financial institution analysis
6. **OpenCorporates-LEI mapping** - Company register integration
7. **REPEX** - Completeness (entities with no parent reporting)

## Recommended Workflow

1. Process LEI Level 2 → Create `gleif_entities` table
2. Process RR relationships → Create `gleif_relationships` table
3. Process QCC mapping → Create `gleif_qcc_mapping` table (China focus)
4. Process cross-references → Create mapping tables for ISIN, BIC, OpenCorporates
5. Create indexed views for fast Phase 6 queries

## Strategic Value for OSINT Analysis

### China Analysis Enhancement
- QCC-to-LEI mapping provides direct link to Chinese corporate entities
- Enables identification of Chinese parent companies for entities operating in target countries
- Can cross-reference with ASPI China Tech Map infrastructure data

### Ownership Network Analysis
- RR relationships enable tracking of ultimate beneficial owners
- Can identify state-owned enterprise connections
- Reveals corporate group structures and control chains

### Financial Links
- ISIN mapping enables tracking of investment positions
- BIC mapping tracks banking relationships
- Combined with SEC_EDGAR data: complete financial link picture

## Next Steps

1. Create comprehensive GLEIF processor script
2. Process LEI entities (895MB JSON file)
3. Process RR relationships (32MB)
4. Process QCC mapping for China analysis enhancement
5. Integrate with Phase 6 international links analysis
6. Consider downloading MIC-to-LEI for exchange ownership analysis

## Estimated Processing Time
- LEI entities: ~30-45 minutes (895MB JSON parsing)
- RR relationships: ~5-10 minutes
- Cross-reference files: ~15-20 minutes total
- **Total: ~1-1.5 hours for complete GLEIF integration**

## Database Schema Requirements

### Tables to Create
1. `gleif_entities` - Core entity records
2. `gleif_relationships` - Parent-child relationships
3. `gleif_qcc_mapping` - Chinese company code mappings
4. `gleif_isin_mapping` - Securities mappings
5. `gleif_bic_mapping` - Bank identifier mappings
6. `gleif_opencorporates_mapping` - Company register links
7. `gleif_repex` - Reporting exceptions

### Indexes Needed
- lei (primary key for all tables)
- country_code (for country-specific queries)
- parent_lei, child_lei (for relationship traversal)
- legal_name (for entity name searches)
- entity_category (for filtering by entity type)
