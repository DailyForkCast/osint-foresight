#!/usr/bin/env python3
"""
MCF/NQPF Venn Diagram Visualization
Slide 12: Shows NQPF encompassing MCF - expansion not replacement
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_nqpf_mcf_venn(output_dir="visualizations/presentation"):
    """
    Create Venn diagram showing NQPF encompassing MCF
    Demonstrates expansion, not replacement
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(32, 24), facecolor='white')

    # MCF circle (inner, smaller)
    mcf_center = (0, 0)
    mcf_radius = 5.5

    # NQPF circle (outer, larger - encompasses MCF)
    nqpf_center = (0, 0)
    nqpf_radius = 10.0

    # Draw NQPF circle (larger, background)
    nqpf_circle = plt.Circle(nqpf_center, nqpf_radius,
                            facecolor='#AED6F1', alpha=0.4,
                            edgecolor='#3498DB', linewidth=5,
                            label='NQPF', zorder=1)
    ax.add_patch(nqpf_circle)

    # Draw MCF circle (smaller, foreground)
    mcf_circle = plt.Circle(mcf_center, mcf_radius,
                           facecolor='#F5B7B1', alpha=0.6,
                           edgecolor='#E74C3C', linewidth=5,
                           label='MCF', zorder=2)
    ax.add_patch(mcf_circle)

    # MCF label (center)
    ax.text(0, 1.5, 'MCF', fontsize=60, fontweight='bold',
           ha='center', va='center', color='#8B0000')

    ax.text(0, 0, '(2015+)', fontsize=40, fontweight='bold',
           ha='center', va='center', color='#C0392B')

    # MCF content (inside MCF circle)
    mcf_content = [
        "Military-Civil Fusion",
        "Six specific domains",
        "Defense-civilian integration",
        "CMC heavily involved",
        "Strategic tech focus"
    ]

    y_pos = -2.0
    for item in mcf_content:
        ax.text(0, y_pos, item, fontsize=34, ha='center',
               va='center', color='#2C3E50', fontweight='semibold')
        y_pos -= 0.7

    # NQPF label (outer region - top)
    ax.text(0, 11.5, 'NQPF', fontsize=64, fontweight='bold',
           ha='center', va='bottom', color='#1A5490')

    ax.text(0, 10.5, '(New Quality Productive Forces - 2023+)',
           fontsize=42, fontweight='bold', ha='center', va='bottom',
           color='#2874A6')

    # NQPF content (outside MCF circle but inside NQPF)
    # Top section
    nqpf_top = [
        "Economy-wide transformation",
        "Beyond defense applications",
        "Green technology emphasis",
        "Digital economy integration"
    ]

    y_pos = 8.0
    for item in nqpf_top:
        ax.text(0, y_pos, item, fontsize=36, ha='center',
               va='center', color='#1A5490', fontweight='semibold')
        y_pos -= 0.8

    # Bottom section (outside MCF but inside NQPF)
    nqpf_bottom = [
        "Broader innovation mandate",
        "Commercial applications",
        "International palatability"
    ]

    y_pos = -7.0
    for item in nqpf_bottom:
        ax.text(0, y_pos, item, fontsize=36, ha='center',
               va='center', color='#1A5490', fontweight='semibold')
        y_pos -= 0.8

    # Key insight boxes (left and right)
    # Left box: Continuity
    left_box_x = -12
    ax.text(left_box_x, 3, 'CONTINUITY', fontsize=48, fontweight='bold',
           ha='center', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    continuity_points = [
        "• Same institutional architecture",
        "• Same legal framework",
        "• Same funding mechanisms",
        "• Same agencies involved",
        "• MCF persists in military docs"
    ]

    y_pos = 1.5
    for point in continuity_points:
        ax.text(left_box_x, y_pos, point, fontsize=34, ha='center',
               color='#34495E')
        y_pos -= 0.7

    # Right box: Expansion
    right_box_x = 12
    ax.text(right_box_x, 3, 'EXPANSION', fontsize=48, fontweight='bold',
           ha='center', color='#2C3E50',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    expansion_points = [
        "• Broader economic scope",
        "• Non-military applications",
        "• Softer international image",
        "• AI & green tech focus",
        "• Commercial innovation priority"
    ]

    y_pos = 1.5
    for point in expansion_points:
        ax.text(right_box_x, y_pos, point, fontsize=34, ha='center',
               color='#34495E')
        y_pos -= 0.7

    # Title
    ax.text(0, 15, 'MCF Evolution: Expansion Not Replacement',
           fontsize=56, fontweight='bold', ha='center', color='#2C3E50')

    # Subtitle
    ax.text(0, 13.8,
           'NQPF encompasses MCF while extending to broader economic transformation',
           fontsize=42, ha='center', color='#34495E', style='italic')

    # Bottom note
    ax.text(0, -11,
           'Key Takeaway: Same capabilities operating under both frameworks. NQPF softens concerns while maintaining MCF structure.',
           fontsize=38, ha='center', color='#E74C3C', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=3))

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#F5B7B1', edgecolor='#E74C3C', linewidth=3,
                      alpha=0.6, label='MCF (2015+): Defense-civilian integration'),
        mpatches.Patch(facecolor='#AED6F1', edgecolor='#3498DB', linewidth=3,
                      alpha=0.4, label='NQPF (2023+): Broader innovation + MCF'),
    ]

    ax.legend(handles=legend_elements, loc='lower center',
             bbox_to_anchor=(0.5, -0.12), fontsize=40,
             framealpha=0.95, edgecolor='#2C3E50', ncol=2, fancybox=True)

    # Styling
    ax.set_xlim(-16, 16)
    ax.set_ylim(-13, 16)
    ax.set_aspect('equal')
    ax.axis('off')

    # Save
    png_path = output_path / "slide12_nqpf_mcf_venn.png"
    svg_path = output_path / "slide12_nqpf_mcf_venn.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("NQPF/MCF VENN DIAGRAM - SLIDE 12")
    print("="*80)
    print("\nCreating Venn diagram showing expansion not replacement...\n")

    create_nqpf_mcf_venn()

    print("\n" + "="*80)
    print("COMPLETE: NQPF/MCF Venn diagram ready")
    print("="*80)
    print("\nFeatures:")
    print("  + MCF circle (inner, defense focus)")
    print("  + NQPF circle (outer, encompasses MCF)")
    print("  + Continuity and Expansion boxes")
    print("  + 34-64pt fonts throughout")
    print("  + Clear visual showing relationship")
