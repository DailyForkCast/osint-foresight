#!/usr/bin/env python3
"""
Simplified MCF Sankey Diagrams
Creates clear, easy-to-understand flow visualizations
"""

import plotly.graph_objects as go
from pathlib import Path


def create_simple_technology_pipeline(output_dir="visualizations"):
    """
    Create simple 3-stage technology pipeline
    Foreign → Chinese Processing → Application
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Simple linear flow
    flows = {
        'nodes': [
            # Stage 1: Foreign Sources
            'Foreign Technology',

            # Stage 2: Chinese Processing
            'Chinese Academy of Sciences',
            'University Defense Labs',
            'State-Owned Enterprises',

            # Stage 3: Applications
            'PLA Military',
            'Civilian Industry'
        ],
        'links': [
            # Foreign → Processing
            {'source': 'Foreign Technology', 'target': 'Chinese Academy of Sciences', 'value': 150},
            {'source': 'Foreign Technology', 'target': 'University Defense Labs', 'value': 120},
            {'source': 'Foreign Technology', 'target': 'State-Owned Enterprises', 'value': 130},

            # Processing → Applications
            {'source': 'Chinese Academy of Sciences', 'target': 'PLA Military', 'value': 85},
            {'source': 'Chinese Academy of Sciences', 'target': 'Civilian Industry', 'value': 65},
            {'source': 'University Defense Labs', 'target': 'PLA Military', 'value': 90},
            {'source': 'University Defense Labs', 'target': 'Civilian Industry', 'value': 30},
            {'source': 'State-Owned Enterprises', 'target': 'PLA Military', 'value': 70},
            {'source': 'State-Owned Enterprises', 'target': 'Civilian Industry', 'value': 60},
        ]
    }

    node_index = {node: i for i, node in enumerate(flows['nodes'])}

    source_indices = [node_index[link['source']] for link in flows['links']]
    target_indices = [node_index[link['target']] for link in flows['links']]
    values = [link['value'] for link in flows['links']]

    # Color nodes by stage
    node_colors = [
        '#E74C3C',  # Foreign (red)
        '#3498DB', '#3498DB', '#3498DB',  # Processing (blue)
        '#E67E22', '#27AE60'  # Applications (orange, green)
    ]

    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=25,
            thickness=30,
            line=dict(color="black", width=1.5),
            label=flows['nodes'],
            color=node_colors,
            x=[0.05, 0.4, 0.4, 0.4, 0.95, 0.95],  # Manual positioning for clarity
            y=[0.5, 0.1, 0.5, 0.9, 0.3, 0.7]
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
            'text': "MCF Technology Pipeline: Acquisition → Processing → Application",
            'font': {'size': 44, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=2000,
        height=900,
        annotations=[
            dict(
                x=0.05, y=1.05, xref='paper', yref='paper',
                text='<b>STAGE 1: ACQUISITION</b>',
                showarrow=False, font=dict(size=30, color='#E74C3C')
            ),
            dict(
                x=0.4, y=1.05, xref='paper', yref='paper',
                text='<b>STAGE 2: PROCESSING</b>',
                showarrow=False, font=dict(size=30, color='#3498DB')
            ),
            dict(
                x=0.95, y=1.05, xref='paper', yref='paper',
                text='<b>STAGE 3: APPLICATION</b>',
                showarrow=False, font=dict(size=30, color='#E67E22')
            )
        ]
    )

    # Save
    html_path = output_path / "mcf_pipeline_simple.html"
    png_path = output_path / "mcf_pipeline_simple.png"
    svg_path = output_path / "mcf_pipeline_simple.svg"

    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=2000, height=900, scale=2)
        fig.write_image(str(svg_path), width=2000, height=900, format='svg')
        print(f"[SAVED] PNG: {png_path}")
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export failed, HTML saved")

    print(f"[SAVED] HTML: {html_path}")

    return str(html_path)


def create_four_initiatives_simplified(output_dir="visualizations"):
    """
    Simplified Four Global Initiatives - clearer structure
    """
    output_path = Path(output_dir)

    flows = {
        'nodes': [
            # Initiatives
            'Belt and Road Initiative',
            'Global Development Initiative',
            'Global Security Initiative',
            'Global Civilization Initiative',

            # Mechanisms
            'Infrastructure',
            'Finance',
            'Technology',
            'Security',
            'Culture',

            # Objectives
            'Economic Influence',
            'Tech Acquisition',
            'Security Presence',
            'Soft Power'
        ],
        'links': [
            # Initiatives → Mechanisms
            {'source': 'Belt and Road Initiative', 'target': 'Infrastructure', 'value': 120},
            {'source': 'Belt and Road Initiative', 'target': 'Technology', 'value': 80},
            {'source': 'Global Development Initiative', 'target': 'Finance', 'value': 100},
            {'source': 'Global Development Initiative', 'target': 'Infrastructure', 'value': 50},
            {'source': 'Global Security Initiative', 'target': 'Security', 'value': 90},
            {'source': 'Global Security Initiative', 'target': 'Technology', 'value': 60},
            {'source': 'Global Civilization Initiative', 'target': 'Culture', 'value': 80},

            # Mechanisms → Objectives
            {'source': 'Infrastructure', 'target': 'Economic Influence', 'value': 120},
            {'source': 'Infrastructure', 'target': 'Security Presence', 'value': 50},
            {'source': 'Finance', 'target': 'Economic Influence', 'value': 100},
            {'source': 'Technology', 'target': 'Tech Acquisition', 'value': 140},
            {'source': 'Security', 'target': 'Security Presence', 'value': 90},
            {'source': 'Culture', 'target': 'Soft Power', 'value': 80},
        ]
    }

    node_index = {node: i for i, node in enumerate(flows['nodes'])}

    source_indices = [node_index[link['source']] for link in flows['links']]
    target_indices = [node_index[link['target']] for link in flows['links']]
    values = [link['value'] for link in flows['links']]

    # Color by stage
    node_colors = [
        '#3498DB', '#3498DB', '#3498DB', '#3498DB',  # Initiatives (blue)
        '#F39C12', '#F39C12', '#F39C12', '#F39C12', '#F39C12',  # Mechanisms (orange)
        '#27AE60', '#27AE60', '#27AE60', '#27AE60'  # Objectives (green)
    ]

    # Manual positioning for clarity
    x_positions = [
        0.05, 0.05, 0.05, 0.05,  # Initiatives (left)
        0.5, 0.5, 0.5, 0.5, 0.5,  # Mechanisms (middle)
        0.95, 0.95, 0.95, 0.95   # Objectives (right)
    ]

    y_positions = [
        0.2, 0.4, 0.6, 0.8,  # Initiatives
        0.1, 0.3, 0.5, 0.7, 0.9,  # Mechanisms
        0.2, 0.4, 0.6, 0.8   # Objectives
    ]

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=1.5),
            label=flows['nodes'],
            color=node_colors,
            x=x_positions,
            y=y_positions
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(200, 200, 200, 0.3)'
        )
    )])

    fig.update_layout(
        title={
            'text': "China's Four Global Initiatives: Strategy → Mechanisms → Goals",
            'font': {'size': 44, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=2000,
        height=1000,
        annotations=[
            dict(
                x=0.05, y=1.05, xref='paper', yref='paper',
                text='<b>INITIATIVES</b>',
                showarrow=False, font=dict(size=30, color='#3498DB')
            ),
            dict(
                x=0.5, y=1.05, xref='paper', yref='paper',
                text='<b>MECHANISMS</b>',
                showarrow=False, font=dict(size=30, color='#F39C12')
            ),
            dict(
                x=0.95, y=1.05, xref='paper', yref='paper',
                text='<b>STRATEGIC GOALS</b>',
                showarrow=False, font=dict(size=30, color='#27AE60')
            )
        ]
    )

    html_path = output_path / "mcf_initiatives_simple.html"
    png_path = output_path / "mcf_initiatives_simple.png"
    svg_path = output_path / "mcf_initiatives_simple.svg"

    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=2000, height=1000, scale=2)
        fig.write_image(str(svg_path), width=2000, height=1000, format='svg')
        print(f"[SAVED] PNG: {png_path}")
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export failed, HTML saved")

    print(f"[SAVED] HTML: {html_path}")

    return str(html_path)


def create_dual_use_flow(output_dir="visualizations"):
    """
    Simple dual-use technology flow
    Research → Military & Civilian
    """
    output_path = Path(output_dir)

    flows = {
        'nodes': [
            'Research Institutions',
            'Military Application',
            'Dual-Use Technology',
            'Civilian Application'
        ],
        'links': [
            {'source': 'Research Institutions', 'target': 'Military Application', 'value': 100},
            {'source': 'Research Institutions', 'target': 'Dual-Use Technology', 'value': 120},
            {'source': 'Research Institutions', 'target': 'Civilian Application', 'value': 80},
            {'source': 'Dual-Use Technology', 'target': 'Military Application', 'value': 70},
            {'source': 'Dual-Use Technology', 'target': 'Civilian Application', 'value': 50},
        ]
    }

    node_index = {node: i for i, node in enumerate(flows['nodes'])}

    source_indices = [node_index[link['source']] for link in flows['links']]
    target_indices = [node_index[link['target']] for link in flows['links']]
    values = [link['value'] for link in flows['links']]

    node_colors = ['#3498DB', '#E74C3C', '#F39C12', '#27AE60']

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=30,
            thickness=35,
            line=dict(color="black", width=2),
            label=flows['nodes'],
            color=node_colors,
            x=[0.1, 0.9, 0.5, 0.9],
            y=[0.5, 0.2, 0.5, 0.8]
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
            'text': "MCF Dual-Use Technology Flow",
            'font': {'size': 44, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1800,
        height=800
    )

    html_path = output_path / "mcf_dual_use_simple.html"
    png_path = output_path / "mcf_dual_use_simple.png"
    svg_path = output_path / "mcf_dual_use_simple.svg"

    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=1800, height=800, scale=2)
        fig.write_image(str(svg_path), width=1800, height=800, format='svg')
        print(f"[SAVED] PNG: {png_path}")
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export failed, HTML saved")

    print(f"[SAVED] HTML: {html_path}")

    return str(html_path)


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING SIMPLIFIED SANKEY DIAGRAMS")
    print("=" * 80)
    print()

    print("1. Simple Technology Pipeline...")
    create_simple_technology_pipeline()
    print()

    print("2. Four Global Initiatives (Simplified)...")
    create_four_initiatives_simplified()
    print()

    print("3. Dual-Use Technology Flow...")
    create_dual_use_flow()
    print()

    print("=" * 80)
    print("COMPLETE - Simplified Sankey diagrams created")
    print("=" * 80)
    print()
    print("These diagrams are:")
    print("  - Linear flows (left to right)")
    print("  - Clear stage separation")
    print("  - Large fonts (28-36pt minimum)")
    print("  - Minimal crossing flows")
    print("  - Easy to understand")
