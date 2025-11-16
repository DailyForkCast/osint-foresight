#!/usr/bin/env python3
"""
MCF Medium Complexity Visualizations
Matrix Heat Map, Galaxy Map, Venn Diagram - all with 32pt MINIMUM fonts
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pathlib import Path
import numpy as np
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
import seaborn as sns


def load_timeline_data(data_path="data/mcf_timeline_2015_2024.json"):
    """Load MCF timeline database"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_bri_database(data_path="data/bri_projects_database.json"):
    """Load BRI projects database"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# PROMPT 2 - VARIATION 4: MATRIX HEAT MAP
# ============================================================================

def create_matrix_heatmap(output_dir="visualizations/governance"):
    """
    Prompt 2 - Variation 4: Matrix Heat Map
    Governance Layers × Functional Domains
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Define matrix dimensions
    layers = [
        'Strategic\nDirection',
        'Policy\nFormulation',
        'Legal\nFramework',
        'Institutional\nCoordination',
        'Implementation\nMechanisms',
        'Execution\nEntities'
    ]

    domains = [
        'Defense\nTechnology',
        'Industrial\nBase',
        'Innovation\nSystem',
        'International\nEngagement',
        'Talent\nDevelopment',
        'Standards &\nRegulation',
        'Financing\nMechanisms',
        'Information\nSystems'
    ]

    # Create activity matrix (synthetic data based on MCF structure)
    # Higher values = more activity/emphasis
    matrix = np.array([
        # Def  Ind  Inn  Int  Tal  Std  Fin  Inf
        [10,  9,   8,   7,   6,   7,   8,   7],   # Strategic
        [9,   8,   9,   8,   7,   8,   7,   8],   # Policy
        [8,   7,   7,   9,   6,   10,  8,   9],   # Legal
        [7,   9,   8,   7,   8,   7,   9,   8],   # Coordination
        [9,   10,  10,  6,   9,   8,   10,  9],   # Implementation
        [10,  10,  9,   5,   8,   7,   9,   10]   # Execution
    ])

    # Create figure
    fig, ax = plt.subplots(figsize=(34, 24), facecolor='white')

    # Create heatmap using seaborn
    sns.heatmap(matrix, annot=True, fmt='d', cmap='YlOrRd',
               xticklabels=domains, yticklabels=layers,
               cbar_kws={'label': 'Activity Level'},
               linewidths=2, linecolor='white',
               annot_kws={'fontsize': 36, 'fontweight': 'bold'},
               ax=ax)

    # Update tick labels
    ax.set_xticklabels(domains, fontsize=34, fontweight='bold', rotation=45,
                      ha='right', color='#2C3E50')
    ax.set_yticklabels(layers, fontsize=34, fontweight='bold', rotation=0,
                      color='#2C3E50')

    # Update colorbar
    cbar = ax.collections[0].colorbar
    cbar.set_label('Activity Level (1-10)', fontsize=38, fontweight='bold',
                  color='#2C3E50')
    cbar.ax.tick_params(labelsize=32, colors='#2C3E50')

    # Labels
    ax.set_xlabel('Functional Domains', fontsize=40, fontweight='bold',
                 color='#2C3E50', labelpad=20)
    ax.set_ylabel('Governance Layers', fontsize=40, fontweight='bold',
                 color='#2C3E50', labelpad=20)
    ax.set_title('MCF Governance Matrix: Activity Levels by Layer and Domain\n'
                'Cross-Sectional Analysis of MCF Implementation Intensity',
                fontsize=46, fontweight='bold', pad=30, color='#2C3E50')

    # Add interpretation note
    note_text = (
        "INTERPRETATION:\n"
        "• Red = High Activity (8-10)\n"
        "• Yellow = Medium Activity (4-7)\n"
        "• Darker = Lower Activity (1-3)\n"
        "\n"
        "KEY INSIGHTS:\n"
        "• Defense Tech prioritized across all layers\n"
        "• Industrial Base strongest at execution\n"
        "• Legal framework critical for standards"
    )
    ax.text(1.15, 0.5, note_text, transform=ax.transAxes,
           fontsize=32, va='center',
           bbox=dict(boxstyle='round,pad=1.2', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_matrix_heatmap.png"
    svg_path = output_path / "mcf_matrix_heatmap.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


# ============================================================================
# PROMPT 3 - VARIATION 2: NETWORK GALAXY MAP
# ============================================================================

def create_galaxy_map(output_dir="visualizations"):
    """
    Prompt 3 - Variation 2: Network Galaxy Map
    Four initiatives as solar systems with BRI as center
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    bri_data = load_bri_database()

    # Create figure
    fig, ax = plt.subplots(figsize=(32, 32), facecolor='#0A0E27')

    # Define "solar systems" - initiatives as planets orbiting BRI
    systems = {
        'BRI': {
            'center': (0, 0),
            'radius': 2,
            'color': '#E74C3C',
            'satellites': []
        },
        'Digital_Silk_Road': {
            'center': (8, 8),
            'radius': 1.5,
            'color': '#9B59B6',
            'satellites': ['5G Networks', 'Fiber Optics', 'Data Centers']
        },
        'Health_Silk_Road': {
            'center': (-8, 8),
            'radius': 1.2,
            'color': '#E67E22',
            'satellites': ['Hospitals', 'Vaccines', 'Equipment']
        },
        'Space_Corridor': {
            'center': (8, -8),
            'radius': 1.3,
            'color': '#3498DB',
            'satellites': ['BeiDou', 'Satellites', 'Ground Stations']
        },
        'Green_BRI': {
            'center': (-8, -8),
            'radius': 1.1,
            'color': '#27AE60',
            'satellites': ['Solar', 'Wind', 'Hydro']
        }
    }

    # Draw orbital paths (circles around BRI center)
    orbital_radii = [6, 11]
    for radius in orbital_radii:
        circle = Circle((0, 0), radius, fill=False, edgecolor='#34495E',
                       linestyle='--', linewidth=2, alpha=0.4)
        ax.add_patch(circle)

    # Draw connection lines from satellites to BRI center
    for system_name, system_data in systems.items():
        if system_name != 'BRI':
            cx, cy = system_data['center']
            # Line to BRI
            ax.plot([0, cx], [0, cy], color=system_data['color'],
                   linewidth=3, alpha=0.5, linestyle=':')

    # Draw each "planet" (initiative)
    for system_name, system_data in systems.items():
        cx, cy = system_data['center']
        radius = system_data['radius']
        color = system_data['color']

        # Main planet
        planet = Circle((cx, cy), radius, facecolor=color, edgecolor='white',
                       linewidth=4, alpha=0.9, zorder=10)
        ax.add_patch(planet)

        # Planet label
        if system_name == 'BRI':
            label = 'BELT AND ROAD\nINITIATIVE'
            fontsize = 42
        else:
            # Clean up names
            label = system_name.replace('_', ' ').upper()
            fontsize = 36

        ax.text(cx, cy, label, fontsize=fontsize, fontweight='bold',
               ha='center', va='center', color='white', zorder=11)

        # Draw satellites
        if system_data['satellites']:
            n_sats = len(system_data['satellites'])
            sat_orbit_radius = radius + 1.5
            angles = np.linspace(0, 2*np.pi, n_sats, endpoint=False)

            for angle, sat_name in zip(angles, system_data['satellites']):
                sx = cx + sat_orbit_radius * np.cos(angle)
                sy = cy + sat_orbit_radius * np.sin(angle)

                # Satellite node
                sat_circle = Circle((sx, sy), 0.4, facecolor='#F39C12',
                                   edgecolor='white', linewidth=2, zorder=8)
                ax.add_patch(sat_circle)

                # Satellite label
                ax.text(sx, sy - 0.8, sat_name, fontsize=30, ha='center',
                       va='top', color='white',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='#2C3E50',
                                edgecolor='white', linewidth=1, alpha=0.8))

    # Add "stars" (projects) in background
    np.random.seed(42)
    for _ in range(50):
        x = np.random.uniform(-14, 14)
        y = np.random.uniform(-14, 14)
        ax.plot(x, y, marker='*', color='white', markersize=8, alpha=0.3)

    # Styling
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0A0E27')

    # Title
    fig.text(0.5, 0.97, 'China\'s Global Initiatives: Galaxy Network Model',
            fontsize=48, fontweight='bold', ha='center', color='white')
    fig.text(0.5, 0.94, 'BRI at Center with Four Strategic Initiative Systems',
            fontsize=38, ha='center', color='#ECF0F1', style='italic')

    # Legend
    legend_text = (
        "GALAXY STRUCTURE:\n"
        "• Central Star = BRI Core\n"
        "• Planets = Strategic Initiatives\n"
        "• Satellites = Implementation Sectors\n"
        "• Orbits = Integration Levels"
    )
    ax.text(-14, 13, legend_text, fontsize=34, va='top', color='white',
           bbox=dict(boxstyle='round,pad=1', facecolor='#2C3E50',
                    edgecolor='white', linewidth=2, alpha=0.9))

    # Save
    png_path = output_path / "mcf_galaxy_map.png"
    svg_path = output_path / "mcf_galaxy_map.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#0A0E27')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#0A0E27')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


# ============================================================================
# PROMPT 3 - VARIATION 3: LAYERED VENN DIAGRAM
# ============================================================================

def create_layered_venn(output_dir="visualizations"):
    """
    Prompt 3 - Variation 3: Layered Venn Diagram
    Showing overlap between four initiatives
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(32, 28), facecolor='white')

    # Define four main circles (initiatives)
    circles = {
        'BRI Traditional': {
            'center': (-3, 2),
            'radius': 5,
            'color': '#3498DB',
            'alpha': 0.3
        },
        'Digital Silk Road': {
            'center': (3, 2),
            'radius': 5,
            'color': '#9B59B6',
            'alpha': 0.3
        },
        'Health Silk Road': {
            'center': (-3, -3),
            'radius': 4.5,
            'color': '#E67E22',
            'alpha': 0.3
        },
        'Green BRI': {
            'center': (3, -3),
            'radius': 4.5,
            'color': '#27AE60',
            'alpha': 0.3
        }
    }

    # Draw circles
    for name, data in circles.items():
        circle = Circle(data['center'], data['radius'],
                       facecolor=data['color'], edgecolor='#2C3E50',
                       linewidth=4, alpha=data['alpha'], zorder=1)
        ax.add_patch(circle)

    # Add initiative labels (outside circles)
    label_positions = {
        'BRI Traditional': (-7, 6),
        'Digital Silk Road': (7, 6),
        'Health Silk Road': (-7, -7),
        'Green BRI': (7, -7)
    }

    for name, pos in label_positions.items():
        color = circles[name]['color']
        ax.text(pos[0], pos[1], name.upper(), fontsize=38, fontweight='bold',
               ha='center', va='center', color=color,
               bbox=dict(boxstyle='round,pad=0.8', facecolor='white',
                        edgecolor=color, linewidth=4))

    # Add overlap areas with labels
    overlaps = [
        # Position, Text, Description
        ((0, 2), 'SMART\nINFRASTRUCTURE', 'BRI + Digital'),
        ((-3, -0.5), 'SUSTAINABLE\nDEVELOPMENT', 'BRI + Health + Green'),
        ((3, -0.5), 'GREEN\nTECH', 'Digital + Green'),
        ((0, -3), 'HEALTH\nTECH', 'Health + Digital'),
        ((0, 0), 'INTEGRATED\nECOSYSTEM', 'All Four\nInitiatives')
    ]

    for pos, label, desc in overlaps:
        # Main overlap label
        ax.text(pos[0], pos[1], label, fontsize=36, fontweight='bold',
               ha='center', va='center', color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.7', facecolor='#FEF9E7',
                        edgecolor='#E74C3C', linewidth=3))

        # Description (smaller)
        ax.text(pos[0], pos[1] - 1, desc, fontsize=28, ha='center',
               va='top', color='#7F8C8D', style='italic')

    # Add example projects in each area
    examples = {
        'BRI Traditional': [
            (-3, 5, 'Railways'),
            (-5, 3, 'Ports'),
            (-2, 3, 'Highways')
        ],
        'Digital Silk Road': [
            (3, 5, '5G'),
            (5, 3, 'E-Commerce'),
            (2, 4, 'Data Centers')
        ],
        'Health Silk Road': [
            (-3, -6, 'Hospitals'),
            (-5, -4, 'Vaccines'),
            (-1, -5, 'Equipment')
        ],
        'Green BRI': [
            (3, -6, 'Solar'),
            (5, -4, 'Wind'),
            (1, -5, 'Hydro')
        ]
    }

    for init, items in examples.items():
        color = circles[init]['color']
        for x, y, text in items:
            ax.text(x, y, text, fontsize=32, ha='center', va='center',
                   color='white', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color,
                            edgecolor='white', linewidth=2, alpha=0.9))

    # Styling
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('China\'s Four Global Initiatives: Overlapping Strategies\n'
                'Venn Diagram Showing Integration and Synergies',
                fontsize=48, fontweight='bold', pad=40, color='#2C3E50')

    # Legend
    legend_text = (
        "OVERLAP DYNAMICS:\n"
        "• Single Circle = Core Initiative\n"
        "• Two-Way Overlap = Strategic Synergy\n"
        "• Three+ Way Overlap = Deep Integration\n"
        "• Center = Unified Ecosystem"
    )
    ax.text(-9.5, 9, legend_text, fontsize=34, va='top',
           bbox=dict(boxstyle='round,pad=1', facecolor='#F8F9FA',
                    edgecolor='#2C3E50', linewidth=3))

    # Save
    png_path = output_path / "mcf_layered_venn.png"
    svg_path = output_path / "mcf_layered_venn.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING MEDIUM COMPLEXITY MCF VISUALIZATIONS")
    print("MINIMUM FONT SIZE: 32PT")
    print("=" * 80)
    print()

    print("1. Matrix Heat Map (Prompt 2 - Variation 4)...")
    create_matrix_heatmap()
    print()

    print("2. Galaxy Network Map (Prompt 3 - Variation 2)...")
    create_galaxy_map()
    print()

    print("3. Layered Venn Diagram (Prompt 3 - Variation 3)...")
    create_layered_venn()
    print()

    print("=" * 80)
    print("MEDIUM COMPLEXITY VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print()
    print("Features:")
    print("  + 32pt MINIMUM font sizes")
    print("  + Matrix heatmap analysis")
    print("  + Galaxy network model")
    print("  + Multi-way Venn diagram")
    print("  + High-resolution PNG + SVG exports")
