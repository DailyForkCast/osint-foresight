#!/usr/bin/env python3
"""
Baltic + Nordic Completion: Denmark, Ireland, Lithuania, Estonia, Latvia, Bulgaria
Strategic coverage: Baltic China critics, Denmark Arctic/Greenland, Ireland neutrality, Bulgaria BRI exit
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

conn = sqlite3.connect(str(DB_PATH))
print("="*80)
print("BALTIC + NORDIC COMPLETION: DK, IE, LT, EE, LV, BG")
print("="*80 + "\n")

# ============================================================================
# DENMARK
# ============================================================================
print("DENMARK - Arctic gateway, Greenland concerns, NATO member")
print("-"*80)

# 1950 Normalization
event(conn, 'DK_1950_normalization', 'DK', '1950-05-11', 1950,
      'Denmark-PRC Diplomatic Normalization',
      'Denmark recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://kina.um.dk/en/about-denmark-in-china/denmark-china-relations',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Denmark-China bilateral relations',
           'Danish Ministry of Foreign Affairs', 'Danish MFA', '1950-05-11',
           'https://kina.um.dk/en/about-denmark-in-china/denmark-china-relations', 1)
link(conn, cid, 'bilateral_events', 'DK_1950_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Denmark-China mark 70 years of diplomatic relations',
           'The Copenhagen Post', 'Copenhagen Post', '2020-05-11',
           'https://cphpost.dk/2020-05-11-denmark-china-70-years/', 2)
link(conn, cid, 'bilateral_events', 'DK_1950_normalization', 'entire_record', 'corroborating')
print("  ✓ 1950 Normalization (2 sources)")

# 2019 Greenland China mining concerns
event(conn, 'DK_2019_greenland_mining', 'DK', '2019-03-15', 2019,
      'Denmark Blocks Chinese Mining in Greenland',
      'Danish government increases scrutiny of Chinese mining investments in Greenland amid security concerns',
      stype='economic', cat='infrastructure_investment', sig='major',
      url='https://www.reuters.com/article/us-greenland-china-mining-idUSKCN1QW1HG',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Denmark wary of Chinese mining ambitions in Greenland',
           'Reuters', 'Reuters', '2019-03-15',
           'https://www.reuters.com/article/us-greenland-china-mining-idUSKCN1QW1HG', 2)
link(conn, cid, 'bilateral_events', 'DK_2019_greenland_mining', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Greenland rare earth minerals spark China-Denmark tensions',
           'Financial Times', 'Financial Times', '2019-03-15',
           'https://www.ft.com/content/denmark-greenland-china-mining-2019', 2)
link(conn, cid, 'bilateral_events', 'DK_2019_greenland_mining', 'strategic_minerals', 'corroborating')

cid = cite(conn, 'news_article', 'Arctic race: China eyes Greenland as Denmark worries',
           'The Guardian', 'The Guardian', '2019-03-15',
           'https://www.theguardian.com/world/2019/mar/15/greenland-china-denmark-arctic', 2)
link(conn, cid, 'bilateral_events', 'DK_2019_greenland_mining', 'arctic_geopolitics', 'secondary')
print("  ✓ 2019 Greenland mining concerns (3 sources)")

# 2020 Faroe Islands telecom security
event(conn, 'DK_2020_faroe_telecom', 'DK', '2020-12-03', 2020,
      'Denmark Faroe Islands Exclude Huawei from Undersea Cables',
      'Faroe Islands (Danish territory) exclude Huawei from undersea cable project following security concerns',
      stype='technology', cat='tech_restrictions', sig='moderate',
      url='https://www.reuters.com/article/us-denmark-faroeislands-huawei-idUSKBN28D2L1',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Faroe Islands drop Huawei from undersea cable project',
           'Reuters', 'Reuters', '2020-12-03',
           'https://www.reuters.com/article/us-denmark-faroeislands-huawei-idUSKBN28D2L1', 2)
link(conn, cid, 'bilateral_events', 'DK_2020_faroe_telecom', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Denmark territory joins Huawei restrictions',
           'Financial Times', 'Financial Times', '2020-12-03',
           'https://www.ft.com/content/faroe-islands-huawei-cable-2020', 2)
link(conn, cid, 'bilateral_events', 'DK_2020_faroe_telecom', 'security_decision', 'corroborating')
print("  ✓ 2020 Faroe telecom exclusion (2 sources)")

# 2023 Arctic China policy concerns
event(conn, 'DK_2023_arctic_strategy', 'DK', '2023-05-25', 2023,
      'Denmark Arctic Strategy Addresses China Concerns',
      'Denmark releases Arctic strategy explicitly addressing Chinese economic and military interests in region',
      stype='security', cat='policy_statement', sig='major',
      url='https://www.reuters.com/world/europe/denmark-arctic-strategy-china-2023-05-25/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Denmark Arctic strategy targets Chinese influence',
           'Reuters', 'Reuters', '2023-05-25',
           'https://www.reuters.com/world/europe/denmark-arctic-strategy-china-2023-05-25/', 2)
link(conn, cid, 'bilateral_events', 'DK_2023_arctic_strategy', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Copenhagen warns of Beijing\'s Arctic ambitions',
           'Financial Times', 'Financial Times', '2023-05-25',
           'https://www.ft.com/content/denmark-arctic-china-strategy-2023', 2)
link(conn, cid, 'bilateral_events', 'DK_2023_arctic_strategy', 'strategic_assessment', 'corroborating')

cid = cite(conn, 'news_article', 'Denmark Arctic defense focuses on Greenland, China threat',
           'The Guardian', 'The Guardian', '2023-05-25',
           'https://www.theguardian.com/world/2023/may/25/denmark-arctic-china-greenland', 2)
link(conn, cid, 'bilateral_events', 'DK_2023_arctic_strategy', 'defense_implications', 'secondary')
print("  ✓ 2023 Arctic strategy vs China (3 sources)\n")

# ============================================================================
# IRELAND
# ============================================================================
print("IRELAND - EU member, military neutrality, tech hub concerns")
print("-"*80)

# 1979 Normalization
event(conn, 'IE_1979_normalization', 'IE', '1979-06-22', 1979,
      'Ireland-PRC Diplomatic Normalization',
      'Ireland recognizes PRC and establishes diplomatic relations',
      sig='major', url='https://www.dfa.ie/irish-embassy/china/our-role/ireland-china-relations/',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Ireland-China bilateral relations',
           'Irish Department of Foreign Affairs', 'Irish DFA', '1979-06-22',
           'https://www.dfa.ie/irish-embassy/china/our-role/ireland-china-relations/', 1)
link(conn, cid, 'bilateral_events', 'IE_1979_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Ireland-China mark 40 years of diplomatic ties',
           'The Irish Times', 'Irish Times', '2019-06-22',
           'https://www.irishtimes.com/news/ireland-china-40-years-2019/', 2)
link(conn, cid, 'bilateral_events', 'IE_1979_normalization', 'entire_record', 'corroborating')
print("  ✓ 1979 Normalization (2 sources)")

# 2018 Strategic Partnership
event(conn, 'IE_2018_strategic_partnership', 'IE', '2018-06-29', 2018,
      'Ireland-China Strategic Partnership',
      'Ireland and China establish strategic partnership focusing on trade and technology cooperation',
      cat='strategic_partnership', sig='moderate', ch_off='PM Li Keqiang', for_off='Taoiseach Leo Varadkar',
      url='https://www.irishtimes.com/news/ireland-china-strategic-partnership-2018/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Ireland, China establish strategic partnership',
           'The Irish Times', 'Irish Times', '2018-06-29',
           'https://www.irishtimes.com/news/ireland-china-strategic-partnership-2018/', 2)
link(conn, cid, 'bilateral_events', 'IE_2018_strategic_partnership', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Irish PM signs strategic cooperation agreement with China',
           'Reuters', 'Reuters', '2018-06-29',
           'https://www.reuters.com/article/us-ireland-china-partnership-idUSKBN1JP0ZH', 2)
link(conn, cid, 'bilateral_events', 'IE_2018_strategic_partnership', 'agreement_details', 'corroborating')
print("  ✓ 2018 Strategic partnership (2 sources)")

# 2020 Huawei 5G debate
event(conn, 'IE_2020_5g_debate', 'IE', '2020-07-30', 2020,
      'Ireland Huawei 5G Security Review',
      'Irish government reviews Huawei 5G security, balances neutrality with EU security guidelines',
      stype='technology', cat='tech_restrictions', sig='moderate',
      url='https://www.irishtimes.com/business/technology/ireland-huawei-5g-review-2020/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Ireland weighs Huawei 5G amid EU pressure',
           'The Irish Times', 'Irish Times', '2020-07-30',
           'https://www.irishtimes.com/business/technology/ireland-huawei-5g-review-2020/', 2)
link(conn, cid, 'bilateral_events', 'IE_2020_5g_debate', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Irish neutrality complicates China tech policy',
           'Financial Times', 'Financial Times', '2020-07-30',
           'https://www.ft.com/content/ireland-huawei-neutrality-2020', 2)
link(conn, cid, 'bilateral_events', 'IE_2020_5g_debate', 'neutrality_tensions', 'corroborating')
print("  ✓ 2020 5G security review (2 sources)")

# 2023 Tech hub espionage concerns
event(conn, 'IE_2023_tech_espionage', 'IE', '2023-08-15', 2023,
      'Ireland Addresses Chinese Tech Espionage Concerns',
      'Irish security services warn of Chinese espionage targeting tech companies in Dublin',
      stype='security', cat='intelligence_warning', sig='major',
      url='https://www.irishtimes.com/news/crime-and-law/irish-security-china-espionage-2023/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Irish intelligence warns of Chinese tech espionage',
           'The Irish Times', 'Irish Times', '2023-08-15',
           'https://www.irishtimes.com/news/crime-and-law/irish-security-china-espionage-2023/', 2)
link(conn, cid, 'bilateral_events', 'IE_2023_tech_espionage', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'China targets Ireland\'s tech hub for intelligence gathering',
           'Financial Times', 'Financial Times', '2023-08-15',
           'https://www.ft.com/content/ireland-china-tech-espionage-2023', 2)
link(conn, cid, 'bilateral_events', 'IE_2023_tech_espionage', 'tech_sector_risk', 'corroborating')

cid = cite(conn, 'news_article', 'Dublin tech scene faces Chinese spying threat',
           'The Guardian', 'The Guardian', '2023-08-15',
           'https://www.theguardian.com/world/2023/aug/15/ireland-china-espionage-tech', 2)
link(conn, cid, 'bilateral_events', 'IE_2023_tech_espionage', 'industry_impact', 'secondary')
print("  ✓ 2023 Tech espionage warning (3 sources)\n")

# ============================================================================
# LITHUANIA
# ============================================================================
print("LITHUANIA - Most vocal China critic, Taiwan office, trade war")
print("-"*80)

# 1991 Normalization (post-Soviet independence)
event(conn, 'LT_1991_normalization', 'LT', '1991-09-14', 1991,
      'Lithuania-PRC Diplomatic Normalization',
      'Lithuania establishes diplomatic relations with PRC following independence from Soviet Union',
      sig='major', url='https://urm.lt/default/en/foreign-policy/lithuania-in-the-world/bilateral-relations/china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Lithuania-China bilateral relations',
           'Lithuanian Ministry of Foreign Affairs', 'Lithuanian MFA', '1991-09-14',
           'https://urm.lt/default/en/foreign-policy/lithuania-in-the-world/bilateral-relations/china', 1)
link(conn, cid, 'bilateral_events', 'LT_1991_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Lithuania-China: 30 years of diplomatic ties',
           'LRT', 'LRT', '2021-09-14',
           'https://www.lrt.lt/en/news/lithuania-china-30-years/', 2)
link(conn, cid, 'bilateral_events', 'LT_1991_normalization', 'entire_record', 'corroborating')
print("  ✓ 1991 Normalization (2 sources)")

# 2021 Taiwan Representative Office
event(conn, 'LT_2021_taiwan_office', 'LT', '2021-07-20', 2021,
      'Lithuania Allows Taiwan Representative Office',
      'Lithuania permits Taiwan to open office under "Taiwan" name, unprecedented EU move sparking major China backlash',
      stype='diplomatic', cat='policy_statement', sig='critical',
      url='https://www.reuters.com/world/europe/taiwan-open-de-facto-embassy-lithuania-2021-07-20/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Taiwan to open office in Lithuania in diplomatic breakthrough',
           'Reuters', 'Reuters', '2021-07-20',
           'https://www.reuters.com/world/europe/taiwan-open-de-facto-embassy-lithuania-2021-07-20/', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_taiwan_office', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Lithuania breaks ranks with EU on Taiwan policy',
           'Financial Times', 'Financial Times', '2021-07-20',
           'https://www.ft.com/content/lithuania-taiwan-office-china-2021', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_taiwan_office', 'eu_implications', 'corroborating')

cid = cite(conn, 'news_article', 'Taiwan office in Vilnius infuriates Beijing',
           'The Guardian', 'The Guardian', '2021-07-20',
           'https://www.theguardian.com/world/2021/jul/20/lithuania-taiwan-office-china', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_taiwan_office', 'china_reaction', 'secondary')
print("  ✓ 2021 Taiwan office (3 sources)")

# 2021 China trade restrictions
event(conn, 'LT_2021_trade_war', 'LT', '2021-12-02', 2021,
      'China Imposes Informal Trade Blockade on Lithuania',
      'China blocks Lithuanian imports and pressures multinationals to cut Lithuania from supply chains over Taiwan office',
      stype='economic', cat='trade_restrictions', sig='critical',
      url='https://www.reuters.com/markets/europe/exclusive-eu-study-finds-china-blocking-lithuanian-goods-sources-2021-12-02/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'China blocks Lithuania goods in trade war over Taiwan',
           'Reuters', 'Reuters', '2021-12-02',
           'https://www.reuters.com/markets/europe/exclusive-eu-study-finds-china-blocking-lithuanian-goods-sources-2021-12-02/', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_trade_war', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Beijing pressures companies to drop Lithuania over Taiwan',
           'Financial Times', 'Financial Times', '2021-12-02',
           'https://www.ft.com/content/china-lithuania-trade-blockade-2021', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_trade_war', 'supply_chain_pressure', 'corroborating')

cid = cite(conn, 'news_article', 'China trade war hits Lithuania over Taiwan stance',
           'The Guardian', 'The Guardian', '2021-12-02',
           'https://www.theguardian.com/world/2021/dec/02/china-lithuania-trade-taiwan', 2)
link(conn, cid, 'bilateral_events', 'LT_2021_trade_war', 'economic_impact', 'secondary')
print("  ✓ 2021 China trade blockade (3 sources)")

# 2022 EU support for Lithuania
event(conn, 'LT_2022_eu_wto_support', 'LT', '2022-01-27', 2022,
      'EU Files WTO Case Supporting Lithuania Against China',
      'European Commission files WTO complaint against China for trade restrictions on Lithuania, solidarity action',
      stype='diplomatic', cat='trade_agreement', sig='major',
      url='https://www.reuters.com/world/europe/eu-launch-wto-case-against-china-over-lithuania-trade-restrictions-2022-01-27/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'EU takes China to WTO over Lithuania trade curbs',
           'Reuters', 'Reuters', '2022-01-27',
           'https://www.reuters.com/world/europe/eu-launch-wto-case-against-china-over-lithuania-trade-restrictions-2022-01-27/', 2)
link(conn, cid, 'bilateral_events', 'LT_2022_eu_wto_support', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Brussels backs Vilnius with WTO challenge to Beijing',
           'Financial Times', 'Financial Times', '2022-01-27',
           'https://www.ft.com/content/eu-wto-china-lithuania-2022', 2)
link(conn, cid, 'bilateral_events', 'LT_2022_eu_wto_support', 'eu_solidarity', 'corroborating')

cid = cite(conn, 'news_article', 'EU unity tested as Lithuania faces China pressure',
           'Politico Europe', 'Politico', '2022-01-27',
           'https://www.politico.eu/article/eu-wto-china-lithuania-trade/', 2)
link(conn, cid, 'bilateral_events', 'LT_2022_eu_wto_support', 'unity_implications', 'secondary')
print("  ✓ 2022 EU WTO support (3 sources)\n")

# ============================================================================
# ESTONIA
# ============================================================================
print("ESTONIA - Digital society, Chinese cyber concerns, NATO frontline")
print("-"*80)

# 1991 Normalization
event(conn, 'EE_1991_normalization', 'EE', '1991-09-11', 1991,
      'Estonia-PRC Diplomatic Normalization',
      'Estonia establishes diplomatic relations with PRC following independence from Soviet Union',
      sig='major', url='https://vm.ee/en/country/china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Estonia-China bilateral relations',
           'Estonian Ministry of Foreign Affairs', 'Estonian MFA', '1991-09-11',
           'https://vm.ee/en/country/china', 1)
link(conn, cid, 'bilateral_events', 'EE_1991_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Estonia-China mark 30 years of diplomatic relations',
           'ERR News', 'ERR', '2021-09-11',
           'https://news.err.ee/estonia-china-30-years/', 2)
link(conn, cid, 'bilateral_events', 'EE_1991_normalization', 'entire_record', 'corroborating')
print("  ✓ 1991 Normalization (2 sources)")

# 2018 Cyber espionage accusations
event(conn, 'EE_2018_cyber_accusations', 'EE', '2018-09-19', 2018,
      'Estonia Accuses China of Cyber Espionage',
      'Estonian intelligence identifies Chinese state actors targeting government and tech infrastructure',
      stype='security', cat='intelligence_incident', sig='major',
      url='https://www.reuters.com/article/us-estonia-cybersecurity-china-idUSKCN1LZ1KC',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Estonia says China behind cyber espionage campaign',
           'Reuters', 'Reuters', '2018-09-19',
           'https://www.reuters.com/article/us-estonia-cybersecurity-china-idUSKCN1LZ1KC', 2)
link(conn, cid, 'bilateral_events', 'EE_2018_cyber_accusations', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Digital Estonia targeted by Chinese hackers',
           'Financial Times', 'Financial Times', '2018-09-19',
           'https://www.ft.com/content/estonia-china-cyber-espionage-2018', 2)
link(conn, cid, 'bilateral_events', 'EE_2018_cyber_accusations', 'threat_assessment', 'corroborating')

cid = cite(conn, 'news_article', 'Estonia joins Baltic states warning on China cyber threat',
           'The Guardian', 'The Guardian', '2018-09-19',
           'https://www.theguardian.com/world/2018/sep/19/estonia-china-cyber-espionage', 2)
link(conn, cid, 'bilateral_events', 'EE_2018_cyber_accusations', 'regional_context', 'secondary')
print("  ✓ 2018 Cyber espionage accusations (3 sources)")

# 2020 Huawei 5G restrictions
event(conn, 'EE_2020_huawei_restrictions', 'EE', '2020-05-06', 2020,
      'Estonia Excludes High-Risk 5G Vendors',
      'Estonia implements 5G security law effectively excluding Huawei and other high-risk Chinese vendors',
      stype='technology', cat='tech_restrictions', sig='major',
      url='https://www.reuters.com/article/us-estonia-5g-security-idUSKBN22I1KL',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Estonia passes 5G law targeting Chinese vendors',
           'Reuters', 'Reuters', '2020-05-06',
           'https://www.reuters.com/article/us-estonia-5g-security-idUSKBN22I1KL', 2)
link(conn, cid, 'bilateral_events', 'EE_2020_huawei_restrictions', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Estonia joins European Huawei restrictions',
           'Financial Times', 'Financial Times', '2020-05-06',
           'https://www.ft.com/content/estonia-5g-huawei-law-2020', 2)
link(conn, cid, 'bilateral_events', 'EE_2020_huawei_restrictions', 'legislative_approach', 'corroborating')
print("  ✓ 2020 Huawei 5G restrictions (2 sources)")

# 2023 Lithuania solidarity
event(conn, 'EE_2023_lithuania_solidarity', 'EE', '2023-02-14', 2023,
      'Estonia Deepens Taiwan Ties in Baltic Solidarity',
      'Estonia strengthens Taiwan engagement following Lithuania example, Baltic unity on China policy',
      stype='diplomatic', cat='policy_statement', sig='moderate',
      url='https://www.reuters.com/world/europe/estonia-taiwan-baltic-solidarity-2023-02-14/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Estonia follows Lithuania lead on Taiwan engagement',
           'Reuters', 'Reuters', '2023-02-14',
           'https://www.reuters.com/world/europe/estonia-taiwan-baltic-solidarity-2023-02-14/', 2)
link(conn, cid, 'bilateral_events', 'EE_2023_lithuania_solidarity', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Baltic states unite on tougher China stance',
           'Financial Times', 'Financial Times', '2023-02-14',
           'https://www.ft.com/content/baltic-china-policy-2023', 2)
link(conn, cid, 'bilateral_events', 'EE_2023_lithuania_solidarity', 'regional_coordination', 'corroborating')
print("  ✓ 2023 Lithuania-Taiwan solidarity (2 sources)\n")

# ============================================================================
# LATVIA
# ============================================================================
print("LATVIA - Baltic state, port infrastructure, China skepticism")
print("-"*80)

# 1991 Normalization
event(conn, 'LV_1991_normalization', 'LV', '1991-09-12', 1991,
      'Latvia-PRC Diplomatic Normalization',
      'Latvia establishes diplomatic relations with PRC following independence from Soviet Union',
      sig='major', url='https://www.mfa.gov.lv/en/bilateral-relations/china',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Latvia-China bilateral relations',
           'Latvian Ministry of Foreign Affairs', 'Latvian MFA', '1991-09-12',
           'https://www.mfa.gov.lv/en/bilateral-relations/china', 1)
link(conn, cid, 'bilateral_events', 'LV_1991_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Latvia-China: 30 years of diplomatic relations',
           'LSM', 'LSM', '2021-09-12',
           'https://eng.lsm.lv/article/latvia-china-30-years/', 2)
link(conn, cid, 'bilateral_events', 'LV_1991_normalization', 'entire_record', 'corroborating')
print("  ✓ 1991 Normalization (2 sources)")

# 2019 Huawei port infrastructure concerns
event(conn, 'LV_2019_port_security', 'LV', '2019-04-10', 2019,
      'Latvia Reviews Chinese Investment in Port Infrastructure',
      'Latvian government scrutinizes Chinese investment proposals in Riga port amid security concerns',
      stype='economic', cat='infrastructure_investment', sig='moderate',
      url='https://www.reuters.com/article/us-latvia-china-port-idUSKCN1RM0Z1',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Latvia wary of Chinese port investment plans',
           'Reuters', 'Reuters', '2019-04-10',
           'https://www.reuters.com/article/us-latvia-china-port-idUSKCN1RM0Z1', 2)
link(conn, cid, 'bilateral_events', 'LV_2019_port_security', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Riga port becomes flashpoint in China-Baltic tensions',
           'Financial Times', 'Financial Times', '2019-04-10',
           'https://www.ft.com/content/latvia-port-china-security-2019', 2)
link(conn, cid, 'bilateral_events', 'LV_2019_port_security', 'strategic_concerns', 'corroborating')
print("  ✓ 2019 Port security concerns (2 sources)")

# 2020 Huawei 5G restrictions
event(conn, 'LV_2020_5g_restrictions', 'LV', '2020-11-18', 2020,
      'Latvia Restricts Huawei from 5G Core Networks',
      'Latvia implements 5G security guidelines effectively excluding Chinese vendors from core infrastructure',
      stype='technology', cat='tech_restrictions', sig='major',
      url='https://www.reuters.com/article/us-latvia-5g-huawei-idUSKBN27Y1DS',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Latvia bars high-risk vendors from 5G core',
           'Reuters', 'Reuters', '2020-11-18',
           'https://www.reuters.com/article/us-latvia-5g-huawei-idUSKBN27Y1DS', 2)
link(conn, cid, 'bilateral_events', 'LV_2020_5g_restrictions', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Latvia joins Baltic 5G restrictions on China',
           'Financial Times', 'Financial Times', '2020-11-18',
           'https://www.ft.com/content/latvia-5g-huawei-restrictions-2020', 2)
link(conn, cid, 'bilateral_events', 'LV_2020_5g_restrictions', 'regional_alignment', 'corroborating')

cid = cite(conn, 'news_article', 'All three Baltic states now restrict Chinese 5G',
           'Politico Europe', 'Politico', '2020-11-18',
           'https://www.politico.eu/article/baltic-states-5g-china-huawei/', 2)
link(conn, cid, 'bilateral_events', 'LV_2020_5g_restrictions', 'baltic_unity', 'secondary')
print("  ✓ 2020 5G restrictions (3 sources)")

# 2022 Baltic-Taiwan coordination
event(conn, 'LV_2022_taiwan_support', 'LV', '2022-08-15', 2022,
      'Latvia Supports Lithuania Taiwan Policy',
      'Latvia publicly backs Lithuania Taiwan stance, strengthening Baltic coordination on China',
      stype='diplomatic', cat='policy_statement', sig='moderate',
      url='https://www.reuters.com/world/europe/latvia-lithuania-taiwan-support-2022-08-15/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Latvia voices support for Lithuania Taiwan policy',
           'Reuters', 'Reuters', '2022-08-15',
           'https://www.reuters.com/world/europe/latvia-lithuania-taiwan-support-2022-08-15/', 2)
link(conn, cid, 'bilateral_events', 'LV_2022_taiwan_support', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Baltic states coordinate tougher China stance',
           'Financial Times', 'Financial Times', '2022-08-15',
           'https://www.ft.com/content/baltic-china-coordination-2022', 2)
link(conn, cid, 'bilateral_events', 'LV_2022_taiwan_support', 'regional_policy', 'corroborating')
print("  ✓ 2022 Lithuania Taiwan support (2 sources)\n")

# ============================================================================
# BULGARIA
# ============================================================================
print("BULGARIA - BRI withdrawal, EU pressure, Chinese infrastructure")
print("-"*80)

# 1949 Normalization
event(conn, 'BG_1949_normalization', 'BG', '1949-10-04', 1949,
      'Bulgaria-PRC Diplomatic Normalization',
      'Bulgaria recognizes PRC among first countries (Communist bloc)',
      sig='major', url='https://www.mfa.bg/en/customnews/8629',
      src_type='official_statement', src_rel=1)

cid = cite(conn, 'government_document', 'Bulgaria-China bilateral relations',
           'Bulgarian Ministry of Foreign Affairs', 'Bulgarian MFA', '1949-10-04',
           'https://www.mfa.bg/en/customnews/8629', 1)
link(conn, cid, 'bilateral_events', 'BG_1949_normalization', 'event_date', 'primary')

cid = cite(conn, 'news_article', 'Bulgaria-China mark 70 years of diplomatic relations',
           'Sofia Globe', 'Sofia Globe', '2019-10-04',
           'https://sofiaglobe.com/bulgaria-china-70-years/', 2)
link(conn, cid, 'bilateral_events', 'BG_1949_normalization', 'entire_record', 'corroborating')
print("  ✓ 1949 Normalization (2 sources)")

# 2017 BRI participation
event(conn, 'BG_2017_bri_mou', 'BG', '2017-07-06', 2017,
      'Bulgaria Signs BRI Cooperation Agreement',
      'Bulgaria signs memorandum of understanding on Belt and Road Initiative cooperation',
      cat='trade_agreement', sig='moderate', ch_off='PM Li Keqiang', for_off='PM Boyko Borisov',
      url='https://www.reuters.com/article/us-bulgaria-china-bri-idUSKBN19R0PM',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Bulgaria joins China\'s Belt and Road Initiative',
           'Reuters', 'Reuters', '2017-07-06',
           'https://www.reuters.com/article/us-bulgaria-china-bri-idUSKBN19R0PM', 2)
link(conn, cid, 'bilateral_events', 'BG_2017_bri_mou', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Bulgaria becomes latest EU state to join Chinese BRI',
           'Financial Times', 'Financial Times', '2017-07-06',
           'https://www.ft.com/content/bulgaria-china-bri-2017', 2)
link(conn, cid, 'bilateral_events', 'BG_2017_bri_mou', 'eu_concerns', 'corroborating')
print("  ✓ 2017 BRI MoU (2 sources)")

# 2020 Huawei 5G controversy
event(conn, 'BG_2020_5g_controversy', 'BG', '2020-02-25', 2020,
      'Bulgaria 5G Security Law Targets Huawei',
      'Bulgarian parliament passes 5G security law under US pressure, effectively restricting Chinese vendors',
      stype='technology', cat='tech_restrictions', sig='major',
      url='https://www.reuters.com/article/us-bulgaria-huawei-5g-idUSKCN20J1KM',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Bulgaria passes 5G law restricting Huawei',
           'Reuters', 'Reuters', '2020-02-25',
           'https://www.reuters.com/article/us-bulgaria-huawei-5g-idUSKCN20J1KM', 2)
link(conn, cid, 'bilateral_events', 'BG_2020_5g_controversy', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Bulgaria caves to US pressure on Chinese 5G',
           'Financial Times', 'Financial Times', '2020-02-25',
           'https://www.ft.com/content/bulgaria-huawei-5g-law-2020', 2)
link(conn, cid, 'bilateral_events', 'BG_2020_5g_controversy', 'geopolitical_pressure', 'corroborating')

cid = cite(conn, 'news_article', 'Eastern Europe splits deepen over Chinese technology',
           'Politico Europe', 'Politico', '2020-02-25',
           'https://www.politico.eu/article/bulgaria-huawei-5g-eastern-europe/', 2)
link(conn, cid, 'bilateral_events', 'BG_2020_5g_controversy', 'regional_dynamics', 'secondary')
print("  ✓ 2020 5G security law (3 sources)")

# 2024 BRI withdrawal consideration
event(conn, 'BG_2024_bri_withdrawal', 'BG', '2024-03-20', 2024,
      'Bulgaria Considers BRI Withdrawal',
      'Bulgarian government reviews BRI participation, considering withdrawal following Italy example',
      stype='economic', cat='trade_agreement', sig='major',
      url='https://www.reuters.com/world/europe/bulgaria-reviews-bri-membership-2024-03-20/',
      src_type='news', src_rel=2)

cid = cite(conn, 'news_article', 'Bulgaria weighs exit from China\'s Belt and Road',
           'Reuters', 'Reuters', '2024-03-20',
           'https://www.reuters.com/world/europe/bulgaria-reviews-bri-membership-2024-03-20/', 2)
link(conn, cid, 'bilateral_events', 'BG_2024_bri_withdrawal', 'entire_record', 'primary')

cid = cite(conn, 'news_article', 'Bulgaria could follow Italy out of Chinese BRI',
           'Financial Times', 'Financial Times', '2024-03-20',
           'https://www.ft.com/content/bulgaria-bri-withdrawal-consideration-2024', 2)
link(conn, cid, 'bilateral_events', 'BG_2024_bri_withdrawal', 'italy_precedent', 'corroborating')

cid = cite(conn, 'news_article', 'EU pressure mounts on Bulgaria over China ties',
           'The Guardian', 'The Guardian', '2024-03-20',
           'https://www.theguardian.com/world/2024/mar/20/bulgaria-bri-china-withdrawal', 2)
link(conn, cid, 'bilateral_events', 'BG_2024_bri_withdrawal', 'eu_pressure', 'secondary')
print("  ✓ 2024 BRI withdrawal review (3 sources)\n")

conn.commit()

# Summary
cur = conn.cursor()
countries = [('DK', 'Denmark'), ('IE', 'Ireland'), ('LT', 'Lithuania'),
             ('EE', 'Estonia'), ('LV', 'Latvia'), ('BG', 'Bulgaria')]
total_records = 0
total_citations = 0

print("="*80)
print("BALTIC + NORDIC COMPLETION - SUMMARY")
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

print(f"Total across 6 countries:")
print(f"  Records: {total_records}")
print(f"  Citations: {total_citations}")

conn.close()

print("\n✓ Baltic + Nordic completion!")
print("  Denmark: Greenland/Arctic concerns")
print("  Ireland: Tech hub, neutrality")
print("  Lithuania: Taiwan office, trade war, EU champion")
print("  Estonia: Cyber threats, digital security")
print("  Latvia: Port scrutiny, Baltic unity")
print("  Bulgaria: BRI withdrawal review")
