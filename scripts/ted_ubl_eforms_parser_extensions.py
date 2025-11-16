#!/usr/bin/env python3
"""
UBL eForms Parser - Extensions Section Extraction Methods

These methods extract contractor, award, and organization data from the
UBLExtensions section where eForms stores all entity information.

To integrate into ted_ubl_eforms_parser.py
"""

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

        org_id = self._get_text(party_id_elem)
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
            org_data['name'] = self._get_text(name_elem)

        # Address
        addr_elem = self._find(company_elem, './/cac:PostalAddress')
        if addr_elem is not None:
            city_elem = self._find(addr_elem, './/cbc:CityName')
            if city_elem is not None:
                org_data['city'] = self._get_text(city_elem)

            street_elem = self._find(addr_elem, './/cbc:StreetName')
            if street_elem is not None:
                org_data['street'] = self._get_text(street_elem)

            postal_elem = self._find(addr_elem, './/cbc:PostalZone')
            if postal_elem is not None:
                org_data['postal_code'] = self._get_text(postal_elem)

            nuts_elem = self._find(addr_elem, './/cbc:CountrySubentityCode')
            if nuts_elem is not None:
                org_data['nuts_code'] = self._get_text(nuts_elem)

            country_elem = self._find(addr_elem, './/cac:Country/cbc:IdentificationCode')
            if country_elem is not None:
                org_data['country_code'] = self._get_text(country_elem)

        # Company/Tax ID
        company_id_elem = self._find(company_elem, './/cac:PartyLegalEntity/cbc:CompanyID')
        if company_id_elem is not None:
            org_data['company_id'] = self._get_text(company_id_elem)

        # Contact info
        contact_elem = self._find(company_elem, './/cac:Contact')
        if contact_elem is not None:
            email_elem = self._find(contact_elem, './/cbc:ElectronicMail')
            if email_elem is not None:
                org_data['email'] = self._get_text(email_elem)

            phone_elem = self._find(contact_elem, './/cbc:Telephone')
            if phone_elem is not None:
                org_data['phone'] = self._get_text(phone_elem)

        # Website
        website_elem = self._find(company_elem, './/cbc:WebsiteURI')
        if website_elem is not None:
            org_data['website'] = self._get_text(website_elem)

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
            party_data['party_id'] = self._get_text(party_id_elem)

        # Party name
        name_elem = self._find(party_elem, './/cbc:Name')
        if name_elem is not None:
            party_data['name'] = self._get_text(name_elem)

        # Reference to organization (ORG-0001, etc.)
        tenderer_elem = self._find(party_elem, './/efac:Tenderer/cbc:ID')
        if tenderer_elem is not None:
            party_data['org_id'] = self._get_text(tenderer_elem)

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

        tender_id = self._get_text(tender_id_elem)

        # Contract value
        amount_elem = self._find(tender_elem, './/cac:LegalMonetaryTotal/cbc:PayableAmount')
        if amount_elem is not None:
            tender_data['amount'] = self._get_text(amount_elem)
            tender_data['currency'] = amount_elem.get('currencyID')

        # Tendering party reference
        party_ref_elem = self._find(tender_elem, './/efac:TenderingParty/cbc:ID')
        if party_ref_elem is not None:
            tender_data['tendering_party_id'] = self._get_text(party_ref_elem)

        # Lot reference
        lot_ref_elem = self._find(tender_elem, './/efac:TenderLot/cbc:ID')
        if lot_ref_elem is not None:
            tender_data['lot_id'] = self._get_text(lot_ref_elem)

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
            contract_data['contract_id'] = self._get_text(contract_id_elem)

        # Award date
        award_date_elem = self._find(contract_elem, './/cbc:AwardDate')
        if award_date_elem is not None:
            contract_data['award_date'] = self._get_text(award_date_elem)

        # Issue date
        issue_date_elem = self._find(contract_elem, './/cbc:IssueDate')
        if issue_date_elem is not None:
            contract_data['issue_date'] = self._get_text(issue_date_elem)

        # Contract reference
        contract_ref_elem = self._find(contract_elem, './/efac:ContractReference/cbc:ID')
        if contract_ref_elem is not None:
            contract_data['contract_reference'] = self._get_text(contract_ref_elem)

        # Tender reference
        tender_ref_elem = self._find(contract_elem, './/efac:LotTender/cbc:ID')
        if tender_ref_elem is not None:
            contract_data['tender_id'] = self._get_text(tender_ref_elem)

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
        party_id = self._get_text(party_id_elem)
        cp_data['party_id'] = party_id

        # Resolve from organizations
        if party_id in organizations:
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
