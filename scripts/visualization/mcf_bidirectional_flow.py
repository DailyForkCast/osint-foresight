#!/usr/bin/env python3
"""
MCF Bidirectional Flow Diagram
Slide 4: Shows military ↔ civilian integration, NOT just military getting civilian tech
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_bidirectional_flow(output_dir="visualizations/presentation"):
    """
    Create bidirectional flow diagram showing MCF as two-way integration
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(36, 24), facecolor='white')

    # Define positions
    military_x = -10
    civilian_x = 10
    center_x = 0
    top_y = 8
    bottom_y = -2

    # MILITARY SIDE (Left)
    # Military box
    military_box = mpatches.FancyBboxPatch(
        (military_x - 3, top_y - 1), 6, 10,
        boxstyle="round,pad=0.3",
        facecolor='#1e3a5f',
        edgecolor='white',
        linewidth=5,
        alpha=0.9,
        zorder=5
    )
    ax.add_patch(military_box)

    # Military label
    ax.text(military_x, top_y + 8, 'MILITARY',
           fontsize=60, fontweight='bold', ha='center', color='white')

    # Military examples
    military_examples = [
        'PLA Equipment Dept',
        'Defense R&D',
        'Military Hospitals',
        'Weapons Programs',
        'Naval Shipyards',
        'Aerospace Programs'
    ]

    y_pos = top_y + 5.5
    for example in military_examples:
        ax.text(military_x, y_pos, example,
               fontsize=36, ha='center', color='white', fontweight='semibold')
        y_pos -= 1.3

    # CIVILIAN SIDE (Right)
    # Civilian box
    civilian_box = mpatches.FancyBboxPatch(
        (civilian_x - 3, top_y - 1), 6, 10,
        boxstyle="round,pad=0.3",
        facecolor='#4682b4',
        edgecolor='white',
        linewidth=5,
        alpha=0.9,
        zorder=5
    )
    ax.add_patch(civilian_box)

    # Civilian label
    ax.text(civilian_x, top_y + 8, 'CIVILIAN',
           fontsize=60, fontweight='bold', ha='center', color='white')

    # Civilian examples
    civilian_examples = [
        'Universities',
        'Tech Companies',
        'Research Institutes',
        'Commercial Industry',
        'Transportation',
        'Communications'
    ]

    y_pos = top_y + 5.5
    for example in civilian_examples:
        ax.text(civilian_x, y_pos, example,
               fontsize=36, ha='center', color='white', fontweight='semibold')
        y_pos -= 1.3

    # CENTER: MCF INTEGRATION LAYER
    # Integration box
    integration_box = mpatches.FancyBboxPatch(
        (center_x - 5, bottom_y - 3), 10, 16,
        boxstyle="round,pad=0.4",
        facecolor='#6b46c1',
        edgecolor='white',
        linewidth=5,
        alpha=0.95,
        zorder=4
    )
    ax.add_patch(integration_box)

    # MCF label
    ax.text(center_x, top_y + 8, 'MCF INTEGRATION',
           fontsize=56, fontweight='bold', ha='center', color='white',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='#6b46c1',
                    edgecolor='white', linewidth=4))

    # Six domains in center
    ax.text(center_x, top_y + 4.5, 'Six Integration Domains:',
           fontsize=42, fontweight='bold', ha='center', color='white')

    domains = [
        '1. Infrastructure',
        '2. Industry',
        '3. Science & Technology',
        '4. Education',
        '5. Social Services',
        '6. Maritime & Space'
    ]

    y_pos = top_y + 2.5
    for domain in domains:
        ax.text(center_x, y_pos, domain,
               fontsize=38, ha='center', color='white', fontweight='semibold')
        y_pos -= 1.5

    # BIDIRECTIONAL ARROWS
    arrow_y_positions = [top_y + 6, top_y + 2, bottom_y + 3, bottom_y - 1]

    # Military to Civilian (through integration)
    for y in arrow_y_positions[:2]:
        # Military to Integration
        arrow_props_mil = dict(arrowstyle='->', lw=6, color='#E74C3C')
        ax.annotate('', xy=(center_x - 5.2, y),
                   xytext=(military_x + 3.2, y),
                   arrowprops=arrow_props_mil, zorder=6)

        # Integration to Civilian
        ax.annotate('', xy=(civilian_x - 3.2, y),
                   xytext=(center_x + 5.2, y),
                   arrowprops=arrow_props_mil, zorder=6)

    # Civilian to Military (through integration)
    for y in arrow_y_positions[2:]:
        # Civilian to Integration
        arrow_props_civ = dict(arrowstyle='->', lw=6, color='#27AE60')
        ax.annotate('', xy=(center_x + 5.2, y),
                   xytext=(civilian_x - 3.2, y),
                   arrowprops=arrow_props_civ, zorder=6)

        # Integration to Military
        ax.annotate('', xy=(military_x + 3.2, y),
                   xytext=(center_x - 5.2, y),
                   arrowprops=arrow_props_civ, zorder=6)

    # Arrow labels
    ax.text(military_x + 3.5, top_y + 7,
           'Military tech\nto civilian use',
           fontsize=32, ha='left', va='center', color='#E74C3C',
           fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                    edgecolor='#E74C3C', linewidth=2))

    ax.text(civilian_x - 3.5, bottom_y + 4,
           'Civilian innovation\nto military apps',
           fontsize=32, ha='right', va='center', color='#27AE60',
           fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                    edgecolor='#27AE60', linewidth=2))

    # Examples of flows
    # Military to Civilian example (top)
    ax.text(-14, top_y + 11,
           'Example: BeiDou navigation\nMilitary GPS → Ride-sharing apps',
           fontsize=34, ha='left', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=3))

    # Civilian to Military example (bottom)
    ax.text(14, bottom_y - 5,
           'Example: DJI drones\nConsumer product → Military surveillance',
           fontsize=34, ha='right', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                    edgecolor='#27AE60', linewidth=3))

    # Title
    ax.text(center_x, 13.5, 'MCF: Bidirectional Integration, Not One-Way Transfer',
           fontsize=58, fontweight='bold', ha='center', color='#2C3E50')

    # Subtitle
    ax.text(center_x, 12,
           'Military ↔ Civilian: Both directions matter. Embedded dual-use from inception.',
           fontsize=44, ha='center', color='#34495E', style='italic')

    # Bottom note
    ax.text(center_x, -8.5,
           'Key Difference from Western Models: MCF eliminates firewall between sectors. Every tech entity can theoretically be mobilized.',
           fontsize=40, ha='center', color='#E74C3C', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=3))

    # Styling
    ax.set_xlim(-17, 17)
    ax.set_ylim(-10, 15)
    ax.axis('off')

    # Save
    png_path = output_path / "slide4_bidirectional_flow.png"
    svg_path = output_path / "slide4_bidirectional_flow.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF BIDIRECTIONAL FLOW DIAGRAM - SLIDE 4")
    print("="*80)
    print("\nCreating bidirectional flow showing two-way integration...\n")

    create_bidirectional_flow()

    print("\n" + "="*80)
    print("COMPLETE: Bidirectional flow diagram ready")
    print("="*80)
    print("\nFeatures:")
    print("  + Military and Civilian boxes")
    print("  + MCF integration layer (6 domains)")
    print("  + Bidirectional arrows (both directions)")
    print("  + Real examples (BeiDou, DJI)")
    print("  + 32-60pt fonts throughout")
