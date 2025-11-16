#!/usr/bin/env python3
"""
Create interactive visualizations for Chinese-European research collaborations
- Network graph of collaborations
- Timeline/heatmap of activity
- Geographic mapping
- Topic clustering
"""

import json
from pathlib import Path
from collections import defaultdict
import html

# Load analysis results
base_path = Path('data/processed/phase2_20251005_093031/correlation_analysis')

# Load all analysis files
with open(base_path / 'cordis_openaire_overlap_analysis.json', 'r', encoding='utf-8') as f:
    overlap_data = json.load(f)

with open(base_path / 'european_partners_analysis.json', 'r', encoding='utf-8') as f:
    partners_data = json.load(f)

with open(base_path / 'collaboration_details_analysis.json', 'r', encoding='utf-8') as f:
    details_data = json.load(f)

print('Creating visualizations...')
print()

# 1. NETWORK GRAPH (D3.js force-directed graph)
print('1. Creating network graph...')

# Build nodes and edges
nodes = []
edges = []
node_ids = set()

# Add Chinese institutions
for inst in overlap_data['all_overlaps']:
    inst_name = inst['entity_name']
    node_ids.add(inst_name)
    nodes.append({
        'id': inst_name,
        'name': inst_name,
        'type': 'chinese',
        'cordis': inst['cordis_participations'],
        'openaire': inst['openaire_publications'],
        'total': inst['cordis_participations'] + inst['openaire_publications']
    })

# Add top European partners
for partner in partners_data['top_50_partners'][:30]:  # Top 30 for clarity
    partner_name = partner['organization']
    if partner_name not in node_ids:
        node_ids.add(partner_name)
        nodes.append({
            'id': partner_name,
            'name': partner_name,
            'type': 'european',
            'country': partner['country'],
            'projects': partner['projects'],
            'chinese_collaborators': partner['chinese_collaborators']
        })

    # Create edges to Chinese partners
    for cn_inst in partner['sample_chinese_partners']:
        if cn_inst in node_ids:
            edges.append({
                'source': partner_name,
                'target': cn_inst,
                'value': 1  # Could weight by number of shared projects
            })

network_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Chinese-European Research Collaboration Network</title>
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
        }}
        #network {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }}
        .node.chinese {{ fill: #e74c3c; }}
        .node.european {{ fill: #3498db; }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.3;
        }}
        .label {{
            font-size: 10px;
            pointer-events: none;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
        }}
        .legend {{
            position: absolute;
            top: 80px;
            right: 40px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            margin: 5px 0;
            display: flex;
            align-items: center;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <h1>Chinese-European Research Collaboration Network</h1>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #e74c3c;"></div>
            <span>Chinese Institutions (68)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #3498db;"></div>
            <span>European Partners (30)</span>
        </div>
    </div>
    <svg id="network" width="1400" height="900"></svg>
    <div class="tooltip"></div>

    <script>
        const data = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(edges)}
        }};

        const width = 1400;
        const height = 900;

        const svg = d3.select("#network");
        const tooltip = d3.select(".tooltip");

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => Math.sqrt(d.total || d.projects || 1) * 3));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link");

        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", d => `node ${{d.type}}`)
            .attr("r", d => Math.sqrt((d.total || d.projects || 1)) * 2 + 5)
            .call(drag(simulation))
            .on("mouseover", function(event, d) {{
                tooltip.style("opacity", 1)
                    .html(d.type === 'chinese'
                        ? `<strong>${{d.name}}</strong><br/>CORDIS: ${{d.cordis}} projects<br/>OpenAIRE: ${{d.openaire}} publications`
                        : `<strong>${{d.name}}</strong><br/>Country: ${{d.country}}<br/>Projects: ${{d.projects}}<br/>Chinese partners: ${{d.chinese_collaborators}}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("opacity", 0);
            }});

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        }});

        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
    </script>
</body>
</html>"""

network_file = base_path / 'visualization_network.html'
with open(network_file, 'w', encoding='utf-8') as f:
    f.write(network_html)

print(f'   Saved: {network_file}')

# 2. TEMPORAL HEATMAP
print('2. Creating temporal heatmap...')

# Prepare timeline data
timeline_data = []
for inst_name, timeline_info in details_data['institution_timelines'].items():
    for year, count in timeline_info['by_year'].items():
        if year != 'Unknown':
            timeline_data.append({
                'institution': inst_name,
                'year': year,
                'projects': count
            })

heatmap_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Collaboration Timeline Heatmap</title>
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
        }}
        #heatmap {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .cell {{
            stroke: white;
            stroke-width: 2px;
        }}
        .label {{
            font-size: 10px;
        }}
        .axis-label {{
            font-size: 12px;
            font-weight: bold;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
        }}
    </style>
</head>
<body>
    <h1>Chinese Institutions - EU Collaboration Timeline (Top 20)</h1>
    <div id="heatmap"></div>
    <div class="tooltip"></div>

    <script>
        const data = {json.dumps(timeline_data)};

        const margin = {{top: 80, right: 50, bottom: 50, left: 300}};
        const cellSize = 40;

        // Get top 20 institutions by total projects
        const instTotals = {{}};
        data.forEach(d => {{
            instTotals[d.institution] = (instTotals[d.institution] || 0) + d.projects;
        }});
        const topInsts = Object.entries(instTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 20)
            .map(d => d[0]);

        const filteredData = data.filter(d => topInsts.includes(d.institution));

        const years = [...new Set(filteredData.map(d => d.year))].sort();

        const width = margin.left + margin.right + (years.length * cellSize);
        const height = margin.top + margin.bottom + (topInsts.length * cellSize);

        const svg = d3.select("#heatmap")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const tooltip = d3.select(".tooltip");

        const colorScale = d3.scaleSequential()
            .domain([0, d3.max(filteredData, d => d.projects)])
            .interpolator(d3.interpolateBlues);

        // Y axis (institutions)
        svg.selectAll(".inst-label")
            .data(topInsts)
            .join("text")
            .attr("class", "label")
            .attr("x", margin.left - 10)
            .attr("y", (d, i) => margin.top + (i * cellSize) + (cellSize / 2))
            .attr("text-anchor", "end")
            .attr("alignment-baseline", "middle")
            .text(d => d.length > 35 ? d.substring(0, 35) + '...' : d);

        // X axis (years)
        svg.selectAll(".year-label")
            .data(years)
            .join("text")
            .attr("class", "label")
            .attr("x", (d, i) => margin.left + (i * cellSize) + (cellSize / 2))
            .attr("y", margin.top - 10)
            .attr("text-anchor", "middle")
            .text(d => d);

        // Cells
        const cells = svg.selectAll(".cell")
            .data(filteredData)
            .join("rect")
            .attr("class", "cell")
            .attr("x", d => margin.left + (years.indexOf(d.year) * cellSize))
            .attr("y", d => margin.top + (topInsts.indexOf(d.institution) * cellSize))
            .attr("width", cellSize - 2)
            .attr("height", cellSize - 2)
            .attr("fill", d => colorScale(d.projects))
            .on("mouseover", function(event, d) {{
                tooltip.style("opacity", 1)
                    .html(`<strong>${{d.institution}}</strong><br/>Year: ${{d.year}}<br/>Projects: ${{d.projects}}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("opacity", 0);
            }});

        // Cell labels
        svg.selectAll(".cell-label")
            .data(filteredData.filter(d => d.projects > 0))
            .join("text")
            .attr("class", "label")
            .attr("x", d => margin.left + (years.indexOf(d.year) * cellSize) + (cellSize / 2))
            .attr("y", d => margin.top + (topInsts.indexOf(d.institution) * cellSize) + (cellSize / 2))
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "middle")
            .attr("fill", d => d.projects > 2 ? "white" : "black")
            .attr("font-weight", "bold")
            .text(d => d.projects);
    </script>
</body>
</html>"""

heatmap_file = base_path / 'visualization_timeline.html'
with open(heatmap_file, 'w', encoding='utf-8') as f:
    f.write(heatmap_html)

print(f'   Saved: {heatmap_file}')

# 3. RESEARCH DOMAINS CHART
print('3. Creating research domains chart...')

domains_data = [
    {'domain': domain, 'projects': info['project_count'], 'institutions': info['institution_count']}
    for domain, info in details_data['research_domains'].items()
]

domains_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Research Domains Analysis</title>
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
        }}
        #chart {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .bar {{
            fill: steelblue;
        }}
        .bar:hover {{
            fill: orange;
        }}
        .axis {{
            font-size: 12px;
        }}
        .axis-label {{
            font-size: 14px;
            font-weight: bold;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
        }}
    </style>
</head>
<body>
    <h1>Research Domains - Chinese-European Collaborations</h1>
    <div id="chart"></div>
    <div class="tooltip"></div>

    <script>
        const data = {json.dumps(domains_data)};

        const margin = {{top: 40, right: 30, bottom: 60, left: 200}};
        const width = 1200 - margin.left - margin.right;
        const height = 600 - margin.top - margin.bottom;

        const svg = d3.select("#chart")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

        const tooltip = d3.select(".tooltip");

        // Sort by projects
        data.sort((a, b) => b.projects - a.projects);

        const x = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.projects)])
            .range([0, width]);

        const y = d3.scaleBand()
            .domain(data.map(d => d.domain))
            .range([0, height])
            .padding(0.2);

        // Bars
        svg.selectAll(".bar")
            .data(data)
            .join("rect")
            .attr("class", "bar")
            .attr("x", 0)
            .attr("y", d => y(d.domain))
            .attr("width", d => x(d.projects))
            .attr("height", y.bandwidth())
            .on("mouseover", function(event, d) {{
                tooltip.style("opacity", 1)
                    .html(`<strong>${{d.domain}}</strong><br/>Projects: ${{d.projects}}<br/>Institutions: ${{d.institutions}}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("opacity", 0);
            }});

        // Y axis
        svg.append("g")
            .attr("class", "axis")
            .call(d3.axisLeft(y));

        // X axis
        svg.append("g")
            .attr("class", "axis")
            .attr("transform", `translate(0,${{height}})`)
            .call(d3.axisBottom(x));

        // X axis label
        svg.append("text")
            .attr("class", "axis-label")
            .attr("x", width / 2)
            .attr("y", height + 40)
            .attr("text-anchor", "middle")
            .text("Number of Projects");

        // Value labels
        svg.selectAll(".value-label")
            .data(data)
            .join("text")
            .attr("x", d => x(d.projects) + 5)
            .attr("y", d => y(d.domain) + y.bandwidth() / 2)
            .attr("alignment-baseline", "middle")
            .attr("font-size", "12px")
            .attr("font-weight", "bold")
            .text(d => d.projects);
    </script>
</body>
</html>"""

domains_file = base_path / 'visualization_domains.html'
with open(domains_file, 'w', encoding='utf-8') as f:
    f.write(domains_html)

print(f'   Saved: {domains_file}')

# 4. GEOGRAPHIC MAP
print('4. Creating geographic distribution map...')

country_data = partners_data['country_breakdown']

map_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>European Collaboration by Country</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://d3js.org/topojson.v3.min.js"></script>
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
        }}
        #map {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .country {{
            stroke: white;
            stroke-width: 1px;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
        }}
        .legend {{
            position: absolute;
            top: 100px;
            right: 40px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>European Collaboration with 68 Chinese Institutions by Country</h1>
    <p style="text-align: center; color: #666;">Darker colors indicate more collaboration projects</p>

    <div class="stats">
        <h2>Top Countries by Collaboration Intensity</h2>
        <table>
            <thead>
                <tr>
                    <th>Country</th>
                    <th>Projects</th>
                    <th>Institutions</th>
                    <th>Chinese Partners</th>
                </tr>
            </thead>
            <tbody>
                {chr(10).join(f'<tr><td>{c["country"]}</td><td>{c["projects"]}</td><td>{c["institutions"]}</td><td>{c["chinese_partners"]}</td></tr>' for c in sorted(country_data, key=lambda x: x["projects"], reverse=True)[:20])}
            </tbody>
        </table>
    </div>

    <script>
        const countryData = {json.dumps({c['country']: c for c in country_data})};
    </script>
</body>
</html>"""

map_file = base_path / 'visualization_map.html'
with open(map_file, 'w', encoding='utf-8') as f:
    f.write(map_html)

print(f'   Saved: {map_file}')

# 5. Create INDEX page
print('5. Creating index page...')

index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Chinese-European Research Collaborations - Visual Analysis</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 40px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #666;
            margin-top: 10px;
        }
        .viz-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .viz-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: transform 0.2s;
        }
        .viz-card:hover {
            transform: translateY(-5px);
        }
        .viz-card h2 {
            color: #333;
            margin-top: 0;
        }
        .viz-card p {
            color: #666;
            line-height: 1.6;
        }
        .viz-card a {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
            transition: background 0.2s;
        }
        .viz-card a:hover {
            background: #2980b9;
        }
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Chinese-European Research Collaborations</h1>
        <p class="subtitle">Visual Analysis of 68 Chinese Institutions & EU Research Partnerships</p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">68</div>
                <div class="stat-label">Chinese Institutions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">240</div>
                <div class="stat-label">EU Projects</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">698</div>
                <div class="stat-label">OpenAIRE Publications</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">20</div>
                <div class="stat-label">EU Countries</div>
            </div>
        </div>

        <div class="viz-grid">
            <div class="viz-card">
                <h2>🔗 Collaboration Network</h2>
                <p>Interactive network graph showing relationships between Chinese institutions and European partners. Node size represents collaboration intensity.</p>
                <a href="visualization_network.html">View Network Graph →</a>
            </div>

            <div class="viz-card">
                <h2>📅 Timeline Heatmap</h2>
                <p>Temporal analysis showing collaboration patterns from 2015-2026 across top 20 Chinese institutions. Darker cells indicate more projects.</p>
                <a href="visualization_timeline.html">View Timeline →</a>
            </div>

            <div class="viz-card">
                <h2>🔬 Research Domains</h2>
                <p>Analysis of research topics: Climate/Environment leads with 106 projects, followed by ICT/Networks (63) and Urban/Smart Cities (47).</p>
                <a href="visualization_domains.html">View Domains →</a>
            </div>

            <div class="viz-card">
                <h2>🗺️ Geographic Distribution</h2>
                <p>Country-level breakdown showing Germany (138 projects), Spain (107), Italy (107), and France (97) as top collaborators.</p>
                <a href="visualization_map.html">View Map →</a>
            </div>
        </div>

        <div class="footer">
            <p>Data Sources: CORDIS H2020/Horizon Europe + OpenAIRE Research Graph</p>
            <p>Generated: October 2025 | OSINT Foresight Analysis System</p>
        </div>
    </div>
</body>
</html>"""

index_file = base_path / 'index.html'
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(index_html)

print(f'   Saved: {index_file}')

print()
print('='*80)
print('VISUALIZATION SUITE COMPLETE')
print('='*80)
print()
print(f'Open in browser: {index_file.absolute()}')
print()
print('Files created:')
print(f'  - index.html (main dashboard)')
print(f'  - visualization_network.html (network graph)')
print(f'  - visualization_timeline.html (temporal heatmap)')
print(f'  - visualization_domains.html (research topics)')
print(f'  - visualization_map.html (geographic distribution)')
print()
