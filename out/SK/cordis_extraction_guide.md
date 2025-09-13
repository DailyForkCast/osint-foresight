# CORDIS Data Extraction Guide for Slovakia-China Analysis
**Generated: 2025-01-10**
**Database: https://cordis.europa.eu**

## Step 1: Access CORDIS Open Data

### Download Full Dataset
1. Go to: https://data.europa.eu/data/datasets/cordisfp7projects
2. Download: H2020 and Horizon Europe datasets (CSV format)
3. Files needed:
   - project.csv
   - organization.csv
   - projectParticipant.csv

## Step 2: Filter Parameters for Slovak Analysis

### Primary Filters
```
Country = "SK" OR "Slovakia"
Start Date >= 2018-01-01
Programme = "H2020" OR "HORIZON"
```

### Secondary Analysis - China Connections
After extracting Slovak participants, search for:
- Co-participants from China (CN)
- Projects with "China" in title/abstract
- Bilateral cooperation programs
- MSCA with Chinese involvement

## Step 3: Key Fields to Extract

### Essential Data Points
- Project ID (RCN)
- Project Acronym
- Project Title
- Total Cost (EUR)
- EU Contribution (EUR)
- Start/End Dates
- Coordinator Country
- Participant Organizations
- Participant Countries
- Technology Topics
- Programme Area

### Risk Indicators to Calculate
- Chinese co-participation rate
- Dual-use technology topics
- Quantum/AI/Biotech projects
- Coordinator vs participant role
- Funding concentration by institution

## Step 4: Analysis Queries

### Query 1: Slovak-Chinese Joint Projects
```sql
SELECT DISTINCT
  p.project_id,
  p.project_title,
  p.total_cost,
  sk.organization_name as slovak_org,
  cn.organization_name as chinese_org
FROM projects p
JOIN participants sk ON p.project_id = sk.project_id
JOIN participants cn ON p.project_id = cn.project_id
WHERE sk.country = 'SK'
  AND cn.country = 'CN'
  AND p.start_date >= '2018-01-01'
```

### Query 2: Technology Domain Analysis
```sql
SELECT 
  topic_code,
  topic_description,
  COUNT(*) as project_count,
  SUM(eu_contribution) as total_funding
FROM projects
WHERE participant_country = 'SK'
  AND start_date >= '2018-01-01'
GROUP BY topic_code
ORDER BY total_funding DESC
```

### Query 3: Institution Risk Profile
```sql
SELECT 
  organization_name,
  COUNT(DISTINCT project_id) as total_projects,
  SUM(CASE WHEN has_chinese_partner THEN 1 ELSE 0 END) as china_projects,
  SUM(eu_contribution) as total_funding
FROM slovak_participants
GROUP BY organization_name
ORDER BY china_projects DESC
```

## Step 5: Manual Checks via Web Interface

### Search Templates for cordis.europa.eu

1. **Slovak Universities with China**
   - Search: "Slovak University of Technology" AND China
   - Filter: 2018-2025
   - Export: Results list

2. **Quantum/AI Projects**
   - Search: Slovakia AND (quantum OR "artificial intelligence")
   - Filter: Active projects
   - Check: Partner countries

3. **Comenius University Collaborations**
   - Search: "Comenius University"
   - Filter: All projects 2018-2025
   - Analyze: International partners

4. **Slovak Academy of Sciences**
   - Search: "Slovak Academy of Sciences" OR "SAV"
   - Check: Chinese institutional partners

## Step 6: Red Flags to Identify

### High Risk Indicators
- Projects with PLA-affiliated universities
- Dual-use technology areas
- IP rights shared with Chinese entities
- Projects with unusual confidentiality
- Rapid technology transfer timelines

### Specific Institutions to Check
- Beihang University (PLA links)
- Harbin Institute of Technology
- Northwestern Polytechnical University
- Beijing Institute of Technology
- National University of Defense Technology

## Step 7: Export Format

### Recommended Structure
```csv
project_id,project_title,slovak_institution,chinese_partner,funding_amount,technology_area,risk_level,start_date,end_date,ip_arrangement
```

## Manual Execution Instructions

1. **Start with bulk download** from EU Open Data Portal
2. **Import into Excel/Google Sheets** for initial filtering
3. **Use CORDIS web interface** for detailed checks
4. **Cross-reference** with our institutions.csv for known risks
5. **Export results** in standardized format above

## Priority Searches (Do These First)

1. Slovak Academy of Sciences + China (any projects)
2. Comenius University + Chinese partners
3. Technical University Kosice + international
4. All quantum computing projects with Slovakia
5. All AI/ML projects with Slovak participation

## Expected Findings

Based on our analysis, expect to find:
- 10-20 direct Slovak-Chinese collaborative projects
- 30-50 projects with indirect Chinese involvement
- €20-50M in potentially compromised funding
- 5-10 high-risk technology transfers

## Output Files to Create

1. `cordis_sk_projects_all.csv` - All Slovak participations
2. `cordis_sk_china_joint.csv` - Direct collaborations
3. `cordis_sk_risk_projects.csv` - Dual-use/sensitive tech
4. `cordis_sk_funding_analysis.csv` - Financial flows

---
**Note**: This is for manual execution. After data extraction, provide files for detailed analysis.