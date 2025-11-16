#!/usr/bin/env python3
"""
Performance Profiling Analysis
Measures execution times for phases, database queries, and improvement generation
"""

import time
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phases.phase_01_data_validation import execute_phase_1
from src.phases.phase_02_technology_landscape import execute_phase_2
from src.phases.phase_03_supply_chain_v3_final import execute_phase_3
from src.phases.phase_04_institutions import execute_phase_4
from src.phases.phase_05_funding import execute_phase_5
from src.phases.phase_06_international_links import execute_phase_6
from src.core.improvement_recommendations import (
    get_phase_1_improvements,
    get_phase_2_improvements,
    get_phase_3_improvements,
    get_phase_4_improvements,
    get_phase_5_improvements,
    get_phase_6_improvements
)


def profile_phase(phase_func, country_code, phase_num, config=None):
    """Profile a single phase execution"""
    if config is None:
        config = {}

    start_time = time.time()

    result = phase_func(country_code, config)

    end_time = time.time()

    execution_time = end_time - start_time

    return {
        'phase': phase_num,
        'execution_time_seconds': round(execution_time, 3),
        'entries_generated': len(result.get('entries', [])),
        'has_improvements': result.get('metadata', {}).get('has_improvements', False)
    }


def profile_improvement_generation(improvement_func, country_code, phase_num):
    """Profile improvement recommendation generation"""
    start_time = time.time()

    improvements = improvement_func(country_code)

    end_time = time.time()
    execution_time = end_time - start_time

    return {
        'phase': phase_num,
        'execution_time_seconds': round(execution_time, 3),
        'has_priority_actions': 'priority_actions' in improvements,
        'priority_action_count': len(improvements.get('priority_actions', []))
    }


def profile_database_load():
    """Profile database loading and config file loading"""
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    config_path = Path("C:/Projects/OSINT - Foresight/config/country_specific_data_sources.json")

    # Database connection
    start_time = time.time()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    db_connect_time = time.time() - start_time

    # Sample query
    start_time = time.time()
    result = conn.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed").fetchone()
    query_time = time.time() - start_time
    conn.close()

    # Config file loading
    start_time = time.time()
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    config_load_time = time.time() - start_time
    config_size_kb = config_path.stat().st_size / 1024

    return {
        'database_connect_time_seconds': round(db_connect_time, 3),
        'sample_query_time_seconds': round(query_time, 3),
        'config_load_time_seconds': round(config_load_time, 3),
        'config_size_kb': round(config_size_kb, 2),
        'config_country_count': len([k for k in config_data.keys() if k != '_TEMPLATE'])
    }


def profile_country_sample(countries):
    """Profile execution for a sample of countries"""

    phase_functions = [
        (execute_phase_1, 1, "Data Validation"),
        (execute_phase_2, 2, "Technology Landscape"),
        (execute_phase_3, 3, "Supply Chain"),
        (execute_phase_4, 4, "Institutions"),
        (execute_phase_5, 5, "Funding Flows"),
        (execute_phase_6, 6, "International Links")
    ]

    improvement_functions = [
        (get_phase_1_improvements, 1),
        (get_phase_2_improvements, 2),
        (get_phase_3_improvements, 3),
        (get_phase_4_improvements, 4),
        (get_phase_5_improvements, 5),
        (get_phase_6_improvements, 6)
    ]

    results = {
        'timestamp': datetime.now().isoformat(),
        'countries_tested': countries,
        'country_count': len(countries),
        'system_info': profile_database_load(),
        'country_results': []
    }

    for country_code, country_name in countries:
        print(f"\nProfiling {country_name} ({country_code})...")

        country_result = {
            'country': country_code,
            'country_name': country_name,
            'phase_timings': [],
            'improvement_timings': [],
            'total_time_seconds': 0
        }

        country_start = time.time()

        # Profile each phase
        for phase_func, phase_num, phase_name in phase_functions:
            print(f"  Phase {phase_num}: {phase_name}...", end=" ")
            try:
                timing = profile_phase(phase_func, country_code, phase_num)
                country_result['phase_timings'].append(timing)
                print(f"{timing['execution_time_seconds']}s ({timing['entries_generated']} entries)")
            except Exception as e:
                print(f"ERROR: {e}")
                country_result['phase_timings'].append({
                    'phase': phase_num,
                    'error': str(e)
                })

        # Profile improvement generation separately
        print(f"  Improvement Recommendations...", end=" ")
        for improvement_func, phase_num in improvement_functions:
            try:
                timing = profile_improvement_generation(improvement_func, country_code, phase_num)
                country_result['improvement_timings'].append(timing)
            except Exception as e:
                country_result['improvement_timings'].append({
                    'phase': phase_num,
                    'error': str(e)
                })

        total_improvement_time = sum(t.get('execution_time_seconds', 0)
                                     for t in country_result['improvement_timings'])
        print(f"{total_improvement_time:.3f}s (all 6 phases)")

        country_end = time.time()
        country_result['total_time_seconds'] = round(country_end - country_start, 3)

        results['country_results'].append(country_result)

        print(f"  Total: {country_result['total_time_seconds']}s")

    return results


def analyze_results(results):
    """Analyze profiling results and generate summary"""

    summary = {
        'timestamp': results['timestamp'],
        'countries_tested': results['country_count'],
        'system_info': results['system_info'],
        'averages': {},
        'bottlenecks': [],
        'recommendations': []
    }

    # Calculate averages
    all_phase_times = []
    all_improvement_times = []
    all_total_times = []

    for country in results['country_results']:
        phase_times = [p.get('execution_time_seconds', 0) for p in country['phase_timings']]
        improvement_times = [i.get('execution_time_seconds', 0) for i in country['improvement_timings']]

        all_phase_times.extend(phase_times)
        all_improvement_times.extend(improvement_times)
        all_total_times.append(country['total_time_seconds'])

    summary['averages'] = {
        'avg_phase_time_seconds': round(sum(all_phase_times) / len(all_phase_times), 3) if all_phase_times else 0,
        'avg_improvement_time_seconds': round(sum(all_improvement_times) / len(all_improvement_times), 3) if all_improvement_times else 0,
        'avg_total_time_per_country_seconds': round(sum(all_total_times) / len(all_total_times), 3) if all_total_times else 0,
        'total_time_all_countries_seconds': round(sum(all_total_times), 3)
    }

    # Identify bottlenecks (phases taking >2 seconds on average)
    phase_avg_times = {}
    for country in results['country_results']:
        for phase in country['phase_timings']:
            if 'error' not in phase:
                phase_num = phase['phase']
                if phase_num not in phase_avg_times:
                    phase_avg_times[phase_num] = []
                phase_avg_times[phase_num].append(phase['execution_time_seconds'])

    for phase_num, times in phase_avg_times.items():
        avg_time = sum(times) / len(times)
        if avg_time > 2.0:
            summary['bottlenecks'].append({
                'phase': phase_num,
                'avg_time_seconds': round(avg_time, 3),
                'severity': 'HIGH' if avg_time > 5.0 else 'MODERATE'
            })

    # Generate recommendations
    if summary['system_info']['config_load_time_seconds'] > 1.0:
        summary['recommendations'].append({
            'area': 'Config Loading',
            'issue': f'Config file takes {summary["system_info"]["config_load_time_seconds"]}s to load',
            'recommendation': 'Consider implementing lazy loading or caching for country config'
        })

    if summary['averages']['avg_improvement_time_seconds'] > 0.1:
        summary['recommendations'].append({
            'area': 'Improvement Generation',
            'issue': f'Improvements take {summary["averages"]["avg_improvement_time_seconds"]}s per phase on average',
            'recommendation': 'Cache improvement recommendations or pre-generate for common countries'
        })

    if summary['bottlenecks']:
        summary['recommendations'].append({
            'area': 'Phase Execution',
            'issue': f'{len(summary["bottlenecks"])} phases identified as bottlenecks',
            'recommendation': 'Profile database queries in slow phases, consider indexing or caching'
        })

    return summary


def main():
    print("="*80)
    print("PERFORMANCE PROFILING ANALYSIS")
    print("="*80)

    # Test countries from different tiers
    test_countries = [
        ('IT', 'Italy'),           # Original (full data)
        ('GR', 'Greece'),          # Tier 1 (template)
        ('US', 'United States'),   # Tier 5 (template)
        ('JP', 'Japan'),           # Tier 6 (template)
        ('BR', 'Brazil')           # Tier 8 (template)
    ]

    print(f"\nTesting {len(test_countries)} countries:")
    for code, name in test_countries:
        print(f"  - {name} ({code})")

    print("\nStarting profiling...")

    start_time = time.time()
    results = profile_country_sample(test_countries)
    end_time = time.time()

    print("\n" + "="*80)
    print(f"PROFILING COMPLETE - Total Time: {end_time - start_time:.2f}s")
    print("="*80)

    # Analyze results
    summary = analyze_results(results)

    # Save results
    output_dir = Path("C:/Projects/OSINT - Foresight/analysis/performance_profiling")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "detailed_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    with open(output_dir / "summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {output_dir}")

    # Print summary
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)

    print(f"\nSystem Info:")
    print(f"  Database connect time: {summary['system_info']['database_connect_time_seconds']}s")
    print(f"  Config load time: {summary['system_info']['config_load_time_seconds']}s")
    print(f"  Config size: {summary['system_info']['config_size_kb']:.2f} KB")
    print(f"  Countries in config: {summary['system_info']['config_country_count']}")

    print(f"\nAverage Timings:")
    print(f"  Avg phase execution: {summary['averages']['avg_phase_time_seconds']}s")
    print(f"  Avg improvement generation: {summary['averages']['avg_improvement_time_seconds']}s")
    print(f"  Avg total per country: {summary['averages']['avg_total_time_per_country_seconds']}s")
    print(f"  Total for all {len(test_countries)} countries: {summary['averages']['total_time_all_countries_seconds']}s")

    if summary['bottlenecks']:
        print(f"\nBottlenecks Identified ({len(summary['bottlenecks'])}):")
        for bottleneck in summary['bottlenecks']:
            print(f"  Phase {bottleneck['phase']}: {bottleneck['avg_time_seconds']}s ({bottleneck['severity']})")
    else:
        print(f"\nNo significant bottlenecks identified (all phases <2s)")

    if summary['recommendations']:
        print(f"\nRecommendations ({len(summary['recommendations'])}):")
        for rec in summary['recommendations']:
            print(f"  [{rec['area']}]")
            print(f"    Issue: {rec['issue']}")
            print(f"    Recommendation: {rec['recommendation']}")

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)


if __name__ == "__main__":
    main()
