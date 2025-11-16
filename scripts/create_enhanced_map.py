#!/usr/bin/env python3
"""
Create enhanced geographic map visualization with actual choropleth map
"""

import json
from pathlib import Path

# Load analysis results
base_path = Path('data/processed/phase2_20251005_093031/correlation_analysis')

with open(base_path / 'european_partners_analysis.json', 'r', encoding='utf-8') as f:
    partners_data = json.load(f)

country_data = partners_data['country_breakdown']

# Create country code to data mapping
country_map = {}
for c in country_data:
    country_map[c['country']] = {
        'projects': c['projects'],
        'institutions': c['institutions'],
        'chinese_partners': c['chinese_partners']
    }

# Convert to format for visualization
country_list = [
    {
        'code': c['country'],
        'projects': c['projects'],
        'institutions': c['institutions'],
        'chinese_partners': c['chinese_partners']
    }
    for c in sorted(country_data, key=lambda x: x['projects'], reverse=True)
]

map_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>European Collaboration Geographic Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }}
        #map {{
            height: 600px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
            position: sticky;
            top: 0;
        }}
        tr:hover {{
            background: #f0f0f0;
        }}
        .legend {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .legend-title {{
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .legend-scale {{
            display: flex;
            height: 20px;
            margin-bottom: 5px;
        }}
        .legend-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }}
        .info-box {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .info-box h4 {{
            margin: 0 0 5px 0;
        }}
    </style>
</head>
<body>
    <h1>🌍 European Collaboration with Chinese Institutions - Geographic Distribution</h1>
    <p class="subtitle">Interactive map showing collaboration intensity by country (darker = more projects)</p>

    <div id="map"></div>

    <div class="stats">
        <h2>Top Countries by Collaboration Intensity</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Country</th>
                    <th>Projects</th>
                    <th>Institutions</th>
                    <th>Chinese Partners</th>
                </tr>
            </thead>
            <tbody>
                {chr(10).join(f'<tr><td>{i+1}</td><td><strong>{c["code"]}</strong></td><td>{c["projects"]}</td><td>{c["institutions"]}</td><td>{c["chinese_partners"]}</td></tr>' for i, c in enumerate(country_list[:20]))}
            </tbody>
        </table>
    </div>

    <script>
        const countryData = {json.dumps(country_map)};

        // Country centroids for markers
        const countryCentroids = {{
            'AT': [47.5, 14.5, 'Austria'],
            'BE': [50.5, 4.5, 'Belgium'],
            'BG': [42.7, 25.5, 'Bulgaria'],
            'HR': [45.1, 15.2, 'Croatia'],
            'CY': [35.1, 33.4, 'Cyprus'],
            'CZ': [49.8, 15.5, 'Czech Republic'],
            'DK': [56.3, 9.5, 'Denmark'],
            'EE': [58.6, 25.0, 'Estonia'],
            'FI': [61.9, 25.7, 'Finland'],
            'FR': [46.2, 2.2, 'France'],
            'DE': [51.2, 10.4, 'Germany'],
            'GR': [39.1, 21.8, 'Greece'],
            'HU': [47.2, 19.5, 'Hungary'],
            'IE': [53.4, -8.2, 'Ireland'],
            'IT': [41.9, 12.6, 'Italy'],
            'LV': [56.9, 24.1, 'Latvia'],
            'LT': [55.2, 23.9, 'Lithuania'],
            'LU': [49.8, 6.1, 'Luxembourg'],
            'MT': [35.9, 14.4, 'Malta'],
            'NL': [52.1, 5.3, 'Netherlands'],
            'PL': [51.9, 19.1, 'Poland'],
            'PT': [39.4, -8.2, 'Portugal'],
            'RO': [45.9, 24.9, 'Romania'],
            'SK': [48.7, 19.7, 'Slovakia'],
            'SI': [46.1, 14.9, 'Slovenia'],
            'ES': [40.5, -3.7, 'Spain'],
            'SE': [60.1, 18.6, 'Sweden'],
            'GB': [55.4, -3.4, 'United Kingdom'],
            'NO': [60.5, 8.5, 'Norway'],
            'IS': [64.9, -19.0, 'Iceland'],
            'CH': [46.8, 8.2, 'Switzerland']
        }};

        // Initialize map
        const map = L.map('map').setView([50.0, 10.0], 4);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }}).addTo(map);

        // Color scale
        const maxProjects = Math.max(...Object.values(countryData).map(d => d.projects));
        const colorScale = d3.scaleSequential()
            .domain([0, maxProjects])
            .interpolator(d3.interpolateBlues);

        // Add circle markers for each country
        Object.entries(countryCentroids).forEach(([code, [lat, lon, name]]) => {{
            if (countryData[code]) {{
                const data = countryData[code];
                const radius = Math.sqrt(data.projects) * 4000; // Scale radius by projects

                const circle = L.circle([lat, lon], {{
                    color: '#2c3e50',
                    fillColor: colorScale(data.projects),
                    fillOpacity: 0.7,
                    radius: radius,
                    weight: 2
                }}).addTo(map);

                circle.bindPopup(`
                    <div class="info-box">
                        <h4>${{name}} (${{code}})</h4>
                        <strong>Projects:</strong> ${{data.projects}}<br>
                        <strong>Institutions:</strong> ${{data.institutions}}<br>
                        <strong>Chinese Partners:</strong> ${{data.chinese_partners}}
                    </div>
                `);

                // Add label for top countries
                if (data.projects > 50) {{
                    L.marker([lat, lon], {{
                        icon: L.divIcon({{
                            className: 'country-label',
                            html: `<div style="background: white; padding: 2px 5px; border-radius: 3px; font-size: 11px; font-weight: bold; box-shadow: 0 1px 3px rgba(0,0,0,0.3);">${{code}}: ${{data.projects}}</div>`,
                            iconSize: [60, 20]
                        }})
                    }}).addTo(map);
                }}
            }}
        }});

        // Add legend
        const legend = L.control({{position: 'bottomright'}});
        legend.onAdd = function(map) {{
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <div class="legend-title">Projects</div>
                <div class="legend-scale">
                    <div style="flex: 1; background: ${{colorScale(0)}};"></div>
                    <div style="flex: 1; background: ${{colorScale(maxProjects * 0.25)}};"></div>
                    <div style="flex: 1; background: ${{colorScale(maxProjects * 0.5)}};"></div>
                    <div style="flex: 1; background: ${{colorScale(maxProjects * 0.75)}};"></div>
                    <div style="flex: 1; background: ${{colorScale(maxProjects)}};"></div>
                </div>
                <div class="legend-labels">
                    <span>0</span>
                    <span>${{Math.round(maxProjects / 2)}}</span>
                    <span>${{maxProjects}}</span>
                </div>
                <div style="margin-top: 10px; font-size: 11px;">
                    Circle size = project count<br>
                    Click circles for details
                </div>
            `;
            return div;
        }};
        legend.addTo(map);
    </script>
</body>
</html>"""

output_file = base_path / 'visualization_map.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(map_html)

print(f'Enhanced map created: {output_file}')
print()
print('Features:')
print('  - Interactive Leaflet map of Europe')
print('  - Circle markers sized by project count')
print('  - Color intensity shows collaboration level')
print('  - Click circles for country details')
print('  - Legend shows scale')
print('  - Top countries labeled')
