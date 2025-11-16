#!/usr/bin/env python3
"""
MCF Timeline Evolution Visualization
Shows governance layer development from 2015-2024
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


def load_timeline_data(data_path="data/mcf_timeline_2015_2024.json"):
    """Load MCF timeline database"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_timeline_evolution(output_dir="visualizations/governance"):
    """
    Prompt 2 - Variation 6: Timeline Evolution (2015-2024)
    Shows how governance layers developed over time
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timeline_data = load_timeline_data()
    events = timeline_data['events']
    layer_evolution = timeline_data['layer_evolution']

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(32, 20), facecolor='white')
    fig.subplots_adjust(hspace=0.3)

    # ===== TOP PANEL: Timeline with events =====

    # Layer colors
    layer_colors = {
        1: '#8b0000',
        2: '#C0392B',
        3: '#E74C3C',
        4: '#F39C12',
        5: '#F1C40F',
        6: '#27AE60'
    }

    # Period backgrounds
    periods = {
        'Foundation\n2015-2016': (2015, 2016.99, '#FFEBEE'),
        'Expansion\n2017-2019': (2017, 2019.99, '#E3F2FD'),
        'Consolidation\n2020-2021': (2020, 2021.99, '#FFF3E0'),
        'Intensification\n2022-2024': (2022, 2024.99, '#E8F5E9')
    }

    for period_name, (start, end, color) in periods.items():
        ax1.axvspan(start, end, alpha=0.15, color=color, zorder=0)
        mid = (start + end) / 2
        ax1.text(mid, 6.8, period_name, ha='center', va='top',
                fontsize=48, fontweight='bold', color='#2C3E50', alpha=0.7)

    # Plot events as points
    for event in events:
        year = event['year']
        layer = event['layer']
        impact = event['impact']

        # Size by impact
        size = {'low': 200, 'medium': 350, 'high': 500, 'critical': 700}.get(impact, 350)

        # Plot point
        ax1.scatter(year, layer, s=size, color=layer_colors[layer],
                   edgecolor='white', linewidth=2.5, zorder=3, alpha=0.85)

        # Add event label for critical/high impact events
        if impact in ['critical', 'high']:
            # Truncate long event names
            event_text = event['event']
            if len(event_text) > 40:
                event_text = event_text[:37] + '...'

            ax1.text(year, layer + 0.2, event_text,
                    fontsize=46, ha='center', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                             edgecolor=layer_colors[layer], alpha=0.9))

    # Styling
    ax1.set_xlim(2014.5, 2024.5)
    ax1.set_ylim(0.5, 7)
    ax1.set_xlabel('Year', fontsize=46, fontweight='bold', color='#2C3E50')
    ax1.set_ylabel('Governance Layer', fontsize=46, fontweight='bold', color='#2C3E50')
    ax1.set_title('MCF Governance Evolution Timeline (2015-2024)\nKey Milestones by Governance Layer',
                 fontsize=48, fontweight='bold', pad=25, color='#2C3E50')

    # Y-axis labels
    ax1.set_yticks([1, 2, 3, 4, 5, 6])
    ax1.set_yticklabels([
        'Layer 1\nStrategic',
        'Layer 2\nPolicy',
        'Layer 3\nLegal',
        'Layer 4\nCoordination',
        'Layer 5\nImplementation',
        'Layer 6\nExecution'
    ], fontsize=46, color='#2C3E50')

    ax1.tick_params(axis='x', labelsize=28, colors='#2C3E50')
    ax1.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Legend for impact
    legend_elements = [
        mpatches.Patch(facecolor='white', edgecolor='#2C3E50', linewidth=2,
                      label='● Critical Impact (700pt)'),
        mpatches.Patch(facecolor='white', edgecolor='#2C3E50', linewidth=2,
                      label='● High Impact (500pt)'),
        mpatches.Patch(facecolor='white', edgecolor='#2C3E50', linewidth=2,
                      label='● Medium Impact (350pt)')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=46,
              title='Event Impact', title_fontsize=48, framealpha=0.95)

    # ===== BOTTOM PANEL: Activity heatmap by layer over time =====

    years = list(range(2015, 2025))
    layers = ['Layer_1_Strategic', 'Layer_2_Policy', 'Layer_3_Legal',
              'Layer_4_Coordination', 'Layer_5_Implementation', 'Layer_6_Execution']

    # Build matrix
    matrix = np.zeros((len(layers), len(years)))
    for i, layer in enumerate(layers):
        for j, year in enumerate(years):
            matrix[i, j] = layer_evolution[layer].get(str(year), 0)

    # Create heatmap
    im = ax2.imshow(matrix, cmap='YlOrRd', aspect='auto', interpolation='nearest')

    # Add values in cells
    for i in range(len(layers)):
        for j in range(len(years)):
            value = int(matrix[i, j])
            if value > 0:
                ax2.text(j, i, str(value),
                        ha='center', va='center',
                        fontsize=48, fontweight='bold',
                        color='white' if value > 1 else '#2C3E50')

    # Styling
    ax2.set_xticks(np.arange(len(years)))
    ax2.set_yticks(np.arange(len(layers)))
    ax2.set_xticklabels(years, fontsize=48, color='#2C3E50')
    ax2.set_yticklabels([
        'Layer 1: Strategic Direction',
        'Layer 2: Policy Formulation',
        'Layer 3: Legal Framework',
        'Layer 4: Institutional Coordination',
        'Layer 5: Implementation Mechanisms',
        'Layer 6: Execution Entities'
    ], fontsize=46, color='#2C3E50')

    ax2.set_xlabel('Year', fontsize=46, fontweight='bold', color='#2C3E50')
    ax2.set_ylabel('Governance Layer', fontsize=46, fontweight='bold', color='#2C3E50')
    ax2.set_title('MCF Governance Activity Heatmap: Events per Layer per Year',
                 fontsize=46, fontweight='bold', pad=25, color='#2C3E50')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label('Number of Events', fontsize=44, fontweight='bold', color='#2C3E50')
    cbar.ax.tick_params(labelsize=26, colors='#2C3E50')

    # Period dividers
    for period_name, (start, end, color) in periods.items():
        start_idx = start - 2015
        end_idx = end - 2015
        ax2.axvspan(start_idx - 0.5, end_idx + 0.5, alpha=0.1,
                   color=color, zorder=0)

    # Save
    png_path = output_path / "mcf_timeline_evolution.png"
    svg_path = output_path / "mcf_timeline_evolution.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


def create_cumulative_layer_chart(output_dir="visualizations/governance"):
    """
    Additional timeline visualization: Cumulative governance development
    """
    output_path = Path(output_dir)

    timeline_data = load_timeline_data()
    layer_evolution = timeline_data['layer_evolution']

    # Create figure
    fig, ax = plt.subplots(figsize=(28, 16), facecolor='white')

    years = list(range(2015, 2025))
    layers = {
        'Layer_1_Strategic': ('#8b0000', 'Strategic Direction'),
        'Layer_2_Policy': ('#C0392B', 'Policy Formulation'),
        'Layer_3_Legal': ('#E74C3C', 'Legal Framework'),
        'Layer_4_Coordination': ('#F39C12', 'Institutional Coordination'),
        'Layer_5_Implementation': ('#F1C40F', 'Implementation Mechanisms'),
        'Layer_6_Execution': ('#27AE60', 'Execution Entities')
    }

    # Plot cumulative lines for each layer
    for layer, (color, label) in layers.items():
        values = [layer_evolution[layer].get(str(year), 0) for year in years]
        cumulative = np.cumsum(values)

        ax.plot(years, cumulative, marker='o', markersize=12, linewidth=4,
               color=color, label=label, alpha=0.85)

        # Add final value label
        ax.text(2024.2, cumulative[-1], str(int(cumulative[-1])),
               fontsize=48, fontweight='bold', color=color, va='center')

    # Styling
    ax.set_xlabel('Year', fontsize=46, fontweight='bold', color='#2C3E50')
    ax.set_ylabel('Cumulative Events', fontsize=46, fontweight='bold', color='#2C3E50')
    ax.set_title('MCF Governance Development: Cumulative Activity by Layer (2015-2024)',
                fontsize=48, fontweight='bold', pad=25, color='#2C3E50')

    ax.tick_params(axis='both', labelsize=28, colors='#2C3E50')
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.legend(loc='upper left', fontsize=48, title='Governance Layers',
             title_fontsize=44, framealpha=0.95)

    # Save
    png_path = output_path / "mcf_cumulative_layer_development.png"
    svg_path = output_path / "mcf_cumulative_layer_development.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING MCF TIMELINE EVOLUTION VISUALIZATIONS")
    print("=" * 80)
    print()

    print("1. Timeline Evolution with Events (Prompt 2 - Variation 6)...")
    create_timeline_evolution()
    print()

    print("2. Cumulative Layer Development Chart...")
    create_cumulative_layer_chart()
    print()

    print("=" * 80)
    print("TIMELINE VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print()
    print("Features:")
    print("  +24 MCF governance events (2015-2024)")
    print("  +Activity heatmap by layer and year")
    print("  +Period classifications (Foundation to Intensification)")
    print("  +Cumulative development tracking")
    print("  +26pt+ fonts throughout")
