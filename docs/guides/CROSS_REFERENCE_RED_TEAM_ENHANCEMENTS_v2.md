# Cross-Reference Analysis Master Plan - Red-Team Enhancements v2.0
**Date:** October 2, 2025
**Purpose:** Critical improvements to incorporate into main master plan
**Source:** ChatGPT red-team review

---

## 🎯 EXECUTIVE SUMMARY OF CHANGES

This document contains **critical methodological improvements** identified through red-team review of the original Cross-Reference Analysis Master Plan v1.0. These enhancements focus on:

1. **Precision over recall** - Stricter detection rules to avoid false positives
2. **Detector independence** - Avoiding double-counting correlated signals
3. **Maximum extraction** - Deeper analysis of each data source
4. **Methodological rigor** - Calibration, validation, and provenance
5. **Database optimization** - DuckDB for analytics, PostgreSQL for OLTP

---

## 🔴 CRITICAL ISSUE #1: PSC Over-Estimation

### **Problem:**
Current PSC detection (1.13M Chinese PSCs) likely includes false positives:
- Conflating PRC with HK/MO/TW
- Using residence instead of nationality as primary signal
- Not deduplicating by (company_number, psc_id)
- Including ceased PSCs without time-slicing

### **Solution: PSC Re-Estimation Protocol**

#### **Step 1: Strict Detection Rules**
```python
def is_chinese_psc_strict(psc_record):
    """
    Strict Chinese PSC detection - nationality-first approach
    Returns (is_chinese, confidence_score, evidence)
    """
    evidence = []

    # PRIMARY: Nationality field (95% confidence)
    if psc_record.nationality in ['Chinese', 'China', 'CN', 'CHN', "People's Republic of China"]:
        # Exclude HK/MO/TW unless explicitly opted in
        if psc_record.nationality not in ['Hong Kong', 'Macau', 'Taiwan', 'HK', 'MO', 'TW']:
            evidence.append(('nationality_prc', psc_record.nationality, 95))

    # SECONDARY: Country of residence (85% confidence, only if nationality matches OR corporate)
    if psc_record.country_of_residence in ['China', 'CN', 'CHN']:
        # Exclude HK/MO for individuals unless nationality also matches
        if psc_record.kind == 'corporate-entity-person-with-significant-control':
            # Corporate PSC registered in PRC
            if 'China' in psc_record.address.get('country', ''):
                evidence.append(('corporate_prc_registered', psc_record.country_of_residence, 90))
        elif evidence:  # Individual with PRC nationality AND residence
            evidence.append(('residence_confirms_nationality', psc_record.country_of_residence, 85))

    # TERTIARY: Chinese characters in name (85% confidence, only if other signals)
    if contains_chinese_characters(psc_record.psc_name) and evidence:
        evidence.append(('chinese_script', 'CJK characters detected', 85))

    # FILTER: Exclude if only residence/script signals (too weak)
    if not any(sig[0].startswith('nationality') or sig[0].startswith('corporate') for sig in evidence):
        return False, 0, []

    # Calculate confidence (max of evidence signals, not additive)
    confidence = max([sig[2] for sig in evidence])

    return True, confidence, evidence
```

#### **Step 2: Deduplication**
```python
# Deduplicate by (company_number, psc_id)
# Collapse ceased PSCs unless time-slicing
deduped_psc = psc_records.drop_duplicates(subset=['company_number', 'psc_id'])

# Filter to active only (unless doing temporal analysis)
active_psc = deduped_psc[deduped_psc['ceased_on'].isna()]
```

#### **Step 3: Stratified Manual Audit (2%)**
```python
# Sample 2% of detected PSCs, stratified by detection type
audit_sample = []
for detection_type in ['nationality_only', 'nationality_residence', 'corporate_prc']:
    subset = chinese_psc[chinese_psc['detection_type'] == detection_type]
    sample_size = max(50, int(len(subset) * 0.02))  # At least 50 per type
    audit_sample.extend(subset.sample(n=sample_size))

# Manual review → measure precision
# Precision = true_positives / (true_positives + false_positives)
# Report with confidence interval
```

#### **Step 4: Revised Estimate with Confidence Interval**
```python
# After re-running with strict rules + audit
chinese_psc_strict = apply_strict_detection(psc_records)

# Calculate confidence interval (95%)
n = len(chinese_psc_strict)
precision_from_audit = 0.92  # Example: 92% precision from audit
margin_of_error = 1.96 * sqrt(precision_from_audit * (1 - precision_from_audit) / n)

print(f"Chinese PSCs (strict): {n:,}")
print(f"Precision: {precision_from_audit:.1%} ± {margin_of_error:.1%}")
print(f"True positives (estimated): {int(n * precision_from_audit):,} - {int(n * (precision_from_audit + margin_of_error)):,}")
```

#### **Step 5: Publish Reconciliation Note**
```markdown
# PSC Detection Reconciliation Note

## Original Estimate (v1.0):
- **1,130,197 Chinese PSCs** detected using broad criteria
- Included: HK/MO/TW, residence-based, ceased records

## Revised Estimate (v2.0):
- **[X] Chinese PSCs** detected using strict nationality-first criteria
- Excluded: HK/MO/TW (unless opted in), residence-only, ceased records
- Precision: [Y]% ± [Z]% (from 2% manual audit)

## Why the Change:
- Avoid conflating PRC with HK/MO/TW (different legal/political status)
- Nationality is stronger signal than residence (per UK PSC guidance)
- Deduplication removes double-counts
- Active-only filter removes historical ceased PSCs

## Toggles Available:
- `include_hk_mo_tw` - Set True to include Hong Kong/Macau/Taiwan
- `include_ceased` - Set True for temporal analysis including historical PSCs
- `residence_only` - Set True to include residence-based detections (lower confidence)
```

---

## 🔴 CRITICAL ISSUE #2: Entity Resolution - CJK Support

### **Problem:**
Current normalization doesn't handle Chinese/Japanese/Korean names properly:
- Family name vs. given name order varies
- Pinyin variants (Zhang vs. Chang)
- Simplified vs. Traditional characters
- Corporate suffixes (有限公司 vs. Ltd)

### **Solution: Extended CJK Normalization**

```python
import opencc  # Simplified ↔ Traditional Chinese conversion
from pypinyin import lazy_pinyin, Style

def normalize_cjk_name(name, entity_type='company'):
    """
    Advanced CJK name normalization
    Returns: (canonical_name, aliases)
    """
    aliases = [name]  # Original name

    # 1. Detect script
    has_cjk = contains_chinese_characters(name)

    if has_cjk:
        # 2. Generate Simplified ↔ Traditional variants
        converter_s2t = opencc.OpenCC('s2t')  # Simplified to Traditional
        converter_t2s = opencc.OpenCC('t2s')  # Traditional to Simplified

        simplified = converter_t2s.convert(name)
        traditional = converter_s2t.convert(name)

        aliases.extend([simplified, traditional])

        # 3. Generate Pinyin variants (with and without tones)
        pinyin_full = ' '.join(lazy_pinyin(name, style=Style.TONE))
        pinyin_no_tone = ' '.join(lazy_pinyin(name, style=Style.NORMAL))

        aliases.extend([pinyin_full, pinyin_no_tone])

        # 4. Corporate suffix handling
        if entity_type == 'company':
            # Remove common Chinese corporate suffixes
            chinese_suffixes = [
                '有限公司', '股份有限公司', '集团', '集團',
                '科技', '技术', '技術', '实业', '實業'
            ]
            for suffix in chinese_suffixes:
                if suffix in name:
                    aliases.append(name.replace(suffix, '').strip())

    # 5. English normalization (always apply)
    english_suffixes = ['Ltd', 'Limited', 'Inc', 'Corp', 'GmbH', 'SA', 'SPA', 'BV']
    name_no_suffix = name
    for suffix in english_suffixes:
        name_no_suffix = re.sub(rf'\b{suffix}\b', '', name_no_suffix, flags=re.IGNORECASE)

    aliases.append(name_no_suffix.strip())

    # 6. Canonical: Use Simplified Chinese + English suffix removed
    if has_cjk:
        canonical = converter_t2s.convert(name_no_suffix).strip().lower()
    else:
        canonical = name_no_suffix.strip().lower()

    # 7. Remove duplicates, preserve provenance
    aliases = list(dict.fromkeys(aliases))  # Dedupe preserving order

    return canonical, aliases

def normalize_cjk_person_name(name):
    """
    Handle family-name-first vs. given-name-first
    Example: "Zhang Wei" vs. "Wei Zhang"
    """
    # If name has CJK characters, assume family-first
    if contains_chinese_characters(name):
        # Generate both orders for matching
        parts = name.split()
        if len(parts) == 2:
            family_first = name
            given_first = f"{parts[1]} {parts[0]}"
            return [family_first, given_first]

    # English names: assume given-first
    return [name]
```

#### **Storage Schema Update**
```sql
-- Add aliases table for name variants
CREATE TABLE name_aliases (
    alias_id TEXT PRIMARY KEY,
    entity_id TEXT,
    alias TEXT,
    alias_type TEXT,  -- original, simplified, traditional, pinyin, suffix_removed
    provenance TEXT,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

-- Create trigram index for fuzzy matching
CREATE INDEX idx_aliases_trigram ON name_aliases USING gin (alias gin_trgm_ops);
```

---

## 🔴 CRITICAL ISSUE #3: Risk Scoring - Detector Independence

### **Problem:**
Current risk scoring adds points for multiple detections without checking correlation:
- "≥3 sources = +30 points" may double-count if sources are correlated
- Example: OpenAlex + CORDIS likely correlated (both academic), should down-weight

### **Solution: Bayesian Fusion with Detector Correlation Matrix**

#### **Step 1: Build Detector Correlation Matrix**
```python
import numpy as np
from sklearn.metrics import matthews_corrcoef

# For each pair of detectors, compute correlation on entity set
detectors = ['usaspending', 'openalex', 'cordis', 'patents', 'psc', 'sec_edgar']

correlation_matrix = np.zeros((len(detectors), len(detectors)))

for i, det_a in enumerate(detectors):
    for j, det_b in enumerate(detectors):
        if i == j:
            correlation_matrix[i, j] = 1.0
        else:
            # Binary: Does detector A fire? Does detector B fire?
            det_a_fires = entities['detection_sources'].str.contains(det_a)
            det_b_fires = entities['detection_sources'].str.contains(det_b)

            # Matthews correlation coefficient (robust to imbalance)
            correlation_matrix[i, j] = matthews_corrcoef(det_a_fires, det_b_fires)

# Example output:
#                usaspending  openalex  cordis  patents  psc  sec_edgar
# usaspending        1.00      0.15     0.12    0.25    0.08   0.35
# openalex           0.15      1.00     0.65    0.55    0.05   0.10
# cordis             0.12      0.65     1.00    0.50    0.04   0.08
# patents            0.25      0.55     0.50    1.00    0.10   0.30
# psc                0.08      0.05     0.04    0.10    1.00   0.15
# sec_edgar          0.35      0.10     0.08    0.30    0.15   1.00

# Observation: OpenAlex ↔ CORDIS highly correlated (0.65) - both academic
```

#### **Step 2: Down-Weight Correlated Detectors**
```python
def calculate_independent_evidence_weight(detectors_fired, correlation_matrix):
    """
    Calculate effective evidence weight accounting for correlation
    Uses Cholesky decomposition to find independent components
    """
    # Map detector names to indices
    detector_indices = [detectors.index(d) for d in detectors_fired]

    if len(detector_indices) == 1:
        return 1.0  # Single detector, full weight

    # Extract sub-matrix for fired detectors
    sub_matrix = correlation_matrix[np.ix_(detector_indices, detector_indices)]

    # Eigenvalue decomposition to find effective dimensionality
    eigenvalues = np.linalg.eigvalsh(sub_matrix)
    effective_dimensions = np.sum(eigenvalues) / len(eigenvalues)

    # Weight: effective_dimensions / actual_dimensions
    # Example: 3 detectors, but eigenvalues suggest only 2 independent → weight = 2/3
    return effective_dimensions
```

#### **Step 3: Bayesian Risk Fusion (Replaces Additive Scoring)**
```python
def calculate_bayesian_risk_score(entity, correlation_matrix):
    """
    Bayesian fusion of detector signals with independence adjustment
    Returns: (posterior_probability, risk_score_0_100)
    """
    # Prior: Base rate of China connections in general population
    # Estimate from data: ~1-5% of entities have China connections
    prior_prob = 0.02  # 2% base rate

    # Likelihood ratios for each detector (from calibration set)
    # Example: If PSC detects Chinese owner, how much more likely is entity China-connected?
    likelihood_ratios = {
        'psc_nationality': 50.0,           # Very strong signal (50x more likely)
        'sec_edgar_china_listed': 30.0,    # Strong (30x)
        'usaspending_cn_address': 20.0,    # Strong (20x)
        'patents_cn_inventor': 5.0,        # Moderate (5x)
        'openalex_cn_collab': 3.0,         # Moderate (3x)
        'cordis_cn_partner': 2.5,          # Moderate (2.5x)
    }

    # Get detections for this entity
    detections = entity.china_connections.detections

    # Calculate combined likelihood ratio with independence adjustment
    combined_lr = 1.0
    detectors_fired = []

    for detection in detections:
        detector_id = detection['detector_id']
        detectors_fired.append(detector_id.split('_')[0])  # Extract source name
        lr = likelihood_ratios.get(detection['detector_id'], 2.0)  # Default 2.0 if unknown
        combined_lr *= lr

    # Apply independence adjustment
    independence_weight = calculate_independent_evidence_weight(detectors_fired, correlation_matrix)

    # Shrink combined LR toward 1.0 based on correlation
    # If fully independent (weight=1.0), use full combined_lr
    # If fully correlated (weight→0), shrink toward 1.0 (no evidence)
    adjusted_lr = 1.0 + (combined_lr - 1.0) * independence_weight

    # Bayes' rule: P(China|evidence) = P(evidence|China) * P(China) / P(evidence)
    # Using odds form: posterior_odds = likelihood_ratio * prior_odds
    prior_odds = prior_prob / (1 - prior_prob)
    posterior_odds = adjusted_lr * prior_odds
    posterior_prob = posterior_odds / (1 + posterior_odds)

    # Convert to 0-100 score
    risk_score = min(100, int(posterior_prob * 100))

    return posterior_prob, risk_score
```

#### **Step 4: Calibration on Gold Set**
```python
# Build gold set: ~300 entities manually labeled
# HIGH (100 entities): Known China-connected (verified)
# LOW (100 entities): Known NOT China-connected (verified)
# CRITICAL (100 entities): High-risk China-connected (verified)

gold_set = [
    {'entity_id': '...', 'label': 'HIGH', 'detections': [...]},
    # ... 300 total
]

# Run Bayesian scoring on gold set
predictions = []
for entity in gold_set:
    posterior_prob, risk_score = calculate_bayesian_risk_score(entity, correlation_matrix)
    predictions.append({
        'entity_id': entity['entity_id'],
        'true_label': entity['label'],
        'posterior_prob': posterior_prob,
        'risk_score': risk_score
    })

# Calculate ROC curve and AUC
from sklearn.metrics import roc_curve, roc_auc_score

true_labels = [1 if p['true_label'] in ['HIGH', 'CRITICAL'] else 0 for p in predictions]
scores = [p['posterior_prob'] for p in predictions]

fpr, tpr, thresholds = roc_curve(true_labels, scores)
auc = roc_auc_score(true_labels, scores)

print(f"AUC: {auc:.3f}")

# Find threshold for 90% precision on CRITICAL
critical_labels = [1 if p['true_label'] == 'CRITICAL' else 0 for p in predictions]
critical_scores = [p['posterior_prob'] for p in predictions]

# Binary search for threshold achieving 90% precision
for threshold in np.linspace(0.5, 1.0, 100):
    predicted_critical = [1 if s >= threshold else 0 for s in critical_scores]
    tp = sum([1 for i, pred in enumerate(predicted_critical) if pred == 1 and critical_labels[i] == 1])
    fp = sum([1 for i, pred in enumerate(predicted_critical) if pred == 1 and critical_labels[i] == 0])

    if tp + fp > 0:
        precision = tp / (tp + fp)
        if precision >= 0.90:
            print(f"Threshold for 90% precision on CRITICAL: {threshold:.3f}")
            print(f"  Precision: {precision:.1%}, Recall: {tp / sum(critical_labels):.1%}")
            break
```

---

## 🔴 CRITICAL ISSUE #4: Maximum Extraction Per Source

### **Problem:**
Current plan doesn't fully exploit each data source's unique capabilities

### **Solution: Source-Specific Extraction Enhancements**

#### **Companies House: Ownership Trees**
```python
def build_ownership_tree(company_number, psc_db, companies_db, max_depth=5):
    """
    Recursively build ownership tree: PSC → Company → Corporate PSC → ...
    Calculate effective ownership % with chain propagation
    """
    tree = {'company_number': company_number, 'children': []}

    # Get all PSCs for this company
    pscs = psc_db.query(f"SELECT * FROM psc WHERE company_number = '{company_number}' AND ceased_on IS NULL")

    for psc in pscs:
        ownership_pct = extract_ownership_percentage(psc['natures_of_control'])

        node = {
            'psc_name': psc['psc_name'],
            'psc_kind': psc['psc_kind'],
            'ownership_pct': ownership_pct,
            'nationality': psc['nationality'],
            'children': []
        }

        # If PSC is a corporate entity, recurse
        if psc['psc_kind'] == 'corporate-entity-person-with-significant-control' and max_depth > 0:
            # Try to find company number for this corporate PSC
            corporate_company_number = resolve_corporate_psc_to_company(psc, companies_db)
            if corporate_company_number:
                node['children'] = build_ownership_tree(corporate_company_number, psc_db, companies_db, max_depth - 1)

        tree['children'].append(node)

    return tree

def calculate_effective_ownership(ownership_tree, path_ownership=1.0):
    """
    Calculate effective ownership % through multi-layer chains
    Example: A owns 60% of B, B owns 50% of C → A effectively owns 30% of C
    """
    effective_owners = []

    for psc in ownership_tree['children']:
        current_ownership = path_ownership * (psc['ownership_pct'] / 100.0)

        # If leaf node (individual or no children), record ownership
        if not psc['children'] or psc['psc_kind'] != 'corporate-entity-person-with-significant-control':
            effective_owners.append({
                'psc_name': psc['psc_name'],
                'nationality': psc['nationality'],
                'effective_ownership_pct': current_ownership * 100,
                'chain_depth': int(np.log10(path_ownership / current_ownership + 1))
            })
        else:
            # Recurse through children
            effective_owners.extend(calculate_effective_ownership(psc['children'], current_ownership))

    return effective_owners
```

#### **USAspending: Full UEI Normalization**
```python
def normalize_usaspending_to_uei(usaspending_db):
    """
    USAspending has migrated from DUNS to UEI (Unique Entity Identifier)
    Extract and normalize all entity identifiers
    """
    # UEI is in multiple fields depending on file schema
    uei_fields = [
        'awardee_or_recipient_uei',
        'ultimate_parent_uei',
        'vendor_uei',
        'recipient_uei'
    ]

    for contract in usaspending_db:
        # Extract UEI from any available field
        contract['normalized_uei'] = None
        for field in uei_fields:
            if field in contract and contract[field]:
                contract['normalized_uei'] = contract[field].strip().upper()
                break

        # Also normalize NAICS/PSC codes to technology buckets
        contract['technology_categories'] = map_naics_to_technology(contract.get('naics_code'))
        contract['procurement_categories'] = map_psc_to_category(contract.get('psc_code'))

        # Include subaward data (if available)
        if 'subawards' in contract:
            contract['subaward_entities'] = [
                normalize_entity(sub['recipient']) for sub in contract['subawards']
            ]

    return usaspending_db
```

#### **Patents: CPC → Technology Buckets**
```python
# Map CPC (Cooperative Patent Classification) to strategic technology areas
CPC_TECHNOLOGY_MAPPING = {
    'artificial_intelligence': [
        'G06N',  # Computing arrangements based on specific computational models
        'G06T',  # Image data processing
        'G10L',  # Speech analysis or synthesis
    ],
    'semiconductors': [
        'H01L',  # Semiconductor devices
        'H01S',  # Lasers
        'C23C',  # Coating by vacuum evaporation
    ],
    'quantum': [
        'G06N10',  # Quantum computing
        'H04L9/0852',  # Quantum cryptography
        'B82Y',  # Nanostructures
    ],
    'telecommunications': [
        'H04L',  # Transmission of digital information
        'H04W',  # Wireless communication networks
        'H04B',  # Transmission
    ],
    # ... more mappings
}

def map_cpc_to_technology_buckets(cpc_codes):
    """Convert patent CPC codes to strategic technology categories"""
    technologies = set()

    for cpc in cpc_codes:
        for tech, cpc_list in CPC_TECHNOLOGY_MAPPING.items():
            if any(cpc.startswith(cpc_prefix) for cpc_prefix in cpc_list):
                technologies.add(tech)

    return list(technologies)

def enhance_patent_record(patent):
    """Add technology buckets and inventor/assignee geo tracking"""
    patent['technology_buckets'] = map_cpc_to_technology_buckets(patent['cpc_codes'])

    # Track first-filing country (priority country)
    patent['first_filing_country'] = extract_priority_country(patent.get('priority_claims', []))

    # Geo-locate inventors and assignees
    patent['inventor_countries'] = [inv['country'] for inv in patent.get('inventors', [])]
    patent['assignee_countries'] = [asn['country'] for asn in patent.get('assignees', [])]

    # China collaboration = at least one CN inventor/assignee + at least one non-CN
    cn_involvement = 'CN' in patent['inventor_countries'] or 'CN' in patent['assignee_countries']
    non_cn_involvement = any(c != 'CN' for c in patent['inventor_countries'] + patent['assignee_countries'])
    patent['china_collaboration'] = cn_involvement and non_cn_involvement

    return patent
```

#### **Research: Join OpenAlex + OpenAIRE + Crossref**
```python
def deduplicate_research_by_doi(openalex_db, openaire_db, crossref_db):
    """
    Merge research records from multiple sources using DOI as key
    Enrich with department parsing and co-author communities
    """
    merged_research = {}

    # Index by DOI
    for source_name, source_db in [('openalex', openalex_db), ('openaire', openaire_db), ('crossref', crossref_db)]:
        for record in source_db:
            doi = record.get('doi')
            if not doi:
                continue

            doi = doi.lower().strip()

            if doi not in merged_research:
                merged_research[doi] = {
                    'doi': doi,
                    'sources': [],
                    'title': record.get('title'),
                    'publication_date': record.get('publication_date'),
                    'authors': [],
                    'affiliations': [],
                    'departments': [],
                }

            merged_research[doi]['sources'].append(source_name)

            # Merge authors (deduplicate by name)
            for author in record.get('authors', []):
                if author not in merged_research[doi]['authors']:
                    merged_research[doi]['authors'].append(author)

            # Parse departments from affiliation strings
            for affiliation in record.get('affiliations', []):
                dept = parse_department(affiliation)
                if dept and dept not in merged_research[doi]['departments']:
                    merged_research[doi]['departments'].append(dept)

    return list(merged_research.values())

def parse_department(affiliation_string):
    """
    Extract department from affiliation string
    Example: "Department of Computer Science, University of Oxford" → "Computer Science"
    """
    dept_patterns = [
        r'Department of ([^,]+)',
        r'Dept\. of ([^,]+)',
        r'School of ([^,]+)',
        r'Faculty of ([^,]+)',
        r'Institute of ([^,]+)',
    ]

    for pattern in dept_patterns:
        match = re.search(pattern, affiliation_string, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None

def compute_coauthor_communities(research_db):
    """
    Build co-author network and detect research communities
    Helps identify persistent China collaboration clusters
    """
    import networkx as nx
    from networkx.algorithms import community

    G = nx.Graph()

    # Add edges for each co-authorship
    for paper in research_db:
        authors = paper['authors']
        for i, author_a in enumerate(authors):
            for author_b in authors[i+1:]:
                # Edge weight = number of co-authored papers
                if G.has_edge(author_a['name'], author_b['name']):
                    G[author_a['name']][author_b['name']]['weight'] += 1
                else:
                    G.add_edge(author_a['name'], author_b['name'], weight=1)

    # Detect communities (Louvain algorithm)
    communities = community.greedy_modularity_communities(G)

    # Label each community by dominant country
    community_profiles = []
    for i, comm in enumerate(communities):
        countries = []
        for author_name in comm:
            # Look up author country from research records
            for paper in research_db:
                for author in paper['authors']:
                    if author['name'] == author_name and 'affiliation' in author:
                        countries.append(extract_country(author['affiliation']))

        country_dist = Counter(countries)
        community_profiles.append({
            'community_id': i,
            'size': len(comm),
            'country_distribution': dict(country_dist),
            'has_china': 'CN' in country_dist,
            'china_percentage': country_dist.get('CN', 0) / len(countries) if countries else 0
        })

    return community_profiles
```

---

## 🔴 CRITICAL ISSUE #5: Database Architecture - DuckDB + PostgreSQL

### **Problem:**
Using SQLite for all storage is suboptimal:
- SQLite: Good for OLTP, poor for analytics on large datasets
- No native JSON indexing, limited parallelization

### **Solution: Hybrid Architecture**

#### **DuckDB for Analytics**
```python
import duckdb

# DuckDB: Columnar storage, optimized for analytics
analytics_db = duckdb.connect('unified_intelligence_analytics.duckdb')

# Load data from source SQLite databases
analytics_db.execute("""
    CREATE TABLE entities AS
    SELECT * FROM sqlite_scan('usaspending_china.db', 'contracts')
    UNION ALL
    SELECT * FROM sqlite_scan('openalex_collaborations.db', 'collaborations')
    -- ... other sources
""")

# Create columnar indexes for fast aggregation
analytics_db.execute("CREATE INDEX idx_entities_country ON entities(country_code)")
analytics_db.execute("CREATE INDEX idx_entities_tech ON entities(technology_category)")

# Fast analytical queries (parallelized)
result = analytics_db.execute("""
    SELECT
        country_code,
        technology_category,
        COUNT(*) as entity_count,
        SUM(risk_score) as total_risk
    FROM entities
    WHERE has_china_connection = true
    GROUP BY country_code, technology_category
    ORDER BY total_risk DESC
""").fetchdf()  # Returns pandas DataFrame
```

#### **PostgreSQL for OLTP + Indexing**
```python
import psycopg2

# PostgreSQL: ACID compliance, complex queries, JSON indexing
oltp_db = psycopg2.connect("dbname=unified_intelligence user=analyst")

# Create tables with advanced indexing
oltp_db.execute("""
    CREATE TABLE entities (
        entity_id UUID PRIMARY KEY,
        canonical_name TEXT,
        aliases JSONB,  -- JSON with indexing
        source_data JSONB,
        ...
    );

    -- GIN index on JSON columns for fast lookups
    CREATE INDEX idx_aliases_gin ON entities USING gin (aliases);
    CREATE INDEX idx_source_data_gin ON entities USING gin (source_data);

    -- Trigram index for fuzzy text search
    CREATE EXTENSION pg_trgm;
    CREATE INDEX idx_canonical_name_trgm ON entities USING gin (canonical_name gin_trgm_ops);
""")
```

#### **SQLite for Unit Testing**
```python
# Keep SQLite for small-scale testing and prototyping
test_db = sqlite3.connect(':memory:')  # In-memory for tests

# Run unit tests on small datasets
def test_entity_resolution():
    # Create test entities
    test_db.execute("INSERT INTO entities VALUES (...)")
    # Test fuzzy matching
    assert fuzzy_match('Huawei Technologies', 'HUAWEI TECH') > 0.85
```

---

## 🔴 CRITICAL ISSUE #6: Validation Suite

### **Problem:**
Current plan has validation, but missing:
- Negative controls (similar names, non-Chinese)
- Temporal sanity checks
- False discovery rate estimation

### **Solution: Comprehensive Validation Suite**

#### **Negative Controls**
```python
# Build negative control set: entities with Chinese-sounding names but NOT Chinese
negative_controls = [
    {'name': 'Chang Enterprises', 'country': 'US', 'expected_detection': False, 'reason': 'Korean surname, US company'},
    {'name': 'Li & Fung Limited', 'country': 'HK', 'expected_detection': False, 'reason': 'Hong Kong, not PRC'},
    {'name': 'Beijing Restaurant', 'country': 'US', 'expected_detection': False, 'reason': 'Named after city, not Chinese-owned'},
    # ... 100 more
]

# Run detections on negative controls
false_positives = 0
for control in negative_controls:
    entity = create_test_entity(control)
    is_detected = run_china_detection(entity)

    if is_detected and not control['expected_detection']:
        false_positives += 1
        print(f"FALSE POSITIVE: {control['name']} - {control['reason']}")

fpr = false_positives / len(negative_controls)
print(f"False Positive Rate on Negative Controls: {fpr:.1%}")
```

#### **Temporal Sanity Checks**
```python
def validate_temporal_consistency(entity):
    """
    Check that events are chronologically consistent
    Example: PSC notified_on must precede first linked activity
    """
    errors = []

    # Check: PSC notification before first activity
    psc_notified_date = entity.psc_records[0]['notified_on'] if entity.psc_records else None
    first_activity_date = min([a['activity_date'] for a in entity.activities]) if entity.activities else None

    if psc_notified_date and first_activity_date:
        if psc_notified_date > first_activity_date:
            errors.append(f"PSC notified ({psc_notified_date}) AFTER first activity ({first_activity_date})")

    # Check: Company incorporation before contracts awarded
    incorporation_date = entity.incorporation_date
    if incorporation_date:
        for activity in entity.activities:
            if activity['activity_type'] == 'contract' and activity['activity_date'] < incorporation_date:
                errors.append(f"Contract awarded ({activity['activity_date']}) BEFORE incorporation ({incorporation_date})")

    # Check: Patent filing before grant
    for patent in entity.patents:
        if patent['grant_date'] < patent['filing_date']:
            errors.append(f"Patent granted ({patent['grant_date']}) BEFORE filed ({patent['filing_date']})")

    return errors

# Run temporal validation on all entities
temporal_errors = []
for entity in entities:
    errors = validate_temporal_consistency(entity)
    if errors:
        temporal_errors.append({'entity_id': entity.entity_id, 'errors': errors})

print(f"Temporal validation errors: {len(temporal_errors)}")
```

#### **Placebo Detectors (False Discovery Rate)**
```python
def estimate_false_discovery_rate():
    """
    Run "placebo detectors" with random tokens to estimate FDR
    Example: Search for "Gondwana" (ancient supercontinent) in company names
    Any detections are guaranteed false positives
    """
    placebo_tokens = [
        'Gondwana', 'Pangaea', 'Atlantis', 'Xanadu', 'Shangri-La',
        'Zephyr', 'Quixote', 'Nebula', 'Zenith', 'Aurora'
    ]

    placebo_detections = 0
    total_entities = len(entities)

    for token in placebo_tokens:
        detections = [e for e in entities if token.lower() in e.canonical_name.lower()]
        placebo_detections += len(detections)
        print(f"Placebo '{token}': {len(detections)} detections")

    # Average placebo detection rate
    avg_placebo_rate = placebo_detections / (len(placebo_tokens) * total_entities)

    # Estimated FDR: Compare to actual China detection rate
    china_detection_rate = len([e for e in entities if e.has_china_connection]) / total_entities

    fdr_estimate = avg_placebo_rate / china_detection_rate if china_detection_rate > 0 else 0

    print(f"Estimated False Discovery Rate: {fdr_estimate:.1%}")
    print(f"  Placebo detection rate: {avg_placebo_rate:.3%}")
    print(f"  China detection rate: {china_detection_rate:.3%}")

    return fdr_estimate
```

---

## 🔴 CRITICAL ISSUE #7: Enhanced Provenance

### **Problem:**
Current provenance (file, line number) is good but missing:
- Detector version (for reproducibility)
- Feature hash (which specific features fired)
- Temporal range (when was this valid)

### **Solution: Extended Provenance Schema**

```sql
CREATE TABLE china_connections (
    connection_id TEXT PRIMARY KEY,
    entity_id TEXT,

    -- Original fields
    detection_layer TEXT,
    evidence TEXT,
    confidence_score INTEGER,

    -- ENHANCED PROVENANCE
    detector_id TEXT,              -- e.g., 'psc_nationality_v2.0'
    detector_version TEXT,          -- e.g., 'v2.0_strict_20251002'
    feature_hash TEXT,              -- SHA256 of features that fired
    feature_details JSONB,          -- Full feature values
    temporal_range JSONB,           -- {"valid_from": "2020-01-01", "valid_to": "2025-10-01"}

    -- Audit trail
    detected_at TIMESTAMP,
    last_verified TIMESTAMP,
    verification_method TEXT,       -- 'manual_review', 'automated_check', 'cross_source_confirm'

    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);
```

```python
def record_detection_with_provenance(entity_id, detection):
    """
    Record China detection with full provenance
    """
    import hashlib
    import json

    # Compute feature hash
    feature_json = json.dumps(detection['features'], sort_keys=True)
    feature_hash = hashlib.sha256(feature_json.encode()).hexdigest()

    # Store detection
    china_connections.insert({
        'connection_id': generate_uuid(),
        'entity_id': entity_id,
        'detection_layer': detection['layer'],
        'evidence': detection['evidence_text'],
        'confidence_score': detection['confidence'],

        # Enhanced provenance
        'detector_id': f"{detection['source']}_{detection['detector_name']}_v{DETECTOR_VERSION}",
        'detector_version': DETECTOR_VERSION,
        'feature_hash': feature_hash,
        'feature_details': detection['features'],
        'temporal_range': {
            'valid_from': detection.get('valid_from', '1900-01-01'),
            'valid_to': detection.get('valid_to', '9999-12-31')
        },

        # Audit
        'detected_at': datetime.now().isoformat(),
        'last_verified': None,
        'verification_method': None
    })
```

---

## 🎯 QUICK WINS (PRIORITY IMPLEMENTATION ORDER)

### **Week 1: Re-Run PSC with Strict Rules**
- [ ] Implement strict PSC detection (nationality-first)
- [ ] Deduplicate by (company_number, psc_id)
- [ ] Run 2% stratified audit
- [ ] Publish reconciliation note

**Expected Impact:** More credible PSC numbers, higher precision

### **Week 2: Detector Correlation Matrix**
- [ ] Build correlation matrix for all detectors
- [ ] Implement Bayesian fusion with independence weighting
- [ ] Replace additive scoring with calibrated probabilities

**Expected Impact:** Eliminate double-counting, more accurate risk scores

### **Week 3: Stand Up DuckDB**
- [ ] Install DuckDB
- [ ] Port validation queries from Appendix C
- [ ] Run performance benchmarks vs SQLite

**Expected Impact:** 10-100x faster analytics queries

### **Week 4: USAspending Canary Checks**
- [ ] Identify 10 known PRC-linked vendors (Huawei, ZTE, DJI, etc.)
- [ ] Add automated checks: "These vendors MUST be detected every run"
- [ ] Alert if canary vendors missing

**Expected Impact:** Early detection of ETL bugs, data quality assurance

---

## 📊 VALIDATION METRICS (TARGET THRESHOLDS)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **PSC Precision** | ≥90% | 2% stratified manual audit |
| **Entity Resolution Accuracy** | ≥85% exact, ≥80% fuzzy | Manual review of 100 matches |
| **False Positive Rate** | <5% | Negative controls + placebo detectors |
| **Temporal Consistency** | 100% | Automated checks (PSC before activities) |
| **Cross-Source Coverage** | ≥70% entities in ≥2 sources | Database query |
| **AUC for Risk Scoring** | ≥0.85 | ROC on gold set (300 entities) |
| **CRITICAL Precision** | ≥90% | Calibration threshold tuning |
| **FDR Estimate** | <10% | Placebo detectors |

---

## 🚨 ETHICAL & SAFETY CONSIDERATIONS

### **PRC vs HK/MO/TW Distinction**
- **WHY:** Different legal systems, political status, risk profiles
- **HOW:** Separate detection toggles, clear labeling in outputs
- **OUTPUT:** "China (PRC)" vs "Hong Kong (SAR)" vs "Taiwan" vs "Macau (SAR)"

### **Nationality vs Residence**
- **WHY:** Nationality is permanent identity, residence can be temporary
- **HOW:** Nationality as primary signal (95% confidence), residence as secondary (85%)
- **OUTPUT:** Label detections as "PRC national" vs "PRC resident" vs "Both"

### **PSC Data Protection**
- **WHY:** PSC data includes personal information (names, addresses, nationalities)
- **HOW:** Use only for lawful purposes (due diligence, risk assessment, research)
- **OUTPUT:** Anonymize in public reports, retain full data internally for legal use

### **Sanctions Overlay**
- **WHY:** Sanctioned entities require special handling
- **HOW:** If on OFAC/EU/UK sanctions lists, cap risk at HIGH+ or raise to CRITICAL
- **OUTPUT:** "SANCTIONED" flag in entity records, separate from China connection score

---

## 📝 IMPLEMENTATION CHECKLIST

### **Phase 0: Pre-Work (Before Entity Resolution)**
- [ ] Re-run PSC detection with strict rules
- [ ] Build CJK normalization functions
- [ ] Build detector correlation matrix
- [ ] Create gold set (300 entities: 100 HIGH, 100 LOW, 100 CRITICAL)
- [ ] Install DuckDB and PostgreSQL (optional)

### **Phase 1: Data Ingestion (Revised)**
- [ ] Extract all source data to staging
- [ ] Apply CJK normalization to company names
- [ ] Normalize USAspending to UEI
- [ ] Map patent CPC codes to technology buckets
- [ ] Merge research sources by DOI
- [ ] Build Companies House ownership trees

### **Phase 2: Entity Resolution (Revised)**
- [ ] Exact matching by unique IDs
- [ ] Fuzzy matching with CJK-aware normalization
- [ ] Network-based resolution (shared attributes)
- [ ] Store all name aliases with provenance

### **Phase 3: Cross-Reference (Revised)**
- [ ] Consolidate China connections with enhanced provenance
- [ ] Apply Bayesian risk fusion (not additive scoring)
- [ ] Build relationship graph with ownership chains
- [ ] Generate technology profiles with CPC buckets

### **Phase 4: Validation (NEW)**
- [ ] Run negative controls (100 entities)
- [ ] Run temporal sanity checks (all entities)
- [ ] Run placebo detectors (estimate FDR)
- [ ] Calibrate risk scoring on gold set
- [ ] Set CRITICAL threshold for 90% precision

### **Phase 5: Reporting**
- [ ] Entity dossiers with provenance
- [ ] Sector reports with technology deep dives
- [ ] Geographic reports (81 countries)
- [ ] Publish PSC reconciliation note
- [ ] Publish validation report (precision, recall, FDR)

---

## 📚 REFERENCES & FURTHER READING

- **Entity Resolution:** Christen, P. (2012). Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection. Springer.
- **Bayesian Fusion:** Pearl, J. (1988). Probabilistic Reasoning in Intelligent Systems. Morgan Kaufmann.
- **CJK Normalization:** OpenCC library (https://github.com/BYVoid/OpenCC)
- **DuckDB:** https://duckdb.org/docs/
- **UK PSC Register Guidance:** Companies House (https://www.gov.uk/government/publications/guidance-to-the-people-with-significant-control-requirements-for-companies-and-limited-liability-partnerships)

---

**END OF RED-TEAM ENHANCEMENTS v2.0**

**Recommendation:** Incorporate these enhancements into master plan incrementally, starting with Quick Wins (PSC re-run, detector correlation, DuckDB, canary checks).
