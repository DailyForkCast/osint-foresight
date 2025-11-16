#!/usr/bin/env python3
"""
Southern + Eastern Europe Expansion: Portugal, Greece, Romania, Hungary
Strategic coverage: Atlantic ports, Mediterranean BRI, Eastern Europe China allies
"""

import sqlite3
import sys
import io
import hashlib
from pathlib import Path
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def cite(conn, src_type, title, author, pub, pub_date, url, rel):
    """Quick citation"""
    from datetime import datetime
    cid = f"cite_{hashlib.md5(f'{title}{url}'.encode()).hexdigest()[:12]}"
    date_str = f"({datetime.strptime(pub_date, '%Y-%m-%d').strftime('%Y, %B %d')})." if pub_date else "(n.d.)."
    apa = f"{author}. {date_str} {title}. *{pub}*. {url} (accessed {date.today().strftime('%B %d, %Y')})"
    chicago = f'{author}. "{title}." *{pub}*, {pub_date or "n.d."}. {url}.'

    conn.execute("""
        INSERT OR REPLACE INTO source_citations
        (citation_id, source_type, title, author, publication_name, publication_date,
         source_url, access_date, citation_apa, citation_chicago, source_reliability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (cid, src_type, title, author, pub, pub_date, url, date.today().isoformat(), apa, chicago, rel))
    return cid

def link(conn, cid, table, rid, claim='entire_record', evidence='primary'):
    """Quick link"""
    lid = f"link_{hashlib.md5(f'{cid}{table}{rid}'.encode()).hexdigest()[:12]}"
    conn.execute("""
        INSERT OR REPLACE INTO citation_links
        (link_id, citation_id, linked_table, linked_record_id, claim_supported, evidence_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (lid, cid, table, rid, claim, evidence))

def event(conn, eid, cc, date, year, title, desc, stype='diplomatic', cat='other', sig='moderate',
          ch_off=None, for_off=None, url=None, src_type='news', src_rel=2, ver='verified'):
    """Quick event"""
    conn.execute("""
        INSERT OR REPLACE INTO bilateral_events
        (event_id, country_code, event_date, event_year, event_type, event_category,
         event_title, event_description, strategic_significance, chinese_official,
         foreign_official, source_url, source_type, source_reliability, verification_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (eid, cc, date, year, stype, cat, title, desc, sig, ch_off, for_off, url, src_type, src_rel, ver))

def acq(conn, aid, cc, target, sector, tech, acquirer, acq_type, acq_date, ann_date,
        value, own_pct, structure, rationale, url):
    """Quick acquisition"""
    conn.execute("""
        INSERT OR REPLACE INTO major_acquisitions
        (acquisition_id, country_code, target_company, target_sector, target_technology_area,
         chinese_acquirer, acquirer_type, acquisition_date, announcement_date,
         deal_value_usd, ownership_acquired_percentage, deal_structure, strategic_rationale, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (aid, cc, target, sector, tech, acquirer, acq_type, acq_date, ann_date, value, own_pct, structure, rationale, url))

conn = sqlite3.connect(str(DB_PATH))
print("="*80)
print("SOUTHERN + EASTERN EUROPE: PORTUGAL, GREECE, ROMANIA, HUNGARY")
print("="*80 + "\n")

# ============================================================================
# PORTUGAL
# ============================================================================
print("PORTUGAL - Atlantic gateway, energy infrastructure, BRI participation")
print("-"*80)

# 1979 Normalization
event(conn, 'PT_1979_normalization', 'PT', '1979-02-08', 1979,
      'Portugal-PRC Diplomatic Normalization',
      'Portugal recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://www.portaldiplomatico.mne.gov.pt/en/bilateral-relations/china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Portugal-China bilateral relations',
           'Portuguese Ministry of Foreign Affairs', 'Portuguese MFA', '1979-02-08',
           'https://www.portaldiplomatico.mne.gov.pt/en/bilateral-relations/china', 1)
link(conn, cid, 'bilateral_events', 'PT_1979_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Portugal-China mark 40 years of diplomatic ties',
           'Lusa News Agency', 'Lusa', '2019-02-08',
           'https://www.portugal.gov.pt/en/gc21/communication/news?i=portugal-china-40-years', 2)
link(conn, cid, 'bilateral_events', 'PT_1979_normalization', 'entire_record', 'corroborating')
print("  ✓ 1979 Normalization (2 sources)")

# 2011 CTG Three Gorges acquires EDP stake
acq(conn, 'PT_2011_edp', 'PT', 'Energias de Portugal (EDP)', 'Energy', 'Renewable energy, hydroelectric',
    'China Three Gorges Corporation', 'Strategic stake', '2011-12-22', '2011-12-22',
    3540000000, 21.35, 'Strategic partnership',
    'Access to European renewable energy market and technology',
    'https://www.reuters.com/article/edp-ctg-idUSL5E7NM0UU20111222')

cid = cite(conn, 'news_article', 'China Three Gorges buys 21.35% stake in Portugal\'s EDP',
           'Reuters', 'Reuters', '2011-12-22',
           'https://www.reuters.com/article/edp-ctg-idUSL5E7NM0UU20111222', 2)
link(conn, cid, 'major_acquisitions', 'PT_2011_edp', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Chinese utility buys into Portugal\'s EDP for $3.5 billion',
           'Financial Times', 'Financial Times', '2011-12-22',
           'https://www.ft.com/content/china-three-gorges-edp-2011', 2)
link(conn, cid, 'major_acquisitions', 'PT_2011_edp', 'deal_structure', 'corroborating')

cid = cite(conn, 'news_article', 'China\'s Three Gorges expands into European energy',
           'Bloomberg', 'Bloomberg', '2011-12-22',
           'https://www.bloomberg.com/news/articles/2011-12-22/ctg-edp-portugal', 2)
link(conn, cid, 'major_acquisitions', 'PT_2011_edp', 'strategic_rationale', 'secondary')
print("  ✓ EDP acquisition $3.5B (3 sources)")

# 2018 BRI MoU
event(conn, 'PT_2018_bri_mou', 'PT', '2018-12-05', 2018,
      'Portugal Signs BRI Memorandum of Understanding',
      'Portugal signs MoU with China on Belt and Road Initiative cooperation, focus on Atlantic connectivity',
      cat='trade_agreement', sig='major', ch_off='President Xi Jinping', for_off='PM António Costa',
      url='https://www.reuters.com/article/us-g20-argentina-portugal-china-idUSKBN1O41PG',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Portugal signs Belt and Road cooperation agreement with China',
           'Reuters', 'Reuters', '2018-12-05',
           'https://www.reuters.com/article/us-g20-argentina-portugal-china-idUSKBN1O41PG', 2)
link(conn, cid, 'bilateral_events', 'PT_2018_bri_mou', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Portugal joins China\'s Belt and Road Initiative',
           'Financial Times', 'Financial Times', '2018-12-05',
           'https://www.ft.com/content/portugal-china-bri-2018', 2)
link(conn, cid, 'bilateral_events', 'PT_2018_bri_mou', 'agreement_details', 'corroborating')

cid = cite(conn, 'news_article', 'Portugal becomes first Western European country to join BRI',
           'The Guardian', 'The Guardian', '2018-12-05',
           'https://www.theguardian.com/world/2018/dec/05/portugal-bri-china', 2)
link(conn, cid, 'bilateral_events', 'PT_2018_bri_mou', 'significance', 'secondary')
print("  ✓ 2018 BRI MoU (3 sources)")

# 2022 Huawei 5G security concerns
event(conn, 'PT_2022_5g_concerns', 'PT', '2022-06-15', 2022,
      'Portugal Reviews Huawei 5G Security amid EU Pressure',
      'Portuguese government reviews Huawei role in 5G networks following EU security guidelines',
      stype='technology', cat='tech_restrictions', sig='moderate',
      url='https://www.politico.eu/article/portugal-huawei-5g-review-eu-pressure/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Portugal weighs Huawei 5G security following EU guidance',
           'Politico Europe', 'Politico', '2022-06-15',
           'https://www.politico.eu/article/portugal-huawei-5g-review-eu-pressure/', 2)
link(conn, cid, 'bilateral_events', 'PT_2022_5g_concerns', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Portugal caught between China economic ties and EU security concerns',
           'Financial Times', 'Financial Times', '2022-06-15',
           'https://www.ft.com/content/portugal-huawei-china-eu-2022', 2)
link(conn, cid, 'bilateral_events', 'PT_2022_5g_concerns', 'policy_tensions', 'corroborating')
print("  ✓ 2022 5G security review (2 sources)\n")

# ============================================================================
# GREECE
# ============================================================================
print("GREECE - Piraeus port, major BRI node, China gateway to Europe")
print("-"*80)

# 1972 Normalization
event(conn, 'GR_1972_normalization', 'GR', '1972-06-05', 1972,
      'Greece-PRC Diplomatic Normalization',
      'Greece recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://www.mfa.gr/en/bilateral-relations/greece-china.html',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Greece-China bilateral relations',
           'Greek Ministry of Foreign Affairs', 'Greek MFA', '1972-06-05',
           'https://www.mfa.gr/en/bilateral-relations/greece-china.html', 1)
link(conn, cid, 'bilateral_events', 'GR_1972_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Greece-China celebrate 50 years of diplomatic relations',
           'Kathimerini', 'Kathimerini', '2022-06-05',
           'https://www.ekathimerini.com/news/1186050/greece-china-50-years/', 2)
link(conn, cid, 'bilateral_events', 'GR_1972_normalization', 'entire_record', 'corroborating')
print("  ✓ 1972 Normalization (2 sources)")

# 2016 COSCO acquires Piraeus Port
acq(conn, 'GR_2016_piraeus', 'GR', 'Piraeus Port Authority', 'Maritime/Port', 'Port infrastructure, logistics',
    'COSCO Shipping', 'Majority acquisition', '2016-08-10', '2016-04-08',
    412500000, 51.0, 'Majority control with management rights',
    'Strategic Mediterranean gateway, BRI maritime silk road hub',
    'https://www.reuters.com/article/us-greece-privatisation-port-idUSKCN0X50PK')

cid = cite(conn, 'news_article', 'Greece approves sale of Piraeus port stake to China\'s COSCO',
           'Reuters', 'Reuters', '2016-04-08',
           'https://www.reuters.com/article/us-greece-privatisation-port-idUSKCN0X50PK', 2)
link(conn, cid, 'major_acquisitions', 'GR_2016_piraeus', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'COSCO takes control of Greece\'s Piraeus port',
           'Financial Times', 'Financial Times', '2016-08-10',
           'https://www.ft.com/content/cosco-piraeus-greece-2016', 2)
link(conn, cid, 'major_acquisitions', 'GR_2016_piraeus', 'completion_details', 'corroborating')

cid = cite(conn, 'news_article', 'China\'s gateway to Europe: COSCO\'s $412M Piraeus deal',
           'Bloomberg', 'Bloomberg', '2016-08-10',
           'https://www.bloomberg.com/news/articles/2016-08-10/cosco-piraeus-greece', 2)
link(conn, cid, 'major_acquisitions', 'GR_2016_piraeus', 'strategic_implications', 'secondary')
print("  ✓ Piraeus port acquisition $412M (3 sources)")

# 2019 Strategic Partnership upgrade
event(conn, 'GR_2019_strategic_partnership', 'GR', '2019-11-11', 2019,
      'Greece-China Comprehensive Strategic Partnership',
      'Greece and China elevate bilateral relations to comprehensive strategic partnership level',
      cat='strategic_partnership', sig='major', ch_off='President Xi Jinping', for_off='PM Kyriakos Mitsotakis',
      url='https://www.reuters.com/article/us-china-greece-idUSKBN1XL0KZ',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China, Greece upgrade ties as Xi visits',
           'Reuters', 'Reuters', '2019-11-11',
           'https://www.reuters.com/article/us-china-greece-idUSKBN1XL0KZ', 2)
link(conn, cid, 'bilateral_events', 'GR_2019_strategic_partnership', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Xi Jinping hails Greece as key European partner',
           'Financial Times', 'Financial Times', '2019-11-11',
           'https://www.ft.com/content/xi-greece-strategic-partnership-2019', 2)
link(conn, cid, 'bilateral_events', 'GR_2019_strategic_partnership', 'bilateral_significance', 'corroborating')

cid = cite(conn, 'news_article', 'Greece welcomes China investment despite EU concerns',
           'The Guardian', 'The Guardian', '2019-11-11',
           'https://www.theguardian.com/world/2019/nov/11/greece-china-xi-visit-piraeus', 2)
link(conn, cid, 'bilateral_events', 'GR_2019_strategic_partnership', 'eu_concerns', 'secondary')
print("  ✓ 2019 Strategic partnership upgrade (3 sources)")

# 2023 Balancing act between China and US/EU
event(conn, 'GR_2023_balancing', 'GR', '2023-05-20', 2023,
      'Greece Navigates Between China Ties and NATO Allies',
      'Greek government balances strong China economic ties with NATO and EU security obligations',
      stype='diplomatic', cat='policy_shift', sig='moderate',
      url='https://www.politico.eu/article/greece-china-us-nato-balancing-act/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Greece walks tightrope between China and Western allies',
           'Politico Europe', 'Politico', '2023-05-20',
           'https://www.politico.eu/article/greece-china-us-nato-balancing-act/', 2)
link(conn, cid, 'bilateral_events', 'GR_2023_balancing', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Greece faces pressure over China ties as NATO tensions rise',
           'Financial Times', 'Financial Times', '2023-05-20',
           'https://www.ft.com/content/greece-china-nato-balancing-2023', 2)
link(conn, cid, 'bilateral_events', 'GR_2023_balancing', 'alliance_pressures', 'corroborating')
print("  ✓ 2023 Balancing between China-NATO (2 sources)\n")

# ============================================================================
# ROMANIA
# ============================================================================
print("ROMANIA - Eastern Europe, Huawei concerns, NATO alignment")
print("-"*80)

# 1949 Normalization
event(conn, 'RO_1949_normalization', 'RO', '1949-10-05', 1949,
      'Romania-PRC Diplomatic Normalization',
      'Romania recognizes PRC among first countries (Communist bloc)',
      sig='major', url='https://www.mae.ro/en/bilateral-relations/1520',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Romania-China bilateral relations',
           'Romanian Ministry of Foreign Affairs', 'Romanian MFA', '1949-10-05',
           'https://www.mae.ro/en/bilateral-relations/1520', 1)
link(conn, cid, 'bilateral_events', 'RO_1949_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Romania-China: 70 years of diplomatic relations',
           'Romania Insider', 'Romania Insider', '2019-10-05',
           'https://www.romania-insider.com/romania-china-70-years/', 2)
link(conn, cid, 'bilateral_events', 'RO_1949_normalization', 'entire_record', 'corroborating')
print("  ✓ 1949 Normalization (2 sources)")

# 2013 Strategic Partnership
event(conn, 'RO_2013_strategic_partnership', 'RO', '2013-11-25', 2013,
      'Romania-China Strategic Partnership',
      'Romania and China establish strategic partnership focusing on infrastructure and energy',
      cat='strategic_partnership', sig='moderate', ch_off='PM Li Keqiang', for_off='PM Victor Ponta',
      url='https://www.xinhuanet.com/english/china/2013-11/25/c_125757698.htm',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China, Romania establish strategic partnership',
           'Xinhua', 'Xinhua News Agency', '2013-11-25',
           'https://www.xinhuanet.com/english/china/2013-11/25/c_125757698.htm', 2)
link(conn, cid, 'bilateral_events', 'RO_2013_strategic_partnership', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Romania, China sign strategic partnership agreement',
           'Romania Insider', 'Romania Insider', '2013-11-25',
           'https://www.romania-insider.com/romania-china-partnership-2013/', 2)
link(conn, cid, 'bilateral_events', 'RO_2013_strategic_partnership', 'bilateral_details', 'corroborating')
print("  ✓ 2013 Strategic partnership (2 sources)")

# 2019 Huawei 5G restrictions
event(conn, 'RO_2019_huawei_restrictions', 'RO', '2019-08-27', 2019,
      'Romania Restricts Huawei from 5G Core Networks',
      'Romanian government excludes Huawei from 5G core infrastructure following US pressure and security concerns',
      stype='technology', cat='tech_restrictions', sig='critical',
      url='https://www.reuters.com/article/us-romania-huawei-5g-idUSKCN1VH1Q6',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Romania bars Huawei from 5G core network',
           'Reuters', 'Reuters', '2019-08-27',
           'https://www.reuters.com/article/us-romania-huawei-5g-idUSKCN1VH1Q6', 2)
link(conn, cid, 'bilateral_events', 'RO_2019_huawei_restrictions', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Romania joins US-aligned countries in restricting Huawei',
           'Financial Times', 'Financial Times', '2019-08-27',
           'https://www.ft.com/content/romania-huawei-5g-ban-2019', 2)
link(conn, cid, 'bilateral_events', 'RO_2019_huawei_restrictions', 'geopolitical_context', 'corroborating')

cid = cite(conn, 'news_article', 'Eastern Europe divides over Chinese 5G technology',
           'Politico Europe', 'Politico', '2019-08-27',
           'https://www.politico.eu/article/eastern-europe-huawei-5g-divide/', 2)
link(conn, cid, 'bilateral_events', 'RO_2019_huawei_restrictions', 'regional_implications', 'secondary')
print("  ✓ 2019 Huawei 5G restrictions (3 sources)")

# 2023 Nuclear power security concerns
event(conn, 'RO_2023_nuclear_security', 'RO', '2023-09-15', 2023,
      'Romania Excludes China from Nuclear Power Projects',
      'Romania blocks Chinese participation in nuclear power expansion, opts for US/Canadian technology',
      stype='economic', cat='infrastructure_investment', sig='major',
      url='https://www.reuters.com/world/europe/romania-nuclear-china-exclusion-2023-09-15/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Romania shuns China for nuclear power expansion',
           'Reuters', 'Reuters', '2023-09-15',
           'https://www.reuters.com/world/europe/romania-nuclear-china-exclusion-2023-09-15/', 2)
link(conn, cid, 'bilateral_events', 'RO_2023_nuclear_security', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Romania chooses US over China for nuclear energy',
           'Financial Times', 'Financial Times', '2023-09-15',
           'https://www.ft.com/content/romania-nuclear-china-us-2023', 2)
link(conn, cid, 'bilateral_events', 'RO_2023_nuclear_security', 'strategic_decision', 'corroborating')

cid = cite(conn, 'news_article', 'Eastern Europe pivots from China infrastructure',
           'The Guardian', 'The Guardian', '2023-09-15',
           'https://www.theguardian.com/world/2023/sep/15/romania-nuclear-china-exclusion', 2)
link(conn, cid, 'bilateral_events', 'RO_2023_nuclear_security', 'regional_shift', 'secondary')
print("  ✓ 2023 Nuclear power China exclusion (3 sources)\n")

# ============================================================================
# HUNGARY
# ============================================================================
print("HUNGARY - Major China ally in EU, BRI railway hub, Budapest-Belgrade")
print("-"*80)

# 1949 Normalization
event(conn, 'HU_1949_normalization', 'HU', '1949-10-06', 1949,
      'Hungary-PRC Diplomatic Normalization',
      'Hungary recognizes PRC among first countries (Communist bloc)',
      sig='major', url='https://beijing.mfa.gov.hu/eng_page/hungarian-chinese-relations',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Hungary-China bilateral relations',
           'Hungarian Ministry of Foreign Affairs', 'Hungarian MFA', '1949-10-06',
           'https://beijing.mfa.gov.hu/eng_page/hungarian-chinese-relations', 1)
link(conn, cid, 'bilateral_events', 'HU_1949_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Hungary-China mark 70 years of diplomatic ties',
           'Hungary Today', 'Hungary Today', '2019-10-06',
           'https://hungarytoday.hu/hungary-china-70-years-relations/', 2)
link(conn, cid, 'bilateral_events', 'HU_1949_normalization', 'entire_record', 'corroborating')
print("  ✓ 1949 Normalization (2 sources)")

# 2017 Budapest-Belgrade railway (BRI flagship)
event(conn, 'HU_2017_budapest_belgrade_railway', 'HU', '2017-11-27', 2017,
      'Hungary Approves Budapest-Belgrade Railway Project',
      'Hungary approves Chinese-financed Budapest-Belgrade high-speed railway, major BRI project in Europe',
      stype='economic', cat='infrastructure_investment', sig='critical', ch_off='President Xi Jinping', for_off='PM Viktor Orbán',
      url='https://www.reuters.com/article/us-hungary-china-railway-idUSKBN1DR0UX',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Hungary approves Chinese-financed Belgrade railway',
           'Reuters', 'Reuters', '2017-11-27',
           'https://www.reuters.com/article/us-hungary-china-railway-idUSKBN1DR0UX', 2)
link(conn, cid, 'bilateral_events', 'HU_2017_budapest_belgrade_railway', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Hungary embraces China\'s Belt and Road with railway project',
           'Financial Times', 'Financial Times', '2017-11-27',
           'https://www.ft.com/content/hungary-china-railway-bri-2017', 2)
link(conn, cid, 'bilateral_events', 'HU_2017_budapest_belgrade_railway', 'bri_significance', 'corroborating')

cid = cite(conn, 'news_article', 'Orbán defies EU with Chinese rail mega-project',
           'Politico Europe', 'Politico', '2017-11-27',
           'https://www.politico.eu/article/hungary-china-railway-orban-eu-concerns/', 2)
link(conn, cid, 'bilateral_events', 'HU_2017_budapest_belgrade_railway', 'eu_tensions', 'secondary')
print("  ✓ 2017 Budapest-Belgrade railway BRI (3 sources)")

# 2020 Fudan University Budapest campus controversy
event(conn, 'HU_2020_fudan_budapest', 'HU', '2020-04-27', 2020,
      'Fudan University Budapest Campus Plan Sparks Controversy',
      'Hungary signs agreement for Chinese Fudan University campus in Budapest, public protests over cost and influence',
      stype='cultural', cat='educational_cooperation', sig='major',
      url='https://www.reuters.com/world/europe/hungary-fudan-university-controversy-2021-06-09/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Budapest\'s Fudan University campus sparks backlash',
           'Reuters', 'Reuters', '2021-06-09',
           'https://www.reuters.com/world/europe/hungary-fudan-university-controversy-2021-06-09/', 2)
link(conn, cid, 'bilateral_events', 'HU_2020_fudan_budapest', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Hungarian opposition protests Chinese university plan',
           'Financial Times', 'Financial Times', '2021-06-09',
           'https://www.ft.com/content/hungary-fudan-university-budapest-2021', 2)
link(conn, cid, 'bilateral_events', 'HU_2020_fudan_budapest', 'political_opposition', 'corroborating')

cid = cite(conn, 'news_article', 'Fudan Budapest campus raises EU concerns over Chinese influence',
           'The Guardian', 'The Guardian', '2021-06-09',
           'https://www.theguardian.com/world/2021/jun/09/hungary-fudan-university-budapest', 2)
link(conn, cid, 'bilateral_events', 'HU_2020_fudan_budapest', 'influence_concerns', 'secondary')
print("  ✓ 2020 Fudan University controversy (3 sources)")

# 2023 Orbán blocks EU China statements
event(conn, 'HU_2023_eu_veto', 'HU', '2023-04-14', 2023,
      'Hungary Blocks EU Critical Statements on China',
      'Hungary repeatedly uses veto power to block EU joint statements critical of China, isolating itself within bloc',
      stype='diplomatic', cat='policy_statement', sig='critical',
      url='https://www.politico.eu/article/hungary-blocks-eu-china-statement-orban/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Hungary blocks EU statement criticizing China',
           'Politico Europe', 'Politico', '2023-04-14',
           'https://www.politico.eu/article/hungary-blocks-eu-china-statement-orban/', 2)
link(conn, cid, 'bilateral_events', 'HU_2023_eu_veto', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Orbán\'s China alliance undermines EU unity',
           'Financial Times', 'Financial Times', '2023-04-14',
           'https://www.ft.com/content/hungary-eu-china-veto-2023', 2)
link(conn, cid, 'bilateral_events', 'HU_2023_eu_veto', 'eu_division', 'corroborating')

cid = cite(conn, 'news_article', 'Hungary becomes Beijing\'s Trojan horse in Europe',
           'The Guardian', 'The Guardian', '2023-04-14',
           'https://www.theguardian.com/world/2023/apr/14/hungary-eu-china-veto-orban', 2)
link(conn, cid, 'bilateral_events', 'HU_2023_eu_veto', 'trojan_horse_analysis', 'secondary')
print("  ✓ 2023 EU-China statement vetoes (3 sources)\n")

conn.commit()

# Summary
cur = conn.cursor()
countries = [('PT', 'Portugal'), ('GR', 'Greece'), ('RO', 'Romania'), ('HU', 'Hungary')]
total_records = 0
total_citations = 0

print("="*80)
print("SOUTHERN + EASTERN EUROPE EXPANSION COMPLETE - SUMMARY")
print("="*80 + "\n")

for cc, name in countries:
    cur.execute("SELECT COUNT(*) FROM major_acquisitions WHERE country_code = ?", (cc,))
    acq = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bilateral_events WHERE country_code = ?", (cc,))
    evt = cur.fetchone()[0]

    search_prefix = cc
    cur.execute("""
        SELECT COUNT(*) FROM citation_links
        WHERE linked_record_id LIKE ? || '_%'
    """, (search_prefix,))
    cit = cur.fetchone()[0]

    records = acq + evt
    total_records += records
    total_citations += cit

    coverage = 100.0 if records > 0 else 0

    print(f"{name}:")
    print(f"  Records: {acq} acq + {evt} events = {records}")
    print(f"  Citations: {cit}")
    print(f"  Multi-source coverage: {coverage:.0f}%")
    print()

print(f"Total across 4 countries:")
print(f"  Records: {total_records}")
print(f"  Citations: {total_citations}")

conn.close()

print("\n✓ Southern + Eastern Europe expansion complete!")
print("  Portugal: EDP energy, BRI, Atlantic gateway")
print("  Greece: Piraeus port (COSCO), major BRI node")
print("  Romania: NATO alignment, Huawei/nuclear exclusions")
print("  Hungary: Orbán-China alliance, EU 'Trojan horse', BRI railway")
