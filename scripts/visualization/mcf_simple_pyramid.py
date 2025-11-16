#!/usr/bin/env python3
"""
Simple MCF Organization - MINIMAL 3-TIER PYRAMID
Clear hierarchy without complexity
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_pyramid(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple 3-tier pyramid"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 22), facecolor='white')

    # Tier 1: Top (Xi Jinping)
    tier1_box = mpatches.FancyBboxPatch(
        (-3, 14), 6, 3,
        boxstyle="round,pad=0.2",
        facecolor='#8B0000',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(tier1_box)
    ax.text(0, 15.5, 'Xi Jinping', fontsize=68, fontweight='bold',
           ha='center', va='center', color='white')

    # Tier 2: Middle (Party + Military + State)
    tier2_width = 14
    tier2_box = mpatches.FancyBboxPatch(
        (-tier2_width/2, 9), tier2_width, 3,
        boxstyle="round,pad=0.2",
        facecolor='#C0392B',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(tier2_box)
    ax.text(0, 10.5, 'Party • Military • State Council', fontsize=58,
           fontweight='bold', ha='center', va='center', color='white')

    # Tier 3: Bottom (Implementation)
    tier3_width = 22
    tier3_box = mpatches.FancyBboxPatch(
        (-tier3_width/2, 4), tier3_width, 3,
        boxstyle="round,pad=0.2",
        facecolor='#E74C3C',
        edgecolor='white',
        linewidth=6,
        zorder=5
    )
    ax.add_patch(tier3_box)
    ax.text(0, 5.5, 'Ministries • Universities • SOEs • Private Companies',
           fontsize=54, fontweight='bold', ha='center', va='center', color='white')

    # Simple arrows connecting tiers
    arrow_props = dict(arrowstyle='->', lw=8, color='#2C3E50')
    ax.annotate('', xy=(0, 9), xytext=(0, 14), arrowprops=arrow_props, zorder=4)
    ax.annotate('', xy=(0, 4), xytext=(0, 9), arrowprops=arrow_props, zorder=4)

    # Title
    ax.text(0, 19, 'MCF Organization Structure',
           fontsize=68, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 17.5, 'Top-down authority cascade',
           fontsize=48, ha='center', color='#7F8C8D', style='italic')

    # Bottom note
    ax.text(0, 1.5, 'Authority flows from top → All levels must comply',
           fontsize=50, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-14, 14)
    ax.set_ylim(0, 20)
    ax.axis('off')

    # Save
    png_path = output_path / "slide8_simple_pyramid.png"
    svg_path = output_path / "slide8_simple_pyramid.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_pyramid()
    print("[COMPLETE] Simple pyramid")
