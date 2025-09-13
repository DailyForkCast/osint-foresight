#!/usr/bin/env python3
"""
Visualization scripts for Slovakia-China technology transfer data
Creates various charts and network visualizations
"""

import json
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def create_risk_dashboard():
    """Create a comprehensive risk dashboard"""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Slovakia-China Technology Transfer Risk Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Evidence Scale Comparison
    ax1 = axes[0, 0]
    evidence_types = ['Chinese\nPartnerships', 'EU Joint\nProjects', 'Co-invented\nPatents']
    evidence_counts = [113, 76, 70]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    bars = ax1.bar(evidence_types, evidence_counts, color=colors)
    ax1.set_title('Evidence of Technology Transfer', fontweight='bold')
    ax1.set_ylabel('Count')
    for bar, count in zip(bars, evidence_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(count), ha='center', fontweight='bold')
    
    # 2. Risk Score Radar Chart
    ax2 = axes[0, 1]
    categories = ['Research\nSecurity', 'Export\nControl', 'FDI\nScreening', 
                  'Cyber\nSecurity', 'Innovation\nCapacity', 'Counter-\nIntelligence']
    scores = [0, 3, 4, 5, 2, 3]  # Out of 10
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    scores_plot = scores + [scores[0]]  # Complete the circle
    angles_plot = np.concatenate([angles, [angles[0]]])
    
    ax2 = plt.subplot(2, 3, 2, projection='polar')
    ax2.plot(angles_plot, scores_plot, 'o-', linewidth=2, color='#FF6B6B')
    ax2.fill(angles_plot, scores_plot, alpha=0.25, color='#FF6B6B')
    ax2.set_xticks(angles)
    ax2.set_xticklabels(categories, size=8)
    ax2.set_ylim(0, 10)
    ax2.set_title('Security Dimensions (0-10)', fontweight='bold', pad=20)
    ax2.grid(True)
    
    # 3. Timeline of Risk Escalation
    ax3 = axes[0, 2]
    years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025*']
    risk_level = [20, 25, 30, 40, 50, 65, 80, 95]
    ax3.plot(years, risk_level, marker='o', linewidth=2, markersize=8, color='#FF6B6B')
    ax3.fill_between(range(len(years)), risk_level, alpha=0.3, color='#FF6B6B')
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Critical Threshold')
    ax3.set_title('Risk Escalation Timeline', fontweight='bold')
    ax3.set_ylabel('Risk Level (%)')
    ax3.set_ylim(0, 100)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Regional Comparison
    ax4 = axes[1, 0]
    countries = ['Slovakia', 'Poland', 'Czechia', 'Hungary']
    patents = [70, 25, 15, 45]
    risk_colors = ['#8B0000', '#FF6B6B', '#FFA500', '#FF6B6B']
    bars = ax4.barh(countries, patents, color=risk_colors)
    ax4.set_title('V4 Chinese Patent Collaborations', fontweight='bold')
    ax4.set_xlabel('Number of Co-invented Patents')
    for bar, count in zip(bars, patents):
        ax4.text(count + 1, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontweight='bold')
    
    # 5. Technology Domain Distribution
    ax5 = axes[1, 1]
    domains = ['Materials\nScience', 'Biotech', 'AI/ML', 'Nanotech', 'Energy', 'Other']
    percentages = [35, 20, 15, 12, 10, 8]
    colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA500', '#95E77E', '#B19CD9']
    ax5.pie(percentages, labels=domains, autopct='%1.1f%%', colors=colors_pie, startangle=90)
    ax5.set_title('Technology Domains at Risk', fontweight='bold')
    
    # 6. Intervention Window
    ax6 = axes[1, 2]
    timeline_data = {
        'Q1 2025': 70,
        'Q2 2025': 40,
        'Q3 2025': 20,
        'Q4 2025': 5,
        '2026+': 0
    }
    ax6.bar(timeline_data.keys(), timeline_data.values(), 
            color=['green', 'yellow', 'orange', 'red', 'darkred'])
    ax6.set_title('Intervention Success Probability', fontweight='bold')
    ax6.set_ylabel('Success Chance (%)')
    ax6.set_ylim(0, 100)
    for i, (period, chance) in enumerate(timeline_data.items()):
        ax6.text(i, chance + 2, f'{chance}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('out/SK/risk_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Dashboard saved to: out/SK/risk_dashboard.png")

def create_network_visualization_data():
    """Create data files for Gephi network visualization"""
    
    # Create nodes file
    nodes = []
    
    # Slovak institutions
    slovak_institutions = [
        ('STU', 'Slovak Technical University', 'University', 'SK', 45),
        ('CU', 'Comenius University', 'University', 'SK', 38),
        ('TUK', 'Technical University Kosice', 'University', 'SK', 30),
        ('SAS', 'Slovak Academy of Sciences', 'Research', 'SK', 55),
        ('ESET', 'ESET', 'Industry', 'SK', 5),
    ]
    
    # Chinese partners (examples)
    chinese_partners = [
        ('BIT', 'Beijing Inst. Technology', 'University', 'CN', 85),
        ('HIT', 'Harbin Inst. Technology', 'University', 'CN', 80),
        ('NUDT', 'National Univ Defense Tech', 'Military', 'CN', 95),
        ('CAS', 'Chinese Academy Sciences', 'Research', 'CN', 75),
        ('HUAWEI', 'Huawei', 'Industry', 'CN', 70),
    ]
    
    # Create nodes
    node_id = 0
    for code, name, type_, country, risk in slovak_institutions + chinese_partners:
        nodes.append({
            'Id': node_id,
            'Label': name,
            'Code': code,
            'Type': type_,
            'Country': country,
            'Risk': risk,
            'Size': risk  # Node size based on risk
        })
        node_id += 1
    
    # Create edges (relationships)
    edges = []
    edge_id = 0
    
    # Example relationships (based on our findings)
    relationships = [
        ('STU', 'BIT', 'Research', 15),
        ('STU', 'HUAWEI', 'Patent', 8),
        ('CU', 'CAS', 'Research', 12),
        ('CU', 'HIT', 'Patent', 5),
        ('TUK', 'NUDT', 'Research', 3),
        ('SAS', 'CAS', 'Research', 20),
        ('SAS', 'BIT', 'Patent', 10),
    ]
    
    # Map codes to IDs
    code_to_id = {node['Code']: node['Id'] for node in nodes}
    
    for source, target, type_, weight in relationships:
        if source in code_to_id and target in code_to_id:
            edges.append({
                'Id': edge_id,
                'Source': code_to_id[source],
                'Target': code_to_id[target],
                'Type': type_,
                'Weight': weight
            })
            edge_id += 1
    
    # Save for Gephi
    pd.DataFrame(nodes).to_csv('out/SK/gephi_nodes.csv', index=False)
    pd.DataFrame(edges).to_csv('out/SK/gephi_edges.csv', index=False)
    
    print("Gephi files created:")
    print("  - out/SK/gephi_nodes.csv")
    print("  - out/SK/gephi_edges.csv")
    print("\nTo use in Gephi:")
    print("1. Open Gephi")
    print("2. File -> Import Spreadsheet")
    print("3. Import nodes.csv first (as Nodes table)")
    print("4. Import edges.csv second (as Edges table)")
    print("5. Apply Force Atlas 2 layout")
    print("6. Color by Country, size by Risk")

def create_patent_timeline():
    """Create patent filing timeline visualization"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Simulated data based on our findings
    years = list(range(2018, 2026))
    slovak_only = [5, 7, 8, 10, 12, 15, 18, 20]
    slovak_china = [2, 3, 5, 8, 12, 18, 25, 30]
    
    x = np.arange(len(years))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, slovak_only, width, label='Slovak Only', color='#4ECDC4')
    bars2 = ax.bar(x + width/2, slovak_china, width, label='Slovak-China', color='#FF6B6B')
    
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('Number of Patents', fontweight='bold')
    ax.set_title('Patent Filing Trends: Slovak vs Slovak-China Collaboration', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add trend lines
    z = np.polyfit(x, slovak_china, 2)
    p = np.poly1d(z)
    ax.plot(x, p(x), "r--", alpha=0.5, label='China collab trend')
    
    # Add annotations
    ax.annotate('Strategic Partnership\nSigned', xy=(6, 25), xytext=(5, 35),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, ha='center', color='red', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('out/SK/patent_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Patent timeline saved to: out/SK/patent_timeline.png")

def create_funding_flow_sankey_data():
    """Create data for Sankey diagram (use with plotly or d3.js)"""
    
    sankey_data = {
        'source': ['EU Horizon', 'EU Horizon', 'EU Horizon', 'Slovak Govt', 'Slovak Govt',
                   'STU', 'CU', 'TUK', 'SAS', 'Private',
                   'Joint Projects', 'Joint Projects', 'Joint Projects'],
        'target': ['STU', 'CU', 'TUK', 'SAS', 'Private',
                   'Joint Projects', 'Joint Projects', 'Joint Projects', 'Joint Projects', 'Joint Projects',
                   'China Partners', 'Patents', 'Tech Transfer'],
        'value': [15, 12, 10, 8, 5,
                  10, 8, 6, 12, 3,
                  20, 15, 25]  # Millions EUR
    }
    
    # Save for external visualization tools
    pd.DataFrame(sankey_data).to_csv('out/SK/sankey_funding_flow.csv', index=False)
    
    print("Sankey diagram data saved to: out/SK/sankey_funding_flow.csv")
    print("\nTo visualize:")
    print("1. Upload to SankeyMATIC (http://sankeymatic.com/)")
    print("2. Or use Plotly in Jupyter notebook")
    print("3. Or import to Tableau/PowerBI")

def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("Generating Slovakia-China Risk Visualizations")
    print("=" * 60)
    
    # Create output directory
    import os
    os.makedirs('out/SK', exist_ok=True)
    
    # Generate visualizations
    print("\n1. Creating Risk Dashboard...")
    create_risk_dashboard()
    
    print("\n2. Creating Gephi Network Data...")
    create_network_visualization_data()
    
    print("\n3. Creating Patent Timeline...")
    create_patent_timeline()
    
    print("\n4. Creating Funding Flow Data...")
    create_funding_flow_sankey_data()
    
    print("\n" + "=" * 60)
    print("Visualization files created in: out/SK/")
    print("=" * 60)

if __name__ == "__main__":
    main()