#!/usr/bin/env python3
"""
Automated Script Quality Audit
Checks for common issues across codebase
"""

import re
import json
from pathlib import Path
from collections import defaultdict

class ScriptQualityAuditor:
    """Automated code quality checks"""

    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

    def audit_script(self, script_path: Path) -> dict:
        """Audit a single script for quality issues"""
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return {'error': str(e)}

        results = {
            'path': str(script_path),
            'size': len(content),
            'lines': len(lines),
            'issues': []
        }

        # Check 1: No error handling
        if 'try:' not in content and 'except' not in content:
            results['issues'].append({
                'severity': 'MEDIUM',
                'type': 'no_error_handling',
                'message': 'No try/except blocks found - no error handling'
            })

        # Check 2: No logging
        if 'logging' not in content and 'print(' not in content:
            results['issues'].append({
                'severity': 'LOW',
                'type': 'no_logging',
                'message': 'No logging or print statements - no visibility'
            })

        # Check 3: Hardcoded credentials
        cred_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]
        for pattern in cred_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                results['issues'].append({
                    'severity': 'CRITICAL',
                    'type': 'hardcoded_credentials',
                    'message': f'Potential hardcoded credential: {pattern}'
                })

        # Check 4: SQL injection risk (string concatenation in SQL)
        if 'SELECT' in content or 'INSERT' in content or 'UPDATE' in content:
            # Look for f-strings or string concatenation in SQL
            if re.search(r'f["\'].*SELECT.*\{', content) or re.search(r'["\'].*SELECT.*["\'].*\+', content):
                results['issues'].append({
                    'severity': 'CRITICAL',
                    'type': 'sql_injection_risk',
                    'message': 'Potential SQL injection: String concatenation in SQL query'
                })

        # Check 5: Hardcoded paths (F:/, C:/)
        if re.search(r'["\'][CF]:[/\\]', content):
            results['issues'].append({
                'severity': 'MEDIUM',
                'type': 'hardcoded_paths',
                'message': 'Hardcoded drive paths (F:/ or C:/) - not portable'
            })

        # Check 6: TODO/FIXME/HACK comments
        todo_count = len(re.findall(r'#.*(?:TODO|FIXME|HACK|XXX)', content, re.IGNORECASE))
        if todo_count > 0:
            results['issues'].append({
                'severity': 'LOW',
                'type': 'technical_debt',
                'message': f'Found {todo_count} TODO/FIXME/HACK comments'
            })

        # Check 7: No docstring
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            results['issues'].append({
                'severity': 'LOW',
                'type': 'no_docstring',
                'message': 'No module docstring'
            })

        # Check 8: Large files (> 500 lines)
        if len(lines) > 500:
            results['issues'].append({
                'severity': 'LOW',
                'type': 'large_file',
                'message': f'{len(lines)} lines - consider splitting'
            })

        # Check 9: Dead code indicators
        if 'if False:' in content or 'if 0:' in content:
            results['issues'].append({
                'severity': 'LOW',
                'type': 'dead_code',
                'message': 'Dead code found (if False or if 0)'
            })

        # Check 10: No main guard
        if '__name__' not in content and 'def main(' in content:
            results['issues'].append({
                'severity': 'LOW',
                'type': 'no_main_guard',
                'message': 'Has main() but no if __name__ == "__main__" guard'
            })

        return results

    def audit_all(self, script_list):
        """Audit all scripts in list"""
        results = []

        for script_info in script_list:
            script_path = Path(script_info['path'])
            if script_path.exists():
                audit_result = self.audit_script(script_path)
                audit_result['category'] = script_info['category']
                audit_result['name'] = script_info['name']
                results.append(audit_result)

        return results

def main():
    # Load sample
    with open('PHASE3_AUDIT_SAMPLE.json') as f:
        sample = json.load(f)

    auditor = ScriptQualityAuditor()
    results = auditor.audit_all(sample)

    # Save detailed results
    with open('PHASE3_AUDIT_RESULTS.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Generate summary
    print("="*80)
    print("SCRIPT QUALITY AUDIT - AUTOMATED CHECKS")
    print("="*80)
    print(f"\nScripts Audited: {len(results)}")

    # Count by severity
    critical = sum(1 for r in results for i in r['issues'] if i['severity'] == 'CRITICAL')
    medium = sum(1 for r in results for i in r['issues'] if i['severity'] == 'MEDIUM')
    low = sum(1 for r in results for i in r['issues'] if i['severity'] == 'LOW')

    print(f"\nIssues Found:")
    print(f"  CRITICAL: {critical}")
    print(f"  MEDIUM:   {medium}")
    print(f"  LOW:      {low}")
    print(f"  TOTAL:    {critical + medium + low}")

    # Top issues
    issue_counts = defaultdict(int)
    for r in results:
        for issue in r['issues']:
            issue_counts[issue['type']] += 1

    print(f"\nTop Issue Types:")
    for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type:30} {count:3} scripts")

    # Show critical issues
    print(f"\n{'='*80}")
    print("CRITICAL ISSUES:")
    print("="*80)
    for r in results:
        critical_issues = [i for i in r['issues'] if i['severity'] == 'CRITICAL']
        if critical_issues:
            print(f"\n{r['name']} ({r['category']}):")
            for issue in critical_issues:
                print(f"  ⚠️  {issue['message']}")

    print(f"\nFull results saved to: PHASE3_AUDIT_RESULTS.json")

if __name__ == "__main__":
    main()
