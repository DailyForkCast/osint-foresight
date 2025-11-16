#!/usr/bin/env python3
"""
Extract comprehensive World Bank indicators for China
All technology, trade, and economic indicators
"""

from google.cloud import bigquery
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def extract_world_bank_comprehensive():
    """
    Extract all relevant World Bank indicators for China
    """
    print("="*80)
    print("WORLD BANK - COMPREHENSIVE INDICATOR EXTRACTION")
    print("="*80)

    client = bigquery.Client()
    output_dir = Path("data/bigquery_comprehensive")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Comprehensive indicator list
    indicators = {
        # Technology & Innovation
        'GB.XPD.RSDV.GD.ZS': 'R&D expenditure (% of GDP)',
        'GB.XPD.RSDV.CD': 'R&D expenditure (current US$)',
        'IP.PAT.RESD': 'Patent applications, residents',
        'IP.PAT.NRES': 'Patent applications, nonresidents',
        'IP.JRN.ARTC.SC': 'Scientific and technical journal articles',
        'TX.VAL.TECH.CD': 'High-technology exports (current US$)',
        'TX.VAL.TECH.MF.ZS': 'High-technology exports (% of manufactured exports)',

        # Trade
        'NE.TRD.GNFS.ZS': 'Trade (% of GDP)',
        'NE.EXP.GNFS.ZS': 'Exports of goods and services (% of GDP)',
        'NE.IMP.GNFS.ZS': 'Imports of goods and services (% of GDP)',
        'TX.VAL.MRCH.CD.WT': 'Merchandise exports (current US$)',
        'TM.VAL.MRCH.CD.WT': 'Merchandise imports (current US$)',
        'TX.VAL.ICTG.ZS.UN': 'ICT goods exports (% of total goods exports)',
        'TM.VAL.ICTG.ZS.UN': 'ICT goods imports (% of total goods imports)',

        # Manufacturing & Industry
        'NV.IND.MANF.ZS': 'Manufacturing, value added (% of GDP)',
        'NV.IND.MANF.CD': 'Manufacturing, value added (current US$)',
        'TX.VAL.MANF.ZS.UN': 'Manufactures exports (% of merchandise exports)',

        # Economy
        'NY.GDP.MKTP.CD': 'GDP (current US$)',
        'NY.GDP.MKTP.KD.ZG': 'GDP growth (annual %)',
        'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
        'NE.GDI.FTOT.ZS': 'Gross fixed capital formation (% of GDP)',

        # Population & Labor
        'SP.POP.TOTL': 'Population, total',
        'SP.POP.GROW': 'Population growth (annual %)',
        'SL.TLF.TOTL.IN': 'Labor force, total',
        'SL.UEM.TOTL.ZS': 'Unemployment, total (% of labor force)',

        # Education
        'SE.TER.ENRR': 'School enrollment, tertiary (% gross)',
        'SE.XPD.TOTL.GD.ZS': 'Government expenditure on education (% of GDP)',

        # Infrastructure
        'IT.NET.USER.ZS': 'Individuals using the Internet (% of population)',
        'IT.CEL.SETS.P2': 'Mobile cellular subscriptions (per 100 people)',

        # Investment
        'BX.KLT.DINV.WD.GD.ZS': 'Foreign direct investment, net inflows (% of GDP)',
        'NE.GDI.TOTL.ZS': 'Gross capital formation (% of GDP)',
    }

    print(f"\nExtracting {len(indicators)} indicators for China...")
    print(f"Indicators include: R&D, patents, trade, GDP, manufacturing, etc.")

    # Build query
    indicator_list = list(indicators.keys())

    query = f"""
    SELECT
        country_name,
        country_code,
        indicator_name,
        indicator_code,
        year,
        value
    FROM `bigquery-public-data.world_bank_wdi.indicators_data`
    WHERE country_code = 'CHN'
        AND indicator_code IN UNNEST({indicator_list})
        AND year >= 1990
    ORDER BY indicator_code, year
    """

    print("\nQuerying World Bank data...")
    job = client.query(query)
    results = list(job.result())

    df = pd.DataFrame([{
        'country_name': r['country_name'],
        'country_code': r['country_code'],
        'indicator_name': r['indicator_name'],
        'indicator_code': r['indicator_code'],
        'year': r['year'],
        'value': r['value']
    } for r in results])

    cost = (job.total_bytes_billed / 1e12) * 5

    # Save data
    output_file = output_dir / 'world_bank_china_comprehensive.csv'
    df.to_csv(output_file, index=False)

    # Create summary
    summary = {
        'extraction_date': datetime.now().isoformat(),
        'total_records': len(df),
        'indicators_requested': len(indicators),
        'indicators_found': df['indicator_code'].nunique(),
        'year_range': f"{df['year'].min()}-{df['year'].max()}" if len(df) > 0 else "N/A",
        'cost_usd': round(cost, 4),
        'indicators': indicators
    }

    # Generate coverage report
    if len(df) > 0:
        print("\n" + "="*80)
        print("INDICATOR COVERAGE")
        print("="*80)

        for code, name in indicators.items():
            indicator_data = df[df['indicator_code'] == code]
            if len(indicator_data) > 0:
                years_str = f"{indicator_data['year'].min()}-{indicator_data['year'].max()}"
                print(f"\n  [{code}]")
                print(f"    {name}")
                print(f"    Years: {years_str} ({len(indicator_data)} records)")
            else:
                print(f"\n  [{code}]")
                print(f"    {name}")
                print(f"    NOT AVAILABLE")

    with open(output_dir / 'world_bank_extraction_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nTotal records: {len(df):,}")
    print(f"Indicators: {df['indicator_code'].nunique()}/{len(indicators)}")
    print(f"Year range: {df['year'].min()}-{df['year'].max()}")
    print(f"Cost: ${cost:.4f}")
    print(f"\nSaved to: {output_file}")
    print(f"Summary: {output_dir / 'world_bank_extraction_summary.json'}")

    return df, cost

if __name__ == "__main__":
    df, cost = extract_world_bank_comprehensive()
