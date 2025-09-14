"""
Temporal validator for OSINT Foresight recommendations.
Ensures all recommendations are future-oriented and realistic.
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Tuple, Optional, Any
import re
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TimeHorizon(Enum):
    """Standard time horizons for recommendations."""
    IMMEDIATE = "immediate"  # Can start now, results in 8-12 months
    SHORT_TERM = "short_term"  # 12-24 months
    MEDIUM_TERM = "medium_term"  # 2-4 years
    LONG_TERM = "long_term"  # 5+ years


class ImplementationType(Enum):
    """Types of implementation with typical timelines."""
    POLICY_CHANGE = "policy_change"  # 3-6 months
    LEGISLATIVE = "legislative"  # 12-18 months
    PROCUREMENT = "procurement"  # 9-15 months
    CAPABILITY_DEVELOPMENT = "capability_development"  # 18-24 months
    ORGANIZATIONAL = "organizational"  # 6-12 months
    TECHNOLOGICAL = "technological"  # 12-36 months


@dataclass
class TemporalContext:
    """Current temporal context for analysis."""
    current_date: date
    fiscal_year: str
    quarter: str
    days_remaining_in_year: int
    next_budget_cycle: str
    earliest_implementation: date
    earliest_results: date

    @classmethod
    def from_date(cls, analysis_date: Optional[date] = None) -> 'TemporalContext':
        """Create temporal context from a given date."""
        if analysis_date is None:
            analysis_date = date.today()

        # Calculate quarter
        quarter = f"Q{(analysis_date.month - 1) // 3 + 1} {analysis_date.year}"

        # Calculate days remaining in year
        year_end = date(analysis_date.year, 12, 31)
        days_remaining = (year_end - analysis_date).days

        # Determine fiscal year (varies by country, using Oct-Sep for US)
        if analysis_date.month >= 10:
            fiscal_year = f"FY{analysis_date.year + 1}"
            next_budget = f"FY{analysis_date.year + 2}"
        else:
            fiscal_year = f"FY{analysis_date.year}"
            next_budget = f"FY{analysis_date.year + 1}"

        # Calculate realistic implementation dates
        earliest_implementation = analysis_date + timedelta(days=30)  # 1 month minimum
        earliest_results = analysis_date + relativedelta(months=8)  # 8 months minimum

        return cls(
            current_date=analysis_date,
            fiscal_year=fiscal_year,
            quarter=quarter,
            days_remaining_in_year=days_remaining,
            next_budget_cycle=next_budget,
            earliest_implementation=earliest_implementation,
            earliest_results=earliest_results
        )


class TemporalValidator:
    """Validates temporal aspects of recommendations and analysis."""

    def __init__(self, current_date: Optional[date] = None):
        """Initialize with current or specified date."""
        self.context = TemporalContext.from_date(current_date)
        self.errors = []
        self.warnings = []

        # Define minimum delays for different types
        self.minimum_delays = {
            ImplementationType.POLICY_CHANGE: 90,  # days
            ImplementationType.LEGISLATIVE: 365,
            ImplementationType.PROCUREMENT: 270,
            ImplementationType.CAPABILITY_DEVELOPMENT: 540,
            ImplementationType.ORGANIZATIONAL: 180,
            ImplementationType.TECHNOLOGICAL: 365
        }

    def validate_recommendation(self, recommendation: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single recommendation for temporal realism."""
        errors = []

        # Extract dates from recommendation
        target_date = self._extract_date(recommendation.get('target_date'))
        implementation_start = self._extract_date(recommendation.get('start_date'))
        expected_completion = self._extract_date(recommendation.get('completion_date'))

        # Check if any dates are in the past
        if target_date and target_date < self.context.current_date:
            errors.append(
                f"Target date {target_date} is in the past (current date: {self.context.current_date})"
            )

        if implementation_start and implementation_start < self.context.current_date:
            errors.append(
                f"Implementation start {implementation_start} is in the past"
            )

        # Check if timeline is realistic
        impl_type = recommendation.get('type', ImplementationType.ORGANIZATIONAL)
        if isinstance(impl_type, str):
            try:
                impl_type = ImplementationType(impl_type)
            except ValueError:
                impl_type = ImplementationType.ORGANIZATIONAL

        min_delay = self.minimum_delays.get(impl_type, 180)

        if implementation_start and expected_completion:
            duration = (expected_completion - implementation_start).days
            if duration < min_delay:
                errors.append(
                    f"{impl_type.value} requires minimum {min_delay} days, "
                    f"but only {duration} days allocated"
                )

        # Check for unrealistic "immediate" claims
        if recommendation.get('priority') == 'immediate':
            if expected_completion:
                min_completion = self.context.current_date + timedelta(days=240)
                if expected_completion < min_completion:
                    errors.append(
                        f"'Immediate' actions cannot complete before {min_completion} "
                        f"(8 months minimum), but targets {expected_completion}"
                    )

        return len(errors) == 0, errors

    def _extract_date(self, date_input: Any) -> Optional[date]:
        """Extract date from various input formats."""
        if date_input is None:
            return None

        if isinstance(date_input, date):
            return date_input

        if isinstance(date_input, datetime):
            return date_input.date()

        if isinstance(date_input, str):
            # Try to parse various date formats
            patterns = [
                (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
                (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
                (r'Q(\d) (\d{4})', None),  # Quarter format
                (r'(\d{4})', '%Y'),  # Year only
            ]

            for pattern, fmt in patterns:
                match = re.match(pattern, date_input)
                if match:
                    if fmt:
                        try:
                            return datetime.strptime(date_input, fmt).date()
                        except ValueError:
                            pass
                    elif 'Q' in date_input:
                        # Handle quarter format
                        quarter, year = match.groups()
                        month = (int(quarter) - 1) * 3 + 1
                        return date(int(year), month, 1)
                    else:
                        # Year only - assume end of year
                        return date(int(match.group(1)), 12, 31)

        return None

    def check_document_dates(self, text: str) -> Dict[str, Any]:
        """Check a document for temporal issues."""
        issues = {
            'past_dates': [],
            'unrealistic_timelines': [],
            'warnings': []
        }

        # Find year references
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, text)

        current_year = self.context.current_date.year

        for year_str in years:
            year = int(year_str)
            if year < current_year:
                # Check if it's used in a forward-looking context
                context = self._get_context(text, year_str)
                if any(word in context.lower() for word in ['will', 'should', 'must', 'target', 'achieve']):
                    issues['past_dates'].append({
                        'year': year,
                        'context': context,
                        'error': f"Cannot set targets for {year} (current year: {current_year})"
                    })

        # Check for unrealistic immediate timelines
        immediate_patterns = [
            r'immediate(?:ly)?\s+(?:achieve|implement|deploy)',
            r'by\s+(?:end\s+of\s+)?(?:this\s+)?(?:month|quarter)',
            r'within\s+(?:weeks|days)',
        ]

        for pattern in immediate_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.group())
                issues['unrealistic_timelines'].append({
                    'text': match.group(),
                    'context': context,
                    'warning': "Unrealistic timeline - minimum 8-12 months for results"
                })

        # Check for outdated fiscal year references
        fy_pattern = r'FY\s?(20\d{2})'
        fy_matches = re.findall(fy_pattern, text)

        for fy_year in fy_matches:
            if int(fy_year) <= current_year:
                context = self._get_context(text, f"FY{fy_year}")
                if any(word in context.lower() for word in ['increase', 'budget', 'allocate', 'fund']):
                    issues['warnings'].append({
                        'fiscal_year': f"FY{fy_year}",
                        'context': context,
                        'warning': f"FY{fy_year} budget likely already committed (current: {self.context.fiscal_year})"
                    })

        return issues

    def _get_context(self, text: str, term: str, window: int = 50) -> str:
        """Get context around a term in text."""
        idx = text.find(term)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(term) + window)
        return text[start:end].strip()

    def suggest_timeline(self, implementation_type: ImplementationType,
                        start_date: Optional[date] = None) -> Dict[str, date]:
        """Suggest realistic timeline for an implementation type."""
        if start_date is None:
            start_date = self.context.earliest_implementation

        min_days = self.minimum_delays[implementation_type]

        timeline = {
            'earliest_start': start_date,
            'planning_complete': start_date + timedelta(days=30),
            'implementation_begin': start_date + timedelta(days=60),
            'milestone_1': start_date + timedelta(days=min_days // 3),
            'milestone_2': start_date + timedelta(days=2 * min_days // 3),
            'expected_completion': start_date + timedelta(days=min_days),
            'full_results': start_date + timedelta(days=int(min_days * 1.5))
        }

        return timeline

    def adjust_recommendation_timeline(self, original: str) -> str:
        """Adjust a recommendation's timeline to be realistic."""
        adjusted = original

        # Replace past years with future ones
        current_year = self.context.current_date.year
        for year in range(2020, current_year):
            if str(year) in adjusted:
                # Calculate appropriate future year
                if 'immediate' in adjusted.lower():
                    new_year = current_year + 1
                elif 'short' in adjusted.lower():
                    new_year = current_year + 2
                else:
                    new_year = current_year + 3

                adjusted = adjusted.replace(str(year), str(new_year))

        # Adjust percentage targets with realistic timelines
        percent_pattern = r'(\d+)%\s+by\s+(20\d{2})'
        matches = re.finditer(percent_pattern, adjusted)

        for match in matches:
            target_percent = int(match.group(1))
            target_year = int(match.group(2))

            if target_year <= current_year:
                # Calculate realistic year based on percentage
                if target_percent <= 25:
                    new_year = current_year + 1
                elif target_percent <= 50:
                    new_year = current_year + 2
                elif target_percent <= 75:
                    new_year = current_year + 3
                else:
                    new_year = current_year + 4

                old_text = match.group(0)
                new_text = f"{target_percent}% by {new_year}"
                adjusted = adjusted.replace(old_text, new_text)

        return adjusted

    def generate_timeline_header(self, horizon: TimeHorizon) -> str:
        """Generate appropriate timeline header based on current date."""
        headers = {
            TimeHorizon.IMMEDIATE: f"Foundation Phase ({self.context.quarter} - Q2 {self.context.current_date.year + 1})",
            TimeHorizon.SHORT_TERM: f"Implementation Phase ({self.context.current_date.year + 1}-{self.context.current_date.year + 2})",
            TimeHorizon.MEDIUM_TERM: f"Development Phase ({self.context.current_date.year + 2}-{self.context.current_date.year + 4})",
            TimeHorizon.LONG_TERM: f"Transformation Phase ({self.context.current_date.year + 5}+)"
        }

        return headers.get(horizon, "Future Phase")

    def validate_brief(self, brief_text: str) -> Dict[str, Any]:
        """Validate an executive brief for temporal issues."""
        issues = self.check_document_dates(brief_text)

        # Additional brief-specific checks
        if 'immediate' in brief_text.lower():
            count = brief_text.lower().count('immediate')
            if count > 3:
                issues['warnings'].append({
                    'issue': 'Overuse of "immediate"',
                    'count': count,
                    'suggestion': 'Reserve "immediate" for truly urgent actions that can start now'
                })

        # Check for budget cycle awareness
        if 'budget' in brief_text.lower() or 'funding' in brief_text.lower():
            if self.context.fiscal_year not in brief_text and self.context.next_budget_cycle not in brief_text:
                issues['warnings'].append({
                    'issue': 'Missing budget cycle context',
                    'suggestion': f'Reference {self.context.next_budget_cycle} for new funding'
                })

        return issues


def validate_timeline_in_text(text: str, current_date: Optional[date] = None) -> str:
    """Validate and correct timelines in text."""
    validator = TemporalValidator(current_date)
    issues = validator.check_document_dates(text)

    report = []

    if issues['past_dates']:
        report.append("⚠️ PAST DATE ISSUES FOUND:")
        for issue in issues['past_dates']:
            report.append(f"  - {issue['error']}")
            report.append(f"    Context: ...{issue['context']}...")

    if issues['unrealistic_timelines']:
        report.append("\n⚠️ UNREALISTIC TIMELINES:")
        for issue in issues['unrealistic_timelines']:
            report.append(f"  - {issue['warning']}")
            report.append(f"    Found: '{issue['text']}'")

    if issues['warnings']:
        report.append("\n⚠️ WARNINGS:")
        for warning in issues['warnings']:
            report.append(f"  - {warning['warning']}")

    if not any(issues.values()):
        report.append("✅ No temporal issues found")

    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Set current date for testing
    current = date(2025, 9, 13)
    validator = TemporalValidator(current)

    print(f"Current Context:")
    print(f"  Date: {validator.context.current_date}")
    print(f"  Quarter: {validator.context.quarter}")
    print(f"  Fiscal Year: {validator.context.fiscal_year}")
    print(f"  Next Budget: {validator.context.next_budget_cycle}")
    print(f"  Earliest Implementation: {validator.context.earliest_implementation}")
    print(f"  Earliest Results: {validator.context.earliest_results}")
    print()

    # Test problematic text
    problematic_text = """
    Immediate (2024-2025):
    1. Secure bipartisan defense spending consensus
       - Target: 1.55% GDP by 2025
       - Focus on capability gaps vs across-board increases
       - Leverage Mediterranean instability for political support

    2. Accelerate STANAG implementation
       - Priority: UAV systems, cyber standards
       - Target: 65% compliance by 2025
       - Industry incentives for rapid adoption
    """

    print("Checking problematic text:")
    print(validate_timeline_in_text(problematic_text, current))
    print()

    # Show corrected version
    corrected = validator.adjust_recommendation_timeline(problematic_text)
    print("Suggested corrections:")
    print(corrected)
    print()

    # Generate proper timeline headers
    print("Proper timeline headers for current date:")
    for horizon in TimeHorizon:
        header = validator.generate_timeline_header(horizon)
        print(f"  {horizon.value}: {header}")

    # Suggest timeline for procurement
    print("\nSuggested procurement timeline:")
    timeline = validator.suggest_timeline(ImplementationType.PROCUREMENT)
    for phase, date_val in timeline.items():
        print(f"  {phase}: {date_val}")
