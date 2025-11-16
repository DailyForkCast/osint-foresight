#!/usr/bin/env python3
"""
MCF Legal Framework - Concentric Rings Visualization
Slide 7: Shows expanding cumulative authority from 2015-2024
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_legal_framework_rings(output_dir="visualizations/presentation"):
    """
    Create concentric rings showing expanding legal authority
    2015 → 2024 cumulative framework
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(28, 28), facecolor='white')

    # Define laws and their rings (inside to outside)
    laws = [
        {
            'year': '2015',
            'name': 'National Security Law',
            'detail': 'Foundational Authority\nArticle 16: Mandates MCF',
            'radius': 3.5,
            'color': '#FFCDD2',
            'edgecolor': '#E57373'
        },
        {
            'year': '2017',
            'name': 'Intelligence Law',
            'detail': 'Compelled Cooperation\nArticle 7: Required assistance',
            'radius': 6.0,
            'color': '#EF9A9A',
            'edgecolor': '#E57373'
        },
        {
            'year': '2021',
            'name': 'Data Security Law',
            'detail': 'Information Control\nArticle 31: Critical data restrictions',
            'radius': 8.5,
            'color': '#E57373',
            'edgecolor': '#EF5350'
        },
        {
            'year': '2024',
            'name': 'State Secrets Law',
            'detail': 'Expanded Classification\n"Work secrets" + pre-publication review',
            'radius': 11.0,
            'color': '#EF5350',
            'edgecolor': '#F44336'
        }
    ]

    # Draw concentric circles (from outside to inside for proper layering)
    for law in reversed(laws):
        # Draw filled circle
        circle = plt.Circle((0, 0), law['radius'],
                           facecolor=law['color'],
                           edgecolor=law['edgecolor'],
                           linewidth=4, alpha=0.85, zorder=1)
        ax.add_patch(circle)

    # Add labels for each ring
    for i, law in enumerate(laws):
        # Calculate angle for label placement (stagger positions)
        angle = 45 + (i * 20)  # Spread labels around
        angle_rad = np.radians(angle)

        # Position for year label (on the ring)
        if i == 0:  # Innermost - place in center
            x_year, y_year = 0, 0
        else:
            radius_pos = (law['radius'] + laws[i-1]['radius']) / 2
            x_year = radius_pos * np.cos(angle_rad)
            y_year = radius_pos * np.sin(angle_rad)

        # Year label (large and bold)
        ax.text(x_year, y_year + 1.2, law['year'],
               fontsize=52, fontweight='bold', ha='center', va='bottom',
               color='#FFFFFF',
               bbox=dict(boxstyle='round,pad=0.6', facecolor=law['edgecolor'],
                        edgecolor='white', linewidth=3))

        # Law name
        ax.text(x_year, y_year, law['name'],
               fontsize=42, fontweight='bold', ha='center', va='top',
               color='#2C3E50')

        # Details (smaller)
        ax.text(x_year, y_year - 0.8, law['detail'],
               fontsize=34, ha='center', va='top',
               color='#34495E', style='italic')

    # Draw expansion arrows (showing cumulative growth)
    arrow_props = dict(arrowstyle='->', lw=5, color='#8B0000', alpha=0.6)

    # Arrows pointing outward from center
    for angle in [0, 90, 180, 270]:
        angle_rad = np.radians(angle)
        x_start = 2.5 * np.cos(angle_rad)
        y_start = 2.5 * np.sin(angle_rad)
        x_end = 11.5 * np.cos(angle_rad)
        y_end = 11.5 * np.sin(angle_rad)

        ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                   arrowprops=arrow_props, zorder=10)

    # Center label
    ax.text(0, -1.5, 'Expanding\nCumulative\nAuthority',
           fontsize=44, fontweight='bold', ha='center', va='center',
           color='#FFFFFF',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#8B0000',
                    edgecolor='white', linewidth=4))

    # Title
    ax.text(0, 13.5, 'MCF Legal Framework: Expanding Rings of Authority',
           fontsize=52, fontweight='bold', ha='center', color='#2C3E50')

    ax.text(0, 12.5, 'Four Key Laws Creating Cumulative, Expanding Legal Power (2015-2024)',
           fontsize=38, ha='center', color='#34495E', style='italic')

    # Legend explaining the concept
    legend_text = [
        "Each law builds on previous authority",
        "Inner rings remain in force",
        "Scope expands from defense to economy to society",
        "Vague definitions enable broad application"
    ]

    legend_y = -10
    for i, text in enumerate(legend_text):
        ax.text(-11, legend_y - (i * 0.8), f"• {text}",
               fontsize=36, ha='left', color='#2C3E50')

    # Note about implementation
    ax.text(0, -13.5,
           'Note: Theoretical authority varies from actual enforcement. Implementation differs by province and sector.',
           fontsize=32, ha='center', color='#7F8C8D', style='italic')

    # Styling
    ax.set_xlim(-14, 14)
    ax.set_ylim(-15, 15)
    ax.set_aspect('equal')
    ax.axis('off')

    # Save
    png_path = output_path / "slide7_legal_framework.png"
    svg_path = output_path / "slide7_legal_framework.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF LEGAL FRAMEWORK VISUALIZATION - SLIDE 7")
    print("="*80)
    print("\nCreating concentric rings showing expanding authority...\n")

    create_legal_framework_rings()

    print("\n" + "="*80)
    print("COMPLETE: Legal framework visualization ready")
    print("="*80)
    print("\nFeatures:")
    print("  + 4 concentric rings (2015, 2017, 2021, 2024)")
    print("  + Color gradient showing expansion")
    print("  + Key provisions labeled")
    print("  + 32-52pt fonts throughout")
    print("  + Expansion arrows showing cumulative authority")
