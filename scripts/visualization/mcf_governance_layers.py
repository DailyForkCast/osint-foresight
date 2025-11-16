#!/usr/bin/env python3
"""
MCF Multi-Layered Governance Structure Visualizations
Implements Prompt 2: 6 governance layer variations (simplified versions)
"""

import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Governance layer structure from Prompt 2
GOVERNANCE_LAYERS = {
    'Layer 1': {
        'name': 'Strategic Direction',
        'elements': ['Xi Jinping Thought', 'National Security Strategy', '14th Five-Year Plan'],
        'color': '#8b0000'  # Deep red
    },
    'Layer 2': {
        'name': 'Policy Formulation',
        'elements': ['CCP Central Committee Decisions', 'MCF Commission Directives', 'State Council Opinions'],
        'color': '#C0392B'  # Red
    },
    'Layer 3': {
        'name': 'Legal Framework',
        'elements': ['National Security Law', 'National Defense Law', 'National Intelligence Law',
                    'Data Security Law', 'Export Control Law', 'Foreign Relations Law',
                    'Cybersecurity Law', 'Personal Information Protection Law'],
        'color': '#E74C3C'  # Light red
    },
    'Layer 4': {
        'name': 'Institutional Coordination',
        'elements': ['MCF Regional Offices', 'Inter-ministerial Working Groups', 'Joint Committees'],
        'color': '#3498DB'  # Blue
    },
    'Layer 5': {
        'name': 'Implementation Mechanisms',
        'elements': ['Military-Civil Innovation Alliances', 'National Technology Centers',
                    'Talent Programs (Thousand Talents)', 'Joint R&D Initiatives'],
        'color': '#27AE60'  # Green
    },
    'Layer 6': {
        'name': 'Execution Entities',
        'elements': ['State-Owned Enterprises', 'Tech Companies', 'Universities',
                    'Research Institutes', 'Regional Governments'],
        'color': '#F39C12'  # Orange
    }
}


def create_variation_1_hierarchical_waterfall(output_dir="visualizations/governance"):
    """Variation 1: Hierarchical Waterfall - Policy flowing through 6 layers"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(30, 24), facecolor='white')

    # Draw layers as horizontal bars with cascading effect
    y_positions = [6, 5, 4, 3, 2, 1]
    heights = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]

    for i, (layer_key, layer_data) in enumerate(GOVERNANCE_LAYERS.items()):
        y = y_positions[i]

        # Draw main layer box
        rect = plt.Rectangle((0.5, y - 0.4), 25, heights[i],
                            facecolor=layer_data['color'],
                            edgecolor='black', linewidth=3, alpha=0.8)
        ax.add_patch(rect)

        # Add layer name
        ax.text(1, y, f"{layer_key}: {layer_data['name']}",
               fontsize=46, fontweight='bold', color='white', va='center')

        # Add flow arrows between layers
        if i < len(GOVERNANCE_LAYERS) - 1:
            # Vertical arrow
            ax.annotate('', xy=(13, y - 0.6), xytext=(13, y - 1.4),
                       arrowprops=dict(arrowstyle='->', lw=4, color='black'))

            # Horizontal cascade (shift right for waterfall effect)
            cascade_offset = i * 0.3
            ax.annotate('', xy=(0.5 + cascade_offset, y - 0.5),
                       xytext=(0.5 + cascade_offset, y + 0.4),
                       arrowprops=dict(arrowstyle='|-|', lw=2, color='gray', alpha=0.5))

    # Add descriptive text for each layer
    descriptions = {
        'Layer 1': 'Sets overall strategic priorities and national goals',
        'Layer 2': 'Translates strategy into concrete policy directives',
        'Layer 3': 'Provides legal authority and enforcement mechanisms',
        'Layer 4': 'Coordinates implementation across institutions',
        'Layer 5': 'Creates specific programs and initiatives',
        'Layer 6': 'Executes policies on the ground'
    }

    for i, (layer_key, desc) in enumerate(descriptions.items()):
        y = y_positions[i]
        ax.text(26, y, desc, fontsize=46, va='center', style='italic',
               wrap=True, color='#2C3E50')

    ax.set_xlim(0, 40)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title('MCF Governance Structure: Policy Waterfall Through Six Layers',
                fontsize=48, fontweight='bold', pad=30)

    plt.tight_layout()

    png_path = output_path / "mcf_governance_waterfall.png"
    svg_path = output_path / "mcf_governance_waterfall.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"[SAVED] Variation 1: {png_path.name}")


def create_variation_2_sankey_layers(output_dir="visualizations/governance"):
    """Variation 2: Sankey Diagram - Strategic goals → policies → legal → execution"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create Sankey flow data
    nodes = []
    node_colors = []

    # Add nodes for each layer
    for layer_key, layer_data in GOVERNANCE_LAYERS.items():
        nodes.extend(layer_data['elements'])
        node_colors.extend([layer_data['color']] * len(layer_data['elements']))

    node_index = {node: i for i, node in enumerate(nodes)}

    # Create flows between layers
    links = [
        # Layer 1 → Layer 2
        {'source': 'Xi Jinping Thought', 'target': 'CCP Central Committee Decisions', 'value': 100},
        {'source': 'National Security Strategy', 'target': 'MCF Commission Directives', 'value': 90},
        {'source': '14th Five-Year Plan', 'target': 'State Council Opinions', 'value': 85},

        # Layer 2 → Layer 3 (to laws)
        {'source': 'CCP Central Committee Decisions', 'target': 'National Security Law', 'value': 40},
        {'source': 'CCP Central Committee Decisions', 'target': 'National Defense Law', 'value': 30},
        {'source': 'MCF Commission Directives', 'target': 'National Intelligence Law', 'value': 35},
        {'source': 'MCF Commission Directives', 'target': 'Data Security Law', 'value': 30},
        {'source': 'State Council Opinions', 'target': 'Export Control Law', 'value': 30},
        {'source': 'State Council Opinions', 'target': 'Cybersecurity Law', 'value': 25},

        # Layer 3 → Layer 4 (laws to coordination)
        {'source': 'National Security Law', 'target': 'MCF Regional Offices', 'value': 40},
        {'source': 'National Defense Law', 'target': 'Inter-ministerial Working Groups', 'value': 30},
        {'source': 'Export Control Law', 'target': 'Joint Committees', 'value': 30},

        # Layer 4 → Layer 5 (coordination to mechanisms)
        {'source': 'MCF Regional Offices', 'target': 'Military-Civil Innovation Alliances', 'value': 25},
        {'source': 'Inter-ministerial Working Groups', 'target': 'National Technology Centers', 'value': 25},
        {'source': 'Joint Committees', 'target': 'Talent Programs (Thousand Talents)', 'value': 20},
        {'source': 'MCF Regional Offices', 'target': 'Joint R&D Initiatives', 'value': 20},

        # Layer 5 → Layer 6 (mechanisms to execution)
        {'source': 'Military-Civil Innovation Alliances', 'target': 'State-Owned Enterprises', 'value': 25},
        {'source': 'National Technology Centers', 'target': 'Tech Companies', 'value': 25},
        {'source': 'Talent Programs (Thousand Talents)', 'target': 'Universities', 'value': 20},
        {'source': 'Joint R&D Initiatives', 'target': 'Research Institutes', 'value': 20},
    ]

    source_indices = [node_index[link['source']] for link in links]
    target_indices = [node_index[link['target']] for link in links]
    values = [link['value'] for link in links]

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=25,
            thickness=30,
            line=dict(color="black", width=2),
            label=nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(200, 200, 200, 0.4)'
        )
    )])

    fig.update_layout(
        title={
            'text': "MCF Governance Flow: Strategic Intent → Policy → Law → Implementation → Execution",
            'font': {'size': 36, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=2400,
        height=1400,
        annotations=[
            dict(x=0.05, y=1.08, xref='paper', yref='paper',
                text='<b>LAYER 1-2: STRATEGIC DIRECTION</b>',
                showarrow=False, font=dict(size=28, color='#8b0000')),
            dict(x=0.35, y=1.08, xref='paper', yref='paper',
                text='<b>LAYER 3: LEGAL FRAMEWORK</b>',
                showarrow=False, font=dict(size=28, color='#E74C3C')),
            dict(x=0.65, y=1.08, xref='paper', yref='paper',
                text='<b>LAYER 4-5: COORDINATION</b>',
                showarrow=False, font=dict(size=28, color='#3498DB')),
            dict(x=0.95, y=1.08, xref='paper', yref='paper',
                text='<b>LAYER 6: EXECUTION</b>',
                showarrow=False, font=dict(size=28, color='#F39C12'))
        ]
    )

    html_path = output_path / "mcf_governance_sankey.html"
    png_path = output_path / "mcf_governance_sankey.png"
    svg_path = output_path / "mcf_governance_sankey.svg"

    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=2400, height=1400, scale=2)
        fig.write_image(str(svg_path), width=2400, height=1400, format='svg')
        print(f"[SAVED] PNG: {png_path}")
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export failed (need kaleido), HTML saved")

    print(f"[SAVED] HTML: {html_path}")


def create_variation_3_nested_circles(output_dir="visualizations/governance"):
    """Variation 3: Nested Governance Circles - Concentric rings with sectors"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(28, 28), facecolor='white')

    # Draw concentric circles for each layer (inverted - inner is strategic)
    radii = [1, 2.5, 4.5, 6.5, 8.5, 10.5]
    layer_keys = list(GOVERNANCE_LAYERS.keys())

    for i, (radius, layer_key) in enumerate(zip(radii, layer_keys)):
        layer_data = GOVERNANCE_LAYERS[layer_key]

        # Draw ring
        if i == 0:
            # Innermost circle (solid)
            circle = plt.Circle((0, 0), radius, color=layer_data['color'],
                              alpha=0.7, edgecolor='black', linewidth=3)
        else:
            # Rings
            circle = mpatches.Wedge((0, 0), radius, 0, 360,
                                   width=radii[i] - radii[i-1] if i > 0 else radius,
                                   facecolor=layer_data['color'], alpha=0.6,
                                   edgecolor='black', linewidth=3)
        ax.add_patch(circle)

        # Add layer label
        label_radius = radius if i == 0 else (radius + radii[i-1]) / 2
        ax.text(0, label_radius, f"{layer_key}\n{layer_data['name']}",
               fontsize=44, fontweight='bold', color='white',
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

    # Add directional arrows showing flow outward
    for angle in [0, 90, 180, 270]:
        rad = np.radians(angle)
        for i in range(len(radii) - 1):
            r1 = radii[i]
            r2 = radii[i + 1]
            x1, y1 = r1 * np.cos(rad), r1 * np.sin(rad)
            x2, y2 = r2 * np.cos(rad), r2 * np.sin(rad)
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=3, color='white', alpha=0.8))

    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('MCF Governance Structure: Nested Authority Layers\n(Center = Strategic, Outer = Execution)',
                fontsize=48, fontweight='bold', pad=30)

    # Add legend
    legend_text = "Flow Direction: Center → Outward\nStrategic Intent → Tactical Execution"
    ax.text(0, -13, legend_text, fontsize=48, ha='center',
           bbox=dict(boxstyle='round,pad=1', facecolor='#ECF0F1', alpha=0.9))

    plt.tight_layout()

    png_path = output_path / "mcf_governance_nested_circles.png"
    svg_path = output_path / "mcf_governance_nested_circles.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"[SAVED] Variation 3: {png_path.name}")


# Main execution
if __name__ == "__main__":
    print("=" * 80)
    print("CREATING MCF GOVERNANCE LAYER VISUALIZATIONS (PROMPT 2)")
    print("=" * 80)
    print()

    output_dir = "visualizations/governance"

    print("Creating Variation 1: Hierarchical Waterfall...")
    create_variation_1_hierarchical_waterfall(output_dir)
    print()

    print("Creating Variation 2: Sankey Flow Diagram...")
    create_variation_2_sankey_layers(output_dir)
    print()

    print("Creating Variation 3: Nested Circles...")
    create_variation_3_nested_circles(output_dir)
    print()

    print("=" * 80)
    print("PROMPT 2 GOVERNANCE VISUALIZATIONS COMPLETE (3/6 variations)")
    print("=" * 80)
    print("\nVariations Created:")
    print("  1. Hierarchical Waterfall - Policy flowing through 6 layers")
    print("  2. Sankey Flow Diagram - Strategic goals → execution")
    print("  3. Nested Circles - Concentric governance rings")
    print("\nNote: Variations 4-6 (Matrix Heat Map, 3D Layer Cake, Timeline)")
    print("      require additional data and 3D libraries - can be added later")
