#!/usr/bin/env python3
"""
run_all_tests.py - Universal Test Runner Orchestrator
Part of Universal Extraction Success Contract v2.2

Automates execution of all validation tests based on tests.yaml configuration.
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class TestOrchestrator:
    """Orchestrates execution of all validation tests"""

    def __init__(self, config_file: str = "tests.yaml", verbose: bool = False):
        self.config_file = Path(config_file)
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "config": str(self.config_file),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": []
        }

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load test configuration from YAML"""
        if not self.config_file.exists():
            print(f"Error: Config file not found: {self.config_file}")
            sys.exit(1)

        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def _expand_env_vars(self, text: str) -> str:
        """Expand environment variables in command"""
        import re

        # First expand from config env section
        if "env" in self.config:
            for key, value in self.config["env"].items():
                text = text.replace(f"${{{key}}}", value)
                text = text.replace(f"${key}", value)

        # Then expand system environment variables
        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        text = re.sub(r'\$\{(\w+)\}', replacer, text)
        text = re.sub(r'\$(\w+)', replacer, text)

        return text

    def run_test(self, test_def: Dict) -> Tuple[str, bool, str]:
        """Run a single test"""
        test_id = test_def.get("id", "UNKNOWN")
        test_name = test_def.get("name", "Unnamed Test")
        cmd = test_def.get("cmd", "")
        expect_status = test_def.get("expect_status", "PASS")

        if not cmd:
            return test_id, False, "No command specified"

        # Expand environment variables
        cmd = self._expand_env_vars(cmd)

        print(f"\nRunning test {test_id}: {test_name}")
        if self.verbose:
            print(f"  Command: {cmd}")

        try:
            # Run command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Check if test passed
            if expect_status == "PASS":
                passed = result.returncode == 0
            elif expect_status == "FAIL":
                passed = result.returncode != 0
            else:
                passed = expect_status in result.stdout

            # Format output
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"

            if passed:
                print(f"  Result: [PASS]")
            else:
                print(f"  Result: [FAIL]")
                if self.verbose:
                    print(f"  Output: {output[:500]}")

            return test_id, passed, output

        except subprocess.TimeoutExpired:
            print(f"  Result: [TIMEOUT]")
            return test_id, False, "Test timed out after 5 minutes"
        except Exception as e:
            print(f"  Result: [ERROR]")
            return test_id, False, f"Error running test: {str(e)}"

    def run_all_tests(self, test_filter: str = None):
        """Run all tests or filtered subset"""
        tests = self.config.get("tests", [])

        if test_filter:
            tests = [t for t in tests if test_filter in t.get("id", "")]
            print(f"Running {len(tests)} filtered tests (filter: {test_filter})")
        else:
            print(f"Running {len(tests)} tests")

        for test_def in tests:
            test_id, passed, output = self.run_test(test_def)

            self.results["tests_run"] += 1
            if passed:
                self.results["tests_passed"] += 1
            else:
                self.results["tests_failed"] += 1

            self.results["test_results"].append({
                "id": test_id,
                "name": test_def.get("name", ""),
                "passed": passed,
                "output": output if not passed else output[:200]  # Truncate success output
            })

        # Run aggregation tests if no filter
        if not test_filter and "aggregation_tests" in self.config:
            print("\nRunning aggregation tests...")
            for test_def in self.config["aggregation_tests"]:
                test_id, passed, output = self.run_test(test_def)

                self.results["tests_run"] += 1
                if passed:
                    self.results["tests_passed"] += 1
                else:
                    self.results["tests_failed"] += 1

                self.results["test_results"].append({
                    "id": test_id,
                    "name": test_def.get("name", ""),
                    "passed": passed,
                    "output": output if not passed else output[:200]
                })

    def generate_report(self) -> str:
        """Generate test report"""
        report = []
        report.append("="*60)
        report.append(f"Test Orchestration Report")
        report.append(f"Generated: {self.results['timestamp']}")
        report.append("="*60)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-"*40)
        report.append(f"Total Tests Run: {self.results['tests_run']}")
        report.append(f"Tests Passed: {self.results['tests_passed']}")
        report.append(f"Tests Failed: {self.results['tests_failed']}")

        pass_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        report.append(f"Pass Rate: {pass_rate:.1f}%")
        report.append("")

        # Failed tests detail
        if self.results['tests_failed'] > 0:
            report.append("FAILED TESTS")
            report.append("-"*40)
            for test in self.results['test_results']:
                if not test['passed']:
                    report.append(f"[FAIL] {test['id']}: {test['name']}")
                    if self.verbose and test['output']:
                        report.append(f"       Output: {test['output'][:200]}")
            report.append("")

        # All tests summary
        report.append("ALL TESTS")
        report.append("-"*40)
        for test in self.results['test_results']:
            status = "[PASS]" if test['passed'] else "[FAIL]"
            report.append(f"{status} {test['id']}: {test['name']}")

        return "\n".join(report)

    def save_results(self, output_file: str = None):
        """Save test results to file"""
        if not output_file:
            output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Universal Test Runner Orchestrator")
    parser.add_argument("--config", default="tests.yaml", help="Test configuration file")
    parser.add_argument("--filter", help="Filter tests by ID pattern")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    orchestrator = TestOrchestrator(args.config, args.verbose)
    orchestrator.run_all_tests(args.filter)

    # Print report
    report = orchestrator.generate_report()
    print("\n" + report)

    # Save results
    if args.output:
        orchestrator.save_results(args.output)
    else:
        orchestrator.save_results()

    # Exit with appropriate code
    if orchestrator.results['tests_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
