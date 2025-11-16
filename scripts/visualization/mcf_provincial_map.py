#!/usr/bin/env python3
"""
MCF Provincial Implementation Map
Slide 19: Shows geographic variance in MCF implementation across key provinces
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_provincial_map(output_dir="visualizations/presentation"):
    """
    Create stylized China map showing provincial MCF implementation variance
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(36, 28), facecolor='white')

    # Define provinces with their characteristics
    provinces = {
        'Beijing': {
            'pos': (0, 5),
            'focus': 'Research & Talent',
            'description': 'Research concentration\nTalent program hub\nUniversity partnerships',
            'color': '#E74C3C',
            'size': 2.5
        },
        'Shanghai': {
            'pos': (3, 0),
            'focus': 'Financial & Investment',
            'description': 'Financial channels\nInvestment coordination\nGlobal partnerships',
            'color': '#F39C12',
            'size': 2.3
        },
        'Guangdong': {
            'pos': (2, -6),
            'focus': 'Commercial Innovation',
            'description': 'Shenzhen tech hub\nCommercial innovation\nPrivate sector integration',
            'color': '#3498DB',
            'size': 3.0
        },
        'Sichuan': {
            'pos': (-4, -2),
            'focus': 'Defense Industry',
            'description': 'Defense integration\nChengdu aerospace\nMilitary production',
            'color': '#8B0000',
            'size': 2.8
        },
        'Zhejiang': {
            'pos': (4, -1),
            'focus': 'Private Sector',
            'description': 'Private enterprise\nE-commerce integration\nDigital economy',
            'color': '#27AE60',
            'size': 2.2
        },
        'Xinjiang': {
            'pos': (-8, 2),
            'focus': 'Surveillance Tech',
            'description': 'Surveillance application\nSocial management\nTech testing ground',
            'color': '#95A5A6',
            'size': 3.5
        }
    }

    # Draw China outline (simplified stylized shape)
    # This is a very simplified representation
    china_outline_x = [-10, -8, -5, -2, 0, 3, 5, 6, 5, 3, 0, -3, -6, -9, -10]
    china_outline_y = [6, 8, 7, 6, 7, 5, 2, -2, -5, -7, -6, -8, -6, -2, 6]

    ax.fill(china_outline_x, china_outline_y, color='#F0F0F0',
           alpha=0.3, edgecolor='#7F8C8D', linewidth=3, zorder=1)

    # Draw province circles and labels
    for province, data in provinces.items():
        x, y = data['pos']
        color = data['color']
        size = data['size']

        # Province circle
        circle = plt.Circle((x, y), size, facecolor=color, alpha=0.7,
                           edgecolor='white', linewidth=4, zorder=3)
        ax.add_patch(circle)

        # Province name
        ax.text(x, y + size + 0.5, province,
               fontsize=46, fontweight='bold', ha='center', va='bottom',
               color=color,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                        edgecolor=color, linewidth=3))

        # Focus area
        ax.text(x, y, data['focus'],
               fontsize=38, fontweight='bold', ha='center', va='center',
               color='white')

    # Legend/Detail boxes positioned around map
    detail_positions = [
        ('Beijing', 12, 5),
        ('Shanghai', 12, 0),
        ('Guangdong', 12, -5),
        ('Sichuan', -14, -2),
        ('Zhejiang', 12, -10),
        ('Xinjiang', -14, 3)
    ]

    for province, box_x, box_y in detail_positions:
        data = provinces[province]

        # Detail box
        ax.text(box_x, box_y, data['description'],
               fontsize=34, ha='center', va='center',
               color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.7', facecolor='white',
                        edgecolor=data['color'], linewidth=3))

        # Connection line from province to detail box
        prov_x, prov_y = data['pos']
        ax.plot([prov_x, box_x], [prov_y, box_y],
               color=data['color'], linewidth=2, linestyle='--',
               alpha=0.5, zorder=2)

    # Title
    ax.text(0, 12, 'MCF Provincial Implementation: Geographic Variance',
           fontsize=56, fontweight='bold', ha='center', color='#2C3E50')

    ax.text(0, 10.5,
           'Wide variation in implementation effectiveness and focus areas across China',
           fontsize=42, ha='center', color='#34495E', style='italic')

    # Key patterns box (bottom)
    patterns_text = """Key Patterns:
• Coastal provinces: Commercial & international focus
• Interior provinces: Defense industry concentration
• Capital (Beijing): Research, policy, and coordination
• Special regions (Xinjiang): Surveillance technology application
• Provincial autonomy: Implementation varies significantly despite central direction"""

    ax.text(0, -12.5, patterns_text,
           fontsize=36, ha='center', va='top', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.9', facecolor='#ECF0F1',
                    edgecolor='#34495E', linewidth=3))

    # Legend for focus areas
    legend_elements = [
        mpatches.Patch(facecolor='#E74C3C', edgecolor='white', linewidth=2,
                      label='Research & Talent'),
        mpatches.Patch(facecolor='#F39C12', edgecolor='white', linewidth=2,
                      label='Financial & Investment'),
        mpatches.Patch(facecolor='#3498DB', edgecolor='white', linewidth=2,
                      label='Commercial Innovation'),
        mpatches.Patch(facecolor='#8B0000', edgecolor='white', linewidth=2,
                      label='Defense Industry'),
        mpatches.Patch(facecolor='#27AE60', edgecolor='white', linewidth=2,
                      label='Private Sector'),
        mpatches.Patch(facecolor='#95A5A6', edgecolor='white', linewidth=2,
                      label='Surveillance Tech'),
    ]

    ax.legend(handles=legend_elements, loc='upper right',
             bbox_to_anchor=(1.0, 0.95), fontsize=38,
             title='Provincial Focus Areas', title_fontsize=42,
             framealpha=0.95, edgecolor='#2C3E50', ncol=2)

    # Note about implementation
    ax.text(0, -16.5,
           'Important: Not monolithic. Guangdong approaches differ from Xinjiang. Provincial competition and local interests create implementation variance.',
           fontsize=38, ha='center', color='#E74C3C', fontweight='semibold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=3))

    # Styling
    ax.set_xlim(-17, 17)
    ax.set_ylim(-18, 14)
    ax.set_aspect('equal')
    ax.axis('off')

    # Save
    png_path = output_path / "slide19_provincial_map.png"
    svg_path = output_path / "slide19_provincial_map.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF PROVINCIAL IMPLEMENTATION MAP - SLIDE 19")
    print("="*80)
    print("\nCreating map showing geographic variance...\n")

    create_provincial_map()

    print("\n" + "="*80)
    print("COMPLETE: Provincial implementation map ready")
    print("="*80)
    print("\nFeatures:")
    print("  + Stylized China map")
    print("  + 6 key provinces highlighted")
    print("  + Color-coded by implementation focus")
    print("  + Detail boxes with descriptions")
    print("  + 34-56pt fonts throughout")
