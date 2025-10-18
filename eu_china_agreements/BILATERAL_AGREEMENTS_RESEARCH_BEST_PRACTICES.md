# Best Practices for Bilateral Agreement Discovery: Research Report

## 🎯 Overview

Based on our harvest limitations (7 generic pages vs specific agreements), this research explores proven methodologies for discovering bilateral agreements, treaties, and international cooperation documents.

---

## 🏛️ Official Government Sources

### **Treaty Databases**
1. **EUR-Lex (EU Official Journal)**
   - URL: https://eur-lex.europa.eu
   - Coverage: All EU official treaties and agreements
   - Access: Free, comprehensive search
   - Best for: Official EU-China agreements

2. **UN Treaty Collection**
   - URL: https://treaties.un.org
   - Coverage: Multilateral treaties registered with UN
   - Search: By country, subject, date
   - Best for: Major bilateral treaties

3. **National Foreign Ministry Archives**
   - Examples:
     - UK: https://www.gov.uk/government/collections/treaties
     - Germany: https://www.auswaertiges-amt.de
     - France: https://www.diplomatie.gouv.fr/fr/le-ministere-et-son-reseau/
   - Best for: Country-specific bilateral agreements

### **Specialized Government Portals**
- **Trade Agreements**: WTO Regional Trade Agreements Database
- **Investment Treaties**: UNCTAD Investment Policy Hub
- **Academic Cooperation**: National education ministry databases

---

## 🏫 Academic and Research Sources

### **University Partnership Databases**
1. **Association of Universities and Colleges of Canada (AUCC)**
2. **European University Association (EUA)**
3. **Universities UK International**
4. **German Academic Exchange Service (DAAD)**

### **Research Collaboration Databases**
- **CORDIS** (EU research projects) - Already explored
- **NSF International Collaborations**
- **Research Gate institutional partnerships**
- **Scopus/Web of Science** for joint publications indicating partnerships

---

## 🏙️ Municipal and Sister City Sources

### **Sister Cities International**
- **Database**: https://sistercities.org
- **Search**: By country pairs
- **Coverage**: Thousands of documented partnerships
- **API Access**: May be available for bulk data

### **Regional Sister City Associations**
- **European**: Town Twinning associations by country
- **National**: Municipal foreign relations offices
- **Local**: City government international relations departments

### **Municipal Government Websites**
- **Direct navigation** to major cities
- **International relations sections**
- **Sister city/partnership pages**
- **Municipal council minutes and resolutions**

---

## 📚 Common Crawl for Bilateral Agreement Discovery

### **What is Common Crawl?**
- **Archive**: Petabyte-scale web crawl archive since 2008
- **Access**: Free via AWS S3 or query interfaces
- **Coverage**: Broader than search engines, includes deep web content
- **Format**: Raw HTML, structured data available

### **Common Crawl Advantages for Agreement Discovery**

#### **1. Comprehensive Coverage**
- **Municipal websites** often poorly indexed by Google
- **University pages** with partnership information
- **Government archives** not prioritized in search results
- **PDF documents** within crawled sites
- **Historical snapshots** of agreements over time

#### **2. Structured Querying**
- **Athena SQL queries** on Common Crawl index
- **Regex pattern matching** for agreement-specific terms
- **Domain filtering** (site:gov.*, site:edu.*, site:ac.*)
- **Language detection** for native language content

#### **3. Bypass Rate Limiting**
- **Archived content** doesn't require live requests
- **Bulk processing** without hitting rate limits
- **Historical data** unavailable through current web scraping

### **Common Crawl Query Strategies for Agreements**

#### **SQL Query Examples**:
```sql
-- Sister city agreements
SELECT url, content
FROM ccindex
WHERE content LIKE '%sister city%China%'
AND (url_host_name LIKE '%.gov.%' OR url_host_name LIKE '%.city.%')

-- University partnerships
SELECT url, content
FROM ccindex
WHERE content LIKE '%partnership%China%university%'
AND url_host_name LIKE '%.edu%'

-- Government agreements by country
SELECT url, content
FROM ccindex
WHERE content LIKE '%agreement%China%'
AND url_host_name LIKE '%.gov.de%'
AND content LIKE '%memorandum%'
```

#### **Domain-Specific Searches**:
- **Municipal**: *.city.*, *.gov.*, *.commune.*, *.municipality.*
- **Academic**: *.edu.*, *.ac.*, *.uni.*, *.university.*
- **Government**: *.gov.*, *.mfa.*, *.foreign.*

#### **Multi-Language Pattern Matching**:
```sql
-- German partnerships
WHERE content LIKE '%Städtepartnerschaft%China%'

-- French partnerships
WHERE content LIKE '%ville jumelée%Chine%'

-- Italian partnerships
WHERE content LIKE '%città gemelle%Cina%'
```

---

## 🔍 Advanced Research Methodologies

### **1. Archival Research**
- **Internet Archive Wayback Machine**
- **National library digital collections**
- **Government publication archives**
- **Historical newspaper databases**

### **2. Freedom of Information Requests**
- **FOIA (US)** for government agreements
- **EU Transparency Regulation**
- **National public records laws**
- **Municipal records requests**

### **3. Academic Research Approaches**
- **Citation tracking** from known agreements
- **Snowball sampling** from reference lists
- **Expert interviews** with diplomats/academics
- **Conference proceedings** on China-EU relations

### **4. Commercial Intelligence Sources**
- **LexisNexis Government Database**
- **Factiva for news coverage** of agreement signings
- **Monitoring services** for new agreement announcements
- **Trade association databases**

---

## 🛠️ Recommended Implementation Strategy

### **Phase 1: Structured Database Access**
1. **EUR-Lex systematic search** for official EU-China agreements
2. **Sister Cities International database** access/scraping
3. **National foreign ministry treaty collections**
4. **University association databases**

### **Phase 2: Common Crawl Analysis**
1. **Set up AWS Athena** for Common Crawl querying
2. **Domain-specific searches** for municipal/academic sites
3. **Multi-language pattern matching** for native content
4. **Historical snapshots** to track agreement evolution

### **Phase 3: Targeted Deep Research**
1. **Manual navigation** to high-probability sources
2. **PDF document repositories**
3. **Archive.org historical searches**
4. **FOIA requests** for specific countries/agreements

### **Phase 4: Verification and Validation**
1. **Cross-reference** multiple sources
2. **Official source confirmation**
3. **Date and party validation**
4. **Status verification** (active/terminated)

---

## 📊 Expected Outcomes by Method

### **Common Crawl Potential**:
- **Sister Cities**: 50-100+ partnerships (archived municipal sites)
- **Academic**: 20-40+ partnerships (university archives)
- **Government**: 10-20+ agreements (archived government pages)
- **Historical**: Agreements no longer on live websites

### **Structured Databases**:
- **Official Treaties**: 5-15+ major bilateral agreements
- **Sister Cities DB**: 20-50+ verified partnerships
- **University Databases**: 10-30+ academic partnerships

### **Manual Research**:
- **High-quality validation** of discovered agreements
- **Current status verification**
- **Complete documentation** with official sources

---

## 💡 Key Insights

### **Why Common Crawl is Valuable**:
1. **Captures content** that search engines deprioritize
2. **Includes historical snapshots** of agreements
3. **Covers municipal/institutional sites** with poor SEO
4. **Enables bulk processing** without rate limits
5. **Provides structured querying** capabilities

### **Limitations to Consider**:
- **Crawl frequency** may miss recent agreements
- **Content quality** varies across archived sites
- **Query complexity** requires SQL expertise
- **Data volume** can be overwhelming without filtering

### **Best Practice Combination**:
- **Common Crawl** for comprehensive discovery
- **Official databases** for authoritative validation
- **Manual research** for current status verification
- **Cross-referencing** for accuracy confirmation

---

## 🎯 Recommendation

**Implement a hybrid approach combining Common Crawl analysis with structured database access** to achieve comprehensive bilateral agreement discovery while maintaining zero fabrication protocols.

This methodology addresses the limitations we encountered with basic web scraping while providing access to the deep web content where bilateral agreements are actually documented.
