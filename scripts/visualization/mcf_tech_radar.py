#!/usr/bin/env python3
"""
MCF Technology Capabilities Radar Chart
Slides 11/20: Shows varying capability levels across priority domains
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path as mPath
from matplotlib.patches import PathPatch
from matplotlib.spines import Spine
from matplotlib.projections import register_projection


def create_tech_capabilities_radar(output_dir="visualizations/presentation"):
    """
    Create radar chart showing MCF capabilities across 6 technology domains
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Technology domains and capabilities (0-10 scale)
    domains = [
        'AI & Autonomous\nSystems',
        'Quantum\nTech',
        'Semiconductors',
        'Biotechnology',
        'Advanced\nMaterials',
        'Aerospace'
    ]

    # Capability levels (based on presentation content)
    capabilities = {
        'Overall Capability': [7, 8, 3, 6, 7, 5],  # Current state
        'Trend (2030 projection)': [9, 9, 5, 8, 8, 7],  # Projected if trends continue
    }

    # Detailed assessment per domain
    assessments = [
        ('AI', 'Strong applications\nWeak foundational\nmodels', '#F39C12'),
        ('Quantum', 'Leading in comm\nBehind in computing', '#27AE60'),
        ('Semis', 'Mature nodes OK\nAdvanced: dependent', '#E74C3C'),
        ('Biotech', 'World-class sequencing\nWeaker drug dev', '#F39C12'),
        ('Materials', 'Rare earth dominance\nMetamatl struggle', '#F39C12'),
        ('Aero', 'Launch competitive\nEngine weakness', '#E74C3C')
    ]

    # Create figure with two subplots
    fig = plt.figure(figsize=(36, 20), facecolor='white')

    # Main radar chart
    ax1 = fig.add_subplot(121, projection='polar')

    # Number of variables
    num_vars = len(domains)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is circular, so we need to close it
    capabilities['Overall Capability'] += capabilities['Overall Capability'][:1]
    capabilities['Trend (2030 projection)'] += capabilities['Trend (2030 projection)'][:1]
    angles += angles[:1]

    # Plot data
    ax1.plot(angles, capabilities['Overall Capability'], 'o-', linewidth=4,
            label='Current Capability (2024)', color='#E74C3C', markersize=12)
    ax1.fill(angles, capabilities['Overall Capability'], alpha=0.25, color='#E74C3C')

    ax1.plot(angles, capabilities['Trend (2030 projection)'], 'o-', linewidth=4,
            label='Projected (2030)', color='#3498DB', markersize=12, linestyle='--')
    ax1.fill(angles, capabilities['Trend (2030 projection)'], alpha=0.15, color='#3498DB')

    # Fix axis to go in the right order and start at 12 o'clock
    ax1.set_theta_offset(np.pi / 2)
    ax1.set_theta_direction(-1)

    # Draw axis labels
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(domains, fontsize=42, fontweight='bold', color='#2C3E50')

    # Set y-axis (capability levels)
    ax1.set_ylim(0, 10)
    ax1.set_yticks([2, 4, 6, 8, 10])
    ax1.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=36, color='#7F8C8D')

    # Add grid
    ax1.grid(True, linewidth=2, color='#BDC3C7', alpha=0.5)

    # Title
    ax1.set_title('MCF Technology Capabilities Radar\nAssessment Across Priority Domains',
                 fontsize=52, fontweight='bold', pad=40, color='#2C3E50')

    # Legend
    ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1),
              fontsize=40, framealpha=0.95, edgecolor='#2C3E50')

    # Capability scale reference circles
    for level in [2, 4, 6, 8, 10]:
        circle = Circle((0, 0), level, transform=ax1.transData._b,
                       fill=False, edgecolor='#BDC3C7', linewidth=1, alpha=0.3)

    # Second subplot: Detailed assessment table
    ax2 = fig.add_subplot(122)
    ax2.axis('off')

    # Title for table
    ax2.text(0.5, 0.95, 'Detailed Capability Assessment',
            fontsize=48, fontweight='bold', ha='center', color='#2C3E50')

    ax2.text(0.5, 0.90, 'Strengths, weaknesses, and dependencies per domain',
            fontsize=38, ha='center', color='#34495E', style='italic')

    # Create assessment boxes
    y_start = 0.80
    y_spacing = 0.13

    for i, (domain, assessment, color) in enumerate(assessments):
        y_pos = y_start - (i * y_spacing)

        # Domain box
        ax2.text(0.15, y_pos, domain,
                fontsize=42, fontweight='bold', ha='center', va='center',
                color='white',
                bbox=dict(boxstyle='round,pad=0.8', facecolor=color,
                         edgecolor='white', linewidth=3))

        # Assessment text
        ax2.text(0.60, y_pos, assessment,
                fontsize=36, ha='center', va='center', color='#2C3E50')

        # Capability bar
        current_cap = capabilities['Overall Capability'][i] / 10
        bar_width = 0.25
        bar_height = 0.05

        # Background bar
        bg_rect = mpatches.FancyBboxPatch(
            (0.88, y_pos - bar_height/2), bar_width, bar_height,
            boxstyle="round,pad=0.005",
            facecolor='#ECF0F1',
            edgecolor='#BDC3C7',
            linewidth=2
        )
        ax2.add_patch(bg_rect)

        # Capability bar (filled portion)
        cap_rect = mpatches.FancyBboxPatch(
            (0.88, y_pos - bar_height/2), bar_width * current_cap, bar_height,
            boxstyle="round,pad=0.005",
            facecolor=color,
            edgecolor='white',
            linewidth=2
        )
        ax2.add_patch(cap_rect)

        # Capability number
        ax2.text(1.16, y_pos, f'{int(capabilities["Overall Capability"][i])}/10',
                fontsize=40, fontweight='bold', ha='left', va='center',
                color=color)

    # Key insights box at bottom
    ax2.text(0.5, 0.05,
            'Key Pattern: ~80% of MCF projects fail. Successes in mature tech and commercial applications.\n' +
            'Failures in cutting-edge, tacit-knowledge-heavy domains (advanced chips, jet engines).',
            fontsize=36, ha='center', va='center', color='#E74C3C',
            fontweight='semibold',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFEBEE',
                     edgecolor='#E74C3C', linewidth=3))

    # Capability legend
    legend_y = -0.10
    ax2.text(0.2, legend_y, 'Capability Scale:', fontsize=38,
            fontweight='bold', color='#2C3E50')

    capability_levels = [
        (0.4, '0-3: Weak/Dependent', '#E74C3C'),
        (0.6, '4-6: Moderate/Mixed', '#F39C12'),
        (0.8, '7-10: Strong/Leading', '#27AE60')
    ]

    for x, text, color in capability_levels:
        ax2.text(x, legend_y, text, fontsize=34, color=color, fontweight='bold')

    plt.tight_layout()

    # Save
    png_path = output_path / "slide11_20_tech_capabilities.png"
    svg_path = output_path / "slide11_20_tech_capabilities.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF TECHNOLOGY CAPABILITIES RADAR - SLIDES 11/20")
    print("="*80)
    print("\nCreating radar chart showing varying capabilities...\n")

    create_tech_capabilities_radar()

    print("\n" + "="*80)
    print("COMPLETE: Technology capabilities radar ready")
    print("="*80)
    print("\nFeatures:")
    print("  + Radar chart with 6 technology domains")
    print("  + Current vs. projected capabilities")
    print("  + Detailed assessment table")
    print("  + Capability bars per domain")
    print("  + 34-52pt fonts throughout")
