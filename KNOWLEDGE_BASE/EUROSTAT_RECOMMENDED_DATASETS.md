# Recommended Eurostat Datasets for China Trade Analysis

## Priority 1: Essential Trade Flow Datasets

### 1. DS-045409 - EU Trade Since 1988 by CN8
- **URL**: `https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Fcomext%2FDS-045409.tsv.gz`
- **Content**: Most detailed trade data at 8-digit product level
- **Why Critical**:
  - Tracks specific technology products (semiconductors, telecom equipment)
  - Identifies dual-use goods at granular level
  - Shows monthly trade flows with China since 1988
- **Size**: ~2-3 GB compressed

### 2. DS-018995 - EU Trade Since 1999 by SITC
- **URL**: `https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Fcomext%2FDS-018995.tsv.gz`
- **Content**: Trade organized by Standard International Trade Classification
- **Why Critical**:
  - SITC Section 7 covers machinery and transport equipment
  - SITC Section 5 covers chemicals (including dual-use)
  - Better for trend analysis than CN8
- **Size**: ~500 MB compressed

### 3. ext_st_eu27_2020sitc - EU27 Trade by SITC
- **URL**: `https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Fcomext%2Fext_st_eu27_2020sitc.tsv.gz`
- **Content**: Current EU27 trade statistics by SITC
- **Why Critical**:
  - Post-Brexit EU trade flows
  - Harmonized with current EU membership
- **Size**: ~300 MB compressed

## Priority 2: High-Tech and Strategic Goods

### 4. DS-066341 - High-tech Trade Statistics
- **Content**: Trade in high-technology products
- **Why Critical**:
  - Aerospace products
  - Computer-office machines
  - Electronics-telecommunications
  - Scientific instruments
  - Electrical/non-electrical machinery
  - Chemistry and pharmaceuticals
  - Armament

### 5. DS-043227 - Trade by BEC (Broad Economic Categories)
- **Content**: Trade classified by economic use
- **Why Critical**:
  - Distinguishes capital goods from consumer goods
  - Identifies intermediate goods for supply chain analysis
  - Tracks technology intensity

## Priority 3: Enterprise and Investment Data

### 6. ext_tec - Trade by Enterprise Characteristics
- **Content**: Trade linked to business characteristics
- **Why Critical**:
  - Shows which types of companies trade with China
  - Identifies SME vs large enterprise patterns
  - Links trade to ownership structures

### 7. DS-053227 - EU Direct Investment Flows
- **Content**: Foreign direct investment statistics
- **Why Critical**:
  - Chinese investment in EU
  - EU investment in China
  - Technology transfer indicators

## Priority 4: Price and Volume Indices

### 8. DS-070991 - Trade Unit Value Indices
- **Content**: Import/export price indices
- **Why Critical**:
  - Tracks pricing power in key sectors
  - Identifies dumping patterns
  - Quality ladder positioning

## Download Strategy

### Immediate Downloads (Critical for China Analysis):
1. **DS-045409** - CN8 detailed trade (MUST HAVE)
2. **DS-018995** - SITC classification (MUST HAVE)
3. **High-tech trade statistics** (MUST HAVE)

### Secondary Downloads:
4. Trade by BEC
5. Trade by enterprise characteristics
6. FDI flows

### Bulk Download Commands:

```bash
# Create download directory
mkdir -p F:/OSINT_Data/eurostat_bulk

# Download DS-045409 (CN8 trade data)
curl -L "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Fcomext%2FDS-045409.tsv.gz" \
     -o F:/OSINT_Data/eurostat_bulk/DS-045409.tsv.gz

# Download DS-018995 (SITC trade data)
curl -L "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Fcomext%2FDS-018995.tsv.gz" \
     -o F:/OSINT_Data/eurostat_bulk/DS-018995.tsv.gz

# Extract after download
gunzip F:/OSINT_Data/eurostat_bulk/*.gz
```

## Data Processing Tips

### CN8 Product Codes to Focus On:
- **8471**: Automatic data processing machines (computers)
- **8517**: Telephone/telecom equipment
- **8541**: Semiconductor devices
- **8542**: Electronic integrated circuits
- **9013**: Liquid crystal devices, lasers
- **9027**: Instruments for physical/chemical analysis
- **8525**: Transmission apparatus
- **8802-8804**: Aircraft and parts
- **3002**: Vaccines, blood products
- **2844**: Radioactive elements

### SITC Sections to Analyze:
- **Section 5**: Chemicals (watch for dual-use)
- **Section 7**: Machinery and transport equipment
- **Section 75**: Office machines and computers
- **Section 76**: Telecommunications equipment
- **Section 77**: Electrical machinery
- **Section 87**: Professional/scientific instruments

## Analysis Priorities

1. **Technology Dependency Mapping**:
   - Which CN8 codes show highest import dependency on China?
   - What's the trend in high-tech imports 2020-2024?

2. **Supply Chain Vulnerabilities**:
   - Intermediate goods (BEC classification) from China
   - Concentration ratios by product

3. **Strategic Autonomy Indicators**:
   - EU production vs imports in critical sectors
   - Diversification trends away from China

4. **Dual-Use Monitoring**:
   - Exports to China in sensitive CN8 codes
   - Re-export patterns through third countries

## Access Methods Based on ALL_DATAFLOWS.xml

### From the XML Analysis:
The datasets exist but must be accessed through:

1. **Eurostat Data Browser** (Recommended):
   - Go to: https://ec.europa.eu/eurostat/databrowser/view/DS-045409/
   - Filter: Reporter=EU27, Partner=CN, Product=[specific codes], Period=2020-2024
   - Download as CSV or TSV

2. **Direct Dataset URLs**:
   - DS-045409: https://ec.europa.eu/eurostat/databrowser/view/DS-045409/default/table
   - DS-059331: https://ec.europa.eu/eurostat/databrowser/view/DS-059331/default/table
   - DS-059329: https://ec.europa.eu/eurostat/databrowser/view/DS-059329/default/table
   - DS-059341: https://ec.europa.eu/eurostat/databrowser/view/DS-059341/default/table

3. **SDMX REST API 2.1** (New Format):
   ```
   https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{dataset_id}/
   ```
   Note: Requires specific key format from metadata

4. **Manual Bulk Download**:
   - Visit: https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/bulk-download
   - Look for COMEXT datasets
   - Download complete archives

### Direct Database Queries:
- Use the Eurostat Data Browser for smaller extracts
- Filter by:
  - Reporter: EU27
  - Partner: CN (China)
  - Product: Specific CN8/SITC codes
  - Period: 2020-2024
  - Flow: Imports/Exports

## Expected Insights

These datasets will reveal:
1. **Critical Dependencies**: Which products EU cannot source elsewhere
2. **Technology Flows**: What advanced tech is flowing to/from China
3. **Trade Asymmetries**: Where China has leverage
4. **Emerging Risks**: New dependencies forming
5. **Decoupling Trends**: Evidence of supply chain shifts
