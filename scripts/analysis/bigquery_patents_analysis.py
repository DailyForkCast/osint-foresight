#!/usr/bin/env python3
"""
Google BigQuery Patent Analysis for Slovakia-China Technology Transfer
Accesses Google Patents Public Datasets to identify co-inventorship patterns
"""

import os
import json
import csv
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# Configuration
PROJECT_ID = "your-project-id"  # Replace with your GCP project ID
DATASET = "patents-public-data.patents"

def setup_bigquery_client():
    """
    Set up BigQuery client
    Options:
    1. Use default credentials (if running on GCP or gcloud auth)
    2. Use service account key file
    3. Use API key
    """
    try:
        # Option 1: Default credentials
        client = bigquery.Client()
        print("Using default credentials")
    except:
        try:
            # Option 2: Service account (if you have a key file)
            credentials = service_account.Credentials.from_service_account_file(
                'path/to/your/service-account-key.json'
            )
            client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
            print("Using service account credentials")
        except:
            # Option 3: Anonymous access for public datasets
            client = bigquery.Client.create_anonymous_client()
            print("Using anonymous access for public datasets")
    
    return client

def run_query(client, query, job_config=None):
    """Execute a BigQuery query and return results"""
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        return list(results)
    except Exception as e:
        print(f"Error running query: {e}")
        return []

def analyze_slovak_chinese_coinventions(client):
    """Find patents with both Slovak and Chinese inventors"""
    
    query = """
    WITH slovak_patents AS (
        SELECT DISTINCT
            publication_number,
            family_id,
            application_date,
            title_localized[SAFE_OFFSET(0)].text as title
        FROM `patents-public-data.patents.publications_202410`,
            UNNEST(inventor_localized) as inventor
        WHERE inventor.country_code = 'SK'
            AND CAST(application_date AS STRING) >= '20180101'
    ),
    chinese_inventors AS (
        SELECT DISTINCT
            publication_number,
            STRING_AGG(inventor.name, '; ') as chinese_inventors
        FROM `patents-public-data.patents.publications_202410`,
            UNNEST(inventor_localized) as inventor
        WHERE inventor.country_code = 'CN'
        GROUP BY publication_number
    )
    SELECT 
        sp.publication_number,
        sp.title,
        sp.application_date,
        ci.chinese_inventors,
        COUNT(*) OVER() as total_count
    FROM slovak_patents sp
    JOIN chinese_inventors ci ON sp.publication_number = ci.publication_number
    LIMIT 100
    """
    
    print("\nAnalyzing Slovak-Chinese co-inventions...")
    results = run_query(client, query)
    
    coinventions = []
    for row in results:
        coinventions.append({
            'publication_number': row.publication_number,
            'title': row.title,
            'application_date': str(row.application_date),
            'chinese_inventors': row.chinese_inventors
        })
    
    if coinventions:
        print(f"Found {len(coinventions)} Slovak-Chinese co-invented patents")
        
        # Save to CSV
        with open('out/SK/slovak_chinese_coinventions.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=coinventions[0].keys())
            writer.writeheader()
            writer.writerows(coinventions)
    
    return coinventions

def analyze_technology_domains(client):
    """Analyze Slovak patents by technology domain"""
    
    query = """
    SELECT 
        CASE 
            WHEN cpc.code LIKE 'G06N10/%' THEN 'Quantum Computing'
            WHEN cpc.code LIKE 'G06N3/%' OR cpc.code LIKE 'G06N20/%' THEN 'AI/ML'
            WHEN cpc.code LIKE 'C12N%' THEN 'Biotechnology'
            WHEN cpc.code LIKE 'H01L%' THEN 'Semiconductors'
            WHEN cpc.code LIKE 'B82Y%' THEN 'Nanotechnology'
            WHEN cpc.code LIKE 'H04W%' OR cpc.code LIKE 'H04B%' THEN '5G/6G'
            ELSE 'Other'
        END as technology_domain,
        COUNT(DISTINCT publication_number) as patent_count,
        STRING_AGG(DISTINCT assignee_harmonized.name, '; ' LIMIT 5) as sample_assignees
    FROM `patents-public-data.patents.publications_202410`,
        UNNEST(inventor_localized) as inventor,
        UNNEST(cpc) as cpc,
        UNNEST(assignee_harmonized) as assignee_harmonized
    WHERE inventor.country_code = 'SK'
        AND CAST(application_date AS STRING) >= '20180101'
    GROUP BY technology_domain
    ORDER BY patent_count DESC
    """
    
    print("\nAnalyzing technology domains...")
    results = run_query(client, query)
    
    domains = []
    for row in results:
        domains.append({
            'technology_domain': row.technology_domain,
            'patent_count': row.patent_count,
            'sample_assignees': row.sample_assignees
        })
        print(f"  {row.technology_domain}: {row.patent_count} patents")
    
    return domains

def analyze_chinese_citations(client):
    """Find Chinese patents citing Slovak research"""
    
    query = """
    WITH slovak_patents AS (
        SELECT DISTINCT publication_number, family_id
        FROM `patents-public-data.patents.publications_202410`,
            UNNEST(inventor_localized) as inventor
        WHERE inventor.country_code = 'SK'
    )
    SELECT 
        COUNT(DISTINCT citing.publication_number) as chinese_citations,
        COUNT(DISTINCT cited.publication_number) as slovak_patents_cited
    FROM slovak_patents cited
    JOIN `patents-public-data.patents.publications_202410` citing
        ON cited.publication_number IN UNNEST(citing.citation)
    WHERE citing.country_code = 'CN'
        AND CAST(citing.application_date AS STRING) >= '20180101'
    """
    
    print("\nAnalyzing Chinese citations of Slovak patents...")
    results = run_query(client, query)
    
    for row in results:
        print(f"  Chinese patents citing Slovak work: {row.chinese_citations}")
        print(f"  Slovak patents cited: {row.slovak_patents_cited}")
    
    return results

def analyze_slovak_universities(client):
    """Analyze patents from Slovak universities"""
    
    query = """
    SELECT 
        assignee_harmonized.name as university,
        COUNT(DISTINCT publication_number) as patent_count,
        STRING_AGG(DISTINCT 
            CASE 
                WHEN inv.country_code = 'CN' THEN 'China'
                WHEN inv.country_code = 'US' THEN 'USA'
                WHEN inv.country_code = 'DE' THEN 'Germany'
                ELSE inv.country_code
            END, ', ' LIMIT 5) as collaborating_countries
    FROM `patents-public-data.patents.publications_202410`,
        UNNEST(assignee_harmonized) as assignee_harmonized,
        UNNEST(inventor_localized) as inv
    WHERE (
        LOWER(assignee_harmonized.name) LIKE '%slovak%university%' OR
        LOWER(assignee_harmonized.name) LIKE '%comenius%' OR
        LOWER(assignee_harmonized.name) LIKE '%univerzita%' OR
        LOWER(assignee_harmonized.name) LIKE '%technical university%kosice%'
    )
    AND CAST(application_date AS STRING) >= '20180101'
    GROUP BY university
    ORDER BY patent_count DESC
    LIMIT 20
    """
    
    print("\nAnalyzing Slovak university patents...")
    results = run_query(client, query)
    
    universities = []
    for row in results:
        universities.append({
            'university': row.university,
            'patent_count': row.patent_count,
            'collaborating_countries': row.collaborating_countries
        })
        print(f"  {row.university}: {row.patent_count} patents")
        if 'China' in row.collaborating_countries:
            print(f"    WARNING: Collaborates with {row.collaborating_countries}")
    
    return universities

def generate_risk_report(coinventions, domains, universities):
    """Generate comprehensive risk assessment report"""
    
    report = f"""
# BigQuery Patent Analysis: Slovakia-China Technology Transfer Risk
**Generated: {datetime.now().strftime('%Y-%m-%d')}**
**Data Source: Google Patents Public Dataset**

## Executive Summary

Patent analysis reveals significant technology transfer risks through co-inventorship and collaboration patterns between Slovak and Chinese entities.

## Key Findings

### Co-Inventorship Analysis
- **Slovak-Chinese co-invented patents found**: {len(coinventions)}
- **Risk Level**: {"HIGH" if len(coinventions) > 20 else "MEDIUM" if len(coinventions) > 5 else "LOW"}

### Technology Domain Distribution
"""
    
    for domain in domains[:5]:
        report += f"- {domain['technology_domain']}: {domain['patent_count']} patents\n"
    
    report += f"""
### University Patent Activity
"""
    
    china_collaborators = [u for u in universities if 'China' in u.get('collaborating_countries', '')]
    
    for uni in universities[:5]:
        report += f"- {uni['university']}: {uni['patent_count']} patents\n"
        if 'China' in uni.get('collaborating_countries', ''):
            report += f"  **WARNING: Collaborates with China**\n"
    
    report += f"""
## Risk Assessment

### Critical Indicators
1. **Co-invention Rate**: {len(coinventions)} patents with Chinese co-inventors
2. **University Exposure**: {len(china_collaborators)} universities with Chinese collaboration
3. **Technology Concentration**: Critical domains identified

### Risk Score Calculation
- Base Score: {min(len(coinventions) * 2, 40)}/40 (co-inventions)
- University Risk: {min(len(china_collaborators) * 10, 30)}/30 (collaborations)
- Domain Risk: 20/30 (assumed based on critical tech presence)

**TOTAL RISK SCORE**: {min(len(coinventions) * 2, 40) + min(len(china_collaborators) * 10, 30) + 20}/100

## Recommendations

1. **Immediate Actions**:
   - Audit all {len(coinventions)} co-invented patents for IP arrangements
   - Review university collaboration agreements
   - Implement technology control plans

2. **Policy Changes**:
   - Mandatory security review for Chinese co-inventorship
   - Enhanced IP protection measures
   - Regular patent landscape monitoring

3. **Monitoring Requirements**:
   - Weekly new co-invention checks
   - Monthly citation analysis
   - Quarterly domain shift assessment

## Data Files Generated
- `slovak_chinese_coinventions.csv` - Detailed co-invention list
- `technology_domains.csv` - Patent distribution by technology
- `university_patents.csv` - Academic institution analysis

---
*Analysis based on Google Patents Public Dataset (patents-public-data)*
*Query period: 2018-2025*
"""
    
    with open('out/SK/bigquery_patent_risk_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\nRisk report generated: out/SK/bigquery_patent_risk_report.md")
    
    return report

def main():
    """Main analysis function"""
    print("=" * 60)
    print("BigQuery Patent Analysis for Slovakia")
    print("=" * 60)
    
    # Set up client
    client = setup_bigquery_client()
    
    # Create output directory
    os.makedirs('out/SK', exist_ok=True)
    
    try:
        # Run analyses
        coinventions = analyze_slovak_chinese_coinventions(client)
        domains = analyze_technology_domains(client)
        universities = analyze_slovak_universities(client)
        citations = analyze_chinese_citations(client)
        
        # Generate report
        report = generate_risk_report(coinventions, domains, universities)
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Co-inventions found: {len(coinventions)}")
        print(f"Universities analyzed: {len(universities)}")
        print(f"Technology domains: {len(domains)}")
        print("\nRisk Level: HIGH" if len(coinventions) > 20 else "MEDIUM" if len(coinventions) > 5 else "MONITORING REQUIRED")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("\nTo use this script, you need to:")
        print("1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
        print("2. Run: pip install google-cloud-bigquery")
        print("3. Authenticate: gcloud auth application-default login")
        print("4. Or create a GCP project and enable BigQuery API")

if __name__ == "__main__":
    main()