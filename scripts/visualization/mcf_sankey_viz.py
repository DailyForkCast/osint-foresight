#!/usr/bin/env python3
"""
MCF Sankey Diagram Visualization
Creates technology flow diagrams showing foreign acquisition -> domestic processing -> military/civilian application
"""

import plotly.graph_objects as go
from pathlib import Path
import json

# Import our data
from mcf_network_data import TECHNOLOGY_FLOWS


def create_technology_flow_sankey(output_dir="visualizations"):
    """
    Create Sankey diagram showing technology flows in MCF ecosystem

    Flow pattern:
    Foreign Sources -> Domestic Processing -> Military/Civilian Application

    Args:
        output_dir: Directory for output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Build node list from flows
    nodes = set()
    for flow in TECHNOLOGY_FLOWS:
        nodes.add(flow['source'])
        nodes.add(flow['target'])

    # Create node index mapping
    node_list = sorted(list(nodes))
    node_index = {node: i for i, node in enumerate(node_list)}

    print(f"Technology Flow Sankey: {len(node_list)} nodes, {len(TECHNOLOGY_FLOWS)} flows")

    # Build Sankey data
    source_indices = [node_index[flow['source']] for flow in TECHNOLOGY_FLOWS]
    target_indices = [node_index[flow['target']] for flow in TECHNOLOGY_FLOWS]
    values = [flow['value'] for flow in TECHNOLOGY_FLOWS]
    colors = [flow.get('color', '#95A5A6') for flow in TECHNOLOGY_FLOWS]

    # Node colors by category
    node_colors = []
    for node in node_list:
        if 'Foreign' in node:
            node_colors.append('#E74C3C')  # Red - Foreign sources
        elif node in ['Chinese Academy of Sciences', 'University Defense Labs',
                      'State-Owned Enterprises', 'Talent Recruitment Programs']:
            node_colors.append('#3498DB')  # Blue - Domestic processing
        elif node in ['PLA Strategic Support Force',
                      'State Administration for Science, Technology and Industry for National Defense']:
            node_colors.append('#E67E22')  # Orange - Military application
        else:
            node_colors.append('#27AE60')  # Green - Civilian application

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_list,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=colors
        )
    )])

    fig.update_layout(
        title={
            'text': "MCF Technology Flow: Foreign Acquisition → Domestic Processing → Application",
            'font': {'size': 20, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=12, family='Arial, sans-serif'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1400,
        height=800
    )

    # Save outputs
    html_path = output_path / "mcf_technology_flow.html"
    png_path = output_path / "mcf_technology_flow.png"
    svg_path = output_path / "mcf_technology_flow.svg"

    fig.write_html(str(html_path))
    fig.write_image(str(png_path), width=1400, height=800, scale=2)
    fig.write_image(str(svg_path), width=1400, height=800, format='svg')

    print(f"[SAVED] HTML: {html_path}")
    print(f"[SAVED] PNG: {png_path}")
    print(f"[SAVED] SVG: {svg_path}")

    return str(html_path), str(png_path), str(svg_path)


def create_bri_initiative_flows(output_dir="visualizations"):
    """
    Create Sankey diagram for China's Four Global Initiatives
    Shows how different initiatives interconnect
    """
    output_path = Path(output_dir)

    # Define initiative flows
    initiatives = {
        'nodes': [
            # Central coordination
            'Central MCF Commission',
            'State Council',
            'Central Military Commission',

            # Four Global Initiatives
            'Belt and Road Initiative (BRI)',
            'Global Development Initiative (GDI)',
            'Global Security Initiative (GSI)',
            'Global Civilization Initiative (GCI)',

            # Implementation mechanisms
            'Infrastructure Projects',
            'Development Finance',
            'Technology Transfer',
            'Security Cooperation',
            'Cultural Exchange',

            # Strategic objectives
            'Economic Influence',
            'Technology Acquisition',
            'Security Presence',
            'Soft Power'
        ],
        'links': [
            # Central coordination to initiatives
            {'source': 'Central MCF Commission', 'target': 'Belt and Road Initiative (BRI)', 'value': 100},
            {'source': 'State Council', 'target': 'Global Development Initiative (GDI)', 'value': 80},
            {'source': 'Central MCF Commission', 'target': 'Global Security Initiative (GSI)', 'value': 90},
            {'source': 'State Council', 'target': 'Global Civilization Initiative (GCI)', 'value': 60},

            # Initiatives to mechanisms
            {'source': 'Belt and Road Initiative (BRI)', 'target': 'Infrastructure Projects', 'value': 120},
            {'source': 'Global Development Initiative (GDI)', 'target': 'Development Finance', 'value': 100},
            {'source': 'Belt and Road Initiative (BRI)', 'target': 'Technology Transfer', 'value': 80},
            {'source': 'Global Security Initiative (GSI)', 'target': 'Security Cooperation', 'value': 85},
            {'source': 'Global Civilization Initiative (GCI)', 'target': 'Cultural Exchange', 'value': 70},

            # Cross-initiative synergies
            {'source': 'Global Development Initiative (GDI)', 'target': 'Infrastructure Projects', 'value': 50},
            {'source': 'Global Security Initiative (GSI)', 'target': 'Technology Transfer', 'value': 60},

            # Mechanisms to strategic objectives
            {'source': 'Infrastructure Projects', 'target': 'Economic Influence', 'value': 110},
            {'source': 'Development Finance', 'target': 'Economic Influence', 'value': 90},
            {'source': 'Technology Transfer', 'target': 'Technology Acquisition', 'value': 100},
            {'source': 'Security Cooperation', 'target': 'Security Presence', 'value': 85},
            {'source': 'Cultural Exchange', 'target': 'Soft Power', 'value': 70},
            {'source': 'Infrastructure Projects', 'target': 'Security Presence', 'value': 40},
        ]
    }

    # Create node index
    node_index = {node: i for i, node in enumerate(initiatives['nodes'])}

    # Build Sankey data
    source_indices = [node_index[link['source']] for link in initiatives['links']]
    target_indices = [node_index[link['target']] for link in initiatives['links']]
    values = [link['value'] for link in initiatives['links']]

    # Color scheme
    node_colors = []
    for node in initiatives['nodes']:
        if 'Commission' in node or node == 'State Council':
            node_colors.append('#E74C3C')  # Red - Central coordination
        elif 'Initiative' in node:
            node_colors.append('#3498DB')  # Blue - Initiatives
        elif node in ['Infrastructure Projects', 'Development Finance',
                      'Technology Transfer', 'Security Cooperation', 'Cultural Exchange']:
            node_colors.append('#F39C12')  # Orange - Mechanisms
        else:
            node_colors.append('#27AE60')  # Green - Objectives

    # Link colors - gradient based on flow type
    link_colors = []
    for link in initiatives['links']:
        if 'Initiative' in link['target']:
            link_colors.append('rgba(231, 76, 60, 0.3)')  # Red tint - coordination flows
        elif link['target'] in ['Infrastructure Projects', 'Development Finance',
                                'Technology Transfer', 'Security Cooperation', 'Cultural Exchange']:
            link_colors.append('rgba(52, 152, 219, 0.3)')  # Blue tint - initiative flows
        else:
            link_colors.append('rgba(243, 156, 18, 0.3)')  # Orange tint - mechanism flows

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=initiatives['nodes'],
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        title={
            'text': "China's Four Global Initiatives: Coordination → Implementation → Strategic Objectives",
            'font': {'size': 24, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=22, family='Arial, sans-serif'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1600,
        height=900
    )

    # Save outputs
    html_path = output_path / "mcf_four_initiatives_flow.html"
    png_path = output_path / "mcf_four_initiatives_flow.png"
    svg_path = output_path / "mcf_four_initiatives_flow.svg"

    fig.write_html(str(html_path))
    fig.write_image(str(png_path), width=1600, height=900, scale=2)
    fig.write_image(str(svg_path), width=1600, height=900, format='svg')

    print(f"[SAVED] HTML: {html_path}")
    print(f"[SAVED] PNG: {png_path}")
    print(f"[SAVED] SVG: {svg_path}")

    return str(html_path), str(png_path), str(svg_path)


def create_sector_priority_sankey(output_dir="visualizations"):
    """
    Create Sankey showing Made in China 2025 sectors -> research -> applications
    """
    output_path = Path(output_dir)

    sectors = {
        'nodes': [
            # Made in China 2025 priority sectors
            'Information Technology',
            'Robotics & Automation',
            'Aerospace & Aviation',
            'Maritime Equipment',
            'New Energy Vehicles',
            'Power Equipment',
            'New Materials',
            'Biopharmaceuticals',

            # Research institutions
            'Chinese Academy of Sciences',
            'University Defense Labs',
            'State-Owned Enterprises',

            # Applications
            'Military Applications',
            'Civilian Applications',
            'Dual-Use Technologies'
        ],
        'links': [
            # Sectors to research institutions
            {'source': 'Information Technology', 'target': 'Chinese Academy of Sciences', 'value': 150},
            {'source': 'Information Technology', 'target': 'University Defense Labs', 'value': 120},
            {'source': 'Robotics & Automation', 'target': 'Chinese Academy of Sciences', 'value': 100},
            {'source': 'Robotics & Automation', 'target': 'State-Owned Enterprises', 'value': 90},
            {'source': 'Aerospace & Aviation', 'target': 'State-Owned Enterprises', 'value': 130},
            {'source': 'Aerospace & Aviation', 'target': 'University Defense Labs', 'value': 80},
            {'source': 'Maritime Equipment', 'target': 'State-Owned Enterprises', 'value': 110},
            {'source': 'New Energy Vehicles', 'target': 'State-Owned Enterprises', 'value': 100},
            {'source': 'New Materials', 'target': 'Chinese Academy of Sciences', 'value': 120},
            {'source': 'New Materials', 'target': 'University Defense Labs', 'value': 90},
            {'source': 'Biopharmaceuticals', 'target': 'Chinese Academy of Sciences', 'value': 80},

            # Research to applications
            {'source': 'Chinese Academy of Sciences', 'target': 'Military Applications', 'value': 200},
            {'source': 'Chinese Academy of Sciences', 'target': 'Dual-Use Technologies', 'value': 180},
            {'source': 'Chinese Academy of Sciences', 'target': 'Civilian Applications', 'value': 120},
            {'source': 'University Defense Labs', 'target': 'Military Applications', 'value': 180},
            {'source': 'University Defense Labs', 'target': 'Dual-Use Technologies', 'value': 110},
            {'source': 'State-Owned Enterprises', 'target': 'Military Applications', 'value': 150},
            {'source': 'State-Owned Enterprises', 'target': 'Civilian Applications', 'value': 180},
            {'source': 'State-Owned Enterprises', 'target': 'Dual-Use Technologies', 'value': 100},
        ]
    }

    # Create node index
    node_index = {node: i for i, node in enumerate(sectors['nodes'])}

    # Build Sankey data
    source_indices = [node_index[link['source']] for link in sectors['links']]
    target_indices = [node_index[link['target']] for link in sectors['links']]
    values = [link['value'] for link in sectors['links']]

    # Color scheme
    node_colors = []
    for node in sectors['nodes']:
        if node in ['Information Technology', 'Robotics & Automation', 'Aerospace & Aviation',
                    'Maritime Equipment', 'New Energy Vehicles', 'Power Equipment',
                    'New Materials', 'Biopharmaceuticals']:
            node_colors.append('#9B59B6')  # Purple - Priority sectors
        elif node in ['Chinese Academy of Sciences', 'University Defense Labs',
                      'State-Owned Enterprises']:
            node_colors.append('#3498DB')  # Blue - Research institutions
        else:
            node_colors.append('#E74C3C')  # Red - Applications

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=sectors['nodes'],
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(155, 89, 182, 0.3)'
        )
    )])

    fig.update_layout(
        title={
            'text': "Made in China 2025 Sectors → Research Institutions → Applications",
            'font': {'size': 20, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=12, family='Arial, sans-serif'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1500,
        height=850
    )

    # Save outputs
    html_path = output_path / "mcf_sector_priority_flow.html"
    png_path = output_path / "mcf_sector_priority_flow.png"
    svg_path = output_path / "mcf_sector_priority_flow.svg"

    fig.write_html(str(html_path))
    fig.write_image(str(png_path), width=1500, height=850, scale=2)
    fig.write_image(str(svg_path), width=1500, height=850, format='svg')

    print(f"[SAVED] HTML: {html_path}")
    print(f"[SAVED] PNG: {png_path}")
    print(f"[SAVED] SVG: {svg_path}")

    return str(html_path), str(png_path), str(svg_path)


if __name__ == "__main__":
    print("=" * 80)
    print("MCF SANKEY DIAGRAM VISUALIZATION")
    print("=" * 80)
    print()

    # Create technology flow diagram
    print("Creating technology flow Sankey diagram...")
    tech_html, tech_png, tech_svg = create_technology_flow_sankey()
    print()

    # Create Four Global Initiatives flow
    print("Creating Four Global Initiatives flow diagram...")
    init_html, init_png, init_svg = create_bri_initiative_flows()
    print()

    # Create sector priority flow
    print("Creating Made in China 2025 sector priority flow...")
    sector_html, sector_png, sector_svg = create_sector_priority_sankey()
    print()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print()
    print("Note: Sankey diagrams are also available as interactive HTML files")
    print("      that can be opened in a web browser for exploration.")
