#!/usr/bin/env python3
"""
NetworkX Entity Relationship Graph
Zero-budget graph database alternative using pure Python
Maps hidden connections between Chinese entities across all systems
"""

import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EntityRelationshipGraph:
    """Build and analyze entity relationship networks using NetworkX"""

    def __init__(self):
        self.G = nx.Graph()  # Undirected graph for relationships
        self.DG = nx.DiGraph()  # Directed graph for influence flows
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.graph_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.setup_database()

    def setup_database(self):
        """Initialize database for storing graph data"""
        conn = sqlite3.connect(self.graph_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_nodes (
                node_id TEXT PRIMARY KEY,
                entity_name TEXT,
                entity_type TEXT,
                risk_score INTEGER,
                country TEXT,
                technologies TEXT,
                data_sources TEXT,
                centrality_score REAL,
                cluster_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_edges (
                edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship_type TEXT,
                strength INTEGER,
                evidence_source TEXT,
                discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_id, target_id, relationship_type)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hidden_connections (
                connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity1 TEXT,
                entity2 TEXT,
                path_length INTEGER,
                intermediate_entities TEXT,
                connection_strength REAL,
                risk_assessment TEXT,
                discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_clusters (
                cluster_id INTEGER PRIMARY KEY,
                cluster_name TEXT,
                entity_count INTEGER,
                key_entities TEXT,
                technology_focus TEXT,
                risk_level TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Graph database initialized")

    def load_entities_from_master(self):
        """Load entities from master database"""
        conn = sqlite3.connect(self.master_db)

        # Get entities from cross-system correlation
        entities_df = pd.read_sql_query("""
            SELECT normalized_entity_name as name,
                   entity_type as type,
                   max_risk_score as risk,
                   technology_focus as tech,
                   total_systems as sources
            FROM cross_system_entity_correlation
        """, conn)

        # Get BIS entities
        bis_df = pd.read_sql_query("""
            SELECT entity_name as name,
                   'export_controlled' as type,
                   risk_score as risk,
                   technology_focus as tech,
                   country
            FROM bis_entity_list_fixed
            WHERE china_related = 1
        """, conn)

        conn.close()

        # Add entities as nodes
        for _, entity in entities_df.iterrows():
            self.add_entity_node(
                name=entity['name'],
                entity_type=entity['type'],
                risk_score=entity['risk'],
                technologies=entity['tech']
            )

        for _, entity in bis_df.iterrows():
            self.add_entity_node(
                name=entity['name'],
                entity_type=entity['type'],
                risk_score=entity['risk'],
                technologies=entity['tech'],
                country=entity.get('country', 'CN')
            )

        logging.info(f"Loaded {self.G.number_of_nodes()} entities into graph")

    def add_entity_node(self, name: str, entity_type: str = 'unknown',
                       risk_score: int = 50, technologies: str = '',
                       country: str = 'CN'):
        """Add entity node to graph"""
        node_id = name.lower().replace(' ', '_')

        self.G.add_node(
            node_id,
            label=name,
            entity_type=entity_type,
            risk_score=risk_score,
            technologies=technologies,
            country=country
        )

        # Also add to directed graph
        self.DG.add_node(
            node_id,
            label=name,
            entity_type=entity_type,
            risk_score=risk_score
        )

    def add_relationship(self, entity1: str, entity2: str,
                        relationship_type: str, strength: int = 50):
        """Add relationship between entities"""
        node1 = entity1.lower().replace(' ', '_')
        node2 = entity2.lower().replace(' ', '_')

        # Add to undirected graph
        self.G.add_edge(
            node1, node2,
            relationship=relationship_type,
            weight=strength
        )

        # Add to directed graph based on relationship type
        if relationship_type in ['owns', 'controls', 'supplies']:
            self.DG.add_edge(node1, node2, weight=strength)
        elif relationship_type in ['owned_by', 'controlled_by', 'supplied_by']:
            self.DG.add_edge(node2, node1, weight=strength)
        else:
            # Bidirectional relationships
            self.DG.add_edge(node1, node2, weight=strength/2)
            self.DG.add_edge(node2, node1, weight=strength/2)

    def discover_relationships(self):
        """Discover relationships from various data sources"""

        # Patent co-inventors (collaboration)
        self.discover_patent_relationships()

        # Trade relationships (supply chain)
        self.discover_trade_relationships()

        # Research collaborations
        self.discover_research_relationships()

        # Corporate ownership
        self.discover_ownership_relationships()

        logging.info(f"Discovered {self.G.number_of_edges()} relationships")

    def discover_patent_relationships(self):
        """Find relationships through patent collaborations"""
        try:
            conn = sqlite3.connect("F:/OSINT_Data/USPTO/uspto_patents_20250926.db")

            # Find co-assignees
            query = """
                SELECT assignee1, assignee2, COUNT(*) as patent_count
                FROM (
                    SELECT DISTINCT a1.assignee as assignee1,
                           a2.assignee as assignee2
                    FROM patents a1
                    JOIN patents a2 ON a1.patent_id = a2.patent_id
                    WHERE a1.assignee != a2.assignee
                    AND a1.assignee IS NOT NULL
                    AND a2.assignee IS NOT NULL
                )
                GROUP BY assignee1, assignee2
                HAVING patent_count > 2
            """

            cursor = conn.execute(query)
            for assignee1, assignee2, count in cursor:
                strength = min(count * 10, 100)
                self.add_relationship(
                    assignee1, assignee2,
                    'patent_collaboration',
                    strength
                )

            conn.close()
        except Exception as e:
            logging.warning(f"Could not discover patent relationships: {e}")

    def discover_trade_relationships(self):
        """Find relationships through trade patterns"""
        try:
            conn = sqlite3.connect("F:/OSINT_Data/Trade_Facilities/uncomtrade_v2.db")

            # Find major trading partners
            query = """
                SELECT reporter_name, partner_name, SUM(trade_value_usd) as total_trade
                FROM trade_flows
                WHERE (reporter_name LIKE '%China%' OR partner_name LIKE '%China%')
                GROUP BY reporter_name, partner_name
                HAVING total_trade > 1000000000
            """

            cursor = conn.execute(query)
            for reporter, partner, value in cursor:
                # Normalize trade value to strength score
                strength = min(int(np.log10(value) * 10), 100)
                self.add_relationship(
                    reporter, partner,
                    'trade_partner',
                    strength
                )

            conn.close()
        except Exception as e:
            logging.warning(f"Could not discover trade relationships: {e}")

    def discover_research_relationships(self):
        """Find relationships through research collaborations"""
        try:
            conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")

            # Find institution collaborations
            query = """
                SELECT institution1, institution2, collaboration_count
                FROM institution_collaborations
                WHERE collaboration_count > 5
            """

            cursor = conn.execute(query)
            for inst1, inst2, count in cursor:
                strength = min(count * 5, 100)
                self.add_relationship(
                    inst1, inst2,
                    'research_collaboration',
                    strength
                )

            conn.close()
        except Exception as e:
            logging.warning(f"Could not discover research relationships: {e}")

    def discover_ownership_relationships(self):
        """Find corporate ownership relationships"""
        # Known ownership relationships (would come from GLEIF or SEC in production)
        known_ownerships = [
            ("Huawei", "HiSilicon", "owns", 100),
            ("Alibaba", "Ant Group", "owns", 33),
            ("Tencent", "WeChat", "owns", 100),
            ("ByteDance", "TikTok", "owns", 100),
            ("State Grid", "multiple_subsidiaries", "owns", 100)
        ]

        for parent, subsidiary, rel_type, strength in known_ownerships:
            self.add_relationship(parent, subsidiary, rel_type, strength)

    def find_hidden_connections(self, entity1: str, entity2: str,
                               max_path_length: int = 5) -> List[List[str]]:
        """Find hidden connection paths between entities"""
        node1 = entity1.lower().replace(' ', '_')
        node2 = entity2.lower().replace(' ', '_')

        if node1 not in self.G or node2 not in self.G:
            return []

        try:
            # Find all simple paths up to max_path_length
            paths = list(nx.all_simple_paths(
                self.G, node1, node2,
                cutoff=max_path_length
            ))

            # Sort by path length (shorter = stronger connection)
            paths.sort(key=len)

            return paths[:10]  # Return top 10 paths

        except nx.NetworkXNoPath:
            return []

    def calculate_centrality_metrics(self):
        """Calculate various centrality metrics for entities"""
        metrics = {}

        # Degree centrality (how connected)
        metrics['degree'] = nx.degree_centrality(self.G)

        # Betweenness centrality (how much of a bridge)
        metrics['betweenness'] = nx.betweenness_centrality(self.G)

        # Eigenvector centrality (connected to important nodes)
        try:
            metrics['eigenvector'] = nx.eigenvector_centrality(self.G, max_iter=1000)
        except:
            metrics['eigenvector'] = {}

        # PageRank (Google's algorithm)
        metrics['pagerank'] = nx.pagerank(self.G)

        # Store top entities by each metric
        results = {}
        for metric_name, scores in metrics.items():
            sorted_entities = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            results[metric_name] = sorted_entities[:10]

        return results

    def detect_communities(self):
        """Detect communities/clusters in the network"""
        # Use Louvain method for community detection
        communities = nx.community.greedy_modularity_communities(self.G)

        # Analyze each community
        community_analysis = []
        for i, community in enumerate(communities):
            if len(community) < 3:
                continue  # Skip tiny communities

            # Get nodes in community
            nodes = list(community)

            # Calculate average risk score
            risk_scores = [self.G.nodes[n].get('risk_score', 0) for n in nodes]
            avg_risk = np.mean(risk_scores) if risk_scores else 0

            # Get common technologies
            all_tech = []
            for node in nodes:
                tech = self.G.nodes[node].get('technologies', '')
                if tech:
                    all_tech.extend(tech.split(';'))

            # Find most common tech
            from collections import Counter
            tech_counter = Counter(all_tech)
            top_tech = tech_counter.most_common(3)

            community_analysis.append({
                'cluster_id': i,
                'size': len(community),
                'avg_risk': avg_risk,
                'key_entities': nodes[:5],  # Top 5 entities
                'technologies': top_tech,
                'risk_level': 'HIGH' if avg_risk > 70 else 'MEDIUM' if avg_risk > 40 else 'LOW'
            })

        return community_analysis

    def visualize_network(self, output_path: str = None):
        """Create network visualization"""
        plt.figure(figsize=(20, 16))

        # Calculate layout
        pos = nx.spring_layout(self.G, k=2, iterations=50)

        # Color nodes by risk score
        node_colors = []
        for node in self.G.nodes():
            risk = self.G.nodes[node].get('risk_score', 0)
            if risk > 80:
                node_colors.append('red')
            elif risk > 60:
                node_colors.append('orange')
            elif risk > 40:
                node_colors.append('yellow')
            else:
                node_colors.append('lightgreen')

        # Size nodes by degree (connections)
        node_sizes = [300 * self.G.degree(n) for n in self.G.nodes()]

        # Draw network
        nx.draw_networkx_nodes(self.G, pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.7)

        nx.draw_networkx_edges(self.G, pos,
                              alpha=0.3,
                              width=0.5)

        # Add labels for high-risk or highly connected nodes
        labels = {}
        for node in self.G.nodes():
            if (self.G.nodes[node].get('risk_score', 0) > 70 or
                self.G.degree(node) > 5):
                labels[node] = self.G.nodes[node].get('label', node)

        nx.draw_networkx_labels(self.G, pos, labels,
                               font_size=8)

        plt.title("China Technology Entity Relationship Network", fontsize=16)
        plt.axis('off')

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logging.info(f"Network visualization saved to {output_path}")
        else:
            plt.show()

        plt.close()

    def generate_network_intelligence_report(self):
        """Generate intelligence report from network analysis"""

        # Calculate metrics
        centrality = self.calculate_centrality_metrics()
        communities = self.detect_communities()

        report = f"""# ENTITY NETWORK INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}
Graph Analysis: NetworkX (Zero Budget Solution)

## NETWORK STATISTICS

- Total Entities: {self.G.number_of_nodes()}
- Total Relationships: {self.G.number_of_edges()}
- Average Connections per Entity: {np.mean([d for n, d in self.G.degree()]):.2f}
- Network Density: {nx.density(self.G):.4f}

## KEY ENTITY ANALYSIS

### Most Connected Entities (Degree Centrality)
"""
        for entity, score in centrality['degree'][:5]:
            label = self.G.nodes[entity].get('label', entity)
            report += f"- {label}: {score:.3f}\n"

        report += """
### Bridge Entities (Betweenness Centrality)
*Entities that connect different parts of the network*
"""
        for entity, score in centrality['betweenness'][:5]:
            label = self.G.nodes[entity].get('label', entity)
            report += f"- {label}: {score:.3f}\n"

        report += """
### Influential Entities (PageRank)
*Entities with high overall influence*
"""
        for entity, score in centrality['pagerank'][:5]:
            label = self.G.nodes[entity].get('label', entity)
            report += f"- {label}: {score:.3f}\n"

        report += f"""
## COMMUNITY DETECTION

Detected {len(communities)} distinct communities/clusters:

"""
        for community in communities[:5]:
            report += f"""### Cluster {community['cluster_id']}
- Size: {community['size']} entities
- Risk Level: {community['risk_level']}
- Average Risk Score: {community['avg_risk']:.1f}
- Key Technologies: {', '.join([t[0] for t in community['technologies']])}
- Key Entities: {', '.join([self.G.nodes[n].get('label', n) for n in community['key_entities'][:3]])}

"""

        # Find hidden connections example
        report += """## HIDDEN CONNECTION ANALYSIS

### Example: Huawei to US Technology
"""
        paths = self.find_hidden_connections("huawei", "united_states", max_path_length=4)
        if paths:
            for i, path in enumerate(paths[:3], 1):
                path_labels = [self.G.nodes[n].get('label', n) for n in path]
                report += f"{i}. Path (length {len(path)-1}): {' → '.join(path_labels)}\n"
        else:
            report += "No direct or indirect connections found within 4 degrees.\n"

        report += """
## INTELLIGENCE INSIGHTS

1. **Network Structure**: The network shows clear clustering around technology domains
2. **Risk Concentration**: High-risk entities tend to cluster together
3. **Bridge Entities**: Key entities connecting different clusters represent critical intelligence targets
4. **Hidden Paths**: Multiple indirect pathways exist between seemingly unconnected entities

## RECOMMENDED ACTIONS

1. Monitor bridge entities for early warning of technology transfer
2. Investigate clusters with high average risk scores
3. Map hidden connection paths for all critical entities
4. Track changes in centrality metrics over time

---
*Network Intelligence Report - NetworkX Graph Analysis*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/NETWORK_INTELLIGENCE_REPORT.md")
        report_path.write_text(report, encoding='utf-8')

        logging.info("Network intelligence report generated")
        return report

    def save_graph_to_database(self):
        """Save graph data to database for persistence"""
        conn = sqlite3.connect(self.graph_db)
        cursor = conn.cursor()

        # Save nodes
        for node in self.G.nodes(data=True):
            node_id = node[0]
            attributes = node[1]

            cursor.execute("""
                INSERT OR REPLACE INTO entities (
                    node_id, entity_name, entity_type, risk_score,
                    country, technologies
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node_id,
                attributes.get('label', node_id),
                attributes.get('entity_type', 'unknown'),
                attributes.get('risk_score', 0),
                attributes.get('country', 'CN'),
                attributes.get('technologies', '')
            ))

        # Save edges
        for edge in self.G.edges(data=True):
            source, target = edge[0], edge[1]
            attributes = edge[2]

            cursor.execute("""
                INSERT OR REPLACE INTO entity_relationships (
                    source_id, target_id, relationship_type, strength
                ) VALUES (?, ?, ?, ?)
            """, (
                source, target,
                attributes.get('relationship', 'connected'),
                attributes.get('weight', 50)
            ))

        conn.commit()
        conn.close()
        logging.info("Graph saved to database")

    def run_analysis(self):
        """Execute complete network analysis"""
        logging.info("Starting entity network analysis")

        # Load entities
        self.load_entities_from_master()

        # Discover relationships
        self.discover_relationships()

        # Perform analysis
        self.generate_network_intelligence_report()

        # Create visualization
        self.visualize_network("C:/Projects/OSINT - Foresight/analysis/entity_network.png")

        # Save to database
        self.save_graph_to_database()

        logging.info("Network analysis completed")


if __name__ == "__main__":
    graph = EntityRelationshipGraph()
    graph.run_analysis()
