#!/usr/bin/env python3
"""
Compliance Tracker: Ensures 100% adherence to playbook requirements
"""

import json
from pathlib import Path
from datetime import datetime

class ComplianceTracker:
    def __init__(self):
        self.requirements = {
            "Phase 0": {
                "artifacts": [
                    "inventory_manifest.json with SHA256 hashes",
                    "OS-level verification (dir /s or ls -lR)",
                    "10 random file paths with size + first 2KB hex dump",
                    "parse_failure_triage classification",
                    "phase0_verification_report.md"
                ],
                "validations": [
                    "Manifest reconciles with OS totals",
                    "SHA256 hashes computed",
                    "Hex dumps generated",
                    "Go/No-Go gate decision"
                ]
            },
            "Phase 1": {
                "artifacts": [
                    "content_profile.json per-file",
                    "Database introspection with table/row counts",
                    "Stratified sampling N=20 per dataset",
                    "Sample packs in samples/<dataset>/",
                    "Delta logging vs previous run"
                ],
                "validations": [
                    "3 proofs for any 'XX GB analyzed' claim",
                    "Parse success rates documented",
                    "Schema inference completed",
                    "Row counts verified"
                ]
            },
            "Phase 2": {
                "artifacts": [
                    "Canonical field definitions",
                    "joinability_matrix.csv",
                    "data_quality_scorecards.json (0-100)",
                    "10 random successful joins per high-viability pair"
                ],
                "validations": [
                    "All sources mapped to canonical fields",
                    "Joinability scores computed",
                    "Quality metrics 0-100 scale",
                    "Join examples documented"
                ]
            },
            "Phase 3": {
                "artifacts": [
                    "china_dictionary.json with sources",
                    "variant_coverage_matrix.csv",
                    "Evidence packs for Huawei, COSCO",
                    "Control group benchmarks",
                    "Cross-script normalization logs"
                ],
                "validations": [
                    "All variant types tested",
                    "False positive/negative rates",
                    "Null justification notes",
                    "Coverage metrics"
                ]
            },
            "Phase 4": {
                "artifacts": [
                    "Temporal views (monthly/yearly)",
                    "Geographic views (ISO, EU buckets)",
                    "Technology taxonomy mapping",
                    "Export SQL/code with row counts",
                    "Reconciliation tables",
                    "Error bars/confidence intervals"
                ],
                "validations": [
                    "Temporal coverage 2000-present",
                    "All EU countries mapped",
                    "Reconciliation deltas <5%",
                    "Bias notes documented"
                ]
            },
            "Phase 5": {
                "artifacts": [
                    "Entity registry with >70% alias coverage",
                    "Entity timelines merged across sources",
                    "10 entity provenance packs (≥3 sources)",
                    "Precision/recall scores",
                    "Mismatch reports"
                ],
                "validations": [
                    "NER recall >70%",
                    "Entity deduplication",
                    "Cross-source verification",
                    "Timeline consistency"
                ]
            },
            "Phase 6": {
                "artifacts": [
                    "Automated readiness scores",
                    "run.json for every step",
                    "Compliance checklist",
                    "Access control implementation",
                    "Retention clocks"
                ],
                "validations": [
                    "All quality gates defined",
                    "Monitoring active",
                    "Governance documented",
                    "Break-glass appendix"
                ]
            }
        }

        self.completed = {}
        self.compliance_report = {
            'generated': datetime.now().isoformat(),
            'phases': {}
        }

    def check_requirement(self, phase, requirement, status=False, evidence=None):
        """Mark a requirement as complete with evidence"""
        if phase not in self.completed:
            self.completed[phase] = {}

        self.completed[phase][requirement] = {
            'status': 'COMPLETE' if status else 'PENDING',
            'evidence': evidence,
            'timestamp': datetime.now().isoformat()
        }

    def get_phase_compliance(self, phase):
        """Calculate compliance percentage for a phase"""
        total_reqs = len(self.requirements[phase]['artifacts']) + len(self.requirements[phase]['validations'])
        completed_reqs = len([r for r in self.completed.get(phase, {}).values() if r['status'] == 'COMPLETE'])

        return (completed_reqs / total_reqs * 100) if total_reqs > 0 else 0

    def generate_checklist(self, phase):
        """Generate checklist for a phase"""
        checklist = f"\n## {phase} Compliance Checklist\n\n"
        checklist += "### Required Artifacts:\n"

        for artifact in self.requirements[phase]['artifacts']:
            status = '✅' if self.completed.get(phase, {}).get(artifact, {}).get('status') == 'COMPLETE' else '❌'
            checklist += f"- [{status}] {artifact}\n"

        checklist += "\n### Required Validations:\n"
        for validation in self.requirements[phase]['validations']:
            status = '✅' if self.completed.get(phase, {}).get(validation, {}).get('status') == 'COMPLETE' else '❌'
            checklist += f"- [{status}] {validation}\n"

        compliance = self.get_phase_compliance(phase)
        checklist += f"\n**Compliance: {compliance:.1f}%**\n"

        return checklist

    def save_compliance_report(self):
        """Save compliance tracking report"""
        for phase in self.requirements.keys():
            self.compliance_report['phases'][phase] = {
                'compliance_percentage': self.get_phase_compliance(phase),
                'requirements': self.completed.get(phase, {}),
                'checklist': self.generate_checklist(phase)
            }

        with open("C:/Projects/OSINT - Foresight/compliance_report.json", 'w') as f:
            json.dump(self.compliance_report, f, indent=2, default=str)

        # Generate markdown report
        report = "# Playbook Compliance Report\n\n"
        report += f"Generated: {self.compliance_report['generated']}\n\n"

        for phase, data in self.compliance_report['phases'].items():
            report += data['checklist']
            report += "\n---\n"

        with open("C:/Projects/OSINT - Foresight/compliance_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        return self.compliance_report

# Global tracker instance
tracker = ComplianceTracker()
