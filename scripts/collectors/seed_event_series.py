"""
Seed Event Series Database
===========================
Populates the event_series table with top 50 strategic technology conferences
for EU-China technology intelligence tracking.

Based on: docs/TECHNOLOGY_EVENTS_COLLECTION_PLAN.md
"""

import sqlite3
from datetime import datetime

# Top 50 Strategic Events (TIER 1 priority for intelligence collection)
EVENT_SERIES = [
    # === AEROSPACE & SPACE (Highest dual-use risk) ===
    {
        'series_name': 'Paris Air Show',
        'organizer': 'SIAE (Salon International de l\'Aéronautique et de l\'Espace)',
        'typical_location': 'Le Bourget, France',
        'frequency': 'Biennial',
        'typical_month': 'June',
        'technology_domains': 'Aerospace, Defense, Space',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.siae.fr/',
        'intelligence_rationale': 'Top global aerospace expo - Chinese military-civil fusion companies, COMAC presence'
    },
    {
        'series_name': 'Farnborough International Airshow',
        'organizer': 'Farnborough International',
        'typical_location': 'Farnborough, UK',
        'frequency': 'Biennial',
        'typical_month': 'July',
        'technology_domains': 'Aerospace, Defense',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.farnboroughairshow.com/',
        'intelligence_rationale': 'Major defense/aerospace expo - track Chinese defense contractors'
    },
    {
        'series_name': 'ILA Berlin Air Show',
        'organizer': 'Messe Berlin',
        'typical_location': 'Berlin, Germany',
        'frequency': 'Biennial',
        'typical_month': 'May',
        'technology_domains': 'Aerospace, Defense, Space',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.ila-berlin.de/',
        'intelligence_rationale': 'Key European aerospace event - EU-China aerospace partnerships'
    },
    {
        'series_name': 'SpaceTech Expo Europe',
        'organizer': 'Terrapinn',
        'typical_location': 'Bremen, Germany',
        'frequency': 'Annual',
        'typical_month': 'November',
        'technology_domains': 'Space, Aerospace',
        'strategic_priority': 'HIGH',
        'website': 'https://www.spacetechexpo-europe.com/',
        'intelligence_rationale': 'Commercial space focus - Chinese NewSpace companies'
    },
    {
        'series_name': 'IAC (International Astronautical Congress)',
        'organizer': 'IAF (International Astronautical Federation)',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'October',
        'technology_domains': 'Space, Aerospace',
        'strategic_priority': 'HIGH',
        'website': 'https://www.iafastro.org/events/iac/',
        'intelligence_rationale': 'Global space congress - Chinese space agency participation'
    },

    # === DEFENSE & SECURITY (Restricted access) ===
    {
        'series_name': 'DSEI (Defence & Security Equipment International)',
        'organizer': 'Clarion Events',
        'typical_location': 'London, UK',
        'frequency': 'Biennial',
        'typical_month': 'September',
        'technology_domains': 'Defense, Cybersecurity',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.dsei.co.uk/',
        'intelligence_rationale': 'Top defense expo - monitor Chinese military-industrial complex participation'
    },
    {
        'series_name': 'Eurosatory',
        'organizer': 'COGES Events',
        'typical_location': 'Paris, France',
        'frequency': 'Biennial',
        'typical_month': 'June',
        'technology_domains': 'Defense, Military Technology',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.eurosatory.com/',
        'intelligence_rationale': 'Land/air defense systems - track Chinese defense exports to Europe'
    },
    {
        'series_name': 'Milipol Paris',
        'organizer': 'Comexposium',
        'typical_location': 'Paris, France',
        'frequency': 'Biennial',
        'typical_month': 'November',
        'technology_domains': 'Security, Surveillance, Cybersecurity',
        'strategic_priority': 'HIGH',
        'website': 'https://www.milipol.com/',
        'intelligence_rationale': 'Internal security - Chinese surveillance tech in Europe'
    },

    # === SEMICONDUCTORS (Export control focus) ===
    {
        'series_name': 'SEMICON Europa',
        'organizer': 'SEMI',
        'typical_location': 'Munich, Germany',
        'frequency': 'Annual',
        'typical_month': 'November',
        'technology_domains': 'Semiconductors, Microelectronics',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.semiconeuropa.org/',
        'intelligence_rationale': 'Key EU semiconductor event - Chinese chipmakers post-export controls'
    },
    {
        'series_name': 'Electronica',
        'organizer': 'Messe München',
        'typical_location': 'Munich, Germany',
        'frequency': 'Biennial',
        'typical_month': 'November',
        'technology_domains': 'Electronics, Semiconductors',
        'strategic_priority': 'HIGH',
        'website': 'https://electronica.de/',
        'intelligence_rationale': 'Electronics expo - Chinese component manufacturers in EU market'
    },
    {
        'series_name': 'IEDM (International Electron Devices Meeting)',
        'organizer': 'IEEE',
        'typical_location': 'San Francisco, USA',
        'frequency': 'Annual',
        'typical_month': 'December',
        'technology_domains': 'Semiconductors, Nanotechnology',
        'strategic_priority': 'HIGH',
        'website': 'https://www.ieee-iedm.org/',
        'intelligence_rationale': 'Top semiconductor research - Chinese university/SMIC papers'
    },

    # === TELECOMMUNICATIONS (5G/6G standards) ===
    {
        'series_name': 'Mobile World Congress Barcelona',
        'organizer': 'GSMA',
        'typical_location': 'Barcelona, Spain',
        'frequency': 'Annual',
        'typical_month': 'February',
        'technology_domains': 'Telecommunications, 5G/6G',
        'strategic_priority': 'CRITICAL',
        'website': 'https://www.mwcbarcelona.com/',
        'intelligence_rationale': 'Largest telecom event - Huawei/ZTE EU market strategy'
    },
    {
        'series_name': '5G World Summit Europe',
        'organizer': 'Informa Tech',
        'typical_location': 'London, UK',
        'frequency': 'Annual',
        'typical_month': 'June',
        'technology_domains': 'Telecommunications, 5G',
        'strategic_priority': 'HIGH',
        'website': 'https://www.5gworldevents.com/',
        'intelligence_rationale': '5G deployment focus - Chinese equipment vendor participation'
    },
    {
        'series_name': 'EuCNC & 6G Summit',
        'organizer': 'European Commission / EU',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'June',
        'technology_domains': 'Telecommunications, 6G Research',
        'strategic_priority': 'HIGH',
        'website': 'https://www.eucnc.eu/',
        'intelligence_rationale': 'EU 6G standards development - Chinese research participation'
    },

    # === ARTIFICIAL INTELLIGENCE ===
    {
        'series_name': 'NeurIPS',
        'organizer': 'Neural Information Processing Systems Foundation',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'December',
        'technology_domains': 'Artificial Intelligence, Machine Learning',
        'strategic_priority': 'HIGH',
        'website': 'https://neurips.cc/',
        'intelligence_rationale': 'Top AI research conference - Chinese AI labs (Alibaba, Tencent, ByteDance)'
    },
    {
        'series_name': 'ICML (International Conference on Machine Learning)',
        'organizer': 'ICML Foundation',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'July',
        'technology_domains': 'Artificial Intelligence, Machine Learning',
        'strategic_priority': 'HIGH',
        'website': 'https://icml.cc/',
        'intelligence_rationale': 'Premier ML conference - Chinese university research output'
    },
    {
        'series_name': 'CVPR (Computer Vision and Pattern Recognition)',
        'organizer': 'IEEE / CVF',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'June',
        'technology_domains': 'Artificial Intelligence, Computer Vision',
        'strategic_priority': 'HIGH',
        'website': 'https://cvpr.thecvf.com/',
        'intelligence_rationale': 'Computer vision focus - Chinese facial recognition companies'
    },
    {
        'series_name': 'AI Summit London',
        'organizer': 'TechEx Events',
        'typical_location': 'London, UK',
        'frequency': 'Annual',
        'typical_month': 'June',
        'technology_domains': 'Artificial Intelligence',
        'strategic_priority': 'MEDIUM',
        'website': 'https://theaisummit.com/',
        'intelligence_rationale': 'Commercial AI focus - Chinese AI companies in EU market'
    },
    {
        'series_name': 'ECCV (European Conference on Computer Vision)',
        'organizer': 'ECCV Foundation',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Biennial',
        'typical_month': 'October',
        'technology_domains': 'Artificial Intelligence, Computer Vision',
        'strategic_priority': 'MEDIUM',
        'website': 'https://eccv.eu/',
        'intelligence_rationale': 'European CV research - Chinese research collaborations'
    },

    # === QUANTUM COMPUTING ===
    {
        'series_name': 'Q2B (Quantum for Business)',
        'organizer': 'QC Ware',
        'typical_location': 'Rotating EU/US',
        'frequency': 'Annual',
        'typical_month': 'December',
        'technology_domains': 'Quantum Computing',
        'strategic_priority': 'CRITICAL',
        'website': 'https://q2b.qcware.com/',
        'intelligence_rationale': 'Commercial quantum focus - Chinese quantum companies'
    },
    {
        'series_name': 'IEEE Quantum Week',
        'organizer': 'IEEE',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'September',
        'technology_domains': 'Quantum Computing, Quantum Communications',
        'strategic_priority': 'CRITICAL',
        'website': 'https://qce.quantum.ieee.org/',
        'intelligence_rationale': 'Quantum engineering - Chinese quantum labs (USTC, Tsinghua)'
    },
    {
        'series_name': 'Quantum.Tech Europe',
        'organizer': 'Alpha Events',
        'typical_location': 'Amsterdam / London',
        'frequency': 'Annual',
        'typical_month': 'May',
        'technology_domains': 'Quantum Computing',
        'strategic_priority': 'HIGH',
        'website': 'https://www.quantumtechdigital.co.uk/',
        'intelligence_rationale': 'European quantum industry - Chinese quantum startups in EU'
    },

    # === CYBERSECURITY ===
    {
        'series_name': 'RSA Conference Europe',
        'organizer': 'RSA Security',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'November',
        'technology_domains': 'Cybersecurity',
        'strategic_priority': 'HIGH',
        'website': 'https://www.rsaconference.com/europe',
        'intelligence_rationale': 'Cybersecurity industry - Chinese security vendors'
    },
    {
        'series_name': 'Black Hat Europe',
        'organizer': 'Informa Tech',
        'typical_location': 'London, UK',
        'frequency': 'Annual',
        'typical_month': 'December',
        'technology_domains': 'Cybersecurity, Offensive Security',
        'strategic_priority': 'HIGH',
        'website': 'https://www.blackhat.com/eu/',
        'intelligence_rationale': 'Offensive security research - Chinese security researchers'
    },
    {
        'series_name': 'NATO CyCon (Cyber Conflict Conference)',
        'organizer': 'NATO CCDCOE',
        'typical_location': 'Tallinn, Estonia',
        'frequency': 'Annual',
        'typical_month': 'May',
        'technology_domains': 'Cybersecurity, Cyber Warfare',
        'strategic_priority': 'MEDIUM',
        'website': 'https://ccdcoe.org/cycon/',
        'intelligence_rationale': 'Cyber defense focus - minimal Chinese participation (policy interest)'
    },

    # === BIOTECHNOLOGY ===
    {
        'series_name': 'BIO-Europe',
        'organizer': 'EBD Group',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'November',
        'technology_domains': 'Biotechnology, Pharmaceuticals',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.ebdgroup.com/bio-europe/',
        'intelligence_rationale': 'European biotech partnerships - Chinese pharma companies'
    },
    {
        'series_name': 'ESMO (European Society for Medical Oncology)',
        'organizer': 'ESMO',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'September',
        'technology_domains': 'Biotechnology, Oncology',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.esmo.org/',
        'intelligence_rationale': 'Cancer research - Chinese biotech collaborations'
    },

    # === ADVANCED MATERIALS ===
    {
        'series_name': 'Materials Science & Technology (MS&T)',
        'organizer': 'ACerS / AIST / TMS',
        'typical_location': 'USA (some EU editions)',
        'frequency': 'Annual',
        'typical_month': 'October',
        'technology_domains': 'Advanced Materials, Nanotechnology',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.matscitech.org/',
        'intelligence_rationale': 'Materials research - Chinese graphene/nanomaterials companies'
    },
    {
        'series_name': 'European Materials Research Society (E-MRS)',
        'organizer': 'E-MRS',
        'typical_location': 'Strasbourg / Warsaw',
        'frequency': 'Biannual (Spring/Fall)',
        'typical_month': 'May / September',
        'technology_domains': 'Advanced Materials',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.european-mrs.com/',
        'intelligence_rationale': 'EU materials science - Chinese research collaborations'
    },

    # === ENERGY & CLEAN TECH ===
    {
        'series_name': 'EU PVSEC (Photovoltaic Solar Energy Conference)',
        'organizer': 'WIP',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'September',
        'technology_domains': 'Solar Energy, Renewable Energy',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.photovoltaic-conference.com/',
        'intelligence_rationale': 'Solar technology - Chinese solar panel manufacturers in EU'
    },
    {
        'series_name': 'WindEurope Conference',
        'organizer': 'WindEurope',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'April',
        'technology_domains': 'Wind Energy, Renewable Energy',
        'strategic_priority': 'MEDIUM',
        'website': 'https://windeurope.org/conferences/',
        'intelligence_rationale': 'Wind energy - Chinese turbine manufacturers'
    },
    {
        'series_name': 'European Energy Storage Conference',
        'organizer': 'EASE',
        'typical_location': 'Rotating EU cities',
        'frequency': 'Annual',
        'typical_month': 'March',
        'technology_domains': 'Energy Storage, Battery Technology',
        'strategic_priority': 'HIGH',
        'website': 'https://ease-storage.eu/',
        'intelligence_rationale': 'Battery tech - Chinese battery giants (CATL, BYD) in EU market'
    },

    # === ROBOTICS & AUTOMATION ===
    {
        'series_name': 'ICRA (International Conference on Robotics and Automation)',
        'organizer': 'IEEE',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'May',
        'technology_domains': 'Robotics, Automation',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.ieee-ras.org/conferences-workshops/fully-sponsored/icra',
        'intelligence_rationale': 'Robotics research - Chinese robotics companies'
    },
    {
        'series_name': 'IROS (International Conference on Intelligent Robots and Systems)',
        'organizer': 'IEEE',
        'typical_location': 'Rotating global',
        'frequency': 'Annual',
        'typical_month': 'October',
        'technology_domains': 'Robotics, AI',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.ieee-ras.org/conferences-workshops/fully-sponsored/iros',
        'intelligence_rationale': 'Intelligent systems - Chinese autonomous systems research'
    },
    {
        'series_name': 'Automatica',
        'organizer': 'Messe München',
        'typical_location': 'Munich, Germany',
        'frequency': 'Biennial',
        'typical_month': 'June',
        'technology_domains': 'Robotics, Industrial Automation',
        'strategic_priority': 'MEDIUM',
        'website': 'https://automatica-munich.com/',
        'intelligence_rationale': 'Industrial robotics - Chinese automation companies'
    },

    # === NUCLEAR TECHNOLOGY (Dual-use) ===
    {
        'series_name': 'IAEA General Conference',
        'organizer': 'IAEA',
        'typical_location': 'Vienna, Austria',
        'frequency': 'Annual',
        'typical_month': 'September',
        'technology_domains': 'Nuclear Technology',
        'strategic_priority': 'HIGH',
        'website': 'https://www.iaea.org/about/governance/general-conference',
        'intelligence_rationale': 'Nuclear policy - Chinese nuclear cooperation with EU'
    },

    # === GENERAL TECHNOLOGY / INNOVATION ===
    {
        'series_name': 'Web Summit',
        'organizer': 'Web Summit',
        'typical_location': 'Lisbon, Portugal',
        'frequency': 'Annual',
        'typical_month': 'November',
        'technology_domains': 'Technology (General), Startups',
        'strategic_priority': 'LOW',
        'website': 'https://websummit.com/',
        'intelligence_rationale': 'Tech industry overview - Chinese tech companies in EU'
    },
    {
        'series_name': 'VivaTech',
        'organizer': 'Publicis / Les Echos',
        'typical_location': 'Paris, France',
        'frequency': 'Annual',
        'typical_month': 'June',
        'technology_domains': 'Technology (General), Innovation',
        'strategic_priority': 'LOW',
        'website': 'https://vivatechnology.com/',
        'intelligence_rationale': 'European tech innovation - Chinese startup ecosystem'
    },

    # === ADDED: Top European Industry Events ===
    {
        'series_name': 'Hannover Messe',
        'organizer': 'Deutsche Messe',
        'typical_location': 'Hannover, Germany',
        'frequency': 'Annual',
        'typical_month': 'April',
        'technology_domains': 'Industrial Technology, Manufacturing, Energy',
        'strategic_priority': 'HIGH',
        'website': 'https://www.hannovermesse.de/',
        'intelligence_rationale': 'Largest industrial trade fair - Chinese manufacturers in EU market'
    },
    {
        'series_name': 'CES (Consumer Electronics Show)',
        'organizer': 'CTA',
        'typical_location': 'Las Vegas, USA',
        'frequency': 'Annual',
        'typical_month': 'January',
        'technology_domains': 'Consumer Electronics, AI, Automotive',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.ces.tech/',
        'intelligence_rationale': 'Consumer tech - Chinese electronics brands (Xiaomi, Huawei, DJI)'
    },
    {
        'series_name': 'IFA Berlin',
        'organizer': 'Messe Berlin',
        'typical_location': 'Berlin, Germany',
        'frequency': 'Annual',
        'typical_month': 'September',
        'technology_domains': 'Consumer Electronics',
        'strategic_priority': 'MEDIUM',
        'website': 'https://www.ifa-berlin.com/',
        'intelligence_rationale': 'European consumer electronics - Chinese brands market penetration'
    },
]


def seed_event_series(db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
    """Populate event_series table with top 50 strategic conferences"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("SEEDING EVENT SERIES DATABASE")
    print("=" * 70)
    print(f"Target database: {db_path}")
    print(f"Event series to insert: {len(EVENT_SERIES)}")
    print()

    inserted = 0
    skipped = 0

    # Priority to tier mapping
    priority_to_tier = {
        'CRITICAL': 1,
        'HIGH': 2,
        'MEDIUM': 3,
        'LOW': 4
    }

    for event in EVENT_SERIES:
        # Check if already exists
        existing = cursor.execute(
            "SELECT series_id FROM event_series WHERE series_name = ?",
            (event['series_name'],)
        ).fetchone()

        if existing:
            print(f"[SKIP] {event['series_name']} - already exists")
            skipped += 1
            continue

        # Generate series_id from name
        series_id = event['series_name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')[:50]

        # Get primary technology domain (first one listed)
        tech_domain = event['technology_domains'].split(',')[0].strip()

        # Convert priority to tier
        tier = priority_to_tier.get(event['strategic_priority'], 3)

        # Insert new event series
        cursor.execute("""
            INSERT INTO event_series (
                series_id, series_name, organizer, typical_location, frequency,
                typical_month, technology_domain, importance_tier,
                strategic_rationale, monitoring_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            event['series_name'],
            event['organizer'],
            event['typical_location'],
            event['frequency'],
            event['typical_month'],
            tech_domain,
            tier,
            event['intelligence_rationale'],
            'active',
            datetime.utcnow().isoformat()
        ))

        print(f"[INSERT] {event['series_name']} (Tier {tier})")
        inserted += 1

    conn.commit()

    print()
    print("=" * 70)
    print(f"SEEDING COMPLETE")
    print("=" * 70)
    print(f"Inserted: {inserted}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Total in database: {inserted + skipped}")
    print()

    # Show summary by tier
    cursor.execute("""
        SELECT importance_tier, COUNT(*)
        FROM event_series
        GROUP BY importance_tier
        ORDER BY importance_tier
    """)

    print("Event Series by Importance Tier:")
    print("-" * 70)
    tier_names = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}
    for tier, count in cursor.fetchall():
        print(f"  Tier {tier} ({tier_names.get(tier, 'UNKNOWN'):.<15}) {count:>5} series")

    conn.close()


if __name__ == '__main__':
    seed_event_series()
