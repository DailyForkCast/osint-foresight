#!/usr/bin/env python3
"""
Intelligence Visualization Dashboard - FIXED VERSION
Creates visual dashboards for OSINT data
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class IntelligenceVisualizer:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis/visualizations")
        self.output_path.mkdir(exist_ok=True)
        plt.style.use('dark_background')

    def create_all_visualizations(self):
        """Create visualization dashboards"""
        print("Creating intelligence visualization dashboards...")

        self.create_risk_matrix()
        self.create_technology_distribution()
        self.create_trend_chart()

        print("Visualizations created!")

    def create_risk_matrix(self):
        """Create risk assessment matrix - FIXED"""
        fig, ax = plt.subplots(figsize=(12, 8))

        entities = []
        scores = []
        categories = []

        leonardo_db = self.warehouse_path / 'osint_master.db'
        if leonardo_db.exists():
            conn = sqlite3.connect(leonardo_db)
            cur = conn.cursor()

            # Get actual columns
            cur.execute('''
                SELECT entity_name, leonardo_composite_score, risk_category
                FROM technology_assessments
            ''')

            for row in cur.fetchall():
                entities.append(row[0])
                scores.append(row[1])
                categories.append(row[2])  # This is index 2, not 3

            conn.close()

        if entities:
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

            y_pos = np.arange(len(entities))
            ax.barh(y_pos, scores, color=colors, alpha=0.8)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(entities)
            ax.set_xlabel('Leonardo Composite Score', fontsize=12)
            ax.set_title('ENTITY RISK ASSESSMENT MATRIX', fontsize=16, fontweight='bold')

            ax.axvline(x=90, color='red', linestyle='--', alpha=0.5, label='Critical')
            ax.axvline(x=75, color='orange', linestyle='--', alpha=0.5, label='High')
            ax.axvline(x=60, color='yellow', linestyle='--', alpha=0.5, label='Elevated')

            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_path / 'risk_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Risk matrix visualization created")

    def create_technology_distribution(self):
        """Create technology distribution chart"""
        fig, ax = plt.subplots(figsize=(10, 8))

        # Get technology counts from MCF database
        mcf_db = self.warehouse_path / 'osint_master.db'
        if mcf_db.exists():
            conn = sqlite3.connect(mcf_db)
            cur = conn.cursor()

            cur.execute('''
                SELECT technology_name, COUNT(*) as freq
                FROM dual_use_technologies
                GROUP BY technology_name
                LIMIT 10
            ''')

            data = cur.fetchall()
            conn.close()

            if data:
                techs = [d[0] for d in data]
                freqs = [d[1] for d in data]

                colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(techs)))
                ax.pie(freqs, labels=techs, colors=colors,
                       autopct='%1.1f%%', startangle=90)
                ax.set_title('DUAL-USE TECHNOLOGY DISTRIBUTION', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_path / 'technology_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Technology distribution visualization created")

    def create_trend_chart(self):
        """Create simple trend chart"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Create sample trend data
        days = np.arange(30)
        trend = 70 + np.cumsum(np.random.normal(0.5, 2, 30))

        ax.plot(days, trend, color='cyan', linewidth=2)
        ax.fill_between(days, trend, 70, alpha=0.3, color='cyan')
        ax.set_xlabel('Days', fontsize=12)
        ax.set_ylabel('Risk Score', fontsize=12)
        ax.set_title('30-DAY RISK TREND', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_path / 'trend_chart.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Trend chart created")

def main():
    visualizer = IntelligenceVisualizer()
    visualizer.create_all_visualizations()
    print(f"All visualizations saved to {visualizer.output_path}")

if __name__ == "__main__":
    main()
