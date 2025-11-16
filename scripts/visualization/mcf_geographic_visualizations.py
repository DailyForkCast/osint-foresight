#!/usr/bin/env python3
"""
MCF Geographic Visualizations
Creates world maps showing BRI projects and technology transfer flows
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import numpy as np


def load_bri_database(data_path="data/bri_projects_database.json"):
    """Load BRI projects database"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_bri_global_flow_map(output_dir="visualizations"):
    """
    Prompt 3 - Variation 4: Global Flow Map
    World map showing BRI projects with flows from China
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load BRI data
    bri_data = load_bri_database()
    projects = bri_data['projects']

    # China's center point
    china_lat, china_lon = 35.8617, 104.1954

    # Prepare project data
    lats = [p['lat'] for p in projects]
    lons = [p['lon'] for p in projects]
    names = [p['name'] for p in projects]
    countries = [p['country'] for p in projects]
    sectors = [p['sector'] for p in projects]
    values = [p['value_usd'] / 1e9 for p in projects]  # Convert to billions
    initiatives = [p['initiative'] for p in projects]

    # Color mapping by initiative
    initiative_colors = {
        'BRI_Traditional': '#3498DB',
        'Digital_Silk_Road': '#9B59B6',
        'Health_Silk_Road': '#E74C3C',
        'Space_Information_Corridor': '#F39C12',
        'Polar_Silk_Road': '#1ABC9C',
        'Green_BRI': '#27AE60'
    }

    colors = [initiative_colors.get(p['initiative'], '#95A5A6') for p in projects]

    # Create figure
    fig = go.Figure()

    # Add flow lines from China to each project
    for i, project in enumerate(projects):
        fig.add_trace(go.Scattergeo(
            lon=[china_lon, project['lon']],
            lat=[china_lat, project['lat']],
            mode='lines',
            line=dict(width=1, color=colors[i]),
            opacity=0.4,
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add project markers
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        mode='markers',
        marker=dict(
            size=[max(8, min(v * 2, 40)) for v in values],  # Size by value, 8-40px
            color=colors,
            line=dict(width=1, color='white'),
            sizemode='diameter'
        ),
        text=[f"<b>{name}</b><br>{country}<br>{sector}<br>${value:.1f}B USD"
              for name, country, sector, value in zip(names, countries, sectors, values)],
        hoverinfo='text',
        name='BRI Projects',
        showlegend=False
    ))

    # Add China marker
    fig.add_trace(go.Scattergeo(
        lon=[china_lon],
        lat=[china_lat],
        mode='markers',
        marker=dict(
            size=30,
            color='#E74C3C',
            symbol='star',
            line=dict(width=2, color='white')
        ),
        text='<b>CHINA</b><br>BRI Origin',
        hoverinfo='text',
        name='China',
        showlegend=False
    ))

    # Create legend manually with annotations
    legend_items = [
        ('BRI Traditional Infrastructure', '#3498DB'),
        ('Digital Silk Road', '#9B59B6'),
        ('Health Silk Road', '#E74C3C'),
        ('Space Information Corridor', '#F39C12'),
        ('Polar Silk Road', '#1ABC9C'),
        ('Green BRI', '#27AE60')
    ]

    annotations = []
    for i, (label, color) in enumerate(legend_items):
        annotations.append(dict(
            x=0.02,
            y=0.98 - (i * 0.06),
            xref='paper',
            yref='paper',
            text=f'<b>●</b> {label}',
            showarrow=False,
            font=dict(size=28, color=color, family='Arial, sans-serif'),
            align='left',
            xanchor='left'
        ))

    fig.update_layout(
        title={
            'text': "Belt and Road Initiative: Global Infrastructure Network<br><sub>Project flows from China across 81 countries</sub>",
            'font': {'size': 48, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top'
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#F5F5F5',
            showocean=True,
            oceancolor='#E8F4F8',
            showcountries=True,
            countrycolor='#CCCCCC',
            coastlinecolor='#999999',
            showlakes=True,
            lakecolor='#E8F4F8',
            bgcolor='white'
        ),
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        width=2400,
        height=1400,
        paper_bgcolor='white',
        annotations=annotations,
        margin=dict(l=0, r=0, t=120, b=0)
    )

    # Save outputs
    html_path = output_path / "bri_global_flow_map.html"
    png_path = output_path / "bri_global_flow_map.png"
    svg_path = output_path / "bri_global_flow_map.svg"

    fig.write_html(str(html_path))
    print(f"[SAVED] HTML: {html_path}")

    try:
        fig.write_image(str(png_path), width=2400, height=1400, scale=2)
        print(f"[SAVED] PNG: {png_path}")
        fig.write_image(str(svg_path), width=2400, height=1400, format='svg')
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export requires kaleido: {e}")

    return str(html_path)


def create_tech_transfer_heat_map(output_dir="visualizations"):
    """
    Prompt 4 - Variation 6: Geographic Heat Map
    World map showing technology transfer source countries with flow arrows to China
    """
    output_path = Path(output_dir)

    # Load tech transfer data
    with open("data/tech_transfer_cases.json", 'r', encoding='utf-8') as f:
        tech_data = json.load(f)

    cases = tech_data['cases']

    # Country coordinates (major source countries)
    country_coords = {
        'United States': (37.0902, -95.7129),
        'Germany': (51.1657, 10.4515),
        'European Union': (50.8503, 4.3517),  # Brussels
        'Netherlands': (52.1326, 5.2913),
        'United Kingdom': (55.3781, -3.4360),
        'France': (46.2276, 2.2137),
        'South Korea': (35.9078, 127.7669),
        'Russia': (61.5240, 105.3188),
        'Canada': (56.1304, -106.3468),
        'Israel': (31.0461, 34.8516),
        'Switzerland': (46.8182, 8.2275),
        'Japan': (36.2048, 138.2529),
        'Global': (20.0, 0.0)  # Midpoint
    }

    china_lat, china_lon = 35.8617, 104.1954

    # Count transfers by country and channel
    country_volumes = {}
    for case in cases:
        country = case['source_country']
        channel = case['channel']

        if country not in country_volumes:
            country_volumes[country] = {'licit': 0, 'gray': 0, 'illicit': 0, 'total': 0}

        country_volumes[country][channel] += case['volume']
        country_volumes[country]['total'] += case['volume']

    # Create figure
    fig = go.Figure()

    # Add flow arrows by channel
    channel_colors = {
        'licit': '#27AE60',
        'gray': '#F39C12',
        'illicit': '#E74C3C'
    }

    for country, volumes in country_volumes.items():
        if country in country_coords:
            lat, lon = country_coords[country]

            # Draw flows for each channel
            for channel, volume in volumes.items():
                if channel != 'total' and volume > 0:
                    fig.add_trace(go.Scattergeo(
                        lon=[lon, china_lon],
                        lat=[lat, china_lat],
                        mode='lines',
                        line=dict(
                            width=max(2, volume / 30),
                            color=channel_colors[channel]
                        ),
                        opacity=0.6,
                        showlegend=False,
                        hoverinfo='skip'
                    ))

    # Add source country markers
    for country, volumes in country_volumes.items():
        if country in country_coords:
            lat, lon = country_coords[country]

            # Determine dominant channel
            dominant = max(volumes, key=lambda k: volumes[k] if k != 'total' else 0)

            fig.add_trace(go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode='markers+text',
                marker=dict(
                    size=max(15, min(volumes['total'] / 10, 50)),
                    color=channel_colors.get(dominant, '#95A5A6'),
                    line=dict(width=2, color='white')
                ),
                text=country if volumes['total'] > 100 else '',
                textposition='top center',
                textfont=dict(size=26, family='Arial, sans-serif', color='#2C3E50'),
                hovertext=f"<b>{country}</b><br>Total Volume: {volumes['total']}<br>"
                          f"Licit: {volumes['licit']}<br>"
                          f"Gray: {volumes['gray']}<br>"
                          f"Illicit: {volumes['illicit']}",
                hoverinfo='text',
                showlegend=False
            ))

    # Add China marker
    fig.add_trace(go.Scattergeo(
        lon=[china_lon],
        lat=[china_lat],
        mode='markers+text',
        marker=dict(
            size=45,
            color='#C0392B',
            symbol='star',
            line=dict(width=3, color='white')
        ),
        text='CHINA',
        textposition='bottom center',
        textfont=dict(size=32, family='Arial, sans-serif', color='#2C3E50', weight='bold'),
        hovertext='<b>CHINA</b><br>Technology Transfer Destination',
        hoverinfo='text',
        showlegend=False
    ))

    # Legend
    legend_annotations = [
        dict(x=0.02, y=0.98, xref='paper', yref='paper',
             text='<b style="font-size:30px">Transfer Channels:</b>',
             showarrow=False, font=dict(size=30, color='#2C3E50', family='Arial'),
             align='left', xanchor='left'),
        dict(x=0.02, y=0.92, xref='paper', yref='paper',
             text='<b>━━</b> Licit (Legal acquisition)',
             showarrow=False, font=dict(size=28, color='#27AE60', family='Arial'),
             align='left', xanchor='left'),
        dict(x=0.02, y=0.87, xref='paper', yref='paper',
             text='<b>━━</b> Gray Zone (Exploitative)',
             showarrow=False, font=dict(size=28, color='#F39C12', family='Arial'),
             align='left', xanchor='left'),
        dict(x=0.02, y=0.82, xref='paper', yref='paper',
             text='<b>━━</b> Illicit (Espionage/Theft)',
             showarrow=False, font=dict(size=28, color='#E74C3C', family='Arial'),
             align='left', xanchor='left')
    ]

    fig.update_layout(
        title={
            'text': "Technology Transfer to China: Global Sources and Methods<br>"
                   "<sub>Flow volumes by channel (licit, gray zone, illicit)</sub>",
            'font': {'size': 48, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top'
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#F8F9FA',
            showocean=True,
            oceancolor='#E3F2FD',
            showcountries=True,
            countrycolor='#DDDDDD',
            coastlinecolor='#AAAAAA',
            bgcolor='white'
        ),
        font=dict(size=28, family='Arial, sans-serif', color='#2C3E50'),
        width=2400,
        height=1400,
        paper_bgcolor='white',
        annotations=legend_annotations,
        margin=dict(l=0, r=0, t=120, b=0)
    )

    # Save
    html_path = output_path / "tech_transfer_heat_map.html"
    png_path = output_path / "tech_transfer_heat_map.png"
    svg_path = output_path / "tech_transfer_heat_map.svg"

    fig.write_html(str(html_path))
    print(f"[SAVED] HTML: {html_path}")

    try:
        fig.write_image(str(png_path), width=2400, height=1400, scale=2)
        print(f"[SAVED] PNG: {png_path}")
        fig.write_image(str(svg_path), width=2400, height=1400, format='svg')
        print(f"[SAVED] SVG: {svg_path}")
    except Exception as e:
        print(f"[NOTE] Image export requires kaleido: {e}")

    return str(html_path)


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING GEOGRAPHIC VISUALIZATIONS")
    print("=" * 80)
    print()

    print("1. BRI Global Flow Map (Prompt 3 - Variation 4)...")
    create_bri_global_flow_map()
    print()

    print("2. Technology Transfer Heat Map (Prompt 4 - Variation 6)...")
    create_tech_transfer_heat_map()
    print()

    print("=" * 80)
    print("GEOGRAPHIC VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print()
    print("Features:")
    print("  + World maps with project/transfer locations")
    print("  +Flow lines from China to global destinations")
    print("  +Color-coded by initiative/channel type")
    print("  +26pt+ fonts on all labels")
    print("  +Interactive HTML + high-res PNG/SVG exports")
