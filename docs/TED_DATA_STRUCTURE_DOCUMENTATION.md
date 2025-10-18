# TED Data Structure Documentation
**Understanding the TED procurement data architecture**

---

## 📁 FILE STRUCTURE

### Nested Archive Format
```
F:/TED_Data/monthly/
├── YYYY/                                    # Year directory
│   ├── TED_monthly_YYYY_MM.tar.gz          # Monthly outer archive (~200-300MB)
│   │   ├── MM/                              # Month directory inside
│   │   │   ├── YYYYMMDD_XXXXXX.tar.gz      # Daily inner archives
│   │   │   │   ├── YYYYMMDD_XXX/           # Daily directory
│   │   │   │   │   ├── XXXXXX_YYYY.xml     # Individual contract notices
│   │   │   │   │   ├── XXXXXX_YYYY.xml
│   │   │   │   │   └── ... (2000-4000 XML files per day)
```

### Example Path
```
F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz
  └── 01/20240116_2024011.tar.gz
      └── 20240116_011/028056_2024.xml
```

### Processing Requirements
- **Two-level extraction:** Must extract outer archive, then inner archives
- **Memory management:** Each inner archive contains 2000-4000 XML files
- **Encoding:** UTF-8 with error handling required

---

## 🏷️ XML STRUCTURE

### Namespace
```xml
xmlns="http://publications.europa.eu/resource/schema/ted/R2.0.9/publication"
```

### Key Elements to Extract

#### 1. Contracting Authority
```xml
<CONTRACTING_BODY>
  <ADDRESS_CONTRACTING_BODY>
    <OFFICIALNAME>Ministero delle Infrastrutture</OFFICIALNAME>
    <COUNTRY VALUE="IT"/>
    <TOWN>Roma</TOWN>
  </ADDRESS_CONTRACTING_BODY>
</CONTRACTING_BODY>
```

#### 2. Contract Object
```xml
<OBJECT_CONTRACT>
  <TITLE>Supply of telecommunications equipment</TITLE>
  <CPV_MAIN>
    <CPV_CODE CODE="32400000"/>  <!-- Telecommunications -->
  </CPV_MAIN>
  <SHORT_DESCR>5G network infrastructure deployment</SHORT_DESCR>
  <VAL_TOTAL CURRENCY="EUR">45000000</VAL_TOTAL>
</OBJECT_CONTRACT>
```

#### 3. Award Information (Winner)
```xml
<AWARD_CONTRACT>
  <AWARDED_CONTRACT>
    <CONTRACTORS>
      <CONTRACTOR>
        <ADDRESS_CONTRACTOR>
          <OFFICIALNAME>Huawei Technologies Italia S.r.l.</OFFICIALNAME>
          <COUNTRY VALUE="IT"/>  <!-- Note: May be local subsidiary -->
          <TOWN>Milano</TOWN>
        </ADDRESS_CONTRACTOR>
      </CONTRACTOR>
    </CONTRACTORS>
    <VALUES>
      <VAL_TOTAL CURRENCY="EUR">45000000</VAL_TOTAL>
    </VALUES>
  </AWARDED_CONTRACT>
</AWARD_CONTRACT>
```

#### 4. Document Metadata
```xml
<CODED_DATA_SECTION>
  <REF_OJS>
    <DATE_PUB>20240115</DATE_PUB>
  </REF_OJS>
  <NOTICE_DATA>
    <NO_DOC_OJS>2024/S 011-028056</NO_DOC_OJS>  <!-- Notice number -->
  </NOTICE_DATA>
</CODED_DATA_SECTION>
```

---

## 🔍 CHINA DETECTION PATTERNS

### Direct Mentions
- Company names: "Huawei", "ZTE", "CRRC", "State Grid"
- Country indicators: "China", "Chinese", "CN"
- Cities: "Beijing", "Shanghai", "Shenzhen", "Guangzhou"

### Subsidiary Patterns
- "Huawei Technologies Italia S.r.l." → Italian subsidiary of Huawei
- "ZTE Deutschland GmbH" → German subsidiary of ZTE
- Pattern: `[Chinese Company] [European Country] [Legal Form]`

### CPV Codes of Interest (Dual-Use)
- 32400000 - Networks and telecommunications
- 31700000 - Electronic equipment
- 35100000 - Emergency and security equipment
- 38000000 - Laboratory and precision equipment
- 30200000 - Computer equipment and supplies

---

## 📊 DATA VOLUMES

### Approximate Scale (per year)
- **Monthly archives:** 12 files
- **Daily archives per month:** 20-30 files
- **XML contracts per day:** 2000-4000 files
- **Total contracts per year:** ~1,000,000

### Processing Estimates
- **Single day:** 5-10 seconds
- **Single month:** 2-3 minutes
- **Single year:** 30-40 minutes
- **Full dataset (2010-2025):** 8-10 hours

---

## 💾 ACTUAL DATA FOUND (January 2024 Sample)

### Quick Scan Results
```
Archive: TED_monthly_2024_01.tar.gz
Inner Archives: 23
Total XML files: ~75,000
China mentions found: 11+ in first 2 inner archives

Examples found:
- File: 00028983_2024.xml - Pattern: ZTE
- File: 027906_2024.xml - Pattern: Beijing
- File: 00030685_2024.xml - Pattern: China
```

### Extraction Rate
- **China mentions:** ~0.18% of contracts (11 in 6,251 checked)
- **Projected for full dataset:** ~18,000 China-related contracts

---

## 🛠️ PROCESSING STRATEGY

### Step 1: Outer Archive Processing
```python
with tarfile.open('TED_monthly_YYYY_MM.tar.gz', 'r:gz') as outer:
    for member in outer.getmembers():
        if member.name.endswith('.tar.gz'):
            # Process inner archive
```

### Step 2: Inner Archive Processing
```python
inner_file = outer.extractfile(member)
with tarfile.open(fileobj=inner_file, mode='r:gz') as inner:
    for xml_member in inner.getmembers():
        if xml_member.name.endswith('.xml'):
            # Process XML
```

### Step 3: XML Parsing with Namespace
```python
content = inner.extractfile(xml_member).read().decode('utf-8', errors='ignore')
root = ET.fromstring(content)

# Use namespace wildcard for extraction
authority = root.find('.//{*}CONTRACTING_BODY//{*}OFFICIALNAME')
country = root.find('.//{*}CONTRACTING_BODY//{*}COUNTRY')
contractor = root.find('.//{*}CONTRACTOR//{*}OFFICIALNAME')
```

### Step 4: China Detection
```python
def is_china_related(xml_content, contractor_name):
    china_patterns = ['China', 'Chinese', 'Huawei', 'ZTE', 'CRRC',
                     'Beijing', 'Shanghai', 'CN']

    content_str = str(xml_content)
    for pattern in china_patterns:
        if pattern in content_str or pattern.lower() in content_str:
            return True, pattern

    return False, None
```

---

## ⚠️ CRITICAL NOTES

### Encoding Issues
- XML files may contain special characters
- Always use: `.decode('utf-8', errors='ignore')`
- Some contractor names may be in local languages (需要注意中文)

### Subsidiary Detection
- Chinese companies often operate through EU subsidiaries
- Check parent company patterns even if country code is EU
- "Huawei Italia" is still Huawei despite IT country code

### Performance Optimization
- Process inner archives in parallel
- Save checkpoint after each month
- Stream XML parsing, don't load all into memory

### Verification
- Every finding must include:
  - Outer archive path: `F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz`
  - Inner archive path: `01/20240116_2024011.tar.gz`
  - XML file path: `20240116_011/028056_2024.xml`
  - Line numbers or element paths for exact location

---

## ✅ VALIDATED STRUCTURE

This documentation is based on actual examination of:
- F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz
- Verified presence of China-related contracts
- Confirmed nested archive structure
- Tested extraction and parsing approach

---

## ✅ PROCESSING STATUS UPDATE

### Updated Processor Status (2025-09-20)
- **Nested Archive Support:** ✅ COMPLETED
- **Multi-Country Analysis:** ✅ COMPLETED
- **Zero Fabrication System:** ✅ IMPLEMENTED
- **Test Results:** Successfully processing 2024 archive with 75,000+ XML files

### Current Processing
- **2023-2025 Data:** 🏃 IN PROGRESS (31 archives)
- **2010-2022 Historical:** ⏳ QUEUED
- **Multi-Country Analysis:** 🏃 RUNNING

### Processor Capabilities
```python
# Updated MultiCountryTEDProcessor handles:
- Nested archives (outer monthly → inner daily → XML files)
- All 30 EU countries simultaneously
- 19 tracked Chinese entities (Huawei, ZTE, CRRC, etc.)
- Subsidiary detection and risk assessment
- Complete verification commands for every finding
- Structured output by country/company/sector
```

### Output Structure Created
```
data/processed/ted_multicountry/
├── by_country/[COUNTRY]_china/     ← Country-specific findings
├── by_company/[ENTITY]/            ← Company-specific analysis
├── by_sector/[SECTOR]/             ← Technology sector breakdown
├── cross_border/                   ← Multi-country patterns
├── networks/                       ← Relationship graphs
├── analysis/                       ← Executive reports
└── checkpoint.json                 ← Processing status
```

---

*Use this documentation when processing TED data to ensure correct handling of the nested structure and proper extraction of China-related contracts.*
