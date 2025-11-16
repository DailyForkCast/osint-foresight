#!/usr/bin/env python3
"""
TED Format Timeline Analyzer
Samples XML files from every 6 months across 2011-2025 to identify format changes
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import tarfile
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class TEDFormatAnalyzer:
    """Analyze TED XML format changes over time"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.results = []

    def get_sample_periods(self) -> List[str]:
        """Generate list of YYYY-MM strings for every 6 months from 2011-2025"""
        periods = []
        for year in range(2011, 2026):
            for month in [1, 7]:  # January and July
                periods.append(f"{year:04d}_{month:02d}")
        return periods

    def find_archive_for_period(self, period: str) -> Optional[Path]:
        """Find TED archive for a specific period"""
        pattern = f"TED_monthly_{period}.tar.gz"
        archives = list(self.source_dir.rglob(pattern))
        return archives[0] if archives else None

    def extract_sample_xml(self, archive_path: Path) -> Optional[Path]:
        """Extract one sample XML file from archive"""
        temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/format_analysis")
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Open outer archive
            with tarfile.open(archive_path, 'r:gz', errorlevel=0) as outer_tar:
                # Get first inner archive
                members = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')]
                if not members:
                    return None

                # Extract first inner archive
                outer_tar.extract(members[0], temp_dir)
                inner_path = temp_dir / members[0].name

                # Open inner archive
                with tarfile.open(inner_path, 'r:gz', errorlevel=0) as inner_tar:
                    # Get first XML file
                    xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')]
                    if not xml_members:
                        return None

                    # Extract first XML
                    inner_tar.extract(xml_members[0], temp_dir)
                    return temp_dir / xml_members[0].name

        except Exception as e:
            print(f"  ERROR extracting {archive_path.name}: {e}")
            return None

    def analyze_xml_structure(self, xml_path: Path) -> Dict:
        """Deep analysis of XML structure"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            analysis = {
                'file_path': str(xml_path),
                'root_tag': root.tag,
                'root_tag_local': root.tag.split('}')[-1] if '}' in root.tag else root.tag,
                'root_attrib': dict(root.attrib),
                'namespace': None,
                'schema_location': None,
                'doc_id': None,
                'edition': None,
                'top_level_elements': [],
                'has_coded_data_section': False,
                'has_form_section': False,
                'has_notice_data': False,
                'notice_structure': {},
                'form_types': [],
                'data_locations': {},
                'sample_paths_found': {}
            }

            # Extract namespace
            if '}' in root.tag:
                analysis['namespace'] = root.tag.split('}')[0][1:]

            # Extract schema location
            schema_loc_key = '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'
            if schema_loc_key in root.attrib:
                analysis['schema_location'] = root.attrib[schema_loc_key]

            # Extract DOC_ID and EDITION
            analysis['doc_id'] = root.attrib.get('DOC_ID')
            analysis['edition'] = root.attrib.get('EDITION')

            # Analyze top-level structure
            for child in root:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                analysis['top_level_elements'].append(tag)

                # Check for key sections
                if tag == 'CODED_DATA_SECTION':
                    analysis['has_coded_data_section'] = True
                    self._analyze_coded_data(child, analysis)
                elif tag == 'FORM_SECTION':
                    analysis['has_form_section'] = True
                    self._analyze_form_section(child, analysis)

            # Search for key data elements throughout the tree
            self._find_data_locations(root, analysis)

            return analysis

        except Exception as e:
            return {'error': str(e), 'file_path': str(xml_path)}

    def _analyze_coded_data(self, coded_section: ET.Element, analysis: Dict):
        """Analyze CODED_DATA_SECTION structure"""
        # Look for NOTICE_DATA
        notice_data = coded_section.find('.//{*}NOTICE_DATA') or coded_section.find('.//NOTICE_DATA')
        if notice_data is not None:
            analysis['has_notice_data'] = True
            analysis['notice_structure'] = {
                'elements': [child.tag.split('}')[-1] if '}' in child.tag else child.tag
                           for child in notice_data]
            }

    def _analyze_form_section(self, form_section: ET.Element, analysis: Dict):
        """Analyze FORM_SECTION structure"""
        # Get form types
        for child in form_section:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag not in ['LEGAL_BASIS', 'LEGAL_BASIS_OTHER']:
                analysis['form_types'].append(tag)

    def _find_data_locations(self, root: ET.Element, analysis: Dict):
        """Find where specific data elements are located in the tree"""
        # Key elements to search for
        search_elements = {
            'NOTICE_NUMBER': [],
            'NO_DOC_OJS': [],
            'DATE_PUB': [],
            'CONTRACTING_AUTHORITY': [],
            'CONTRACTOR': [],
            'ECONOMIC_OPERATOR': [],
            'NAME': [],
            'COUNTRY': [],
            'TITLE': [],
            'CPV_CODE': [],
            'AWARD_DATE': [],
            'VAL_TOTAL': [],
        }

        # Search for each element
        for element_name in search_elements.keys():
            # Try with namespace
            ns_path = f'.//{{{analysis.get("namespace", "")}}}{element_name}'
            elements = root.findall(ns_path) if analysis.get('namespace') else []

            # Try without namespace
            if not elements:
                elements = root.findall(f'.//{element_name}')

            if elements:
                # Get path to first occurrence
                path = self._get_element_path(root, elements[0])
                search_elements[element_name] = path

        analysis['data_locations'] = search_elements

        # Try to extract sample values
        analysis['sample_paths_found'] = {
            'notice_number': self._get_text_any(root, ['NOTICE_NUMBER', 'NO_DOC_OJS']),
            'date': self._get_text_any(root, ['DATE_PUB']),
            'country': self._get_text_any(root, ['ISO_COUNTRY']),
            'contractor_name': self._get_text_any(root, ['CONTRACTOR/NAME', 'ECONOMIC_OPERATOR/NAME']),
            'title': self._get_text_any(root, ['TITLE', 'CONTRACT_TITLE'])
        }

    def _get_element_path(self, root: ET.Element, target: ET.Element) -> str:
        """Get XPath-like path to an element"""
        path = []
        current = target

        # Build path backwards
        while current is not None and current != root:
            parent = self._find_parent(root, current)
            if parent is not None:
                tag = current.tag.split('}')[-1] if '}' in current.tag else current.tag
                siblings = [c for c in parent if (c.tag.split('}')[-1] if '}' in c.tag else c.tag) == tag]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    path.insert(0, f"{tag}[{index}]")
                else:
                    path.insert(0, tag)
                current = parent
            else:
                break

        return '/' + '/'.join(path)

    def _find_parent(self, root: ET.Element, target: ET.Element) -> Optional[ET.Element]:
        """Find parent of an element"""
        for parent in root.iter():
            if target in list(parent):
                return parent
        return None

    def _get_text_any(self, root: ET.Element, paths: List[str]) -> Optional[str]:
        """Try multiple paths to get text"""
        for path in paths:
            elem = root.find(f'.//{path}')
            if elem is None:
                # Try with namespace
                elem = root.find(f'.//{{{root.tag.split("}")[0][1:]}}}{path}') if '}' in root.tag else None
            if elem is not None:
                text = elem.text or elem.get('VALUE') or elem.get('value')
                if text:
                    return text.strip()
        return None

    def run_analysis(self):
        """Run complete format analysis across all periods"""
        print("="*80)
        print("TED FORMAT TIMELINE ANALYSIS")
        print("Sampling XML files from every 6 months: 2011-2025")
        print("="*80)

        periods = self.get_sample_periods()
        print(f"\nAnalyzing {len(periods)} time periods...")

        for period in periods:
            print(f"\n[{period}] ", end='', flush=True)

            # Find archive
            archive = self.find_archive_for_period(period)
            if not archive:
                print("[SKIP] No archive found")
                self.results.append({
                    'period': period,
                    'status': 'no_archive',
                    'archive_name': None
                })
                continue

            print(f"Found: {archive.name} ", end='', flush=True)

            # Extract sample XML
            xml_file = self.extract_sample_xml(archive)
            if not xml_file:
                print("[FAIL] Could not extract XML")
                self.results.append({
                    'period': period,
                    'status': 'extraction_failed',
                    'archive_name': archive.name
                })
                continue

            print(f"[OK] Analyzing...", end='', flush=True)

            # Analyze structure
            analysis = self.analyze_xml_structure(xml_file)
            analysis['period'] = period
            analysis['archive_name'] = archive.name
            analysis['status'] = 'success'

            self.results.append(analysis)

            # Print key findings
            namespace = analysis.get('namespace', 'NONE')
            doc_id = analysis.get('doc_id', 'NONE')
            has_data = any(analysis.get('sample_paths_found', {}).values())
            print(f" [DONE] NS: {namespace[:40] if namespace and namespace != 'NONE' else 'NONE'} | Data: {'YES' if has_data else 'NO'}")

            # Cleanup
            if xml_file.exists():
                import shutil
                shutil.rmtree(xml_file.parent, ignore_errors=True)

        # Save results
        self.save_results()
        self.generate_report()

    def save_results(self):
        """Save detailed results to JSON"""
        output_file = Path("C:/Projects/OSINT - Foresight/analysis/TED_FORMAT_TIMELINE_ANALYSIS.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n[SUCCESS] Detailed results saved: {output_file}")

    def generate_report(self):
        """Generate human-readable format timeline report"""
        report_file = Path("C:/Projects/OSINT - Foresight/analysis/TED_FORMAT_TIMELINE_REPORT.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# TED XML Format Timeline Analysis\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Periods Analyzed**: {len(self.results)}\n\n")

            f.write("---\n\n")

            # Group by format characteristics
            format_groups = {}
            for result in self.results:
                if result.get('status') != 'success':
                    continue

                # Create format signature
                namespace = result.get('namespace', 'NONE')
                schema = result.get('schema_location', 'NONE')
                key = f"{namespace}|{schema}"

                if key not in format_groups:
                    format_groups[key] = []
                format_groups[key].append(result)

            f.write(f"## Format Groups Identified: {len(format_groups)}\n\n")

            for group_num, (key, results) in enumerate(format_groups.items(), 1):
                namespace, schema = key.split('|')
                f.write(f"### Format Group {group_num}\n\n")
                f.write(f"**Namespace**: `{namespace if namespace != 'NONE' else 'No namespace'}`\n\n")
                f.write(f"**Schema**: `{schema if schema != 'NONE' else 'No schema location'}`\n\n")

                # Time period
                periods = [r['period'] for r in results]
                f.write(f"**Time Period**: {periods[0]} to {periods[-1]} ({len(periods)} samples)\n\n")

                # Structure characteristics
                sample = results[0]
                f.write("**Structure**:\n")
                f.write(f"- Top-level elements: {', '.join(sample.get('top_level_elements', []))}\n")
                f.write(f"- Has CODED_DATA_SECTION: {sample.get('has_coded_data_section', False)}\n")
                f.write(f"- Has FORM_SECTION: {sample.get('has_form_section', False)}\n")
                f.write(f"- Has NOTICE_DATA: {sample.get('has_notice_data', False)}\n\n")

                # Data locations
                f.write("**Data Element Locations**:\n")
                for elem, path in sample.get('data_locations', {}).items():
                    if path:
                        f.write(f"- {elem}: `{path}`\n")

                f.write("\n**Sample Data Found**:\n")
                for key, value in sample.get('sample_paths_found', {}).items():
                    if value:
                        f.write(f"- {key}: `{value[:100]}`\n")

                f.write("\n---\n\n")

        print(f"[SUCCESS] Timeline report saved: {report_file}")


if __name__ == '__main__':
    analyzer = TEDFormatAnalyzer()
    analyzer.run_analysis()
