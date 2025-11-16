#!/usr/bin/env python3
"""
Simple MCF Bidirectional Flow - MINIMAL VERSION
Just two boxes with bidirectional arrows
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_flow(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple bidirectional flow"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 20), facecolor='white')

    # Two simple boxes
    # Military box (left)
    military_box = mpatches.FancyBboxPatch(
        (-8, 3), 6, 8,
        boxstyle="round,pad=0.3",
        facecolor='#2C5F8D',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(military_box)

    ax.text(-5, 10, 'MILITARY', fontsize=72, fontweight='bold',
           ha='center', color='white')
    ax.text(-5, 7, 'Defense\nWeapons\nR&D', fontsize=48,
           ha='center', va='center', color='white', linespacing=1.8)

    # Civilian box (right)
    civilian_box = mpatches.FancyBboxPatch(
        (2, 3), 6, 8,
        boxstyle="round,pad=0.3",
        facecolor='#27AE60',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(civilian_box)

    ax.text(5, 10, 'CIVILIAN', fontsize=72, fontweight='bold',
           ha='center', color='white')
    ax.text(5, 7, 'Universities\nCompanies\nResearch', fontsize=48,
           ha='center', va='center', color='white', linespacing=1.8)

    # Simple bidirectional arrows
    # Arrow to right
    arrow_right = dict(arrowstyle='->', lw=8, color='#E74C3C')
    ax.annotate('', xy=(1.8, 8), xytext=(-1.8, 8),
               arrowprops=arrow_right, zorder=6)

    # Arrow to left
    arrow_left = dict(arrowstyle='->', lw=8, color='#E74C3C')
    ax.annotate('', xy=(-1.8, 5.5), xytext=(1.8, 5.5),
               arrowprops=arrow_left, zorder=6)

    # Center label
    ax.text(0, 13, 'MCF Integration',
           fontsize=64, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 12, 'Two-way flow between military and civilian sectors',
           fontsize=44, ha='center', color='#7F8C8D', style='italic')

    # Bottom note - simple
    ax.text(0, 1, 'Both directions matter',
           fontsize=52, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-12, 12)
    ax.set_ylim(0, 14)
    ax.axis('off')

    # Save
    png_path = output_path / "slide4_simple_flow.png"
    svg_path = output_path / "slide4_simple_flow.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_flow()
    print("[COMPLETE] Simple bidirectional flow")
