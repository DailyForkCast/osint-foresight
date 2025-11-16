#!/usr/bin/env python3
"""
MCF Four Global Initiatives - Pillars Diagram
Slide 13: Shows China's four initiatives normalizing MCF approaches globally
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_global_initiatives_pillars(output_dir="visualizations/presentation"):
    """
    Create four pillars diagram showing global initiatives normalizing MCF
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(40, 24), facecolor='white')

    # Define the four initiatives
    initiatives = [
        {
            'acronym': 'GSI',
            'name': 'Global Security\nInitiative',
            'year': '2022',
            'key_point': 'Redefines security\nto include technology',
            'details': [
                '• "Common security"',
                '• Tech sharing framework',
                '• 100+ countries support',
                '• Challenges Western norms'
            ],
            'x': -12,
            'color': '#E74C3C'
        },
        {
            'acronym': 'GDI',
            'name': 'Global Development\nInitiative',
            'year': '2021',
            'key_point': 'Development requires\ntech transfer',
            'details': [
                '• Infrastructure + tech',
                '• UN framework integration',
                '• Creates dependencies',
                '• BRI complement'
            ],
            'x': -4,
            'color': '#F39C12'
        },
        {
            'acronym': 'GCI',
            'name': 'Global Civilization\nInitiative',
            'year': '2023',
            'key_point': '"Mutual learning"\nin technology',
            'details': [
                '• Challenges IP protection',
                '• "Western-centric" critique',
                '• Alternative tech governance',
                '• Soft power element'
            ],
            'x': 4,
            'color': '#3498DB'
        },
        {
            'acronym': 'GDSI',
            'name': 'Global Data Security\nInitiative',
            'year': '2020',
            'key_point': 'Data governance with\nChinese characteristics',
            'details': [
                '• Data localization',
                '• Opposes "tech monopoly"',
                '• Alternative to Western rules',
                '• Sovereignty emphasis'
            ],
            'x': 12,
            'color': '#9B59B6'
        }
    ]

    # Draw base platform (foundation)
    base_platform = mpatches.FancyBboxPatch(
        (-18, -3), 36, 1.5,
        boxstyle="round,pad=0.1",
        facecolor='#2C3E50',
        edgecolor='white',
        linewidth=4,
        alpha=0.95,
        zorder=5
    )
    ax.add_patch(base_platform)

    # Platform label
    ax.text(0, -2.25, 'NORMALIZING MCF-STYLE GOVERNANCE GLOBALLY',
           fontsize=50, fontweight='bold', ha='center', va='center',
           color='white')

    # Draw pillars
    pillar_width = 5
    pillar_base_y = -1.5

    for initiative in initiatives:
        x = initiative['x']
        color = initiative['color']

        # Pillar height (variable to show importance/adoption)
        pillar_height = 12

        # Draw pillar (3D effect)
        # Front face
        front_pillar = mpatches.FancyBboxPatch(
            (x - pillar_width/2, pillar_base_y), pillar_width, pillar_height,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor='white',
            linewidth=4,
            alpha=0.9,
            zorder=4
        )
        ax.add_patch(front_pillar)

        # Capital (top of pillar)
        capital = mpatches.FancyBboxPatch(
            (x - pillar_width/2 - 0.3, pillar_base_y + pillar_height),
            pillar_width + 0.6, 0.8,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor='white',
            linewidth=4,
            alpha=1.0,
            zorder=6
        )
        ax.add_patch(capital)

        # Acronym (on pillar)
        ax.text(x, pillar_base_y + pillar_height - 2, initiative['acronym'],
               fontsize=64, fontweight='bold', ha='center', va='center',
               color='white')

        # Full name (on pillar)
        ax.text(x, pillar_base_y + pillar_height - 5, initiative['name'],
               fontsize=40, fontweight='bold', ha='center', va='center',
               color='white')

        # Year (on pillar)
        ax.text(x, pillar_base_y + pillar_height - 7.5, f"({initiative['year']})",
               fontsize=36, ha='center', va='center',
               color='white', style='italic')

        # Key point (middle of pillar)
        ax.text(x, pillar_base_y + pillar_height/2 + 1, initiative['key_point'],
               fontsize=38, fontweight='bold', ha='center', va='center',
               color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                        edgecolor=color, linewidth=3))

        # Details (below pillar)
        details_y = pillar_base_y - 4
        for i, detail in enumerate(initiative['details']):
            ax.text(x, details_y - (i * 0.9), detail,
                   fontsize=34, ha='center', va='top',
                   color='#34495E', fontweight='semibold')

    # Top arch connecting pillars
    arch_y = pillar_base_y + 13.5
    arch = mpatches.FancyBboxPatch(
        (-16, arch_y), 32, 1.2,
        boxstyle="round,pad=0.2",
        facecolor='#2C3E50',
        edgecolor='white',
        linewidth=4,
        alpha=0.95,
        zorder=7
    )
    ax.add_patch(arch)

    # Arch text
    ax.text(0, arch_y + 0.6, 'State-Directed Tech Transfer & Blurred Civil-Military Boundaries',
           fontsize=46, fontweight='bold', ha='center', va='center',
           color='white')

    # Title
    ax.text(0, 17, "China's Four Global Initiatives",
           fontsize=60, fontweight='bold', ha='center', color='#2C3E50')

    ax.text(0, 15.5, 'Normalizing MCF-Style Approaches in International Governance',
           fontsize=48, ha='center', color='#34495E', style='italic')

    # Impact boxes (left and right)
    # Left box: Methods
    ax.text(-18, 5, 'HOW THEY WORK', fontsize=44, fontweight='bold',
           ha='left', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    methods = [
        '• Frame tech as security',
        '• Link dev to tech transfer',
        '• Challenge IP norms',
        '• Promote data localization',
        '• Offer alternatives to West'
    ]

    y_pos = 3.5
    for method in methods:
        ax.text(-18, y_pos, method,
               fontsize=36, ha='left', color='#34495E')
        y_pos -= 0.9

    # Right box: Impact
    ax.text(18, 5, 'GLOBAL IMPACT', fontsize=44, fontweight='bold',
           ha='right', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    impacts = [
        '• 100+ countries support GSI',
        '• UN framework integration',
        '• Standards body influence',
        '• Global South appeal',
        '• Norm shift in progress'
    ]

    y_pos = 3.5
    for impact in impacts:
        ax.text(18, y_pos, impact,
               fontsize=36, ha='right', color='#34495E')
        y_pos -= 0.9

    # Bottom warning box
    ax.text(0, -9.5,
           'Capacity Building Implication: The norms you defend are being challenged systematically at multilateral level.\n' +
           'These initiatives create alternative frameworks that normalize state-directed tech transfer globally.',
           fontsize=40, ha='center', color='#E74C3C', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.9', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=4))

    # Styling
    ax.set_xlim(-21, 21)
    ax.set_ylim(-11, 18)
    ax.axis('off')

    # Save
    png_path = output_path / "slide13_global_initiatives.png"
    svg_path = output_path / "slide13_global_initiatives.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF FOUR GLOBAL INITIATIVES - SLIDE 13")
    print("="*80)
    print("\nCreating pillars diagram showing global normalization...\n")

    create_global_initiatives_pillars()

    print("\n" + "="*80)
    print("COMPLETE: Global initiatives pillars ready")
    print("="*80)
    print("\nFeatures:")
    print("  + 4 classical pillars (GSI, GDI, GCI, GDSI)")
    print("  + Shared foundation and arch")
    print("  + Key points and details per initiative")
    print("  + Methods and impact boxes")
    print("  + 34-64pt fonts throughout")
