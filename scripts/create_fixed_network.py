#!/usr/bin/env python3
"""
Create fixed network visualization with better layout and controls
"""

import json
from pathlib import Path

# Load analysis results
base_path = Path('data/processed/phase2_20251005_093031/correlation_analysis')

with open(base_path / 'cordis_openaire_overlap_analysis.json', 'r', encoding='utf-8') as f:
    overlap_data = json.load(f)

with open(base_path / 'european_partners_analysis.json', 'r', encoding='utf-8') as f:
    partners_data = json.load(f)

# Build nodes and edges with better filtering
nodes = []
edges = []
node_ids = set()

# Add Chinese institutions (top 30 by activity)
top_chinese = sorted(
    overlap_data['all_overlaps'],
    key=lambda x: x['cordis_participations'] + x['openaire_publications'],
    reverse=True
)[:30]

for inst in top_chinese:
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

# Add top European partners (limit to top 20 for clarity)
for partner in partners_data['top_50_partners'][:20]:
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
                'value': 1
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
            overflow-x: hidden;
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
        .controls {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .controls button {{
            padding: 10px 20px;
            margin: 0 5px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .controls button:hover {{
            background: #2980b9;
        }}
        #network {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: block;
            margin: 0 auto;
        }}
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }}
        .node.chinese {{ fill: #e74c3c; }}
        .node.european {{ fill: #3498db; }}
        .node.highlighted {{ stroke: #f39c12; stroke-width: 4px; }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .link.highlighted {{
            stroke: #f39c12;
            stroke-opacity: 1;
            stroke-width: 3px;
        }}
        .label {{
            font-size: 11px;
            pointer-events: none;
            fill: #333;
            text-anchor: middle;
            dominant-baseline: middle;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.9);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
            max-width: 300px;
        }}
        .legend {{
            position: absolute;
            top: 140px;
            right: 40px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            margin: 8px 0;
            display: flex;
            align-items: center;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .stats {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-box {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <h1>🔗 Chinese-European Research Collaboration Network</h1>
    <p class="subtitle">Top 30 Chinese Institutions × Top 20 European Partners</p>

    <div class="controls">
        <button onclick="resetSimulation()">Reset Layout</button>
        <button onclick="fitToView()">Fit to View</button>
        <button onclick="clearHighlight()">Clear Selection</button>
    </div>

    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #e74c3c;"></div>
            <span><strong>Chinese Institutions</strong> (30)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #3498db;"></div>
            <span><strong>European Partners</strong> (20)</span>
        </div>
        <div style="margin-top: 15px; font-size: 11px; color: #666;">
            • Node size = activity level<br>
            • Click node to highlight connections<br>
            • Drag nodes to rearrange<br>
            • Scroll to zoom
        </div>
    </div>

    <svg id="network" width="1400" height="800"></svg>
    <div class="tooltip"></div>

    <div class="stats">
        <h3 style="margin-top: 0;">Network Statistics</h3>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{len(nodes)}</div>
                <div class="stat-label">Total Nodes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(edges)}</div>
                <div class="stat-label">Connections</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len([n for n in nodes if n['type'] == 'chinese'])}</div>
                <div class="stat-label">Chinese Institutions</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len([n for n in nodes if n['type'] == 'european'])}</div>
                <div class="stat-label">European Partners</div>
            </div>
        </div>
    </div>

    <script>
        const data = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(edges)}
        }};

        const width = 1400;
        const height = 800;

        const svg = d3.select("#network");
        const tooltip = d3.select(".tooltip");

        // Add zoom behavior
        const g = svg.append("g");

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});

        svg.call(zoom);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-500))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => getRadius(d) + 10))
            .force("x", d3.forceX(width / 2).strength(0.05))
            .force("y", d3.forceY(height / 2).strength(0.05));

        function getRadius(d) {{
            return Math.sqrt((d.total || d.projects || 1)) * 2.5 + 8;
        }}

        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", 1.5);

        const node = g.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", d => `node ${{d.type}}`)
            .attr("r", getRadius)
            .call(drag(simulation))
            .on("click", highlightConnections)
            .on("mouseover", function(event, d) {{
                tooltip.style("opacity", 1)
                    .html(d.type === 'chinese'
                        ? `<strong>${{d.name}}</strong><br/>CORDIS: ${{d.cordis}} projects<br/>OpenAIRE: ${{d.openaire}} publications<br/>Total: ${{d.total}}`
                        : `<strong>${{d.name}}</strong><br/>Country: ${{d.country}}<br/>Projects: ${{d.projects}}<br/>Chinese partners: ${{d.chinese_collaborators}}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("opacity", 0);
            }});

        // Add labels for larger nodes
        const label = g.append("g")
            .selectAll("text")
            .data(data.nodes.filter(d => (d.total || d.projects || 0) > 15))
            .join("text")
            .attr("class", "label")
            .text(d => {{
                const name = d.name;
                // Shorten long names
                if (name.length > 30) {{
                    return name.substring(0, 27) + '...';
                }}
                return name;
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

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y + getRadius(d) + 12);
        }});

        function highlightConnections(event, d) {{
            event.stopPropagation();

            // Get connected node IDs
            const connectedIds = new Set();
            connectedIds.add(d.id);

            link.each(function(l) {{
                if (l.source.id === d.id || l.target.id === d.id) {{
                    connectedIds.add(l.source.id);
                    connectedIds.add(l.target.id);
                }}
            }});

            // Highlight connected nodes
            node.classed("highlighted", n => connectedIds.has(n.id));

            // Highlight connected links
            link.classed("highlighted", l =>
                l.source.id === d.id || l.target.id === d.id
            );

            // Fade non-connected elements
            node.style("opacity", n => connectedIds.has(n.id) ? 1 : 0.2);
            link.style("opacity", l =>
                (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.1
            );
            label.style("opacity", n => connectedIds.has(n.id) ? 1 : 0.2);
        }}

        function clearHighlight() {{
            node.classed("highlighted", false)
                .style("opacity", 1);
            link.classed("highlighted", false)
                .style("opacity", 0.6);
            label.style("opacity", 1);
        }}

        function resetSimulation() {{
            simulation.alpha(1).restart();
        }}

        function fitToView() {{
            const bounds = g.node().getBBox();
            const fullWidth = bounds.width;
            const fullHeight = bounds.height;
            const midX = bounds.x + fullWidth / 2;
            const midY = bounds.y + fullHeight / 2;

            const scale = 0.8 / Math.max(fullWidth / width, fullHeight / height);
            const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
        }}

        // Clear highlight on background click
        svg.on("click", clearHighlight);

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

        // Initial fit to view
        setTimeout(fitToView, 1000);
    </script>
</body>
</html>"""

output_file = base_path / 'visualization_network.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(network_html)

print(f'Fixed network visualization created: {output_file}')
print()
print('Improvements:')
print('  - Reduced to top 30 Chinese + top 20 European (clearer layout)')
print('  - Added zoom and pan controls')
print('  - Click nodes to highlight connections')
print('  - "Fit to View" button to reset zoom')
print('  - "Clear Selection" to remove highlighting')
print('  - Better force simulation with collision detection')
print('  - Labels on major nodes')
print('  - Network statistics panel')
