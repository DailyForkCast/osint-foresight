#!/usr/bin/env python3
"""
Simple MCF Timeline - MINIMAL VERSION
Clean horizontal timeline with key dates
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_timeline(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple timeline"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 18), facecolor='white')

    # Timeline data - simplified
    events = [
        ('2015', 'National Security Law\nMCF becomes law', '#E74C3C'),
        ('2017', 'Intelligence Law\nCompelled cooperation', '#F39C12'),
        ('2019', 'Cryptography Law\nData control', '#3498DB'),
        ('2021', 'Data Security Law\nExpanded authority', '#9B59B6'),
        ('2024', 'State Secrets Law\nFull integration', '#E74C3C'),
    ]

    # Draw horizontal line
    ax.plot([-10, 10], [6, 6], color='#2C3E50', linewidth=6, zorder=1)

    # Position events evenly
    x_positions = [-9, -4.5, 0, 4.5, 9]

    for i, (year, label, color) in enumerate(events):
        x = x_positions[i]

        # Circle marker
        circle = plt.Circle((x, 6), 0.6, facecolor=color,
                           edgecolor='white', linewidth=4, zorder=3)
        ax.add_patch(circle)

        # Year (on timeline)
        ax.text(x, 6, year, fontsize=52, fontweight='bold',
               ha='center', va='center', color='white', zorder=4)

        # Label (above)
        ax.text(x, 8.5, label, fontsize=40, ha='center', va='bottom',
               color='#2C3E50', linespacing=1.6)

    # Title
    ax.text(0, 12, 'MCF Legal Framework Evolution',
           fontsize=64, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 11, '2015-2024: Systematic expansion of authority',
           fontsize=44, ha='center', color='#7F8C8D', style='italic')

    # Bottom note
    ax.text(0, 2, 'Each law builds on previous → Cumulative legal authority',
           fontsize=48, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-12, 12)
    ax.set_ylim(0, 13)
    ax.axis('off')

    # Save
    png_path = output_path / "slide6_simple_timeline.png"
    svg_path = output_path / "slide6_simple_timeline.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_timeline()
    print("[COMPLETE] Simple timeline")
