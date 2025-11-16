#!/usr/bin/env python3
"""
Simple MCF Technology Capabilities - MINIMAL BAR CHART
Clean horizontal bars showing capability levels
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_tech(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple tech capabilities bar chart"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 22), facecolor='white')

    # Technology domains with capability (0-10 scale)
    domains = [
        ('AI & Machine Learning', 7, '#F39C12'),
        ('Quantum Technology', 8, '#27AE60'),
        ('Semiconductors', 3, '#E74C3C'),
        ('Biotechnology', 6, '#F39C12'),
        ('Advanced Materials', 7, '#27AE60'),
        ('Aerospace', 5, '#F39C12'),
    ]

    # Reverse for top-to-bottom display
    domains = list(reversed(domains))

    y_start = 13
    bar_height = 1.5
    y_spacing = 2.2

    for i, (domain, capability, color) in enumerate(domains):
        y = y_start - (i * y_spacing)

        # Domain label
        ax.text(-11, y, domain, fontsize=52, fontweight='bold',
               ha='left', va='center', color='#2C3E50')

        # Background bar (full width = 10)
        bg_bar = mpatches.FancyBboxPatch(
            (-1, y - bar_height/2), 10, bar_height,
            boxstyle="round,pad=0.05",
            facecolor='#ECF0F1',
            edgecolor='#BDC3C7',
            linewidth=3,
            zorder=2
        )
        ax.add_patch(bg_bar)

        # Capability bar (filled portion)
        cap_bar = mpatches.FancyBboxPatch(
            (-1, y - bar_height/2), capability, bar_height,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor='white',
            linewidth=3,
            zorder=3
        )
        ax.add_patch(cap_bar)

        # Capability number
        ax.text(10, y, f'{capability}/10', fontsize=50, fontweight='bold',
               ha='left', va='center', color=color)

    # Title
    ax.text(0, 17, 'MCF Technology Capabilities',
           fontsize=68, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 15.5, 'Current assessment across priority domains',
           fontsize=46, ha='center', color='#7F8C8D', style='italic')

    # Legend
    legend_y = -1
    ax.text(-11, legend_y, 'Capability:', fontsize=46, fontweight='bold',
           ha='left', color='#2C3E50')
    ax.text(-6, legend_y, '0-3: Weak', fontsize=42, ha='left',
           color='#E74C3C', fontweight='bold')
    ax.text(-1.5, legend_y, '4-6: Moderate', fontsize=42, ha='left',
           color='#F39C12', fontweight='bold')
    ax.text(4, legend_y, '7-10: Strong', fontsize=42, ha='left',
           color='#27AE60', fontweight='bold')

    # Bottom note
    ax.text(0, -3, '~80% of MCF projects fail • Success in mature tech, struggle in cutting-edge',
           fontsize=48, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-12, 12)
    ax.set_ylim(-4, 18)
    ax.axis('off')

    # Save
    png_path = output_path / "slide11_simple_tech.png"
    svg_path = output_path / "slide11_simple_tech.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_tech()
    print("[COMPLETE] Simple tech capabilities")
