# PROMPT: TED PROCUREMENT PROCESSING & CROSS-SYSTEM VALIDATION FRAMEWORK

## CONTEXT
You are working on the OSINT China Risk Intelligence Platform. There is €2 trillion worth of EU public procurement data sitting unprocessed at F:/TED_Data/monthly/ covering years 2006-2025. This data could reveal Chinese contractors, technology procurement patterns, and dual-use technology acquisitions in the EU.

## PRIMARY OBJECTIVES

### 1. PROCESS TED PROCUREMENT DATA
**Location**: F:/TED_Data/monthly/
**Format**: Compressed XML files (tar.gz) organized by year/month
**Volume**: ~50GB compressed, ~500GB uncompressed
**Years Available**: 2006-2025

**Required Processing Steps**:
```python
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
import json

def process_ted_data():
    """
    Extract and parse TED XML files to identify:
    1. Chinese contractors/suppliers
    2. Technology-related contracts
    3. Dual-use goods procurement
    4. Research collaborations
    """

    # Database to store results
    ted_db = "F:/OSINT_WAREHOUSE/ted_procurement.db"

    # Chinese entity patterns to search for
    chinese_patterns = [
        "Huawei", "ZTE", "Alibaba", "Tencent", "Baidu",
        "CRRC", "COSCO", "China", "Chinese", "Beijing",
        "Shanghai", "Shenzhen", "Guangzhou", "中国"
    ]

    # Technology keywords
    tech_keywords = [
        "artificial intelligence", "AI", "machine learning",
        "semiconductor", "5G", "telecommunications",
        "quantum", "biotechnology", "aerospace", "satellite",
        "cyber", "encryption", "surveillance", "drone"
    ]

    # Start with recent years first (more relevant)
    for year in range(2023, 2019, -1):  # 2023, 2022, 2021, 2020
        process_year(year)
```

**Priority Processing**:
1. Start with 2020-2024 (most recent/relevant)
2. Focus on technology sectors
3. Extract: contractor name, contract value, technology area, dates
4. Create searchable database

**Expected Outputs**:
- SQLite database with parsed contracts
- China-linked contractors list
- Technology procurement patterns
- Temporal trend analysis

### 2. BUILD CROSS-SYSTEM VALIDATION FRAMEWORK

Create a validation system that ensures data consistency across all intelligence systems:

```python
class CrossSystemValidator:
    def __init__(self):
        self.systems = {
            'bis': "F:/OSINT_WAREHOUSE/osint_master.db",
            'ted': "F:/OSINT_WAREHOUSE/ted_procurement.db",
            'patents': "F:/OSINT_Data/USPTO/uspto_patents_20250926.db",
            'trade': "F:/OSINT_Data/Trade_Facilities/uncomtrade_v2.db",
            'research': "F:/OSINT_WAREHOUSE/openalex_china_final.db"
        }

    def validate_entity(self, entity_name):
        """
        Check if entity appears consistently across systems
        Return validation report with confidence scores
        """
        results = {}

        # Normalize entity name
        normalized = self.normalize_entity_name(entity_name)

        # Check each system
        for system, db_path in self.systems.items():
            results[system] = self.check_system(normalized, db_path)

        # Calculate cross-system confidence
        confidence = self.calculate_confidence(results)

        return {
            'entity': entity_name,
            'normalized': normalized,
            'systems_found': results,
            'confidence': confidence,
            'validation': 'PASS' if confidence > 0.6 else 'NEEDS_REVIEW'
        }

    def batch_validate(self):
        """Run validation on all high-priority entities"""
        priority_entities = [
            "Huawei Technologies",
            "Semiconductor Manufacturing International Corporation",
            "Beijing University of Aeronautics and Astronautics",
            "Tsinghua University",
            "ZTE Corporation"
        ]

        for entity in priority_entities:
            report = self.validate_entity(entity)
            self.save_validation_report(report)
```

**Validation Rules**:
- Entity name normalization (handle variations)
- Temporal alignment (same time periods)
- Risk score consistency (±10% variance acceptable)
- Technology classification matching
- Geographic consistency

**Output Format**:
```json
{
    "entity": "Huawei Technologies",
    "validation_timestamp": "2025-09-28T12:00:00Z",
    "systems_detected": {
        "bis": true,
        "ted": true,
        "patents": true,
        "trade": false,
        "research": true
    },
    "confidence_score": 0.85,
    "inconsistencies": [],
    "recommendation": "HIGH_CONFIDENCE"
}
```

### 3. IMPLEMENT LEONARDO STANDARD SCORING

The Leonardo Standard is a 20-point scoring system for technology criticality assessment:

```python
class LeonardoStandardScorer:
    """
    Leonardo Standard: 20-point technology assessment
    Based on Italy defense contractor framework
    """

    def score_technology(self, technology_data):
        score = 0
        details = {}

        # 1. Exact Technology Match (0-3 points)
        if self.is_exact_match(technology_data):
            score += 3
            details['exact_match'] = "Perfect match to critical technology list"
        elif self.is_variant_match(technology_data):
            score += 2
            details['exact_match'] = "Variant of critical technology"
        else:
            score += 1
            details['exact_match'] = "Related technology area"

        # 2. China Access Assessment (0-3 points)
        china_access = self.assess_china_access(technology_data)
        if china_access == "unrestricted":
            score += 3
            details['china_access'] = "China has unrestricted access"
        elif china_access == "limited":
            score += 2
            details['china_access'] = "China has limited access"
        else:
            score += 1
            details['china_access'] = "China access restricted"

        # 3. Exploitation Path (0-3 points)
        exploitation = self.identify_exploitation_path(technology_data)
        if exploitation == "direct":
            score += 3
            details['exploitation'] = "Direct exploitation path identified"
        elif exploitation == "indirect":
            score += 2
            details['exploitation'] = "Indirect path via third parties"
        else:
            score += 1
            details['exploitation'] = "Theoretical exploitation possible"

        # 4. Timeline Criticality (0-3 points)
        timeline = self.assess_timeline(technology_data)
        if timeline == "immediate":
            score += 3
            details['timeline'] = "Immediate threat (0-6 months)"
        elif timeline == "near_term":
            score += 2
            details['timeline'] = "Near-term threat (6-24 months)"
        else:
            score += 1
            details['timeline'] = "Long-term concern (>24 months)"

        # 5. Alternative Sources (0-2 points)
        if not self.has_alternatives(technology_data):
            score += 2
            details['alternatives'] = "No alternative sources available"
        elif self.has_limited_alternatives(technology_data):
            score += 1
            details['alternatives'] = "Limited alternatives exist"
        else:
            details['alternatives'] = "Multiple alternatives available"

        # 6. Dual-Use Potential (0-3 points)
        dual_use = self.assess_dual_use(technology_data)
        if dual_use == "confirmed":
            score += 3
            details['dual_use'] = "Confirmed military applications"
        elif dual_use == "probable":
            score += 2
            details['dual_use'] = "Probable military applications"
        else:
            score += 1
            details['dual_use'] = "Possible dual-use applications"

        # 7. Oversight Gaps (0-3 points)
        if self.has_oversight_gaps(technology_data):
            score += 3
            details['oversight'] = "Significant oversight gaps identified"
        elif self.has_partial_oversight(technology_data):
            score += 2
            details['oversight'] = "Partial oversight coverage"
        else:
            score += 1
            details['oversight'] = "Adequate oversight mechanisms"

        return {
            'technology': technology_data['name'],
            'leonardo_score': score,
            'max_score': 20,
            'risk_level': self.get_risk_level(score),
            'scoring_details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def get_risk_level(self, score):
        if score >= 15:
            return "CRITICAL"
        elif score >= 10:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
```

**Apply to All Technologies**:
```python
# Score all technologies found in TED data
technologies_to_score = [
    "5G telecommunications equipment",
    "AI facial recognition systems",
    "Quantum computing components",
    "Semiconductor manufacturing equipment",
    "Satellite communication systems"
]

for tech in technologies_to_score:
    score = scorer.score_technology({'name': tech})
    save_to_database(score)
```

### 4. ZERO FABRICATION PROTOCOL

Implement strict data integrity checking:

```python
class ZeroFabricationProtocol:
    """
    Ensures all data claims have verifiable sources
    Never estimate, assume, or fabricate
    """

    def __init__(self):
        self.forbidden_terms = [
            "typically", "generally", "usually", "likely",
            "probably", "estimated", "approximately", "expected"
        ]
        self.required_evidence = {
            'numeric_claims': 'source_required',
            'percentage_claims': 'calculation_shown',
            'trend_claims': 'data_points_required',
            'comparison_claims': 'both_values_required'
        }

    def validate_claim(self, claim_text, evidence=None):
        """
        Validate that a claim has proper evidence
        """
        # Check for forbidden terms
        for term in self.forbidden_terms:
            if term.lower() in claim_text.lower():
                return {
                    'valid': False,
                    'reason': f"Contains forbidden term: '{term}'",
                    'suggestion': "Replace with specific, evidenced statement"
                }

        # Check for numeric claims
        if any(char.isdigit() for char in claim_text):
            if not evidence or 'source' not in evidence:
                return {
                    'valid': False,
                    'reason': "Numeric claim without source",
                    'suggestion': "Add source reference or remove number"
                }

        # Validate evidence quality
        if evidence:
            if 'source' in evidence:
                if not self.verify_source_exists(evidence['source']):
                    return {
                        'valid': False,
                        'reason': "Source cannot be verified",
                        'suggestion': "Use only accessible, verifiable sources"
                    }

        return {'valid': True, 'validated_at': datetime.now().isoformat()}

    def document_gap(self, gap_type, description):
        """
        When data is missing, document it transparently
        """
        gap_record = {
            'gap_type': gap_type,
            'description': description,
            'documented_at': datetime.now().isoformat(),
            'attempted_sources': [],
            'recommendation': "Acknowledge gap in analysis"
        }

        # Save to gap log
        with open('data_gaps_log.json', 'a') as f:
            json.dump(gap_record, f)
            f.write('\n')

        return f"DATA GAP: {description} [Logged at {gap_record['documented_at']}]"
```

## IMPLEMENTATION SEQUENCE

### Phase 1: TED Data Processing (Week 1)
1. Set up TED database schema
2. Process 2023-2024 data first (most relevant)
3. Extract Chinese contractor patterns
4. Create searchable index

### Phase 2: Cross-System Validation (Week 2)
1. Build entity normalization functions
2. Create validation framework
3. Run batch validation on priority entities
4. Generate validation reports

### Phase 3: Leonardo Scoring (Week 3)
1. Implement 20-point scoring system
2. Score all identified technologies
3. Rank by criticality
4. Create risk matrix

### Phase 4: Zero Fabrication Protocol (Ongoing)
1. Implement validation checks
2. Create gap documentation system
3. Add to all output functions
4. Regular audit trail generation

## SUCCESS METRICS

1. **TED Processing**:
   - Process minimum 2020-2024 data
   - Identify 100+ Chinese contractors
   - Extract 1000+ technology contracts

2. **Validation Framework**:
   - 95% entity name matching accuracy
   - <5% false positive rate
   - All high-priority entities validated

3. **Leonardo Scoring**:
   - Score 100+ technologies
   - Identify top 20 critical technologies
   - Generate risk matrix

4. **Zero Fabrication**:
   - 100% of claims have sources
   - 0% forbidden terms in output
   - All gaps documented

## ERROR HANDLING

```python
def safe_process_with_logging(func):
    """Decorator for safe processing with full logging"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            log_success(func.__name__, result)
            return result
        except Exception as e:
            log_error(func.__name__, str(e))
            # Continue processing other data
            return None
    return wrapper
```

## OUTPUT LOCATION

All outputs should be saved to:
- Databases: F:/OSINT_WAREHOUSE/
- Reports: C:/Projects/OSINT - Foresight/analysis/
- Logs: C:/Projects/OSINT - Foresight/logs/
- Validation: C:/Projects/OSINT - Foresight/validation/

## NOTES

- Prioritize recent data (2020-2024) over historical
- Focus on technology and defense sectors
- Document all assumptions and gaps
- Never interpolate or estimate missing data
- Use exact quotes from source documents
- Maintain complete audit trail

---

*This prompt provides everything needed to process the TED data and build the validation framework. Execute sequentially for best results.*
