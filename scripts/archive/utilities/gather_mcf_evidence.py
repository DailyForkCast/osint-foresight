#!/usr/bin/env python3
"""
Gather evidence from database for MCF presentation citations
"""

import sqlite3
import json

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

evidence = {
    "metadata": {
        "generated": "2025-10-18",
        "database": db_path
    },
    "findings": {}
}

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. OpenAlex collaborations
    try:
        cursor.execute("SELECT COUNT(*) FROM openalex_works")
        openalex_total = cursor.fetchone()[0]
        evidence["findings"]["openalex_works_total"] = openalex_total
    except Exception as e:
        evidence["findings"]["openalex_works_total"] = f"Error: {e}"

    # 2. CORDIS EU-China projects
    try:
        cursor.execute("SELECT COUNT(DISTINCT rcn) FROM cordis_projects")
        cordis_total = cursor.fetchone()[0]
        evidence["findings"]["cordis_projects_total"] = cordis_total
    except Exception as e:
        evidence["findings"]["cordis_projects_total"] = f"Error: {e}"

    # 3. USPTO Chinese patents
    try:
        cursor.execute("SELECT COUNT(*) FROM uspto_patents_chinese")
        uspto_chinese = cursor.fetchone()[0]
        evidence["findings"]["uspto_chinese_patents"] = uspto_chinese
    except Exception as e:
        evidence["findings"]["uspto_chinese_patents"] = f"Error: {e}"

    # 4. TED contracts
    try:
        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production")
        ted_total = cursor.fetchone()[0]
        evidence["findings"]["ted_contracts_total"] = ted_total

        cursor.execute("SELECT COUNT(*) FROM ted_contracts_production WHERE has_chinese_involvement = 1")
        ted_chinese = cursor.fetchone()[0]
        evidence["findings"]["ted_chinese_contracts"] = ted_chinese
    except Exception as e:
        evidence["findings"]["ted_contracts"] = f"Error: {e}"

    # 5. AidData
    try:
        cursor.execute("SELECT COUNT(*) FROM aiddata_seaport_finance")
        seaports = cursor.fetchone()[0]
        evidence["findings"]["aiddata_seaports"] = seaports

        cursor.execute("SELECT COUNT(*) FROM aiddata_ai_exports")
        ai_exports = cursor.fetchone()[0]
        evidence["findings"]["aiddata_ai_exports"] = ai_exports
    except Exception as e:
        evidence["findings"]["aiddata"] = f"Error: {e}"

    # 6. arXiv technology papers
    try:
        cursor.execute("""
            SELECT COUNT(*) as papers,
                   SUM(CASE WHEN categories LIKE '%cs.AI%' OR categories LIKE '%cs.LG%' THEN 1 ELSE 0 END) as ai_papers,
                   SUM(CASE WHEN categories LIKE '%quant-ph%' THEN 1 ELSE 0 END) as quantum_papers
            FROM arxiv_papers
        """)
        row = cursor.fetchone()
        evidence["findings"]["arxiv_total_papers"] = row[0]
        evidence["findings"]["arxiv_ai_papers"] = row[1]
        evidence["findings"]["arxiv_quantum_papers"] = row[2]
    except Exception as e:
        evidence["findings"]["arxiv"] = f"Error: {e}"

    # 7. ASPI infrastructure
    try:
        cursor.execute("SELECT COUNT(*) FROM aspi_infrastructure")
        aspi_infra = cursor.fetchone()[0]
        evidence["findings"]["aspi_infrastructure_records"] = aspi_infra
    except Exception as e:
        evidence["findings"]["aspi"] = f"Error: {e}"

    # 8. USAspending Chinese entities
    try:
        cursor.execute("SELECT COUNT(DISTINCT recipient_name) FROM usaspending_china_comprehensive")
        us_chinese_entities = cursor.fetchone()[0]
        evidence["findings"]["usaspending_chinese_entities"] = us_chinese_entities
    except Exception as e:
        evidence["findings"]["usaspending"] = f"Error: {e}"

    # 9. OpenSanctions
    try:
        cursor.execute("SELECT COUNT(*) FROM opensanctions_entities WHERE country = 'cn' OR country = 'CN'")
        sanctions_cn = cursor.fetchone()[0]
        evidence["findings"]["opensanctions_chinese_entities"] = sanctions_cn
    except Exception as e:
        evidence["findings"]["opensanctions"] = f"Error: {e}"

    # 10. GLEIF Chinese entities
    try:
        cursor.execute("SELECT COUNT(*) FROM gleif_entities WHERE legal_jurisdiction LIKE '%CN%'")
        gleif_cn = cursor.fetchone()[0]
        evidence["findings"]["gleif_chinese_entities"] = gleif_cn
    except Exception as e:
        evidence["findings"]["gleif"] = f"Error: {e}"

    conn.close()

except Exception as e:
    evidence["error"] = str(e)

# Output JSON
print(json.dumps(evidence, indent=2))

# Also save to file
with open("C:/Projects/OSINT - Foresight/mcf_evidence_citations.json", "w") as f:
    json.dump(evidence, f, indent=2)

print("\n\n=== Evidence saved to mcf_evidence_citations.json ===")
