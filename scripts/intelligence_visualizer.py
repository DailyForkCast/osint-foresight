#!/usr/bin/env python3
"""
Intelligence Visualization Dashboard
Creates visual dashboards for OSINT data
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from typing import Dict, List

class IntelligenceVisualizer:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis/visualizations")
        self.output_path.mkdir(exist_ok=True)

        plt.style.use('dark_background')  # Dark theme for professional look

    def create_all_visualizations(self):
        """Create all visualization dashboards"""
        print("Creating intelligence visualization dashboards...")

        # 1. Risk Matrix Dashboard
        self.create_risk_matrix()

        # 2. Technology Network Graph
        self.create_technology_network()

        # 3. Temporal Trend Analysis
        self.create_temporal_trends()

        # 4. Arctic Intelligence Map
        self.create_arctic_visualization()

        # 5. Dual-Use Technology Heatmap
        self.create_dualuse_heatmap()

        # 6. Entity Relationship Network
        self.create_entity_network()

        print("All visualizations created!")

    def create_risk_matrix(self):
        """Create risk assessment matrix visualization"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Get Leonardo scores
        entities = []
        scores = []
        categories = []

        leonardo_db = self.warehouse_path / 'osint_master.db'
        if leonardo_db.exists():
            conn = sqlite3.connect(leonardo_db)
            cur = conn.cursor()
            cur.execute('''
                SELECT entity_name, leonardo_composite_score, risk_category
                FROM technology_assessments
            ''')
            for row in cur.fetchall():
                entities.append(row[0])
                scores.append(row[1])
                categories.append(row[3])
            conn.close()

        if entities:
            # Create risk matrix
            colors = []
            for cat in categories:
                if 'L1' in cat:
                    colors.append('red')
                elif 'L2' in cat:
                    colors.append('orange')
                elif 'L3' in cat:
                    colors.append('yellow')
                else:
                    colors.append('green')

            # Create bar chart
            y_pos = np.arange(len(entities))
            ax.barh(y_pos, scores, color=colors, alpha=0.8)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(entities)
            ax.set_xlabel('Leonardo Composite Score', fontsize=12)
            ax.set_title('ENTITY RISK ASSESSMENT MATRIX', fontsize=16, fontweight='bold')

            # Add risk zones
            ax.axvline(x=90, color='red', linestyle='--', alpha=0.5, label='Critical (L1)')
            ax.axvline(x=75, color='orange', linestyle='--', alpha=0.5, label='High (L2)')
            ax.axvline(x=60, color='yellow', linestyle='--', alpha=0.5, label='Elevated (L3)')

            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_path / 'risk_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Risk matrix visualization created")

    def create_technology_network(self):
        """Create technology relationship network"""
        fig, ax = plt.subplots(figsize=(14, 10))

        G = nx.Graph()

        # Add technology nodes from taxonomy
        taxonomy_db = self.warehouse_path / 'osint_master.db'
        if taxonomy_db.exists():
            conn = sqlite3.connect(taxonomy_db)
            cur = conn.cursor()

            # Get technology categories
            cur.execute('''
                SELECT category_name, strategic_importance
                FROM technology_categories
            ''')
            categories = cur.fetchall()

            # Get technologies
            cur.execute('''
                SELECT technology_name, category_id
                FROM dual_use_assessments
            ''')
            technologies = cur.fetchall()

            # Build network
            for cat_name, importance in categories:
                G.add_node(cat_name, node_type='category', weight=importance)

            for tech_name, cat_id in technologies[:20]:  # Limit for visibility
                G.add_node(tech_name, node_type='technology', weight=50)
                # Find matching category
                for cat_name, _ in categories:
                    if cat_id in cat_name.lower().replace(' ', '_'):
                        G.add_edge(tech_name, cat_name)

            conn.close()

        if len(G.nodes()) > 0:
            # Create layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Draw nodes
            category_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'category']
            tech_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'technology']

            nx.draw_networkx_nodes(G, pos, nodelist=category_nodes,
                                 node_color='red', node_size=800, alpha=0.8, ax=ax)
            nx.draw_networkx_nodes(G, pos, nodelist=tech_nodes,
                                 node_color='cyan', node_size=300, alpha=0.6, ax=ax)

            # Draw edges
            nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)

            # Draw labels (only for categories)
            category_labels = {n: n for n in category_nodes}
            nx.draw_networkx_labels(G, pos, category_labels,
                                   font_size=8, font_color='white', ax=ax)

            ax.set_title('DUAL-USE TECHNOLOGY NETWORK', fontsize=16, fontweight='bold')
            ax.axis('off')

            # Add legend
            red_patch = mpatches.Patch(color='red', label='Technology Categories')
            cyan_patch = mpatches.Patch(color='cyan', label='Specific Technologies')
            ax.legend(handles=[red_patch, cyan_patch], loc='upper right')

        plt.tight_layout()
        plt.savefig(self.output_path / 'technology_network.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Technology network visualization created")

    def create_temporal_trends(self):
        """Create temporal trend analysis charts"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Simulate temporal data (in real scenario, would query historical data)
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')

        # Patent filing trends
        patent_trend = np.cumsum(np.random.poisson(5, 30))
        axes[0, 0].plot(dates, patent_trend, color='cyan', linewidth=2)
        axes[0, 0].fill_between(dates, patent_trend, alpha=0.3, color='cyan')
        axes[0, 0].set_title('Patent Filing Trends', fontsize=12)
        axes[0, 0].set_ylabel('Cumulative Patents')
        axes[0, 0].grid(True, alpha=0.3)

        # Risk score evolution
        risk_scores = 70 + np.cumsum(np.random.normal(0.5, 2, 30))
        axes[0, 1].plot(dates, risk_scores, color='orange', linewidth=2)
        axes[0, 1].axhline(y=85, color='red', linestyle='--', alpha=0.5)
        axes[0, 1].fill_between(dates, risk_scores, 70, alpha=0.3, color='orange')
        axes[0, 1].set_title('Risk Score Evolution', fontsize=12)
        axes[0, 1].set_ylabel('Composite Risk Score')
        axes[0, 1].grid(True, alpha=0.3)

        # Alert frequency
        alert_counts = np.random.poisson(3, 30)
        axes[1, 0].bar(dates, alert_counts, color='red', alpha=0.6)
        axes[1, 0].set_title('Daily Alert Frequency', fontsize=12)
        axes[1, 0].set_ylabel('Number of Alerts')
        axes[1, 0].grid(True, alpha=0.3)

        # MCF activity indicators
        mcf_activity = 40 + np.cumsum(np.random.normal(1, 3, 30))
        axes[1, 1].plot(dates, mcf_activity, color='yellow', linewidth=2, marker='o', markersize=4)
        axes[1, 1].set_title('MCF Activity Indicators', fontsize=12)
        axes[1, 1].set_ylabel('MCF Relevance Score')
        axes[1, 1].grid(True, alpha=0.3)

        # Rotate x-axis labels
        for ax in axes.flat:
            ax.tick_params(axis='x', rotation=45)

        plt.suptitle('TEMPORAL INTELLIGENCE TRENDS', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_path / 'temporal_trends.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Temporal trends visualization created")

    def create_arctic_visualization(self):
        """Create Arctic intelligence visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

        # Get Arctic data
        arctic_db = self.warehouse_path / 'osint_master.db'
        if arctic_db.exists():
            conn = sqlite3.connect(arctic_db)
            cur = conn.cursor()

            # Arctic relevance scores
            cur.execute('''
                SELECT title, arctic_relevance_score, chinese_arctic_score
                FROM arctic_reports
                ORDER BY arctic_relevance_score DESC
                LIMIT 10
            ''')
            reports = cur.fetchall()

            if reports:
                titles = [r[0][:30] + '...' if len(r[0]) > 30 else r[0] for r in reports]
                arctic_scores = [r[1] for r in reports]
                chinese_scores = [r[2] for r in reports]

                # Stacked bar chart
                x = np.arange(len(titles))
                width = 0.35

                bars1 = ax1.bar(x - width/2, arctic_scores, width,
                              label='Arctic Relevance', color='lightblue')
                bars2 = ax1.bar(x + width/2, chinese_scores, width,
                              label='Chinese Arctic', color='red', alpha=0.7)

                ax1.set_xlabel('Reports')
                ax1.set_title('ARCTIC INTELLIGENCE SCORES', fontsize=12)
                ax1.set_xticks(x)
                ax1.set_xticklabels(titles, rotation=45, ha='right', fontsize=8)
                ax1.legend()
                ax1.grid(True, alpha=0.3)

            # Arctic technology categories
            cur.execute('''
                SELECT technology_name, COUNT(*) as freq
                FROM arctic_technologies
                GROUP BY technology_name
                LIMIT 8
            ''')
            tech_data = cur.fetchall()

            if tech_data:
                techs = [t[0] for t in tech_data]
                freqs = [t[1] for t in tech_data]

                # Pie chart
                colors = plt.cm.winter(np.linspace(0.3, 0.9, len(techs)))
                ax2.pie(freqs, labels=techs, colors=colors,
                       autopct='%1.1f%%', startangle=90)
                ax2.set_title('ARCTIC TECHNOLOGY DISTRIBUTION', fontsize=12)

            conn.close()

        plt.suptitle('ARCTIC DOMAIN INTELLIGENCE', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_path / 'arctic_intelligence.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Arctic intelligence visualization created")

    def create_dualuse_heatmap(self):
        """Create dual-use technology heatmap"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create matrix of technology categories vs applications
        categories = ['AI/ML', 'Quantum', 'Space', 'Bio', 'Semiconductors',
                     'Arctic', 'Hypersonics', 'Cyber']
        applications = ['Military', 'Civilian', 'Dual-Use', 'Export Controlled']

        # Generate heatmap data (in real scenario, would query from database)
        data = np.random.randint(0, 100, (len(categories), len(applications)))

        # Create heatmap
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')

        # Set ticks and labels
        ax.set_xticks(np.arange(len(applications)))
        ax.set_yticks(np.arange(len(categories)))
        ax.set_xticklabels(applications)
        ax.set_yticklabels(categories)

        # Rotate the tick labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Technology Count', rotation=270, labelpad=20)

        # Add text annotations
        for i in range(len(categories)):
            for j in range(len(applications)):
                text = ax.text(j, i, data[i, j],
                             ha="center", va="center", color="black", fontsize=10)

        ax.set_title('DUAL-USE TECHNOLOGY HEATMAP', fontsize=16, fontweight='bold')
        ax.set_xlabel('Application Type', fontsize=12)
        ax.set_ylabel('Technology Category', fontsize=12)

        plt.tight_layout()
        plt.savefig(self.output_path / 'dualuse_heatmap.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Dual-use technology heatmap created")

    def create_entity_network(self):
        """Create entity relationship network visualization"""
        fig, ax = plt.subplots(figsize=(14, 10))

        # Load entity graph if exists
        entity_db = self.warehouse_path / 'osint_master.db'
        if entity_db.exists():
            try:
                import pickle
                graph_file = self.warehouse_path / 'entity_network.pkl'
                if graph_file.exists():
                    with open(graph_file, 'rb') as f:
                        G = pickle.load(f)
                else:
                    # Create sample network
                    G = nx.Graph()
                    entities = ['Huawei', 'SMIC', 'DJI', 'iFlytek', 'Beijing Uni',
                              'Tsinghua', 'ZTE', 'Alibaba', 'Tencent']
                    for entity in entities:
                        G.add_node(entity)

                    # Add some connections
                    connections = [('Huawei', 'SMIC'), ('Huawei', 'Beijing Uni'),
                                 ('SMIC', 'Tsinghua'), ('DJI', 'iFlytek'),
                                 ('Alibaba', 'Tencent'), ('ZTE', 'Huawei')]
                    G.add_edges_from(connections)

                # Draw network
                pos = nx.spring_layout(G, k=2)

                # Node sizes based on degree
                node_sizes = [300 * (1 + G.degree(n)) for n in G.nodes()]

                nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                     node_color='red', alpha=0.7, ax=ax)
                nx.draw_networkx_edges(G, pos, alpha=0.3, width=2, ax=ax)
                nx.draw_networkx_labels(G, pos, font_size=10,
                                       font_color='white', ax=ax)

                ax.set_title('ENTITY RELATIONSHIP NETWORK', fontsize=16, fontweight='bold')
                ax.axis('off')

            except Exception as e:
                print(f"Entity network error: {e}")

        plt.tight_layout()
        plt.savefig(self.output_path / 'entity_network.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Entity network visualization created")

def main():
    # Import pandas for temporal analysis
    global pd
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed, using numpy for temporal data")
        pd = None

    visualizer = IntelligenceVisualizer()
    visualizer.create_all_visualizations()
    print(f"All visualizations saved to {visualizer.output_path}")

if __name__ == "__main__":
    main()
