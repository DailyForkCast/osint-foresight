#!/usr/bin/env python3
"""
Simple Global Initiatives - MINIMAL 4 BOXES
Clean 2x2 grid showing four initiatives
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

def create_simple_global(output_dir="visualizations/presentation_simple"):
    """Create ultra-simple 4-box grid"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(36, 22), facecolor='white')

    # Four initiatives in 2x2 grid
    initiatives = [
        {
            'acronym': 'GSI',
            'name': 'Global Security\nInitiative',
            'year': '2022',
            'key': 'Redefines security\nto include tech',
            'x': -6,
            'y': 9,
            'color': '#E74C3C'
        },
        {
            'acronym': 'GDI',
            'name': 'Global Development\nInitiative',
            'year': '2021',
            'key': 'Development requires\ntech transfer',
            'x': 6,
            'y': 9,
            'color': '#F39C12'
        },
        {
            'acronym': 'GCI',
            'name': 'Global Civilization\nInitiative',
            'year': '2023',
            'key': 'Mutual learning\nin technology',
            'x': -6,
            'y': 3,
            'color': '#3498DB'
        },
        {
            'acronym': 'GDSI',
            'name': 'Global Data Security\nInitiative',
            'year': '2020',
            'key': 'Data governance\nChinese-style',
            'x': 6,
            'y': 3,
            'color': '#9B59B6'
        }
    ]

    box_width = 10
    box_height = 5

    for init in initiatives:
        # Box
        box = mpatches.FancyBboxPatch(
            (init['x'] - box_width/2, init['y'] - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.3",
            facecolor=init['color'],
            edgecolor='white',
            linewidth=6,
            zorder=5
        )
        ax.add_patch(box)

        # Acronym
        ax.text(init['x'], init['y'] + 1.5, init['acronym'],
               fontsize=72, fontweight='bold', ha='center',
               va='center', color='white')

        # Full name
        ax.text(init['x'], init['y'] + 0.2, init['name'],
               fontsize=42, ha='center', va='center',
               color='white', linespacing=1.5)

        # Year
        ax.text(init['x'], init['y'] - 1, f"({init['year']})",
               fontsize=38, ha='center', va='center',
               color='white', style='italic')

        # Key point (below box)
        ax.text(init['x'], init['y'] - 3.5, init['key'],
               fontsize=38, ha='center', va='top',
               color='#2C3E50', linespacing=1.5, fontweight='semibold')

    # Title
    ax.text(0, 16, "China's Four Global Initiatives",
           fontsize=68, fontweight='bold', ha='center', color='#2C3E50')
    ax.text(0, 14.5, 'Normalizing MCF approaches in international governance',
           fontsize=46, ha='center', color='#7F8C8D', style='italic')

    # Bottom note
    ax.text(0, -2, '100+ countries support • UN framework integration • Norm shift in progress',
           fontsize=48, ha='center', color='#E74C3C', fontweight='bold')

    # Styling
    ax.set_xlim(-13, 13)
    ax.set_ylim(-3, 17)
    ax.axis('off')

    # Save
    png_path = output_path / "slide13_simple_global.png"
    svg_path = output_path / "slide13_simple_global.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] {svg_path}")

    plt.close()
    return str(png_path)

if __name__ == "__main__":
    create_simple_global()
    print("[COMPLETE] Simple global initiatives")
