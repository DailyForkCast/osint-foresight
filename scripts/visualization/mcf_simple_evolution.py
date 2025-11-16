#!/usr/bin/env python3
"""
Simple NQPF Evolution - MINIMAL ARROW
Clean left-to-right evolution showing expansion
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_evolution(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple evolution arrow"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 18), facecolor='white')

    # MCF box (left)
    mcf_box = mpatches.FancyBboxPatch(
        (-10, 4), 6, 5,
        boxstyle="round,pad=0.3",
        facecolor='#E74C3C',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(mcf_box)

    ax.text(-7, 7.5, 'MCF', fontsize=72, fontweight='bold',
           ha='center', va='center', color='white')
    ax.text(-7, 6, '(2015-2024)', fontsize=44, ha='center',
           va='center', color='white', style='italic')
    ax.text(-7, 4.8, 'Defense focus', fontsize=38, ha='center',
           va='center', color='white')

    # Large arrow
    arrow_props = dict(arrowstyle='->', lw=12, color='#2C3E50',
                      mutation_scale=80)
    ax.annotate('', xy=(3.5, 6.5), xytext=(-3.5, 6.5),
               arrowprops=arrow_props, zorder=4)

    # Evolution label on arrow
    ax.text(0, 8.5, 'EXPANSION', fontsize=56, fontweight='bold',
           ha='center', color='#2C3E50')

    # NQPF box (right)
    nqpf_box = mpatches.FancyBboxPatch(
        (4, 3), 8, 7,
        boxstyle="round,pad=0.3",
        facecolor='#3498DB',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(nqpf_box)

    ax.text(8, 8, 'NQPF', fontsize=72, fontweight='bold',
           ha='center', va='center', color='white')
    ax.text(8, 6.8, '(2024+)', fontsize=44, ha='center',
           va='center', color='white', style='italic')
    ax.text(8, 5.6, 'Whole-of-nation', fontsize=42, ha='center',
           va='center', color='white')
    ax.text(8, 4.5, 'All industries', fontsize=42, ha='center',
           va='center', color='white')
    ax.text(8, 3.5, 'Broader scope', fontsize=42, ha='center',
           va='center', color='white')

    # Title
    ax.text(0, 12, 'MCF → NQPF Evolution',
           fontsize=68, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 10.5, 'Expansion, not replacement',
           fontsize=48, ha='center', color='#7F8C8D', style='italic')

    # Bottom note
    ax.text(0, 1, 'Same architecture • Same goals • Wider application',
           fontsize=50, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-13, 13)
    ax.set_ylim(0, 13)
    ax.axis('off')

    # Save
    png_path = output_path / "slide12_simple_evolution.png"
    svg_path = output_path / "slide12_simple_evolution.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_evolution()
    print("[COMPLETE] Simple evolution arrow")
