#!/usr/bin/env python3
"""
SIA Global Semiconductor Market - Netherlands Context Integration

Extracts key metrics from SIA 2025 report for Netherlands v1 strategic assessment.
"""

import json
from datetime import datetime

# Load SIA industry metrics
with open('data/external/sia_industry_metrics_2025.json', 'r') as f:
    sia_data = json.load(f)

print("="*80)
print("SIA GLOBAL SEMICONDUCTOR MARKET - STRATEGIC CONTEXT")
print("="*80)
print(f"\nSource: {sia_data['metadata']['source']}")
print(f"Extracted: {sia_data['metadata']['extracted_date']}")
print(f"Zero Fabrication Compliant: {sia_data['metadata']['zero_fabrication_compliant']}")

print("\n[GLOBAL MARKET SIZE]")
print("-" * 80)
market = sia_data['market_overview']
print(f"2024 Actual:      ${market['global_sales_2024']['value']}B")
print(f"2025 Projected:   ${market['projected_sales_2025']['value']}B")
print(f"Growth Rate:      +{market['projected_sales_2025']['growth_rate']}%")

print("\n[UNITED STATES POSITION]")
print("-" * 80)
us = sia_data['us_industry_metrics']
us_share = market['us_market_share_global']['value']
print(f"Global Sales Share:  {us_share}%")
print(f"R&D Investment:      ${us['rd_spending_2024']['value']}B ({us['rd_spending_2024']['percentage_of_revenue']}% of revenue)")
print(f"Direct Employment:   {us['us_employment']['direct_jobs_2024']['value']:,} jobs (2024)")
print(f"Projected Jobs:      {us['us_employment']['projected_jobs_2032']['value']:,} by 2032")
print(f"Manufacturing:       Expected to triple capacity by 2032")

print("\n[SUPPLY CHAIN VALUE-ADDED BY REGION]")
print("-" * 80)
supply_chain = sia_data['supply_chain_value_added']['regions']
print(f"{'Region':<20} {'Design':<10} {'Mfg':<10} {'Equipment':<12} {'Materials':<12}")
print("-" * 80)
for region, data in supply_chain.items():
    region_name = region.replace('_', ' ').title()
    print(f"{region_name:<20} {data['design']:>3}%{'':<6} {data['manufacturing']:>3}%{'':<6} {data['equipment']:>3}%{'':<8} {data['materials']:>3}%")

print("\n[EUROPE'S SEMICONDUCTOR VALUE CHAIN POSITION]")
print("-" * 80)
europe = supply_chain['europe']
print(f"Equipment:       {europe['equipment']}% of global (ASML, ASMI)")
print(f"Design:          {europe['design']}% of global")
print(f"Manufacturing:   {europe['manufacturing']}% of global")
print(f"Materials:       {europe['materials']}% of global")
print("\nKey Insight: Europe punches above weight in EQUIPMENT (19% global)")
print("             via Netherlands' ASML EUV lithography monopoly")

print("\n[MARKET SEGMENTS 2024]")
print("-" * 80)
segments = sia_data['market_segments_2024']
print(f"Computing/AI:    {segments['computing_ai']['value']}% (${market['global_sales_2024']['value'] * segments['computing_ai']['value'] / 100:.1f}B)")
print(f"Communications:  {segments['communications']['value']}% (${market['global_sales_2024']['value'] * segments['communications']['value'] / 100:.1f}B)")
print(f"Automotive:      {segments['automotive']['value']}% (${market['global_sales_2024']['value'] * segments['automotive']['value'] / 100:.1f}B)")
print(f"Industrial:      {segments['industrial']['value']}% (${market['global_sales_2024']['value'] * segments['industrial']['value'] / 100:.1f}B)")
print(f"Consumer:        {segments['consumer']['value']}% (${market['global_sales_2024']['value'] * segments['consumer']['value'] / 100:.1f}B)")

# Create Netherlands context summary
netherlands_context = {
    'metadata': {
        'generated': datetime.now().isoformat(),
        'source': 'SIA State of the U.S. Semiconductor Industry 2025',
        'purpose': 'Netherlands v1 report global context',
        'zero_fabrication_compliant': True
    },
    'global_market': {
        'size_2024_billions': market['global_sales_2024']['value'],
        'size_2025_billions': market['projected_sales_2025']['value'],
        'growth_2025_percent': market['projected_sales_2025']['growth_rate']
    },
    'competitive_landscape': {
        'us_share_percent': us_share,
        'us_rd_billions': us['rd_spending_2024']['value'],
        'us_rd_intensity_percent': us['rd_spending_2024']['percentage_of_revenue']
    },
    'europe_value_chain': {
        'equipment_share': europe['equipment'],
        'design_share': europe['design'],
        'manufacturing_share': europe['manufacturing'],
        'materials_share': europe['materials'],
        'key_strength': 'Equipment (19% global via ASML EUV monopoly)'
    },
    'market_segments_2024': {
        'computing_ai': segments['computing_ai']['value'],
        'communications': segments['communications']['value'],
        'automotive': segments['automotive']['value']
    },
    'netherlands_positioning': {
        'context': 'ASML operates within $701B global semiconductor market (2025 projected)',
        'asml_role': 'Critical equipment supplier - EUV lithography monopoly',
        'europe_equipment_dominance': 'Europe controls 19% of global semiconductor equipment market',
        'asml_contribution': 'ASML is primary driver of Europes 19% equipment market share',
        'strategic_importance': 'Netherlands punches far above weight via ASMLs equipment monopoly',
        'china_relevance': 'ASML EUV export restrictions central to US-China tech competition',
        'us_china_dynamic': 'US leads design (50%), China leads manufacturing (28%), Netherlands controls critical equipment'
    },
    'key_metrics_for_report': {
        'global_market_2025': '$701B',
        'us_share': '50.4%',
        'china_manufacturing_share': '28%',
        'europe_equipment_share': '19%',
        'us_rd_investment': '$62.7B (17.7% of revenue)',
        'asml_strategic_position': 'Monopoly on EUV lithography (essential for advanced chips <7nm)'
    }
}

with open('analysis/sia_global_semiconductor_context_netherlands.json', 'w') as f:
    json.dump(netherlands_context, f, indent=2)

print("\n[NETHERLANDS STRATEGIC POSITIONING]")
print("="*80)
print("Global Market Context:")
print(f"  - Total Market: ${market['projected_sales_2025']['value']}B (2025 projected)")
print(f"  - Growing +{market['projected_sales_2025']['growth_rate']}% YoY")
print()
print("Competitive Landscape:")
print("  - US leads DESIGN: 50% global share")
print("  - China leads MANUFACTURING: 28% global share")
print("  - Netherlands controls EQUIPMENT: via ASML EUV monopoly")
print()
print("Netherlands Outsized Influence:")
print("  - Small EU member state")
print("  - Drives 19% of global semiconductor equipment market")
print("  - ASML EUV monopoly = strategic chokepoint")
print("  - Export restrictions = powerful geopolitical lever")
print()
print("US-China Tech Competition:")
print("  - US: 50.4% market share, $62.7B R&D")
print("  - China: 28% manufacturing, 8% design")
print("  - Netherlands: EUV export controls = US primary tool to limit Chinas advanced chipmaking")

print("\nContext saved to: analysis/sia_global_semiconductor_context_netherlands.json")
print("="*80)
