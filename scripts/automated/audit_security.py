#!/usr/bin/env python3
"""
Phase 8: Security Vulnerability Assessment
Identifies security vulnerabilities and risks
"""

import re
import json
from pathlib import Path
from collections import defaultdict


class SecurityAuditor:
    """Audit for security vulnerabilities"""

    def __init__(self):
        self.vulnerabilities = []
        self.security_stats = {}

    def scan_sql_injection_patterns(self):
        """Scan for SQL injection vulnerabilities"""
        print("\n" + "="*80)
        print("TEST 1: SQL Injection Vulnerability Scan")
        print("="*80)

        scripts_dir = Path("C:/Projects/OSINT-Foresight/scripts")
        if not scripts_dir.exists():
            print("  [SKIP] Scripts directory not accessible")
            return {}

        results = {
            'scripts_scanned': 0,
            'vulnerable_scripts': 0,
            'total_vulnerabilities': 0,
            'details': []
        }

        # Patterns indicating SQL injection risk
        sql_injection_patterns = [
            (r'execute\s*\(\s*f["\'].*SELECT.*\{', 'F-string in SQL query'),
            (r'execute\s*\(\s*["\'].*SELECT.*["\'].*\+', 'String concatenation in SQL'),
            (r'execute\s*\(\s*.*%.*format\s*\(', 'String formatting in SQL'),
        ]

        for script_path in scripts_dir.rglob("*.py"):
            results['scripts_scanned'] += 1

            try:
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                vulnerabilities_found = []
                for pattern, description in sql_injection_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        vulnerabilities_found.append({
                            'line': line_num,
                            'type': description,
                            'snippet': match.group()[:80]
                        })
                        results['total_vulnerabilities'] += 1

                if vulnerabilities_found:
                    results['vulnerable_scripts'] += 1
                    results['details'].append({
                        'file': script_path.name,
                        'vulnerabilities': vulnerabilities_found
                    })

            except Exception as e:
                pass  # Skip files that can't be read

        print(f"  Scripts scanned: {results['scripts_scanned']}")
        print(f"  Vulnerable scripts: {results['vulnerable_scripts']}")
        print(f"  Total SQL injection patterns: {results['total_vulnerabilities']}")

        if results['vulnerable_scripts'] > 0:
            print(f"\n  Top vulnerable scripts:")
            for detail in sorted(results['details'], key=lambda x: len(x['vulnerabilities']), reverse=True)[:5]:
                print(f"    {detail['file']:60} {len(detail['vulnerabilities'])} patterns")

        if results['vulnerable_scripts'] > 0:
            self.vulnerabilities.append({
                'vulnerability_type': 'sql_injection',
                'severity': 'CRITICAL',
                'count': results['vulnerable_scripts'],
                'message': f"{results['vulnerable_scripts']} scripts with SQL injection patterns",
                'affected_scripts': [d['file'] for d in results['details'][:10]]
            })

        self.security_stats['sql_injection'] = results
        return results

    def scan_hardcoded_credentials(self):
        """Scan for hardcoded credentials"""
        print("\n" + "="*80)
        print("TEST 2: Hardcoded Credentials Scan")
        print("="*80)

        scripts_dir = Path("C:/Projects/OSINT-Foresight/scripts")
        if not scripts_dir.exists():
            print("  [SKIP] Scripts directory not accessible")
            return {}

        results = {
            'scripts_scanned': 0,
            'potential_credentials': 0,
            'details': []
        }

        # Patterns for potential credentials (conservative to avoid false positives)
        credential_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']{16,}["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{32,}["\']', 'Hardcoded token'),
        ]

        for script_path in scripts_dir.rglob("*.py"):
            results['scripts_scanned'] += 1

            try:
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                credentials_found = []
                for pattern, description in credential_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Filter out obvious test/example values
                        value = match.group()
                        if any(test in value.lower() for test in ['test', 'example', 'your_', 'dummy', 'placeholder']):
                            continue

                        line_num = content[:match.start()].count('\n') + 1
                        credentials_found.append({
                            'line': line_num,
                            'type': description
                        })
                        results['potential_credentials'] += 1

                if credentials_found:
                    results['details'].append({
                        'file': script_path.name,
                        'credentials': credentials_found
                    })

            except Exception as e:
                pass

        print(f"  Scripts scanned: {results['scripts_scanned']}")
        print(f"  Potential credentials found: {results['potential_credentials']}")

        if results['potential_credentials'] > 0:
            print(f"\n  Files with potential credentials:")
            for detail in results['details'][:5]:
                print(f"    {detail['file']:60} {len(detail['credentials'])} instances")

            self.vulnerabilities.append({
                'vulnerability_type': 'hardcoded_credentials',
                'severity': 'HIGH',
                'count': len(results['details']),
                'message': f"{len(results['details'])} scripts may have hardcoded credentials",
                'affected_scripts': [d['file'] for d in results['details'][:5]]
            })

        self.security_stats['hardcoded_credentials'] = results
        return results

    def scan_input_validation(self):
        """Check for input validation"""
        print("\n" + "="*80)
        print("TEST 3: Input Validation Assessment")
        print("="*80)

        scripts_dir = Path("C:/Projects/OSINT-Foresight/scripts")
        if not scripts_dir.exists():
            print("  [SKIP] Scripts directory not accessible")
            return {}

        results = {
            'scripts_scanned': 0,
            'scripts_with_validation': 0,
            'scripts_without_validation': 0,
            'details': []
        }

        # Patterns indicating input validation
        validation_patterns = [
            r'isinstance\s*\(',
            r'assert\s+',
            r'if\s+not\s+\w+:.*raise',
            r'validate',
            r'sanitize',
        ]

        for script_path in scripts_dir.rglob("*.py"):
            if script_path.name.startswith('test_'):
                continue  # Skip test files

            results['scripts_scanned'] += 1

            try:
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                has_validation = any(re.search(pattern, content, re.IGNORECASE) for pattern in validation_patterns)

                if has_validation:
                    results['scripts_with_validation'] += 1
                else:
                    results['scripts_without_validation'] += 1

            except Exception as e:
                pass

        validation_rate = (results['scripts_with_validation'] / results['scripts_scanned'] * 100) if results['scripts_scanned'] > 0 else 0

        print(f"  Scripts scanned: {results['scripts_scanned']}")
        print(f"  Scripts with validation: {results['scripts_with_validation']} ({validation_rate:.1f}%)")
        print(f"  Scripts without validation: {results['scripts_without_validation']}")

        if validation_rate < 30:
            self.vulnerabilities.append({
                'vulnerability_type': 'insufficient_input_validation',
                'severity': 'MEDIUM',
                'count': results['scripts_without_validation'],
                'message': f"Only {validation_rate:.1f}% of scripts have input validation",
                'recommendation': 'Add input validation to prevent injection and data corruption'
            })

        self.security_stats['input_validation'] = results
        return results

    def scan_file_permissions(self):
        """Check for sensitive file exposure"""
        print("\n" + "="*80)
        print("TEST 4: Sensitive File Exposure Check")
        print("="*80)

        project_root = Path("C:/Projects/OSINT-Foresight")
        if not project_root.exists():
            print("  [SKIP] Project root not accessible")
            return {}

        results = {
            'sensitive_files_found': 0,
            'files': []
        }

        # Sensitive file patterns
        sensitive_patterns = [
            '*.env',
            '.env.*',
            '*credentials*.json',
            '*secrets*.json',
            '*.pem',
            '*.key',
            '*password*.txt',
        ]

        for pattern in sensitive_patterns:
            for file_path in project_root.rglob(pattern):
                # Exclude example files
                if 'example' in file_path.name.lower():
                    continue

                results['sensitive_files_found'] += 1
                results['files'].append({
                    'file': str(file_path.relative_to(project_root)),
                    'type': pattern
                })

        print(f"  Sensitive files found: {results['sensitive_files_found']}")

        if results['sensitive_files_found'] > 0:
            print(f"\n  Sensitive files:")
            for file_info in results['files'][:10]:
                print(f"    {file_info['file']}")

            self.vulnerabilities.append({
                'vulnerability_type': 'sensitive_file_exposure',
                'severity': 'HIGH',
                'count': results['sensitive_files_found'],
                'message': f"{results['sensitive_files_found']} sensitive files found in project",
                'recommendation': 'Add to .gitignore and ensure not committed to repository'
            })

        self.security_stats['file_permissions'] = results
        return results

    def check_dependency_security(self):
        """Check for outdated or vulnerable dependencies"""
        print("\n" + "="*80)
        print("TEST 5: Dependency Security Check")
        print("="*80)

        requirements_path = Path("C:/Projects/OSINT-Foresight/requirements.txt")

        results = {
            'has_requirements': requirements_path.exists(),
            'dependencies_count': 0,
            'outdated_dependencies': 0
        }

        if not requirements_path.exists():
            print("  [INFO] No requirements.txt found")
            print("  Recommendation: Create requirements.txt to track dependencies")

            self.vulnerabilities.append({
                'vulnerability_type': 'no_dependency_tracking',
                'severity': 'MEDIUM',
                'message': 'No requirements.txt found - dependencies not tracked',
                'recommendation': 'Create requirements.txt to enable security scanning'
            })
        else:
            try:
                with open(requirements_path, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    results['dependencies_count'] = len(deps)

                print(f"  Dependencies found: {results['dependencies_count']}")
                print(f"  Recommendation: Run 'pip-audit' to check for vulnerabilities")

            except Exception as e:
                print(f"  [ERROR] Could not read requirements.txt: {e}")

        self.security_stats['dependencies'] = results
        return results

    def generate_summary(self):
        """Generate security audit summary"""
        print("\n" + "="*80)
        print("PHASE 8: SECURITY VULNERABILITY ASSESSMENT SUMMARY")
        print("="*80)

        total_vulnerabilities = len(self.vulnerabilities)

        print(f"\nSecurity Vulnerabilities Found: {total_vulnerabilities}")

        if total_vulnerabilities == 0:
            print("\n[EXCELLENT] No security vulnerabilities detected")
        else:
            print("\n" + "-"*80)
            print("VULNERABILITIES BY SEVERITY")
            print("-"*80)

            by_severity = defaultdict(list)
            for vuln in self.vulnerabilities:
                by_severity[vuln['severity']].append(vuln)

            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    print(f"\n{severity} Severity ({len(by_severity[severity])} vulnerabilities):")
                    for vuln in by_severity[severity]:
                        print(f"  - {vuln['message']}")

        return {
            'total_vulnerabilities': total_vulnerabilities,
            'vulnerabilities': self.vulnerabilities,
            'security_stats': self.security_stats
        }


def main():
    print("="*80)
    print("PHASE 8: SECURITY VULNERABILITY ASSESSMENT")
    print("Identifying security vulnerabilities and risks")
    print("="*80)

    auditor = SecurityAuditor()

    # Run all security tests
    auditor.scan_sql_injection_patterns()
    auditor.scan_hardcoded_credentials()
    auditor.scan_input_validation()
    auditor.scan_file_permissions()
    auditor.check_dependency_security()

    # Generate summary
    summary = auditor.generate_summary()

    # Save results
    output_file = Path("PHASE8_SECURITY_AUDIT_RESULTS.json")
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {output_file}")

    return summary


if __name__ == "__main__":
    main()
