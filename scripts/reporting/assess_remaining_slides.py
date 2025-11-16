#!/usr/bin/env python3
"""
Quick assessment for remaining medium-priority slides: 7, 12, 15
Determine if enrichment is feasible with available data or if placeholders are adequate
"""
import sqlite3

db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*80)
print("QUICK ASSESSMENT: SLIDES 7, 12, 15")
print("="*80)

# ============================================================================
# Slide 7: Dual-Use Domains (AI/ML, Semiconductors, Quantum, Space, Biotech, Materials)
# ============================================================================
print("\n[SLIDE 7] Dual-Use Domains → Capacity Gaps")
print("  Content: 6 technology hexagons (AI/ML, Semiconductors, Quantum, Space, Biotech, Materials)")
print("  Need: Link domains to project findings, add capacity gap metrics")

# Check if we have technology-specific data
domains = ['AI', 'semiconductor', 'quantum', 'space', 'biotech', 'material']
domain_data = {}

for domain in domains:
    # Check BIS Entity List for domain-specific entries
    cursor.execute(f"""
    SELECT COUNT(*) FROM bis_entity_list_fixed
    WHERE technology_focus LIKE '%{domain}%'
    """)
    count = cursor.fetchone()[0]
    domain_data[domain] = count

print("\n  Data Available (BIS Entity List by technology):")
for domain, count in domain_data.items():
    print(f"    {domain}: {count} entities")

total_domain_entities = sum(domain_data.values())
if total_domain_entities >= 20:
    slide7_potential = "MEDIUM - Could add BIS entity counts by domain"
    print(f"\n  ASSESSMENT: MEDIUM POTENTIAL")
    print(f"    Total entities across domains: {total_domain_entities}")
    print(f"    Could enrich with entity counts per technology area")
else:
    slide7_potential = "LOW - Limited domain-specific data"
    print(f"\n  ASSESSMENT: LOW POTENTIAL")
    print(f"    Limited technology-specific data available")

# ============================================================================
# Slide 12: Global Implications (Data/Privacy, Supply-Chains, Research, Standards, Finance)
# ============================================================================
print("\n[SLIDE 12] Global Implications → Capacity Needs")
print("  Content: 5x2 matrix of vulnerabilities across sectors")
print("  Need: Replace generic vulnerabilities with specific examples")

# Check for cross-system vulnerability data
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%risk%' OR name LIKE '%vulner%')")
risk_tables = cursor.fetchall()
print(f"\n  Risk/vulnerability tables available: {len(risk_tables)}")

cursor.execute("SELECT COUNT(*) FROM entity_risk_factors")
risk_factors = cursor.fetchone()[0]
print(f"  Entity risk factors: {risk_factors}")

if risk_factors >= 100:
    slide12_potential = "MEDIUM - Could add risk factor examples"
    print(f"\n  ASSESSMENT: MEDIUM POTENTIAL")
    print(f"    Could extract risk factors to illustrate vulnerabilities")
else:
    slide12_potential = "LOW - Limited vulnerability-specific data"
    print(f"\n  ASSESSMENT: LOW POTENTIAL")
    print(f"    Limited specific vulnerability data")

# ============================================================================
# Slide 15: Capacity Gaps Map (Academia, Industry, Space, Bio)
# ============================================================================
print("\n[SLIDE 15] Capacity Gaps Map (Where & Why)")
print("  Content: 4-column table mapping gaps by sector")
print("  Need: Link to policy recommendations, add gap assessments")

# This would require analysis reports or think tank data
# Check if we have any reports or recommendations tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%report%' OR name LIKE '%recommend%' OR name LIKE '%policy%')")
report_tables = cursor.fetchall()
print(f"\n  Report/recommendation tables: {len(report_tables)}")
if report_tables:
    for table in report_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    {table[0]}: {count} records")

if len(report_tables) >= 2:
    slide15_potential = "MEDIUM - Could extract recommendations"
    print(f"\n  ASSESSMENT: MEDIUM POTENTIAL")
else:
    slide15_potential = "LOW - No specific policy recommendation data"
    print(f"\n  ASSESSMENT: LOW POTENTIAL")
    print(f"    Would require manual synthesis from existing enrichments")

# ============================================================================
# Overall Assessment
# ============================================================================
print("\n" + "="*80)
print("OVERALL ASSESSMENT")
print("="*80)

slides_assessed = {
    'Slide 7 (Dual-Use Domains)': slide7_potential,
    'Slide 12 (Global Implications)': slide12_potential,
    'Slide 15 (Capacity Gaps Map)': slide15_potential
}

print("\nSummary:")
for slide, potential in slides_assessed.items():
    print(f"  {slide}: {potential}")

medium_count = sum(1 for p in slides_assessed.values() if 'MEDIUM' in p)
low_count = sum(1 for p in slides_assessed.values() if 'LOW' in p)

print(f"\nEnrichment Potential:")
print(f"  MEDIUM: {medium_count}/3 slides")
print(f"  LOW: {low_count}/3 slides")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

if medium_count >= 2:
    print("\nPROCEED with enrichment for slides with MEDIUM potential")
    print("Estimated time: 1-2 hours for all three slides")
else:
    print("\nLEAVE AS RECOMMENDATIONS for future enrichment")
    print("\nRationale:")
    print("  - These are framework/conceptual slides (less data-intensive)")
    print("  - Available data is limited or would require significant synthesis")
    print("  - High-priority and most critical medium-priority slides already enriched")
    print(f"  - Current enrichment: 5 slides complete (6, 8, 10, 13, 14)")
    print("\nCurrent enrichment provides substantial value:")
    print("  - Real trend data (Slide 6)")
    print("  - Case studies (Slide 8)")
    print("  - Entity validation (Slides 10, 14)")
    print("  - Gray-zone pattern (Slide 13)")
    print("\nSlides 7, 12, 15 function well as conceptual frameworks with existing placeholders.")

conn.close()
