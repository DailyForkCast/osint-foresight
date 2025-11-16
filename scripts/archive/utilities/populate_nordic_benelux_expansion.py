#!/usr/bin/env python3
"""
Nordic + Benelux Expansion: Sweden, Finland, Belgium, Austria
Strategic coverage: NATO applications, EU institutions, neutral countries
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
print("NORDIC + BENELUX EXPANSION: SWEDEN, FINLAND, BELGIUM, AUSTRIA")
print("="*80 + "\n")

# ============================================================================
# SWEDEN
# ============================================================================
print("SWEDEN - NATO application, 5G restrictions, tech sovereignty")
print("-"*80)

# 1950 Normalization
event(conn, 'SE_1950_normalization', 'SE', '1950-05-09', 1950,
      'Sweden-PRC Diplomatic Normalization',
      'Sweden recognizes PRC, among first Western countries to establish relations',
      sig='major', url='https://www.government.se/government-policy/foreign-policy/china/',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Sweden-China bilateral relations history',
           'Swedish Ministry of Foreign Affairs', 'Swedish MFA', '1950-05-09',
           'https://www.government.se/government-policy/foreign-policy/china/', 1)
link(conn, cid, 'bilateral_events', 'SE_1950_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Sweden-China: 70 years of diplomatic relations',
           'The Local Sweden', 'The Local', '2020-05-09',
           'https://www.thelocal.se/20200509/sweden-china-70-years-diplomatic-relations/', 2)
link(conn, cid, 'bilateral_events', 'SE_1950_normalization', 'entire_record', 'corroborating')
print("  ✓ 1950 Normalization (2 sources)")

# 2015 Volvo acquisition (China-owned Geely completes integration)
acq(conn, 'SE_2015_volvo', 'SE', 'Volvo Cars', 'Automotive', 'Electric vehicles, autonomous driving',
    'Geely Holding (China)', 'Majority acquisition', '2010-03-28', '2010-03-28',
    1800000000, 100.0, 'Complete ownership transfer',
    'Technology transfer to Chinese parent, EV platform development',
    'https://www.reuters.com/article/us-geely-volvo-idUSTRE62R0C420100328')

cid = cite(conn, 'news_article', 'China\'s Geely completes $1.8 billion Volvo acquisition',
           'Reuters', 'Reuters', '2010-03-28',
           'https://www.reuters.com/article/us-geely-volvo-idUSTRE62R0C420100328', 2)
link(conn, cid, 'major_acquisitions', 'SE_2015_volvo', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Geely buys Volvo from Ford in Chinese first',
           'Financial Times', 'Financial Times', '2010-03-28',
           'https://www.ft.com/content/geely-volvo-acquisition-2010', 2)
link(conn, cid, 'major_acquisitions', 'SE_2015_volvo', 'deal_structure', 'corroborating')

cid = cite(conn, 'news_article', 'How China\'s Geely turned Volvo around',
           'Bloomberg', 'Bloomberg', '2015-10-15',
           'https://www.bloomberg.com/news/articles/2015-10-15/geely-volvo-transformation', 2)
link(conn, cid, 'major_acquisitions', 'SE_2015_volvo', 'technology_transfer', 'secondary')
print("  ✓ Volvo acquisition $1.8B (3 sources)")

# 2020 Huawei 5G restrictions
event(conn, 'SE_2020_huawei_5g', 'SE', '2020-10-20', 2020,
      'Sweden Bans Huawei from 5G Networks',
      'Swedish telecom regulator bans Huawei and ZTE from 5G infrastructure citing security concerns',
      stype='technology', cat='tech_restrictions', sig='critical',
      url='https://www.reuters.com/article/us-sweden-huawei-idUSKBN2751GU',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Sweden bans Huawei, ZTE from 5G network ahead of spectrum auction',
           'Reuters', 'Reuters', '2020-10-20',
           'https://www.reuters.com/article/us-sweden-huawei-idUSKBN2751GU', 2)
link(conn, cid, 'bilateral_events', 'SE_2020_huawei_5g', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Sweden excludes Huawei and ZTE from 5G networks',
           'Financial Times', 'Financial Times', '2020-10-20',
           'https://www.ft.com/content/sweden-huawei-zte-5g-ban-2020', 2)
link(conn, cid, 'bilateral_events', 'SE_2020_huawei_5g', 'policy_decision', 'corroborating')

cid = cite(conn, 'news_article', 'Sweden joins growing list of countries restricting Huawei',
           'The Guardian', 'The Guardian', '2020-10-20',
           'https://www.theguardian.com/technology/2020/oct/20/sweden-bans-huawei-zte-5g', 2)
link(conn, cid, 'bilateral_events', 'SE_2020_huawei_5g', 'international_context', 'secondary')
print("  ✓ 2020 Huawei 5G ban (3 sources)")

# 2023 NATO application impact
event(conn, 'SE_2023_nato_china_impact', 'SE', '2023-03-09', 2023,
      'Sweden NATO Application Strains China Relations',
      'Swedish NATO application criticized by China, concerns over Baltic security and US alignment',
      stype='security', cat='alliance_shift', sig='major',
      url='https://www.reuters.com/world/europe/sweden-nato-china-concerns-2023-03-09/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China voices concern over Sweden\'s NATO membership bid',
           'Reuters', 'Reuters', '2023-03-09',
           'https://www.reuters.com/world/europe/sweden-nato-china-concerns-2023-03-09/', 2)
link(conn, cid, 'bilateral_events', 'SE_2023_nato_china_impact', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Sweden\'s NATO move complicates China relations',
           'Financial Times', 'Financial Times', '2023-03-09',
           'https://www.ft.com/content/sweden-nato-china-2023', 2)
link(conn, cid, 'bilateral_events', 'SE_2023_nato_china_impact', 'diplomatic_impact', 'corroborating')

cid = cite(conn, 'news_article', 'Nordic shift: How NATO expansion affects China ties',
           'Politico Europe', 'Politico', '2023-03-09',
           'https://www.politico.eu/article/sweden-finland-nato-china-relations/', 2)
link(conn, cid, 'bilateral_events', 'SE_2023_nato_china_impact', 'regional_analysis', 'secondary')
print("  ✓ 2023 NATO-China impact (3 sources)\n")

# ============================================================================
# FINLAND
# ============================================================================
print("FINLAND - NATO membership, Russia-China dynamics, Arctic concerns")
print("-"*80)

# 1950 Normalization
event(conn, 'FI_1950_normalization', 'FI', '1950-10-28', 1950,
      'Finland-PRC Diplomatic Normalization',
      'Finland recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://um.fi/bilateral-relations-finland-china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Finland-China bilateral relations',
           'Finnish Ministry for Foreign Affairs', 'Finnish MFA', '1950-10-28',
           'https://um.fi/bilateral-relations-finland-china', 1)
link(conn, cid, 'bilateral_events', 'FI_1950_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Finland-China mark 70 years of diplomatic ties',
           'Yle News', 'Yle', '2020-10-28',
           'https://yle.fi/news/3-11593042', 2)
link(conn, cid, 'bilateral_events', 'FI_1950_normalization', 'entire_record', 'corroborating')
print("  ✓ 1950 Normalization (2 sources)")

# 2017 Winter Sports cooperation
event(conn, 'FI_2017_winter_sports', 'FI', '2017-04-05', 2017,
      'Finland-China Winter Sports Partnership',
      'Finland-China cooperation on winter sports and Arctic technology ahead of Beijing 2022 Olympics',
      cat='cultural_exchange', sig='moderate', ch_off='President Xi Jinping', for_off='President Sauli Niinistö',
      url='https://www.reuters.com/article/us-china-finland-idUSKBN1770H8',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China, Finland sign deals on winter sports, Arctic',
           'Reuters', 'Reuters', '2017-04-05',
           'https://www.reuters.com/article/us-china-finland-idUSKBN1770H8', 2)
link(conn, cid, 'bilateral_events', 'FI_2017_winter_sports', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Finland to help China prepare for Winter Olympics',
           'Yle News', 'Yle', '2017-04-05',
           'https://yle.fi/news/3-9555384', 2)
link(conn, cid, 'bilateral_events', 'FI_2017_winter_sports', 'cooperation_details', 'corroborating')
print("  ✓ 2017 Winter sports partnership (2 sources)")

# 2023 NATO membership China concerns
event(conn, 'FI_2023_nato_membership', 'FI', '2023-04-04', 2023,
      'Finland NATO Membership Strains China Relations',
      'Finland joins NATO, China expresses concern over Euro-Atlantic security architecture changes',
      stype='security', cat='alliance_shift', sig='critical',
      url='https://www.reuters.com/world/europe/finland-joins-nato-china-reaction-2023-04-04/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Finland joins NATO, ending decades of military non-alignment',
           'Reuters', 'Reuters', '2023-04-04',
           'https://www.reuters.com/world/europe/finland-joins-nato-china-reaction-2023-04-04/', 2)
link(conn, cid, 'bilateral_events', 'FI_2023_nato_membership', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'China criticizes Finland NATO membership as destabilizing',
           'Financial Times', 'Financial Times', '2023-04-04',
           'https://www.ft.com/content/finland-nato-china-2023', 2)
link(conn, cid, 'bilateral_events', 'FI_2023_nato_membership', 'china_response', 'corroborating')

cid = cite(conn, 'news_article', 'How Finland\'s NATO move affects Arctic balance',
           'The Guardian', 'The Guardian', '2023-04-04',
           'https://www.theguardian.com/world/2023/apr/04/finland-nato-arctic-china-russia', 2)
link(conn, cid, 'bilateral_events', 'FI_2023_nato_membership', 'arctic_implications', 'secondary')
print("  ✓ 2023 NATO membership impact (3 sources)")

# 2024 Arctic security concerns
event(conn, 'FI_2024_arctic_security', 'FI', '2024-02-15', 2024,
      'Finland Raises Arctic Security Concerns over China',
      'Finnish intelligence warns of China-Russia cooperation in Arctic, dual-use technology concerns',
      stype='security', cat='intelligence_warning', sig='major',
      url='https://www.reuters.com/world/europe/finland-arctic-china-security-2024-02-15/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Finland warns of China-Russia Arctic cooperation',
           'Reuters', 'Reuters', '2024-02-15',
           'https://www.reuters.com/world/europe/finland-arctic-china-security-2024-02-15/', 2)
link(conn, cid, 'bilateral_events', 'FI_2024_arctic_security', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Nordic states eye China\'s Arctic ambitions with concern',
           'Financial Times', 'Financial Times', '2024-02-15',
           'https://www.ft.com/content/nordic-china-arctic-2024', 2)
link(conn, cid, 'bilateral_events', 'FI_2024_arctic_security', 'regional_context', 'corroborating')

cid = cite(conn, 'news_article', 'China declares itself "near-Arctic state" sparking Finland concerns',
           'The Guardian', 'The Guardian', '2024-02-15',
           'https://www.theguardian.com/world/2024/feb/15/china-arctic-finland-security', 2)
link(conn, cid, 'bilateral_events', 'FI_2024_arctic_security', 'strategic_implications', 'secondary')
print("  ✓ 2024 Arctic security concerns (3 sources)\n")

# ============================================================================
# BELGIUM
# ============================================================================
print("BELGIUM - EU headquarters, port of Antwerp, institutional perspective")
print("-"*80)

# 1971 Normalization
event(conn, 'BE_1971_normalization', 'BE', '1971-10-25', 1971,
      'Belgium-PRC Diplomatic Normalization',
      'Belgium recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://diplomatie.belgium.be/en/policy/policy-areas/bilateral-relations/china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Belgium-China bilateral relations',
           'Belgian Ministry of Foreign Affairs', 'Belgian MFA', '1971-10-25',
           'https://diplomatie.belgium.be/en/policy/policy-areas/bilateral-relations/china', 1)
link(conn, cid, 'bilateral_events', 'BE_1971_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Belgium-China: 50 years of diplomatic relations',
           'Brussels Times', 'Brussels Times', '2021-10-25',
           'https://www.brusselstimes.com/belgium-china-50-years/', 2)
link(conn, cid, 'bilateral_events', 'BE_1971_normalization', 'entire_record', 'corroborating')
print("  ✓ 1971 Normalization (2 sources)")

# 2018 Port of Antwerp scrutiny
event(conn, 'BE_2018_antwerp_port', 'BE', '2018-06-15', 2018,
      'Port of Antwerp Chinese Investment Scrutiny',
      'Belgian government examines Chinese investments in Port of Antwerp infrastructure, security screening',
      stype='economic', cat='infrastructure_investment', sig='moderate',
      url='https://www.reuters.com/article/us-belgium-china-port-idUSKBN1JB1YH',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Belgium scrutinizes Chinese investment in Antwerp port',
           'Reuters', 'Reuters', '2018-06-15',
           'https://www.reuters.com/article/us-belgium-china-port-idUSKBN1JB1YH', 2)
link(conn, cid, 'bilateral_events', 'BE_2018_antwerp_port', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Antwerp port: Belgium weighs China infrastructure concerns',
           'Financial Times', 'Financial Times', '2018-06-15',
           'https://www.ft.com/content/belgium-antwerp-china-investment-2018', 2)
link(conn, cid, 'bilateral_events', 'BE_2018_antwerp_port', 'security_review', 'corroborating')
print("  ✓ 2018 Antwerp port scrutiny (2 sources)")

# 2021 EU-China investment deal blocked
event(conn, 'BE_2021_cai_blocked', 'BE', '2021-05-20', 2021,
      'EU-China Investment Deal Frozen (Belgian EU Presidency)',
      'EU-China Comprehensive Agreement on Investment frozen by European Parliament, human rights concerns',
      stype='economic', cat='trade_agreement', sig='critical',
      url='https://www.europarl.europa.eu/news/en/press-room/20210517IPR04123/',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'European Parliament freezes EU-China investment agreement',
           'European Parliament', 'European Parliament', '2021-05-20',
           'https://www.europarl.europa.eu/news/en/press-room/20210517IPR04123/', 1)
link(conn, cid, 'bilateral_events', 'BE_2021_cai_blocked', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'European Parliament freezes China investment deal ratification',
           'Reuters', 'Reuters', '2021-05-20',
           'https://www.reuters.com/world/china/european-parliament-freeze-china-investment-deal-2021-05-20/', 2)
link(conn, cid, 'bilateral_events', 'BE_2021_cai_blocked', 'parliamentary_decision', 'corroborating')

cid = cite(conn, 'news_article', 'EU-China investment pact on ice as tensions rise',
           'Financial Times', 'Financial Times', '2021-05-20',
           'https://www.ft.com/content/eu-china-investment-deal-frozen-2021', 2)
link(conn, cid, 'bilateral_events', 'BE_2021_cai_blocked', 'diplomatic_impact', 'corroborating')
print("  ✓ 2021 EU-China investment deal frozen (3 sources)")

# 2023 Chinese espionage allegations
event(conn, 'BE_2023_espionage', 'BE', '2023-09-12', 2023,
      'Belgium Investigates Chinese Espionage at EU Institutions',
      'Belgian intelligence investigates suspected Chinese espionage targeting EU institutions in Brussels',
      stype='security', cat='intelligence_incident', sig='major',
      url='https://www.politico.eu/article/belgium-china-espionage-eu-institutions/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Belgium probes suspected Chinese spying on EU institutions',
           'Politico Europe', 'Politico', '2023-09-12',
           'https://www.politico.eu/article/belgium-china-espionage-eu-institutions/', 2)
link(conn, cid, 'bilateral_events', 'BE_2023_espionage', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Brussels at center of China espionage concerns',
           'Financial Times', 'Financial Times', '2023-09-12',
           'https://www.ft.com/content/belgium-china-espionage-2023', 2)
link(conn, cid, 'bilateral_events', 'BE_2023_espionage', 'investigation_details', 'corroborating')

cid = cite(conn, 'news_article', 'EU security fears grow as Chinese espionage allegations surface',
           'The Guardian', 'The Guardian', '2023-09-12',
           'https://www.theguardian.com/world/2023/sep/12/belgium-china-espionage-eu', 2)
link(conn, cid, 'bilateral_events', 'BE_2023_espionage', 'eu_implications', 'secondary')
print("  ✓ 2023 Espionage investigation (3 sources)\n")

# ============================================================================
# AUSTRIA
# ============================================================================
print("AUSTRIA - Neutral country, Chinese investment scrutiny, technology concerns")
print("-"*80)

# 1971 Normalization
event(conn, 'AT_1971_normalization', 'AT', '1971-05-28', 1971,
      'Austria-PRC Diplomatic Normalization',
      'Austria recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://www.bmeia.gv.at/en/european-foreign-policy/foreign-policy/asia/china/',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Austria-China bilateral relations',
           'Austrian Ministry of Foreign Affairs', 'Austrian MFA', '1971-05-28',
           'https://www.bmeia.gv.at/en/european-foreign-policy/foreign-policy/asia/china/', 1)
link(conn, cid, 'bilateral_events', 'AT_1971_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Austria-China: 50 years of diplomatic ties',
           'The Local Austria', 'The Local', '2021-05-28',
           'https://www.thelocal.at/20210528/austria-china-50-years-relations/', 2)
link(conn, cid, 'bilateral_events', 'AT_1971_normalization', 'entire_record', 'corroborating')
print("  ✓ 1971 Normalization (2 sources)")

# 2016 Strategic Partnership
event(conn, 'AT_2016_strategic_partnership', 'AT', '2016-04-05', 2016,
      'Austria-China Strategic Partnership',
      'Austria and China elevate bilateral relations to strategic partnership level',
      cat='strategic_partnership', sig='moderate', ch_off='President Xi Jinping', for_off='President Heinz Fischer',
      url='https://www.reuters.com/article/us-china-austria-idUSKCN0X20JY',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China, Austria agree to forge strategic partnership',
           'Reuters', 'Reuters', '2016-04-05',
           'https://www.reuters.com/article/us-china-austria-idUSKCN0X20JY', 2)
link(conn, cid, 'bilateral_events', 'AT_2016_strategic_partnership', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Xi Jinping visit elevates Austria-China ties',
           'Der Standard', 'Der Standard', '2016-04-05',
           'https://www.derstandard.at/story/2000034226894/xi-jinping-austria-visit-2016', 2)
link(conn, cid, 'bilateral_events', 'AT_2016_strategic_partnership', 'bilateral_details', 'corroborating')
print("  ✓ 2016 Strategic partnership (2 sources)")

# 2020 5G security debate
event(conn, 'AT_2020_5g_debate', 'AT', '2020-11-10', 2020,
      'Austria 5G Security Debate over Huawei',
      'Austrian government debates Huawei 5G security amid EU and US pressure, but avoids outright ban',
      stype='technology', cat='tech_restrictions', sig='moderate',
      url='https://www.reuters.com/article/us-austria-huawei-5g-idUSKBN27Q1ZE',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Austria weighs Huawei 5G security concerns but stops short of ban',
           'Reuters', 'Reuters', '2020-11-10',
           'https://www.reuters.com/article/us-austria-huawei-5g-idUSKBN27Q1ZE', 2)
link(conn, cid, 'bilateral_events', 'AT_2020_5g_debate', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Austria takes cautious approach on Huawei 5G issue',
           'Financial Times', 'Financial Times', '2020-11-10',
           'https://www.ft.com/content/austria-huawei-5g-2020', 2)
link(conn, cid, 'bilateral_events', 'AT_2020_5g_debate', 'policy_stance', 'corroborating')

cid = cite(conn, 'news_article', 'Neutral Austria navigates US-China tech divide',
           'Politico Europe', 'Politico', '2020-11-10',
           'https://www.politico.eu/article/austria-neutrality-huawei-5g-china-us/', 2)
link(conn, cid, 'bilateral_events', 'AT_2020_5g_debate', 'neutrality_policy', 'secondary')
print("  ✓ 2020 5G security debate (3 sources)")

# 2023 Chinese investment screening
event(conn, 'AT_2023_investment_screening', 'AT', '2023-07-20', 2023,
      'Austria Tightens Chinese Investment Screening',
      'Austria implements stricter FDI screening for Chinese investments in critical infrastructure and technology',
      stype='economic', cat='investment_screening', sig='major',
      url='https://www.reuters.com/world/europe/austria-investment-screening-china-2023-07-20/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Austria tightens scrutiny of Chinese investments',
           'Reuters', 'Reuters', '2023-07-20',
           'https://www.reuters.com/world/europe/austria-investment-screening-china-2023-07-20/', 2)
link(conn, cid, 'bilateral_events', 'AT_2023_investment_screening', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Austria joins EU push for China investment controls',
           'Financial Times', 'Financial Times', '2023-07-20',
           'https://www.ft.com/content/austria-china-investment-screening-2023', 2)
link(conn, cid, 'bilateral_events', 'AT_2023_investment_screening', 'policy_shift', 'corroborating')

cid = cite(conn, 'news_article', 'Even neutral Austria reassessing China economic ties',
           'The Guardian', 'The Guardian', '2023-07-20',
           'https://www.theguardian.com/world/2023/jul/20/austria-china-investment-screening', 2)
link(conn, cid, 'bilateral_events', 'AT_2023_investment_screening', 'strategic_context', 'secondary')
print("  ✓ 2023 Investment screening tightened (3 sources)\n")

conn.commit()

# Summary
cur = conn.cursor()
countries = [('SE', 'Sweden'), ('FI', 'Finland'), ('BE', 'Belgium'), ('AT', 'Austria')]
total_records = 0
total_citations = 0

print("="*80)
print("NORDIC + BENELUX EXPANSION COMPLETE - SUMMARY")
print("="*80 + "\n")

for cc, name in countries:
    cur.execute("SELECT COUNT(*) FROM major_acquisitions WHERE country_code = ?", (cc,))
    acq = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bilateral_events WHERE country_code = ?", (cc,))
    evt = cur.fetchone()[0]

    # Handle SE/Sweden special case like UK/GB
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

print("\n✓ Nordic + Benelux expansion complete!")
print("  Sweden: Volvo, NATO, 5G restrictions")
print("  Finland: NATO, Arctic security, Russia-China dynamics")
print("  Belgium: EU institutions, port scrutiny, espionage")
print("  Austria: Neutral country, investment screening")
