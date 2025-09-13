#!/usr/bin/env python3
"""
Verify phase renumbering is complete
"""
import os
from pathlib import Path

def check_files():
    """Check that all renamed files exist and old names don't"""
    
    # Mapping of old to new phase numbers
    phase_map = {
        'X': '0',
        '0': '1', 
        '1': '2',
        '2': '3',
        '2S': '4',
        '3': '5',
        '4': '6',
        '5': '7',
        '6': '8',
        '7C': '9',
        '7R': '10',
        '8': '11',
        '9': '12',
        '10': '13'
    }
    
    issues = []
    
    # Check Python analysis scripts
    analysis_dir = Path('src/analysis')
    expected_scripts = {
        'phase3_landscape.py': 'Phase 3 (was 2)',
        'phase4_supply_chain.py': 'Phase 4 (was 2S)',
        'phase5_institutions.py': 'Phase 5 (was 3)',
        'phase6_funders.py': 'Phase 6 (was 4)',
        'phase7_links.py': 'Phase 7 (was 5)',
        'phase8_risk.py': 'Phase 8 (was 6)',
        'phase9_posture.py': 'Phase 9 (was 7C)',
        'phase11_foresight.py': 'Phase 11 (was 8)',
    }
    
    print("Checking Python analysis scripts...")
    for script, desc in expected_scripts.items():
        path = analysis_dir / script
        if path.exists():
            print(f"  [OK] {script} - {desc}")
        else:
            issues.append(f"Missing: {path}")
            print(f"  [X] {script} - MISSING")
    
    # Check for old script names that shouldn't exist
    old_scripts = ['phase2_landscape.py', 'phase2s_supply_chain.py', 'phase3_institutions.py',
                   'phase4_funders.py', 'phase5_links.py', 'phase6_risk.py', 
                   'phase7c_posture.py', 'phase8_foresight.py']
    
    print("\nChecking old script names are removed...")
    for old in old_scripts:
        path = analysis_dir / old
        if path.exists():
            issues.append(f"Old file still exists: {path}")
            print(f"  [X] {old} still exists!")
        else:
            print(f"  [OK] {old} removed")
    
    # Check Makefile references
    print("\nChecking Makefile references...")
    makefile = Path('Makefile')
    if makefile.exists():
        content = makefile.read_text()
        new_refs = [
            'phase3_landscape',
            'phase4_supply_chain', 
            'phase5_institutions',
            'phase6_funders',
            'phase7_links',
            'phase8_risk',
            'phase9_posture',
            'phase11_foresight'
        ]
        for ref in new_refs:
            if ref in content:
                print(f"  [OK] Found {ref}")
            else:
                issues.append(f"Makefile missing: {ref}")
                print(f"  [X] Missing {ref}")
    
    # Check config files
    print("\nChecking config files...")
    models_yaml = Path('config/models.yaml')
    if models_yaml.exists():
        content = models_yaml.read_text()
        if 'phase9:' in content:
            print("  [OK] models.yaml updated to phase9")
        else:
            issues.append("models.yaml not updated")
            print("  [X] models.yaml still has old phase reference")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("[SUCCESS] All phase renumbering checks passed!")
        print("\nPhase Renumbering Summary:")
        print("  X -> 0  (Taxonomy)")
        print("  0 -> 1  (Setup)")
        print("  1 -> 2  (Indicators)")
        print("  2 -> 3  (Landscape)")
        print("  2S -> 4 (Supply Chain)")
        print("  3 -> 5  (Institutions)")
        print("  4 -> 6  (Funders)")
        print("  5 -> 7  (Links)")
        print("  6 -> 8  (Risk)")
        print("  7C -> 9 (PRC/MCF)")
        print("  7R -> 10 (Red Team)")
        print("  8 -> 11 (Foresight)")
        print("  9 -> 12 (Extended)")
        print("  10 -> 13 (Closeout)")
        return 0

if __name__ == "__main__":
    exit(check_files())