# Italy-US Data Collection Folder Structure

*Created: 2025-09-14*

## 📁 Directory Organization

```
C:\Projects\OSINT - Foresight\data\collected\italy_us\
│
├── 📁 fpds_contracts\
│   ├── drs_technologies_contracts_20250914.csv
│   ├── drs_technical_services_20250914.csv
│   ├── leonardo_drs_all_20250914.csv
│   └── README.txt (search parameters used)
│
├── 📁 sec_filings\
│   ├── leonardo_drs_10k_2023.txt
│   ├── leonardo_drs_10q_latest.txt
│   ├── fincantieri_marine_8k.txt
│   └── stmicro_20f_extract.txt
│
├── 📁 scopus_papers\
│   ├── mit_politecnico_quantum_2020_2025.csv
│   ├── stanford_sapienza_ai_2022_2025.csv
│   ├── author_affiliations.xlsx
│   └── collaboration_network.csv
│
├── 📁 patents\
│   ├── mit_italy_coinventors.csv
│   ├── leonardo_boeing_joint.csv
│   ├── politecnico_us_patents.csv
│   └── patent_families.xlsx
│
├── 📁 sam_gov\
│   ├── leonardo_drs_entity_profile.pdf
│   ├── cage_codes.txt
│   ├── facility_clearances.csv
│   └── naics_codes.txt
│
├── 📁 linkedin_profiles\
│   ├── leonardo_drs_employees.xlsx
│   ├── researcher_movements.csv
│   ├── key_personnel.xlsx
│   └── connection_maps.csv
│
├── 📁 usaspending\
│   ├── leonardo_drs_awards_fy2020_2025.csv
│   ├── subcontracts.csv
│   ├── geographic_distribution.xlsx
│   └── award_summaries.txt
│
├── 📁 orcid\
│   ├── mit_to_italy_researchers.csv
│   ├── italy_to_us_researchers.csv
│   ├── dual_affiliations.csv
│   └── publication_history.xlsx
│
├── 📁 github\
│   ├── leonardo_repositories.csv
│   ├── quantum_projects.txt
│   ├── contributor_analysis.xlsx
│   └── code_dependencies.txt
│
└── 📁 company_reports\
    ├── leonardo_annual_report_2023.pdf
    ├── fincantieri_investor_deck.pdf
    ├── mit_italy_program_report.pdf
    └── financial_extracts.xlsx
```

## 📝 File Naming Convention

**Format:** `[source]_[entity]_[type]_[YYYYMMDD].[ext]`

Examples:
- `fpds_drs_technologies_contracts_20250914.csv`
- `sec_leonardo_drs_10k_20250914.txt`
- `scopus_mit_politecnico_papers_20250914.csv`

## 🎯 What Goes Where

### fpds_contracts/
- All FPDS.gov CSV exports
- Contract award data
- Search parameter documentation

### sec_filings/
- 10-K, 10-Q, 8-K extracts
- Key financial tables
- Risk factors sections
- Related party transactions

### scopus_papers/
- Academic publication exports
- Co-authorship data
- Abstract collections
- Citation networks

### patents/
- Google Patents exports
- USPTO search results
- Co-inventor listings
- Patent family trees

### sam_gov/
- Entity registration data
- CAGE codes
- Facility clearance levels
- NAICS classifications

### linkedin_profiles/
- Employee lists
- Career movement tracking
- Key personnel profiles
- Network connections

### usaspending/
- Federal spending data
- Contract and grant awards
- Subcontract information
- Geographic analysis

### orcid/
- Researcher profiles
- Employment history
- Publication records
- Affiliation changes

### github/
- Repository lists
- Contributor analysis
- Project dependencies
- Code metrics

### company_reports/
- Annual reports
- Investor presentations
- Program reports
- Financial summaries

## 🔄 Collection Workflow

1. **Start Collection**
   - Save each CSV/export to appropriate folder
   - Use consistent naming convention
   - Add timestamp to filename

2. **Document Sources**
   - Create README.txt in each folder
   - Note search parameters used
   - Record date and time of collection

3. **Track Progress**
   - Mark completed in dashboard
   - Update collection_tracker.json
   - Note any issues or gaps

4. **Quality Check**
   - Verify file completeness
   - Check for export errors
   - Ensure proper formatting

## 📊 Expected File Sizes

- FPDS contracts: 5-50 MB per CSV
- SEC filings: 100-500 KB per extract
- Scopus papers: 1-10 MB per export
- Patents: 2-20 MB per search
- LinkedIn: 500 KB - 5 MB
- USAspending: 10-100 MB

## 🚀 Quick Actions

**Copy paths for easy access:**
```
C:\Projects\OSINT - Foresight\data\collected\italy_us\fpds_contracts\
C:\Projects\OSINT - Foresight\data\collected\italy_us\sec_filings\
C:\Projects\OSINT - Foresight\data\collected\italy_us\scopus_papers\
C:\Projects\OSINT - Foresight\data\collected\italy_us\patents\
```

## ✅ Collection Checklist

- [ ] FPDS contracts downloaded
- [ ] SEC 10-K extracted
- [ ] Scopus papers exported
- [ ] Patents searched
- [ ] SAM.gov profiles saved
- [ ] LinkedIn data collected
- [ ] USAspending.gov exported
- [ ] ORCID researchers tracked
- [ ] Company reports downloaded

---

**Remember:** Keep original filenames where possible, but add date stamps for version control.
