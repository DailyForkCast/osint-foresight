# Trade Facilities and Logistics Data Integration Guide

**Last Updated:** 2025-09-21
**Status:** Active Implementation
**Data Location:** F:/OSINT_Data/Trade_Facilities/

## Overview

This guide documents the integration of trade facilities and logistics data sources for supply chain analysis, focusing on Chinese trade networks and Belt & Road Initiative (BRI) infrastructure.

## Data Sources Integrated

### 1. UN/LOCODE (United Nations Code for Trade and Transport Locations)

**Status:** ✅ Successfully processed
**Records:** 1,859 Chinese locations extracted
**File:** `F:/loc242csv.zip` (2024-2 release)

#### Key Statistics:
- **Ports:** 804 facilities
- **Rail terminals:** 267 locations
- **Road terminals:** 889 locations
- **Airports:** 214 facilities
- **Multimodal hubs:** 245 locations
- **Border crossings:** 6 locations

#### Major Hubs Identified:

**Ports:**
- Shanghai (6 codes: PDG, SGH, SHA, SHG, PVG, SHZ)
- Ningbo (3 codes: NBO, NGB, NBG)
- Shenzhen (6 codes: QSE, SNZ, SZX, SZP, SZZ, SZW)
- Guangzhou (8 codes including CAN)
- Qingdao (4 codes: QIN, TAO, QDG)
- Tianjin (8 codes including TSN)
- Dalian (4 codes: DAL, DAG, DLC)
- Xiamen (10 codes: XMN, XMG, etc.)
- Hong Kong (3 codes: HKG, CL4)

**Belt & Road Nodes:**
- Xi'an (53 locations! - major BRI hub)
- Chongqing (4 codes: CQI, CKG, CHQ, CQD)
- Urumqi (3 codes: URM, URC, ULZ)
- Zhengzhou (3 codes: ZGZ, CGO, ZZZ)
- Wuhan (4 codes: WHG, WUH)
- Lanzhou (2 codes: LAZ, LHW)

### 2. UN/ECE Recommendation 20 (Units of Measurement)

**Status:** ✅ Database created
**File:** `F:/rec20.zip`
**Database:** `F:/OSINT_Data/Trade_Facilities/databases/units_measurement.db`

#### Common Trade Units Standardized:
- **Weight:** KGM (Kilogram), TNE (Metric ton), GRM (Gram), DTN (Decitonne)
- **Volume:** LTR (Litre), MTQ (Cubic metre)
- **Quantity:** NAR (Number of articles), PCE (Piece)
- **Length:** MTR (Metre)
- **Area:** MTK (Square metre)

### 3. Open Supply Hub

**Status:** ⏳ Pending API key
**Required:** User registration at https://opensupplyhub.org
**Purpose:** Manufacturing facility identification and ownership mapping

### 4. UN Comtrade API

**Status:** ⏳ Pending credentials
**Required:** User registration at https://comtrade.un.org
**Purpose:** Bilateral trade flow analysis

### 5. Eurostat COMEXT

**Status:** 🔄 API issues, bulk download recommended
**Alternative:** Bulk datasets available at:
- https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/database

**Key Datasets:**
- DS-045409: Detailed CN8 trade data
- ext_st_eu27_2020sitc: SITC categorized trade
- DS-018995: Extra-EU trade by partner

**Strategic Focus Categories:**
- SITC 5: Chemicals
- SITC 7: Machinery and transport equipment
- SITC 75: Office machines and data processing
- SITC 76: Telecommunications equipment
- SITC 77: Electrical machinery
- SITC 87: Professional/scientific instruments
- SITC 88: Photographic/optical goods

## Database Schema

### Integrated Trade Database
**Location:** `F:/OSINT_Data/Trade_Facilities/databases/integrated_trade_20250921.db`

#### Tables:

**chinese_locations**
- All 1,859 UN/LOCODE locations
- Columns: change, country, locode, name, name_ascii, subdivision, function, status, date, iata, coordinates, remarks

**port_facility_mapping**
- UNLOCODE to facility type mapping
- Identifies ports, airports, rail terminals, BRI nodes
- Links to coordinates and timezone

**trade_routes**
- Origin-destination pairs
- Product categories
- Volume and frequency data
- Strategic importance ratings

**measurement_units**
- Standardized conversion factors
- Trade unit harmonization
- Cross-reference with customs codes

## Processing Scripts

### Core Scripts Created:

1. **process_unlocode_units.py**
   - Extracts Chinese locations from UN/LOCODE
   - Creates units conversion database
   - Identifies major logistics hubs
   - Maps Belt & Road Initiative nodes

2. **download_trade_facilities.py**
   - Comprehensive collector for all trade sources
   - Handles API authentication
   - Creates directory structures
   - Database initialization

3. **download_eurostat_comext.py**
   - Eurostat COMEXT data collection
   - Strategic goods focus
   - Technology transfer tracking
   - CN8/SITC classification

## Key Findings

### Logistics Network Concentration
- **Xi'an:** 53 locations - major BRI consolidation hub
- **Shanghai/Guangzhou/Shenzhen:** Primary export gateways
- **Urumqi/Lanzhou:** Western corridor nodes to Central Asia

### Infrastructure Capabilities
- 804 port facilities for maritime trade
- 214 airports for air cargo
- 267 rail terminals for China-Europe trains
- 245 multimodal hubs for integrated logistics

## Integration Points

### With Existing Data:
- **GLEIF LEI:** Match facility operators to legal entities
- **OpenSanctions:** Screen facility operators against sanctions
- **SEC EDGAR:** Link to US-listed Chinese logistics companies
- **USPTO Patents:** Technology in logistics automation

### Analysis Opportunities:
1. **Chokepoint Analysis:** Identify critical nodes in supply chains
2. **Ownership Mapping:** Connect facilities to parent companies
3. **Sanctions Exposure:** Flag facilities with sanctioned entities
4. **Technology Transfer Routes:** Track high-tech goods flows
5. **BRI Network Analysis:** Map infrastructure dependencies

## Next Steps

1. **Immediate:**
   - Obtain Open Supply Hub API key
   - Register for UN Comtrade access
   - Download Eurostat bulk datasets

2. **Analysis Phase:**
   - Cross-reference facilities with company ownership
   - Map critical supply chain nodes
   - Identify dual-use technology routes
   - Assess sanctions vulnerabilities

3. **Reporting:**
   - Generate facility risk profiles
   - Create supply chain dependency maps
   - Produce BRI infrastructure assessments

## Quality Notes

- UN/LOCODE data is authoritative for location codes
- Some location codes have NaN values (older entries)
- Xi'an's 53 locations likely include district subdivisions
- Units database enables accurate volume conversions
- Eurostat API requires specific parameter formats for bulk data

## References

- UN/LOCODE: https://unece.org/trade/uncefact/unlocode
- UN/ECE Rec 20: https://unece.org/trade/uncefact/cl-recommendations
- Open Supply Hub: https://opensupplyhub.org
- UN Comtrade: https://comtrade.un.org
- Eurostat: https://ec.europa.eu/eurostat

---

*This integration provides the foundation for comprehensive supply chain analysis and trade flow monitoring.*
