#!/usr/bin/env python3
"""
TED UBL eForms Parser (Era 3: Feb 2024 - Present)

Comprehensive parser for EU eForms (Universal Business Language) format
introduced in February 2024. Extracts all available procurement data fields
with completeness prioritized over speed.

UBL eForms Specification: https://docs.ted.europa.eu/eforms/
OASIS UBL Standard: http://docs.oasis-open.org/ubl/

Uses lxml for proper namespace prefix support in XPath queries.
"""

from lxml import etree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UBLEFormsParser:
    """
    Comprehensive parser for UBL eForms (Era 3) TED procurement notices

    Handles all notice types:
    - ContractNotice-2
    - ContractAwardNotice-2
    - CompetitionNotice-2
    - PlanningNotice-2
    - And other eForms variants
    """

    def __init__(self):
        """Initialize UBL parser with comprehensive namespace support"""

        # UBL eForms namespaces (comprehensive list)
        self.namespaces = {
            # Core UBL 2.3 namespaces
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',

            # Notice-specific namespaces
            'cn': 'urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2',
            'can': 'urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2',
            'pin': 'urn:oasis:names:specification:ubl:schema:xsd:PriorInformationNotice-2',

            # eForms extensions
            'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
            'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
            'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',

            # Additional standards
            'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2',
            'udt': 'urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2',
        }

        self.statistics = {
            'total_parsed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'notices_by_type': {},
            'fields_extracted': {}
        }

    def parse_notice(self, xml_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a UBL eForms XML notice and extract all available fields

        Args:
            xml_path: Path to XML file

        Returns:
            Dictionary with all extracted fields, or None if parsing fails
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Extract actual namespaces from the XML document
            self.namespaces = self._extract_namespaces(root)

            # Detect notice type from root element
            notice_type = self._detect_notice_type(root)

            self.statistics['total_parsed'] += 1
            self.statistics['notices_by_type'][notice_type] = \
                self.statistics['notices_by_type'].get(notice_type, 0) + 1

            # STEP 1: Extract organizations FIRST (master lookup from UBLExtensions)
            organizations = self._extract_organizations(root)

            # STEP 2: Extract supporting data from NoticeResult (in UBLExtensions)
            tendering_parties = self._extract_tendering_parties(root)
            lot_tenders = self._extract_lot_tenders(root)
            settled_contracts = self._extract_settled_contracts(root)

            # STEP 3: Resolve entities using v2 methods with organizations dict
            contracting_party_resolved = self._extract_contracting_party_v2(root, organizations)
            economic_operators_resolved = self._extract_economic_operators_v2(
                root, organizations, tendering_parties, lot_tenders, settled_contracts
            )
            award_results_resolved = self._extract_award_results_v2(
                root, settled_contracts, lot_tenders, tendering_parties, organizations
            )

            # Extract all fields comprehensively
            notice_data = {
                # Core identification
                'notice_type': notice_type,
                'notice_id': self._extract_notice_id(root),
                'issue_date': self._extract_issue_date(root),
                'issue_time': self._extract_issue_time(root),

                # Version and customization
                'ubl_version': self._extract_ubl_version(root),
                'customization_id': self._extract_customization_id(root),
                'eforms_sdk_version': self._extract_eforms_sdk_version(root),

                # Regulatory and administrative
                'regulatory_domain': self._extract_regulatory_domain(root),
                'notice_type_code': self._extract_notice_type_code(root),
                'notice_language': self._extract_notice_language(root),
                'contract_folder_id': self._extract_contract_folder_id(root),
                'version_id': self._extract_version_id(root),

                # Contracting authority/party information (RESOLVED from organizations)
                'contracting_party': contracting_party_resolved,

                # Procurement project details
                'procurement_project': self._extract_procurement_project(root),

                # Tendering process
                'tendering_process': self._extract_tendering_process(root),

                # Tendering terms
                'tendering_terms': self._extract_tendering_terms(root),

                # Economic operators (contractors/winners) - RESOLVED from organizations
                'economic_operators': economic_operators_resolved,

                # Award results (for contract award notices) - RESOLVED with complete data
                'award_results': award_results_resolved,

                # Lots information
                'lots': self._extract_lots(root),

                # Items and deliverables
                'items': self._extract_items(root),

                # Additional information
                'additional_info': self._extract_additional_information(root),

                # Extensions and custom fields
                'extensions': self._extract_extensions(root),

                # Metadata
                'source_file': str(xml_path),
                'extraction_timestamp': datetime.now().isoformat(),
                'format_era': 'ERA_3_UBL_EFORMS'
            }

            self.statistics['successful_extractions'] += 1
            return notice_data

        except Exception as e:
            logger.error(f"Failed to parse {xml_path}: {e}")
            self.statistics['failed_extractions'] += 1
            return None

    def _extract_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """
        Extract namespace prefixes from XML root element
        Returns a dictionary mapping prefixes to namespace URIs

        lxml properly extracts namespaces from the document
        """
        # Get namespaces from the document (lxml does this automatically)
        nsmap = root.nsmap if hasattr(root, 'nsmap') else {}

        # Create a clean namespace dictionary (remove None key)
        namespaces = {}
        for prefix, uri in nsmap.items():
            if prefix is not None:  # Skip default namespace (None key)
                namespaces[prefix] = uri

        # Ensure we have all standard UBL eForms namespaces
        # (in case document doesn't declare all of them)
        standard_ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
            'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
            'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        }

        # Merge: prefer document namespaces, add missing standard ones
        for prefix, uri in standard_ns.items():
            if prefix not in namespaces:
                namespaces[prefix] = uri

        return namespaces

    def _detect_notice_type(self, root: ET.Element) -> str:
        """Detect notice type from root element"""
        root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        return root_tag

    def _find(self, root: ET.Element, xpath: str) -> Optional[ET.Element]:
        """Find element with namespace support"""
        try:
            elem = root.find(xpath, namespaces=self.namespaces)
            return elem
        except:
            # Try without namespace as fallback
            try:
                return root.find(xpath)
            except:
                return None

    def _findall(self, root: ET.Element, xpath: str) -> List[ET.Element]:
        """Find all elements with namespace support"""
        try:
            elements = root.findall(xpath, namespaces=self.namespaces)
            return elements if elements else []
        except:
            # Try without namespace as fallback
            try:
                return root.findall(xpath)
            except:
                return []

    def _get_text(self, root: ET.Element, xpath: str, default: Optional[str] = None) -> Optional[str]:
        """Get text content with namespace support"""
        elem = self._find(root, xpath)
        if elem is not None:
            text = elem.text or elem.get('value') or elem.get('VALUE')
            return str(text).strip() if text else default
        return default

    def _extract_notice_id(self, root: ET.Element) -> Optional[str]:
        """Extract notice ID (replaces NO_DOC_OJS from Era 2)"""
        # Try multiple possible paths
        paths = [
            './/cbc:ID',
            './/ID',
            './/cbc:ContractFolderID'
        ]
        for path in paths:
            notice_id = self._get_text(root, path)
            if notice_id:
                return notice_id
        return None

    def _extract_issue_date(self, root: ET.Element) -> Optional[str]:
        """Extract issue date (replaces DATE_PUB from Era 2)"""
        return self._get_text(root, './/cbc:IssueDate') or self._get_text(root, './/IssueDate')

    def _extract_issue_time(self, root: ET.Element) -> Optional[str]:
        """Extract issue time"""
        return self._get_text(root, './/cbc:IssueTime') or self._get_text(root, './/IssueTime')

    def _extract_ubl_version(self, root: ET.Element) -> Optional[str]:
        """Extract UBL version"""
        return self._get_text(root, './/cbc:UBLVersionID') or self._get_text(root, './/UBLVersionID')

    def _extract_customization_id(self, root: ET.Element) -> Optional[str]:
        """Extract customization ID"""
        return self._get_text(root, './/cbc:CustomizationID') or self._get_text(root, './/CustomizationID')

    def _extract_eforms_sdk_version(self, root: ET.Element) -> Optional[str]:
        """Extract eForms SDK version from customization ID"""
        custom_id = self._extract_customization_id(root)
        if custom_id and 'eforms-sdk' in custom_id:
            # Extract version like "eforms-sdk-1.7"
            parts = custom_id.split('-')
            if len(parts) >= 3:
                return parts[-1]
        return None

    def _extract_regulatory_domain(self, root: ET.Element) -> Optional[str]:
        """Extract regulatory domain"""
        paths = [
            './/cbc:RegulatoryDomain',
            './/RegulatoryDomain',
            './/cbc:RegulatoryDomainCode'
        ]
        for path in paths:
            value = self._get_text(root, path)
            if value:
                return value
        return None

    def _extract_notice_type_code(self, root: ET.Element) -> Optional[str]:
        """Extract notice type code"""
        paths = [
            './/cbc:NoticeTypeCode',
            './/NoticeTypeCode'
        ]
        for path in paths:
            value = self._get_text(root, path)
            if value:
                return value
        return None

    def _extract_notice_language(self, root: ET.Element) -> Optional[str]:
        """Extract notice language code"""
        paths = [
            './/cbc:NoticeLanguageCode',
            './/NoticeLanguageCode'
        ]
        for path in paths:
            value = self._get_text(root, path)
            if value:
                return value
        return None

    def _extract_contract_folder_id(self, root: ET.Element) -> Optional[str]:
        """Extract contract folder ID"""
        return self._get_text(root, './/cbc:ContractFolderID') or self._get_text(root, './/ContractFolderID')

    def _extract_version_id(self, root: ET.Element) -> Optional[str]:
        """Extract version ID"""
        return self._get_text(root, './/cbc:VersionID') or self._get_text(root, './/VersionID')

    def _extract_contracting_party(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract contracting party/authority information (comprehensive)
        Replaces CONTRACTING_BODY from Era 2
        """
        contracting_party = {}

        # Find ContractingParty element
        cp_elem = self._find(root, './/cac:ContractingParty') or self._find(root, './/ContractingParty')
        if not cp_elem:
            return contracting_party

        # Find Party element within ContractingParty
        party_elem = self._find(cp_elem, './/cac:Party') or self._find(cp_elem, './/Party')
        if not party_elem:
            return contracting_party

        # Party name
        party_name_elem = self._find(party_elem, './/cac:PartyName') or self._find(party_elem, './/PartyName')
        if party_name_elem:
            contracting_party['name'] = self._get_text(party_name_elem, './/cbc:Name') or self._get_text(party_name_elem, './/Name')

        # Postal address
        address_elem = self._find(party_elem, './/cac:PostalAddress') or self._find(party_elem, './/PostalAddress')
        if address_elem:
            contracting_party['address'] = {
                'street': self._get_text(address_elem, './/cbc:StreetName'),
                'city': self._get_text(address_elem, './/cbc:CityName'),
                'postal_code': self._get_text(address_elem, './/cbc:PostalZone'),
                'country_subentity': self._get_text(address_elem, './/cbc:CountrySubentity'),
                'country_code': self._get_text(address_elem, './/cac:Country/cbc:IdentificationCode') or \
                               self._get_text(address_elem, './/Country/IdentificationCode'),
                'address_lines': []
            }

            # Additional address lines
            for line_elem in self._findall(address_elem, './/cbc:AddressLine') or self._findall(address_elem, './/AddressLine'):
                line_text = self._get_text(line_elem, '.')
                if line_text:
                    contracting_party['address']['address_lines'].append(line_text)

        # Contact information
        contact_elem = self._find(party_elem, './/cac:Contact') or self._find(party_elem, './/Contact')
        if contact_elem:
            contracting_party['contact'] = {
                'name': self._get_text(contact_elem, './/cbc:Name'),
                'telephone': self._get_text(contact_elem, './/cbc:Telephone'),
                'email': self._get_text(contact_elem, './/cbc:ElectronicMail'),
                'telefax': self._get_text(contact_elem, './/cbc:Telefax')
            }

        # Website
        website_elem = self._find(party_elem, './/cbc:WebsiteURI') or self._find(party_elem, './/WebsiteURI')
        if website_elem:
            contracting_party['website'] = website_elem.text

        # Party identification
        party_id_elem = self._find(party_elem, './/cac:PartyIdentification') or self._find(party_elem, './/PartyIdentification')
        if party_id_elem:
            contracting_party['party_id'] = self._get_text(party_id_elem, './/cbc:ID')

        # Industry classification codes
        industry_codes = []
        for ic_elem in self._findall(party_elem, './/cac:IndustryClassificationCode') or self._findall(party_elem, './/IndustryClassificationCode'):
            code = self._get_text(ic_elem, '.')
            if code:
                industry_codes.append(code)
        if industry_codes:
            contracting_party['industry_codes'] = industry_codes

        return contracting_party

    def _extract_procurement_project(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract procurement project details (comprehensive)
        Replaces OBJECT_CONTRACT from Era 2
        """
        project = {}

        # Find ProcurementProject element
        pp_elem = self._find(root, './/cac:ProcurementProject') or self._find(root, './/ProcurementProject')
        if not pp_elem:
            return project

        # Basic information
        project['name'] = self._get_text(pp_elem, './/cbc:Name') or self._get_text(pp_elem, './/Name')
        project['description'] = self._get_text(pp_elem, './/cbc:Description') or self._get_text(pp_elem, './/Description')
        project['procurement_type_code'] = self._get_text(pp_elem, './/cbc:ProcurementTypeCode')

        # CPV classification (Main commodity classification)
        cpv_elem = self._find(pp_elem, './/cac:MainCommodityClassification') or \
                   self._find(pp_elem, './/MainCommodityClassification')
        if cpv_elem:
            project['cpv_main'] = {
                'code': self._get_text(cpv_elem, './/cbc:ItemClassificationCode'),
                'list_name': cpv_elem.find('.//cbc:ItemClassificationCode', self.namespaces).get('listName') \
                             if cpv_elem.find('.//cbc:ItemClassificationCode', self.namespaces) is not None else None
            }

        # Additional commodity classifications
        additional_cpvs = []
        for ac_elem in self._findall(pp_elem, './/cac:AdditionalCommodityClassification'):
            code = self._get_text(ac_elem, './/cbc:ItemClassificationCode')
            if code:
                additional_cpvs.append(code)
        if additional_cpvs:
            project['cpv_additional'] = additional_cpvs

        # Budget amount / estimated value
        budget_elem = self._find(pp_elem, './/cac:RequestedTenderTotal') or \
                     self._find(pp_elem, './/RequestedTenderTotal')
        if budget_elem:
            project['budget'] = {
                'estimated_amount': self._get_text(budget_elem, './/cbc:EstimatedOverallContractAmount'),
                'currency': budget_elem.find('.//cbc:EstimatedOverallContractAmount', self.namespaces).get('currencyID') \
                           if budget_elem.find('.//cbc:EstimatedOverallContractAmount', self.namespaces) is not None else None,
                'tax_excluded_amount': self._get_text(budget_elem, './/cbc:TaxExcludedAmount'),
                'total_amount': self._get_text(budget_elem, './/cbc:TotalAmount')
            }

        # Realization location
        location_elem = self._find(pp_elem, './/cac:RealizedLocation') or \
                       self._find(pp_elem, './/RealizedLocation')
        if location_elem:
            project['location'] = {
                'address': {},
                'location_codes': []
            }

            addr_elem = self._find(location_elem, './/cac:Address') or self._find(location_elem, './/Address')
            if addr_elem:
                project['location']['address'] = {
                    'city': self._get_text(addr_elem, './/cbc:CityName'),
                    'country_code': self._get_text(addr_elem, './/cac:Country/cbc:IdentificationCode'),
                    'country_subentity': self._get_text(addr_elem, './/cbc:CountrySubentity'),
                    'region': self._get_text(addr_elem, './/cbc:Region')
                }

            # Location codes (NUTS codes)
            for lc_elem in self._findall(location_elem, './/cac:LocationCode') or self._findall(location_elem, './/LocationCode'):
                code = self._get_text(lc_elem, '.')
                if code:
                    project['location']['location_codes'].append(code)

        # Planned period
        period_elem = self._find(pp_elem, './/cac:PlannedPeriod') or self._find(pp_elem, './/PlannedPeriod')
        if period_elem:
            project['planned_period'] = {
                'duration_measure': self._get_text(period_elem, './/cbc:DurationMeasure'),
                'start_date': self._get_text(period_elem, './/cbc:StartDate'),
                'end_date': self._get_text(period_elem, './/cbc:EndDate'),
                'description': self._get_text(period_elem, './/cbc:Description')
            }

        return project

    def _extract_tendering_process(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract tendering process information
        Contains award results and procedure details
        """
        process = {}

        tp_elem = self._find(root, './/cac:TenderingProcess') or self._find(root, './/TenderingProcess')
        if not tp_elem:
            return process

        # Process identification
        process['procedure_code'] = self._get_text(tp_elem, './/cbc:ProcedureCode')
        process['description'] = self._get_text(tp_elem, './/cbc:Description')

        # Submission deadline
        process['tender_submission_deadline'] = self._get_text(tp_elem, './/cbc:SubmissionMethodDetails')

        # Opening date/time
        process['document_availability_period'] = {
            'start_date': self._get_text(tp_elem, './/cac:DocumentAvailabilityPeriod/cbc:StartDate'),
            'end_date': self._get_text(tp_elem, './/cac:DocumentAvailabilityPeriod/cbc:EndDate')
        }

        # Participation
        process['participation'] = {
            'eligible_countries': [],
            'economic_operator_short_list': []
        }

        # Economic operator short list (for restricted procedures)
        for eo_elem in self._findall(tp_elem, './/cac:EconomicOperatorShortList/cac:Party'):
            party_name = self._get_text(eo_elem, './/cac:PartyName/cbc:Name')
            if party_name:
                process['participation']['economic_operator_short_list'].append(party_name)

        return process

    def _extract_tendering_terms(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract tendering terms and conditions
        """
        terms = {}

        tt_elem = self._find(root, './/cac:TenderingTerms') or self._find(root, './/TenderingTerms')
        if not tt_elem:
            return terms

        # Award criteria
        award_criteria = []
        for ac_elem in self._findall(tt_elem, './/cac:AwardingCriterion') or self._findall(tt_elem, './/AwardingCriterion'):
            criterion = {
                'description': self._get_text(ac_elem, './/cbc:Description'),
                'weight': self._get_text(ac_elem, './/cbc:Weight'),
                'calculation_expression': self._get_text(ac_elem, './/cbc:CalculationExpression')
            }
            award_criteria.append(criterion)

        if award_criteria:
            terms['award_criteria'] = award_criteria

        # Required financial guarantee
        terms['required_financial_guarantee'] = self._get_text(tt_elem, './/cbc:RequiredFinancialGuarantee')

        # Funding program
        funding_elem = self._find(tt_elem, './/cac:FundingProgram') or self._find(tt_elem, './/FundingProgram')
        if funding_elem:
            terms['funding_program'] = {
                'name': self._get_text(funding_elem, './/cbc:Name'),
                'code': self._get_text(funding_elem, './/cbc:Code')
            }

        return terms

    def _extract_economic_operators(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract economic operators (contractors/winners)
        Replaces CONTRACTOR from Era 2
        This is CRITICAL for Chinese entity detection
        """
        operators = []

        # Multiple possible locations for economic operators
        search_paths = [
            './/cac:EconomicOperatorParty',
            './/EconomicOperatorParty',
            './/cac:TenderingProcess//cac:EconomicOperatorParty',
            './/cac:AwardedTenderedProject//cac:EconomicOperatorParty',
            './/cac:TenderResult//cac:EconomicOperatorParty'
        ]

        for search_path in search_paths:
            for eo_elem in self._findall(root, search_path):
                operator = self._extract_party_details(eo_elem)
                if operator and operator.get('name'):
                    operators.append(operator)

        # Remove duplicates based on name
        unique_operators = []
        seen_names = set()
        for op in operators:
            name = op.get('name')
            if name and name not in seen_names:
                unique_operators.append(op)
                seen_names.add(name)

        return unique_operators

    def _extract_party_details(self, party_elem: ET.Element) -> Dict[str, Any]:
        """
        Extract comprehensive party/organization details
        Used for both contracting authorities and economic operators
        """
        party = {}

        # Find nested Party element
        p_elem = self._find(party_elem, './/cac:Party') or self._find(party_elem, './/Party') or party_elem

        # Name (critical for Chinese detection)
        party_name_elem = self._find(p_elem, './/cac:PartyName') or self._find(p_elem, './/PartyName')
        if party_name_elem:
            party['name'] = self._get_text(party_name_elem, './/cbc:Name') or self._get_text(party_name_elem, './/Name')

        # Party identification (VAT, registration number, etc.)
        party_ids = []
        for pid_elem in self._findall(p_elem, './/cac:PartyIdentification') or self._findall(p_elem, './/PartyIdentification'):
            id_value = self._get_text(pid_elem, './/cbc:ID')
            if id_value:
                party_ids.append(id_value)
        if party_ids:
            party['party_ids'] = party_ids

        # Address
        address_elem = self._find(p_elem, './/cac:PostalAddress') or self._find(p_elem, './/PostalAddress')
        if address_elem:
            party['address'] = {
                'street': self._get_text(address_elem, './/cbc:StreetName'),
                'city': self._get_text(address_elem, './/cbc:CityName'),
                'postal_code': self._get_text(address_elem, './/cbc:PostalZone'),
                'country_subentity': self._get_text(address_elem, './/cbc:CountrySubentity'),
                'country_code': self._get_text(address_elem, './/cac:Country/cbc:IdentificationCode') or \
                               self._get_text(address_elem, './/Country/IdentificationCode')
            }

        # Contact
        contact_elem = self._find(p_elem, './/cac:Contact') or self._find(p_elem, './/Contact')
        if contact_elem:
            party['contact'] = {
                'name': self._get_text(contact_elem, './/cbc:Name'),
                'telephone': self._get_text(contact_elem, './/cbc:Telephone'),
                'email': self._get_text(contact_elem, './/cbc:ElectronicMail')
            }

        # Website
        website = self._get_text(p_elem, './/cbc:WebsiteURI')
        if website:
            party['website'] = website

        # Legal entity
        legal_elem = self._find(p_elem, './/cac:PartyLegalEntity') or self._find(p_elem, './/PartyLegalEntity')
        if legal_elem:
            party['legal_entity'] = {
                'registration_name': self._get_text(legal_elem, './/cbc:RegistrationName'),
                'company_id': self._get_text(legal_elem, './/cbc:CompanyID')
            }

        return party

    def _extract_award_results(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract award results (for contract award notices)
        Contains winning bids and contractor information
        """
        results = []

        # Find all TenderResult elements
        for tr_elem in self._findall(root, './/cac:TenderResult') or self._findall(root, './/TenderResult'):
            result = {
                'result_code': self._get_text(tr_elem, './/cbc:ResultCode'),
                'description': self._get_text(tr_elem, './/cbc:Description'),
                'award_date': self._get_text(tr_elem, './/cbc:AwardDate'),
                'awarded_lot_id': self._get_text(tr_elem, './/cbc:AwardedLotID'),
                'received_tenders_quantity': self._get_text(tr_elem, './/cbc:ReceivedTenderQuantity'),
            }

            # Contract value
            contract_elem = self._find(tr_elem, './/cac:AwardedTenderedProject')
            if contract_elem:
                budget_elem = self._find(contract_elem, './/cac:LegalMonetaryTotal')
                if budget_elem:
                    result['contract_value'] = {
                        'amount': self._get_text(budget_elem, './/cbc:PayableAmount'),
                        'currency': budget_elem.find('.//cbc:PayableAmount', self.namespaces).get('currencyID') \
                                   if budget_elem.find('.//cbc:PayableAmount', self.namespaces) is not None else None
                    }

            # Winner (economic operator)
            winner_elem = self._find(tr_elem, './/cac:WinningParty') or \
                         self._find(tr_elem, './/cac:EconomicOperatorParty')
            if winner_elem:
                result['winner'] = self._extract_party_details(winner_elem)

            results.append(result)

        return results

    def _extract_lots(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract procurement lots (if procedure is divided into lots)
        """
        lots = []

        # Find all ProcurementProjectLot elements
        for lot_elem in self._findall(root, './/cac:ProcurementProjectLot') or \
                        self._findall(root, './/ProcurementProjectLot'):
            lot = {
                'lot_id': self._get_text(lot_elem, './/cbc:ID'),
                'procurement_project': {}
            }

            # Lot-specific procurement project
            pp_elem = self._find(lot_elem, './/cac:ProcurementProject')
            if pp_elem:
                lot['procurement_project'] = {
                    'name': self._get_text(pp_elem, './/cbc:Name'),
                    'description': self._get_text(pp_elem, './/cbc:Description'),
                    'quantity': self._get_text(pp_elem, './/cbc:Quantity'),
                }

                # Lot-specific CPV
                cpv_elem = self._find(pp_elem, './/cac:MainCommodityClassification')
                if cpv_elem:
                    lot['procurement_project']['cpv_code'] = self._get_text(cpv_elem, './/cbc:ItemClassificationCode')

            # Lot-specific tendering terms
            tt_elem = self._find(lot_elem, './/cac:TenderingTerms')
            if tt_elem:
                lot['tendering_terms'] = {
                    'required_deposit': self._get_text(tt_elem, './/cbc:RequiredDeposit')
                }

            # Lot-specific tendering process
            tp_elem = self._find(lot_elem, './/cac:TenderingProcess')
            if tp_elem:
                lot['tendering_process'] = {
                    'procedure_code': self._get_text(tp_elem, './/cbc:ProcedureCode')
                }

            lots.append(lot)

        return lots

    def _extract_items(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract line items/deliverables
        """
        items = []

        # Find all Item elements
        for item_elem in self._findall(root, './/cac:Item') or self._findall(root, './/Item'):
            item = {
                'description': self._get_text(item_elem, './/cbc:Description'),
                'name': self._get_text(item_elem, './/cbc:Name'),
                'classification_code': self._get_text(item_elem, './/cac:CommodityClassification/cbc:ItemClassificationCode'),
                'quantity': self._get_text(item_elem, './/cbc:Quantity')
            }
            items.append(item)

        return items

    def _extract_additional_information(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract additional information sections
        """
        info = {}

        # AdditionalDocumentReference
        doc_refs = []
        for doc_elem in self._findall(root, './/cac:AdditionalDocumentReference'):
            doc_ref = {
                'id': self._get_text(doc_elem, './/cbc:ID'),
                'document_type_code': self._get_text(doc_elem, './/cbc:DocumentTypeCode'),
                'document_description': self._get_text(doc_elem, './/cbc:DocumentDescription')
            }
            doc_refs.append(doc_ref)

        if doc_refs:
            info['additional_documents'] = doc_refs

        # Signature
        signature_elem = self._find(root, './/cac:Signature')
        if signature_elem:
            info['signature'] = {
                'id': self._get_text(signature_elem, './/cbc:ID'),
                'note': self._get_text(signature_elem, './/cbc:Note')
            }

        return info

    def _extract_extensions(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract UBL extensions (custom/proprietary fields)
        """
        extensions = {}

        # Find UBLExtensions element
        ext_root = self._find(root, './/ext:UBLExtensions') or self._find(root, './/UBLExtensions')
        if not ext_root:
            return extensions

        # eForms-specific extensions
        for ext_elem in self._findall(ext_root, './/ext:UBLExtension') or self._findall(ext_root, './/UBLExtension'):
            ext_name = self._get_text(ext_elem, './/ext:ExtensionName')
            ext_content = self._get_text(ext_elem, './/ext:ExtensionContent')

            if ext_name:
                extensions[ext_name] = ext_content

        return extensions

    def _extract_organizations(self, root) -> dict:
        """
        Extract all organizations from UBLExtensions/Organizations section

        Returns dict mapping org_id → organization details
        This is the master lookup for all entities (CA, contractors, review bodies)
        """
        organizations = {}

        # Path to organizations in extensions
        orgs_path = './/efext:EformsExtension/efac:Organizations/efac:Organization'
        org_elements = self._findall(root, orgs_path)

        if not org_elements:
            # Try without efext prefix
            orgs_path = './/efac:Organizations/efac:Organization'
            org_elements = self._findall(root, orgs_path)

        for org_elem in org_elements:
            company_elem = self._find(org_elem, './/efac:Company')
            if company_elem is None:
                continue

            # Extract party ID
            party_id_elem = self._find(company_elem, './/cac:PartyIdentification/cbc:ID')
            if party_id_elem is None:
                continue

            org_id = self._get_text(party_id_elem, '.')
            if not org_id:
                continue

            # Extract full organization details
            org_data = {
                'org_id': org_id,
                'name': None,
                'country_code': None,
                'city': None,
                'street': None,
                'postal_code': None,
                'nuts_code': None,
                'company_id': None,  # Tax/registration ID
                'email': None,
                'phone': None,
                'website': None,
            }

            # Name
            name_elem = self._find(company_elem, './/cac:PartyName/cbc:Name')
            if name_elem is not None:
                org_data['name'] = self._get_text(name_elem, '.')

            # Address
            addr_elem = self._find(company_elem, './/cac:PostalAddress')
            if addr_elem is not None:
                city_elem = self._find(addr_elem, './/cbc:CityName')
                if city_elem is not None:
                    org_data['city'] = self._get_text(city_elem, '.')

                street_elem = self._find(addr_elem, './/cbc:StreetName')
                if street_elem is not None:
                    org_data['street'] = self._get_text(street_elem, '.')

                postal_elem = self._find(addr_elem, './/cbc:PostalZone')
                if postal_elem is not None:
                    org_data['postal_code'] = self._get_text(postal_elem, '.')

                nuts_elem = self._find(addr_elem, './/cbc:CountrySubentityCode')
                if nuts_elem is not None:
                    org_data['nuts_code'] = self._get_text(nuts_elem, '.')

                country_elem = self._find(addr_elem, './/cac:Country/cbc:IdentificationCode')
                if country_elem is not None:
                    org_data['country_code'] = self._get_text(country_elem, '.')

            # Company/Tax ID
            company_id_elem = self._find(company_elem, './/cac:PartyLegalEntity/cbc:CompanyID')
            if company_id_elem is not None:
                org_data['company_id'] = self._get_text(company_id_elem, '.')

            # Contact info
            contact_elem = self._find(company_elem, './/cac:Contact')
            if contact_elem is not None:
                email_elem = self._find(contact_elem, './/cbc:ElectronicMail')
                if email_elem is not None:
                    org_data['email'] = self._get_text(email_elem, '.')

                phone_elem = self._find(contact_elem, './/cbc:Telephone')
                if phone_elem is not None:
                    org_data['phone'] = self._get_text(phone_elem, '.')

            # Website
            website_elem = self._find(company_elem, './/cbc:WebsiteURI')
            if website_elem is not None:
                org_data['website'] = self._get_text(website_elem, '.')

            organizations[org_id] = org_data

        return organizations

    def _extract_tendering_parties(self, root) -> list:
        """
        Extract tendering parties (winners) from NoticeResult

        Returns list of dicts with party_id, name, and org_id reference
        """
        tendering_parties = []

        # Path to tendering parties in NoticeResult
        parties_path = './/efext:EformsExtension/efac:NoticeResult/efac:TenderingParty'
        party_elements = self._findall(root, parties_path)

        if not party_elements:
            # Try without efext prefix
            parties_path = './/efac:NoticeResult/efac:TenderingParty'
            party_elements = self._findall(root, parties_path)

        for party_elem in party_elements:
            party_data = {}

            # Party ID (TPA-0001, etc.)
            party_id_elem = self._find(party_elem, './/cbc:ID')
            if party_id_elem is not None:
                party_data['party_id'] = self._get_text(party_id_elem, '.')

            # Party name
            name_elem = self._find(party_elem, './/cbc:Name')
            if name_elem is not None:
                party_data['name'] = self._get_text(name_elem, '.')

            # Reference to organization (ORG-0001, etc.)
            tenderer_elem = self._find(party_elem, './/efac:Tenderer/cbc:ID')
            if tenderer_elem is not None:
                party_data['org_id'] = self._get_text(tenderer_elem, '.')

            if party_data:
                tendering_parties.append(party_data)

        return tendering_parties

    def _extract_lot_tenders(self, root) -> dict:
        """
        Extract lot tenders (tender values and references)

        Returns dict mapping tender_id → tender details
        """
        lot_tenders = {}

        # Path to lot tenders
        tenders_path = './/efext:EformsExtension/efac:NoticeResult/efac:LotTender'
        tender_elements = self._findall(root, tenders_path)

        if not tender_elements:
            tenders_path = './/efac:NoticeResult/efac:LotTender'
            tender_elements = self._findall(root, tenders_path)

        for tender_elem in tender_elements:
            tender_data = {}

            # Tender ID (TEN-0001, etc.)
            tender_id_elem = self._find(tender_elem, './/cbc:ID')
            if tender_id_elem is None:
                continue

            tender_id = self._get_text(tender_id_elem, '.')

            # Contract value
            amount_elem = self._find(tender_elem, './/cac:LegalMonetaryTotal/cbc:PayableAmount')
            if amount_elem is not None:
                tender_data['amount'] = self._get_text(amount_elem, '.')
                tender_data['currency'] = amount_elem.get('currencyID')

            # Tendering party reference
            party_ref_elem = self._find(tender_elem, './/efac:TenderingParty/cbc:ID')
            if party_ref_elem is not None:
                tender_data['tendering_party_id'] = self._get_text(party_ref_elem, '.')

            # Lot reference
            lot_ref_elem = self._find(tender_elem, './/efac:TenderLot/cbc:ID')
            if lot_ref_elem is not None:
                tender_data['lot_id'] = self._get_text(lot_ref_elem, '.')

            if tender_data:
                lot_tenders[tender_id] = tender_data

        return lot_tenders

    def _extract_settled_contracts(self, root) -> list:
        """
        Extract settled contracts (award details)

        Returns list of contract award information
        """
        contracts = []

        # Path to settled contracts
        contracts_path = './/efext:EformsExtension/efac:NoticeResult/efac:SettledContract'
        contract_elements = self._findall(root, contracts_path)

        if not contract_elements:
            contracts_path = './/efac:NoticeResult/efac:SettledContract'
            contract_elements = self._findall(root, contracts_path)

        for contract_elem in contract_elements:
            contract_data = {}

            # Contract ID
            contract_id_elem = self._find(contract_elem, './/cbc:ID')
            if contract_id_elem is not None:
                contract_data['contract_id'] = self._get_text(contract_id_elem, '.')

            # Award date
            award_date_elem = self._find(contract_elem, './/cbc:AwardDate')
            if award_date_elem is not None:
                contract_data['award_date'] = self._get_text(award_date_elem, '.')

            # Issue date
            issue_date_elem = self._find(contract_elem, './/cbc:IssueDate')
            if issue_date_elem is not None:
                contract_data['issue_date'] = self._get_text(issue_date_elem, '.')

            # Contract reference
            contract_ref_elem = self._find(contract_elem, './/efac:ContractReference/cbc:ID')
            if contract_ref_elem is not None:
                contract_data['contract_reference'] = self._get_text(contract_ref_elem, '.')

            # Tender reference
            tender_ref_elem = self._find(contract_elem, './/efac:LotTender/cbc:ID')
            if tender_ref_elem is not None:
                contract_data['tender_id'] = self._get_text(tender_ref_elem, '.')

            if contract_data:
                contracts.append(contract_data)

        return contracts

    def _extract_contracting_party_v2(self, root, organizations: dict) -> dict:
        """
        Extract contracting party and resolve from organizations

        Args:
            root: XML root element
            organizations: Dict mapping org_id → org details

        Returns:
            Contracting party details with resolved information
        """
        cp_data = {}

        # Get CA party ID reference from main body
        party_id_elem = self._find(root, './/cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID')
        if party_id_elem is not None:
            party_id = self._get_text(party_id_elem, '.')
            cp_data['party_id'] = party_id

            # Resolve from organizations
            if organizations and party_id in organizations:
                org = organizations[party_id]
                cp_data.update({
                    'name': org.get('name'),
                    'country_code': org.get('country_code'),
                    'city': org.get('city'),
                    'street': org.get('street'),
                    'postal_code': org.get('postal_code'),
                    'nuts_code': org.get('nuts_code'),
                    'company_id': org.get('company_id'),
                    'email': org.get('email'),
                    'phone': org.get('phone'),
                    'website': org.get('website'),
                })

        return cp_data

    def _extract_economic_operators_v2(self, root, organizations: dict, tendering_parties: list,
                                        lot_tenders: dict, settled_contracts: list) -> list:
        """
        Extract economic operators (contractors/winners) by resolving references

        Args:
            root: XML root element
            organizations: Dict mapping org_id → org details
            tendering_parties: List of tendering party references
            lot_tenders: Dict mapping tender_id → tender details
            settled_contracts: List of settled contracts

        Returns:
            List of economic operator/contractor details
        """
        economic_operators = []

        if not organizations or not tendering_parties or not lot_tenders or not settled_contracts:
            return economic_operators

        # Build mapping of tender_id → tender details
        tender_to_party = {}
        for tender_id, tender_data in lot_tenders.items():
            party_id = tender_data.get('tendering_party_id')
            if party_id:
                tender_to_party[tender_id] = {
                    'party_id': party_id,
                    'amount': tender_data.get('amount'),
                    'currency': tender_data.get('currency'),
                    'lot_id': tender_data.get('lot_id'),
                }

        # Build mapping of party_id → org_id
        party_to_org = {}
        for party in tendering_parties:
            party_id = party.get('party_id')
            org_id = party.get('org_id')
            if party_id and org_id:
                party_to_org[party_id] = {
                    'org_id': org_id,
                    'name': party.get('name'),
                }

        # Match settled contracts to economic operators
        for contract in settled_contracts:
            tender_id = contract.get('tender_id')
            if not tender_id or tender_id not in tender_to_party:
                continue

            tender_info = tender_to_party[tender_id]
            party_id = tender_info['party_id']

            if party_id not in party_to_org:
                continue

            party_info = party_to_org[party_id]
            org_id = party_info['org_id']

            if org_id not in organizations:
                continue

            org = organizations[org_id]

            # Build complete economic operator record
            econ_op = {
                'org_id': org_id,
                'name': org.get('name'),
                'country_code': org.get('country_code'),
                'city': org.get('city'),
                'street': org.get('street'),
                'postal_code': org.get('postal_code'),
                'nuts_code': org.get('nuts_code'),
                'company_id': org.get('company_id'),
                'email': org.get('email'),
                'phone': org.get('phone'),
                'website': org.get('website'),
                'role': 'winner',
                'contract_id': contract.get('contract_id'),
                'award_date': contract.get('award_date'),
                'award_value': tender_info.get('amount'),
                'award_currency': tender_info.get('currency'),
                'lot_id': tender_info.get('lot_id'),
            }

            economic_operators.append(econ_op)

        return economic_operators

    def _extract_award_results_v2(self, root, settled_contracts: list, lot_tenders: dict,
                                    tendering_parties: list, organizations: dict) -> list:
        """
        Extract award results with complete information

        Args:
            root: XML root element
            settled_contracts: List of settled contract details
            lot_tenders: Dict of lot tender details
            tendering_parties: List of tendering parties
            organizations: Dict of organizations

        Returns:
            List of award result details
        """
        award_results = []

        if not settled_contracts:
            return award_results

        # Build party_id → org mapping
        party_to_org = {}
        for party in tendering_parties:
            party_id = party.get('party_id')
            org_id = party.get('org_id')
            if party_id and org_id:
                party_to_org[party_id] = org_id

        for contract in settled_contracts:
            tender_id = contract.get('tender_id')
            if not tender_id or tender_id not in lot_tenders:
                # Add contract without tender details
                award_results.append({
                    'contract_id': contract.get('contract_id'),
                    'award_date': contract.get('award_date'),
                    'contract_reference': contract.get('contract_reference'),
                    'winner_name': None,
                    'winner_country': None,
                    'award_value': None,
                    'award_currency': None,
                    'lot_id': None,
                })
                continue

            tender = lot_tenders[tender_id]
            party_id = tender.get('tendering_party_id')

            winner_name = None
            winner_country = None

            if party_id and party_id in party_to_org:
                org_id = party_to_org[party_id]
                if org_id in organizations:
                    org = organizations[org_id]
                    winner_name = org.get('name')
                    winner_country = org.get('country_code')

            award_results.append({
                'contract_id': contract.get('contract_id'),
                'award_date': contract.get('award_date'),
                'contract_reference': contract.get('contract_reference'),
                'winner_name': winner_name,
                'winner_country': winner_country,
                'winner_org_id': party_to_org.get(party_id) if party_id else None,
                'award_value': tender.get('amount'),
                'award_currency': tender.get('currency'),
                'lot_id': tender.get('lot_id'),
            })

        return award_results

    def to_detection_schema(self, notice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert UBL notice data to our detection schema format
        Maps UBL fields to the same structure as Era 1/2 processors
        This enables DataQualityAssessor compatibility
        """
        if not notice_data:
            return {}

        # Map to standard detection schema
        detection_record = {
            # Notice identification
            'notice_number': notice_data.get('notice_id'),
            'notice_date': notice_data.get('issue_date'),
            'notice_type': notice_data.get('notice_type'),
            'format_era': 'ERA_3_UBL_EFORMS',

            # Contracting authority (v2 resolved data - flat structure)
            'ca_name': notice_data.get('contracting_party', {}).get('name'),
            'ca_country': notice_data.get('contracting_party', {}).get('country_code'),
            'ca_city': notice_data.get('contracting_party', {}).get('city'),

            # Procurement project
            'contract_title': notice_data.get('procurement_project', {}).get('name'),
            'contract_description': notice_data.get('procurement_project', {}).get('description'),
            'cpv_code': notice_data.get('procurement_project', {}).get('cpv_main', {}).get('code'),

            # Financial
            'contract_value': notice_data.get('procurement_project', {}).get('budget', {}).get('estimated_amount'),
            'contract_currency': notice_data.get('procurement_project', {}).get('budget', {}).get('currency'),

            # Location
            'contract_location_country': notice_data.get('procurement_project', {}).get('location', {}).get('address', {}).get('country_code'),
            'contract_location_nuts': notice_data.get('procurement_project', {}).get('location', {}).get('location_codes', [None])[0] if notice_data.get('procurement_project', {}).get('location', {}).get('location_codes') else None,

            # Economic operators (contractors) - CRITICAL for Chinese detection
            'contractors': [],

            # Awards (v2 resolved data - flat structure)
            'award_date': notice_data.get('award_results', [{}])[0].get('award_date') if notice_data.get('award_results') else None,
            'award_value': notice_data.get('award_results', [{}])[0].get('award_value') if notice_data.get('award_results') else None,
            'award_currency': notice_data.get('award_results', [{}])[0].get('award_currency') if notice_data.get('award_results') else None,

            # Metadata
            'source_file': notice_data.get('source_file'),
            'extraction_timestamp': notice_data.get('extraction_timestamp'),
            'ubl_version': notice_data.get('ubl_version'),
            'eforms_sdk_version': notice_data.get('eforms_sdk_version'),
        }

        # Extract all contractors/economic operators
        contractors = []

        # From economic_operators list (v2 resolved data - flat structure)
        for eo in notice_data.get('economic_operators', []):
            contractor = {
                'name': eo.get('name'),
                'country': eo.get('country_code'),  # Flat from v2
                'city': eo.get('city'),  # Flat from v2
                'postal_code': eo.get('postal_code'),  # Flat from v2
                'nuts_code': eo.get('nuts_code'),  # Flat from v2
                'company_id': eo.get('company_id'),  # New field from v2
                'email': eo.get('email'),  # Flat from v2
                'phone': eo.get('phone'),  # Flat from v2
                'website': eo.get('website'),
                'award_value': eo.get('award_value'),  # Direct from v2
                'award_currency': eo.get('award_currency'),  # Direct from v2
                'award_date': eo.get('award_date'),  # Direct from v2
                'role': eo.get('role', 'winner'),
                'source': 'economic_operators_v2'
            }
            contractors.append(contractor)

        # From award results (v2 resolved data - flat structure)
        # NOTE: This is likely redundant with economic_operators_v2, but kept for completeness
        for award in notice_data.get('award_results', []):
            winner_name = award.get('winner_name')  # v2 flat field
            if winner_name:
                contractor = {
                    'name': winner_name,
                    'country': award.get('winner_country'),  # v2 flat field
                    'award_value': award.get('award_value'),  # v2 flat field
                    'award_currency': award.get('award_currency'),  # v2 flat field
                    'award_date': award.get('award_date'),
                    'contract_id': award.get('contract_id'),
                    'source': 'award_results_v2'
                }
                contractors.append(contractor)

        # Deduplicate contractors by name
        unique_contractors = []
        seen_names = set()
        for c in contractors:
            name = c.get('name')
            if name and name not in seen_names:
                unique_contractors.append(c)
                seen_names.add(name)

        detection_record['contractors'] = unique_contractors
        detection_record['contractor_count'] = len(unique_contractors)

        return detection_record

    def get_statistics(self) -> Dict[str, Any]:
        """Get parser statistics"""
        return self.statistics


# Example usage and testing
if __name__ == '__main__':
    import json

    parser = UBLEFormsParser()

    # Test with February 2024 sample files
    sample_dir = Path("C:/Projects/OSINT - Foresight/data/temp/ubl_test_sample")
    sample_files = list(sample_dir.glob("**/*.xml"))

    if not sample_files:
        print(f"No sample files found in: {sample_dir}")
        print("Please run extract_feb2024_sample.py first")
        exit(1)

    print("="*80)
    print("UBL EFORMS PARSER TEST")
    print(f"Testing with {len(sample_files)} February 2024 samples")
    print("="*80)

    for sample_file in sample_files:
        print(f"\n{'='*80}")
        print(f"Testing: {sample_file.name}")
        print(f"{'='*80}")

        # Parse notice
        notice_data = parser.parse_notice(sample_file)

        if notice_data:
            print(f"[SUCCESS] Parsed UBL eForms notice")
            print(f"\nCore Information:")
            print(f"  Notice ID: {notice_data.get('notice_id')}")
            print(f"  Notice Type: {notice_data.get('notice_type')}")
            print(f"  Issue Date: {notice_data.get('issue_date')}")
            print(f"  Issue Time: {notice_data.get('issue_time')}")
            print(f"  UBL Version: {notice_data.get('ubl_version')}")
            print(f"  eForms SDK: {notice_data.get('eforms_sdk_version')}")
            print(f"  Language: {notice_data.get('notice_language')}")

            print(f"\nContracting Party (v2 resolved):")
            cp = notice_data.get('contracting_party', {})
            print(f"  Name: {cp.get('name')}")
            print(f"  Country: {cp.get('country_code')}")  # v2 flat structure
            print(f"  City: {cp.get('city')}")  # v2 flat structure
            print(f"  Company ID: {cp.get('company_id')}")

            print(f"\nProcurement Project:")
            pp = notice_data.get('procurement_project', {})
            # Safe unicode printing
            name = pp.get('name', 'None')
            desc = pp.get('description', '')
            try:
                print(f"  Name: {name}")
                print(f"  Description: {desc[:100] if desc else 'None'}...")
            except UnicodeEncodeError:
                print(f"  Name: [Unicode content]")
                print(f"  Description: [Unicode content]...")
            print(f"  CPV Code: {pp.get('cpv_main', {}).get('code')}")
            print(f"  Budget: {pp.get('budget', {}).get('estimated_amount')} {pp.get('budget', {}).get('currency')}")

            print(f"\nEconomic Operators (v2 resolved):")
            eo_list = notice_data.get('economic_operators', [])
            print(f"  Found: {len(eo_list)}")
            for i, eo in enumerate(eo_list[:3], 1):  # Show first 3
                print(f"    {i}. {eo.get('name')} ({eo.get('country_code')}) - {eo.get('city')}")  # v2 flat
                print(f"        Award: {eo.get('award_value')} {eo.get('award_currency')}")  # v2 direct
                print(f"        Company ID: {eo.get('company_id')}")

            print(f"\nAward Results (v2 resolved):")
            awards = notice_data.get('award_results', [])
            print(f"  Found: {len(awards)}")
            for i, award in enumerate(awards[:3], 1):  # Show first 3
                print(f"    {i}. Winner: {award.get('winner_name')} ({award.get('winner_country')})")  # v2 flat
                print(f"       Value: {award.get('award_value')} {award.get('award_currency')}")  # v2 flat
                print(f"       Date: {award.get('award_date')}")
                print(f"       Contract ID: {award.get('contract_id')}")

            # Convert to detection schema
            print(f"\n{'='*40}")
            print("DETECTION SCHEMA CONVERSION")
            print(f"{'='*40}")
            detection_record = parser.to_detection_schema(notice_data)
            print(f"[SUCCESS] Converted to detection schema")
            print(f"\nDetection Fields:")
            print(f"  Notice Number: {detection_record.get('notice_number')}")
            print(f"  Notice Date: {detection_record.get('notice_date')}")
            print(f"  CA Name: {detection_record.get('ca_name')}")
            print(f"  CA Country: {detection_record.get('ca_country')}")
            print(f"  Contract Title: {detection_record.get('contract_title')}")
            print(f"  Contract Value: {detection_record.get('contract_value')} {detection_record.get('contract_currency')}")
            print(f"  Contractors for Detection: {detection_record.get('contractor_count')}")

            if detection_record.get('contractors'):
                print(f"\n  Contractor Details:")
                for i, contractor in enumerate(detection_record['contractors'][:3], 1):
                    print(f"    {i}. {contractor.get('name')}")
                    print(f"       Country: {contractor.get('country')}")
                    print(f"       City: {contractor.get('city')}")
                    print(f"       Source: {contractor.get('source')}")

            # Save sample detection record
            output_file = Path(f"C:/Projects/OSINT - Foresight/analysis/ubl_test_{sample_file.stem}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(detection_record, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVED] Detection record: {output_file}")

        else:
            print("[FAILED] Could not parse notice")

    # Show final statistics
    print(f"\n{'='*80}")
    print("PARSER STATISTICS")
    print(f"{'='*80}")
    stats = parser.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
