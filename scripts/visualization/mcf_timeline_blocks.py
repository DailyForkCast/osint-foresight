#!/usr/bin/env python3
"""
MCF Policy Evolution Timeline - Building Blocks
Slide 6: Shows systematic development 2015-2023
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def create_timeline_blocks(output_dir="visualizations/presentation"):
    """
    Create ascending building blocks showing MCF policy evolution
    2015-2023 systematic development
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(36, 20), facecolor='white')

    # Define milestones (year, title, description)
    milestones = [
        {
            'year': '2015',
            'title': 'National\nStrategy',
            'detail': 'Xi elevates MCF\nto national priority',
            'height': 1,
            'x': 0
        },
        {
            'year': '2016',
            'title': 'CMC S&T\nCommission',
            'detail': 'Military tech\nwindow created',
            'height': 2,
            'x': 6
        },
        {
            'year': '2017',
            'title': 'CCIMCD\nEstablished',
            'detail': 'Xi chairs central\ncoordination body',
            'height': 3,
            'x': 12
        },
        {
            'year': '2018',
            'title': 'Constitutional\nAmendment',
            'detail': 'MCF written into\nconstitution',
            'height': 4,
            'x': 18
        },
        {
            'year': '2021',
            'title': '14th Five-Year\nPlan',
            'detail': 'Deepened implementation\nwith metrics',
            'height': 5,
            'x': 24
        },
        {
            'year': '2023',
            'title': 'NQPF\nConcept',
            'detail': 'Expansion beyond\ndefense domains',
            'height': 6,
            'x': 30
        }
    ]

    # Color gradient (light to dark red)
    colors = ['#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336', '#E53935']

    # Draw blocks
    block_width = 4.5
    base_y = 0

    for i, milestone in enumerate(milestones):
        # Calculate dimensions
        height = milestone['height'] * 2.5  # Scale height
        x = milestone['x']
        y = base_y

        # Draw 3D block effect
        # Main block (front face)
        front_rect = mpatches.FancyBboxPatch(
            (x, y), block_width, height,
            boxstyle="round,pad=0.1",
            facecolor=colors[i],
            edgecolor='white',
            linewidth=4,
            alpha=0.95,
            zorder=5
        )
        ax.add_patch(front_rect)

        # Top face (3D effect)
        top_points = np.array([
            [x, y + height],
            [x + 0.3, y + height + 0.3],
            [x + block_width + 0.3, y + height + 0.3],
            [x + block_width, y + height]
        ])
        top_poly = mpatches.Polygon(top_points, closed=True,
                                    facecolor=colors[i], alpha=0.7,
                                    edgecolor='white', linewidth=3, zorder=4)
        ax.add_patch(top_poly)

        # Right face (3D effect)
        right_points = np.array([
            [x + block_width, y],
            [x + block_width + 0.3, y + 0.3],
            [x + block_width + 0.3, y + height + 0.3],
            [x + block_width, y + height]
        ])
        right_poly = mpatches.Polygon(right_points, closed=True,
                                      facecolor=colors[i], alpha=0.5,
                                      edgecolor='white', linewidth=3, zorder=3)
        ax.add_patch(right_poly)

        # Year label (large, top of block)
        ax.text(x + block_width/2, y + height - 0.8, milestone['year'],
               fontsize=52, fontweight='bold', ha='center', va='center',
               color='white',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#8B0000',
                        edgecolor='white', linewidth=3))

        # Title (middle of block)
        ax.text(x + block_width/2, y + height/2 + 0.3, milestone['title'],
               fontsize=42, fontweight='bold', ha='center', va='center',
               color='#2C3E50')

        # Detail (bottom of block)
        ax.text(x + block_width/2, y + 1.2, milestone['detail'],
               fontsize=34, ha='center', va='center',
               color='#34495E', style='italic')

        # Arrow to next block (except last)
        if i < len(milestones) - 1:
            arrow_props = dict(arrowstyle='->', lw=4, color='#2C3E50')
            ax.annotate('', xy=(milestones[i+1]['x'] - 0.5, base_y + height/2),
                       xytext=(x + block_width + 0.5, base_y + height/2),
                       arrowprops=arrow_props, zorder=6)

    # Title
    ax.text(17, 17, 'MCF Policy Evolution: Systematic Development',
           fontsize=56, fontweight='bold', ha='center', color='#2C3E50')

    ax.text(17, 15.5, '2015-2023: Sustained, systematic development regardless of external pressure',
           fontsize=42, ha='center', color='#34495E', style='italic')

    # Timeline base line
    ax.plot([0, 35], [base_y, base_y], color='#95A5A6', linewidth=3, zorder=1)

    # Key insights boxes
    insight_y = -4
    insights = [
        {
            'title': 'Institutional\nDepth',
            'content': 'Central coordination\nthrough multiple bodies',
            'x': 5
        },
        {
            'title': 'Constitutional\nFoundation',
            'content': 'Written into basic law\nshowing permanence',
            'x': 17
        },
        {
            'title': 'Evolution\nNot Stagnation',
            'content': 'Terminology adapts\nwhile structure persists',
            'x': 29
        }
    ]

    for insight in insights:
        # Box
        ax.text(insight['x'], insight_y, insight['title'],
               fontsize=40, fontweight='bold', ha='center', va='top',
               color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.6', facecolor='#ECF0F1',
                        edgecolor='#34495E', linewidth=3))

        # Content
        ax.text(insight['x'], insight_y - 2.5, insight['content'],
               fontsize=34, ha='center', va='top', color='#34495E')

    # Bottom note
    ax.text(17, -8.5,
           'Pattern Recognition: Each step builds on previous foundation. No reversals or major pivots. Institutional commitment deepening over time.',
           fontsize=38, ha='center', color='#E74C3C', fontweight='semibold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFEBEE',
                    edgecolor='#E74C3C', linewidth=3))

    # Styling
    ax.set_xlim(-2, 37)
    ax.set_ylim(-10, 18)
    ax.axis('off')

    # Save
    png_path = output_path / "slide6_timeline_blocks.png"
    svg_path = output_path / "slide6_timeline_blocks.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF TIMELINE BUILDING BLOCKS - SLIDE 6")
    print("="*80)
    print("\nCreating ascending blocks showing policy evolution...\n")

    create_timeline_blocks()

    print("\n" + "="*80)
    print("COMPLETE: Timeline building blocks ready")
    print("="*80)
    print("\nFeatures:")
    print("  + 6 ascending blocks (2015-2023)")
    print("  + 3D block effects")
    print("  + Color gradient showing progression")
    print("  + 34-56pt fonts throughout")
    print("  + Key insights highlighted")
