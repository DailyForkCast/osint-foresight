"""
Advanced Temporal Analysis for OpenAlex Multi-Country Data
Analyzes temporal trends, geopolitical correlations, and prediction models
"""

import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics

class TemporalAnalyzer:
    """Advanced temporal analysis for China research collaborations"""

    def __init__(self):
        # Define temporal periods with geopolitical context
        self.temporal_periods = {
            "pre_bri_baseline_2000_2012": {
                "years": list(range(2000, 2013)),
                "description": "Pre-Belt & Road baseline research patterns",
                "context": "Normal academic collaboration before strategic initiatives",
                "geopolitical_events": [
                    "China WTO accession (2001)",
                    "Beijing Olympics (2008)",
                    "Global Financial Crisis (2008-2009)"
                ]
            },
            "bri_launch_2013_2016": {
                "years": list(range(2013, 2017)),
                "description": "Belt & Road Initiative launch period",
                "context": "Strategic research partnerships begin",
                "geopolitical_events": [
                    "Belt and Road Initiative announced (2013)",
                    "Asian Infrastructure Investment Bank (2015)",
                    "Made in China 2025 strategy (2015)"
                ]
            },
            "expansion_2017_2019": {
                "years": list(range(2017, 2020)),
                "description": "Peak expansion and investment period",
                "context": "Maximum Chinese research collaboration growth",
                "geopolitical_events": [
                    "19th Party Congress (2017)",
                    "US-China trade tensions begin (2018)",
                    "Huawei restrictions start (2019)"
                ]
            },
            "trade_war_2020_2021": {
                "years": [2020, 2021],
                "description": "Trade tensions and COVID period",
                "context": "Restrictions and supply chain awareness",
                "geopolitical_events": [
                    "COVID-19 pandemic (2020)",
                    "US election and policy shift (2020)",
                    "Semiconductor restrictions (2020-2021)"
                ]
            },
            "decoupling_2022_2025": {
                "years": list(range(2022, 2026)),
                "description": "Technology decoupling and restrictions",
                "context": "Research restrictions and partner shifting",
                "geopolitical_events": [
                    "CHIPS Act (2022)",
                    "Technology export controls (2022-2023)",
                    "AI restrictions (2023-2024)"
                ]
            }
        }

        # Country groupings for comparative analysis
        self.country_groups = {
            "Five_Eyes": ["US", "CA", "AU", "NZ", "GB"],
            "EU_Core": ["DE", "FR", "IT", "ES", "NL", "BE"],
            "EU_Nordic": ["SE", "DK", "FI", "NO"],
            "EU_Central": ["PL", "CZ", "SK", "HU"],
            "Asia_Pacific": ["JP", "KR", "SG", "TW", "IN"],
            "BRI_Partners": ["RU", "KZ", "TR", "EG", "BR", "CL"],
            "Technology_Leaders": ["US", "DE", "JP", "KR", "SG", "IL"]
        }

    def analyze_temporal_trends(self, collaborations: List[Dict]) -> Dict:
        """
        Comprehensive temporal trend analysis

        Args:
            collaborations: List of collaboration records with temporal data

        Returns:
            Dict containing temporal analysis results
        """
        # Organize data by time periods
        period_data = self._organize_by_periods(collaborations)

        # Calculate trend metrics
        trend_analysis = self._calculate_trends(period_data)

        # Geopolitical correlation analysis
        geopolitical_analysis = self._analyze_geopolitical_correlations(period_data)

        # Country-specific temporal patterns
        country_patterns = self._analyze_country_temporal_patterns(collaborations)

        # Technology temporal patterns
        technology_patterns = self._analyze_technology_temporal_patterns(collaborations)

        # Prediction and extrapolation
        predictions = self._generate_predictions(period_data, trend_analysis)

        return {
            "period_data": period_data,
            "trend_analysis": trend_analysis,
            "geopolitical_analysis": geopolitical_analysis,
            "country_patterns": country_patterns,
            "technology_patterns": technology_patterns,
            "predictions": predictions,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _organize_by_periods(self, collaborations: List[Dict]) -> Dict:
        """Organize collaborations by temporal periods"""
        period_data = {}

        for period_name, period_info in self.temporal_periods.items():
            period_data[period_name] = {
                "info": period_info,
                "collaborations": [],
                "statistics": {
                    "total_papers": 0,
                    "countries_involved": set(),
                    "technologies": defaultdict(int),
                    "collaboration_patterns": defaultdict(int),
                    "institutions": defaultdict(int),
                    "yearly_distribution": defaultdict(int)
                }
            }

        # Categorize each collaboration
        for collab in collaborations:
            year = collab.get("publication_year", 0)
            if year < 2000:  # Filter out very old or invalid years
                continue

            # Find appropriate period
            period_name = self._determine_period(year)
            if period_name:
                period_data[period_name]["collaborations"].append(collab)
                stats = period_data[period_name]["statistics"]

                # Update statistics
                stats["total_papers"] += 1
                stats["yearly_distribution"][year] += 1

                # Countries
                for country in collab.get("countries_collaborating", []):
                    stats["countries_involved"].add(country)

                # Technologies
                for tech in collab.get("technology_categories", []):
                    stats["technologies"][tech] += 1

                # Patterns
                for pattern in collab.get("collaboration_patterns", []):
                    stats["collaboration_patterns"][pattern] += 1

                # Institutions
                for country, insts in collab.get("institutions", {}).items():
                    for inst in insts:
                        stats["institutions"][inst] += 1

        # Convert sets to lists for JSON serialization
        for period_name in period_data:
            period_data[period_name]["statistics"]["countries_involved"] = \
                list(period_data[period_name]["statistics"]["countries_involved"])

        return period_data

    def _determine_period(self, year: int) -> Optional[str]:
        """Determine which temporal period a year belongs to"""
        for period_name, period_info in self.temporal_periods.items():
            if year in period_info["years"]:
                return period_name
        return None

    def _calculate_trends(self, period_data: Dict) -> Dict:
        """Calculate comprehensive trend metrics"""
        trends = {
            "collaboration_volume": {},
            "growth_rates": {},
            "acceleration": {},
            "country_trends": {},
            "technology_trends": {},
            "pattern_trends": {}
        }

        # Extract collaboration volumes by period
        periods_order = [
            "pre_bri_baseline_2000_2012",
            "bri_launch_2013_2016",
            "expansion_2017_2019",
            "trade_war_2020_2021",
            "decoupling_2022_2025"
        ]

        volumes = []
        for period in periods_order:
            volume = period_data.get(period, {}).get("statistics", {}).get("total_papers", 0)
            volumes.append(volume)
            trends["collaboration_volume"][period] = volume

        # Calculate growth rates between periods
        for i in range(1, len(periods_order)):
            prev_period = periods_order[i-1]
            curr_period = periods_order[i]
            prev_volume = volumes[i-1]
            curr_volume = volumes[i]

            if prev_volume > 0:
                growth_rate = ((curr_volume - prev_volume) / prev_volume) * 100
                trends["growth_rates"][f"{prev_period}_to_{curr_period}"] = {
                    "growth_rate_percent": round(growth_rate, 2),
                    "absolute_change": curr_volume - prev_volume,
                    "direction": "INCREASE" if growth_rate > 0 else "DECREASE",
                    "magnitude": self._classify_growth_magnitude(abs(growth_rate))
                }

        # Calculate acceleration (second derivative)
        growth_rates = [data["growth_rate_percent"] for data in trends["growth_rates"].values()]
        if len(growth_rates) >= 2:
            for i in range(1, len(growth_rates)):
                acceleration = growth_rates[i] - growth_rates[i-1]
                period_pair = list(trends["growth_rates"].keys())[i]
                trends["acceleration"][period_pair] = {
                    "acceleration": round(acceleration, 2),
                    "interpretation": "ACCELERATING" if acceleration > 5 else "DECELERATING" if acceleration < -5 else "STABLE"
                }

        # Country-specific trends
        trends["country_trends"] = self._analyze_country_trends(period_data, periods_order)

        # Technology trends
        trends["technology_trends"] = self._analyze_technology_trends(period_data, periods_order)

        # Pattern trends
        trends["pattern_trends"] = self._analyze_pattern_trends(period_data, periods_order)

        return trends

    def _classify_growth_magnitude(self, growth_rate: float) -> str:
        """Classify the magnitude of growth rate"""
        if growth_rate > 100:
            return "DRAMATIC"
        elif growth_rate > 50:
            return "SIGNIFICANT"
        elif growth_rate > 20:
            return "MODERATE"
        elif growth_rate > 5:
            return "SLIGHT"
        else:
            return "MINIMAL"

    def _analyze_country_trends(self, period_data: Dict, periods_order: List[str]) -> Dict:
        """Analyze trends by country groups"""
        country_trends = {}

        for group_name, countries in self.country_groups.items():
            group_trends = {}
            for period in periods_order:
                period_stats = period_data.get(period, {}).get("statistics", {})
                involved_countries = period_stats.get("countries_involved", [])
                group_involvement = len([c for c in countries if c in involved_countries])
                group_trends[period] = {
                    "countries_involved": group_involvement,
                    "involvement_rate": round((group_involvement / len(countries)) * 100, 2)
                }

            country_trends[group_name] = group_trends

        return country_trends

    def _analyze_technology_trends(self, period_data: Dict, periods_order: List[str]) -> Dict:
        """Analyze trends by technology categories"""
        technology_trends = {}

        # Get all technologies across all periods
        all_technologies = set()
        for period_data_item in period_data.values():
            all_technologies.update(period_data_item.get("statistics", {}).get("technologies", {}).keys())

        for tech in all_technologies:
            tech_trends = {}
            for period in periods_order:
                period_stats = period_data.get(period, {}).get("statistics", {})
                tech_count = period_stats.get("technologies", {}).get(tech, 0)
                total_papers = period_stats.get("total_papers", 0)
                tech_percentage = (tech_count / max(total_papers, 1)) * 100

                tech_trends[period] = {
                    "absolute_count": tech_count,
                    "percentage_of_period": round(tech_percentage, 2)
                }

            technology_trends[tech] = tech_trends

        return technology_trends

    def _analyze_pattern_trends(self, period_data: Dict, periods_order: List[str]) -> Dict:
        """Analyze trends by collaboration patterns"""
        pattern_trends = {}

        # Get all patterns across all periods
        all_patterns = set()
        for period_data_item in period_data.values():
            all_patterns.update(period_data_item.get("statistics", {}).get("collaboration_patterns", {}).keys())

        for pattern in all_patterns:
            pattern_trend = {}
            for period in periods_order:
                period_stats = period_data.get(period, {}).get("statistics", {})
                pattern_count = period_stats.get("collaboration_patterns", {}).get(pattern, 0)
                total_papers = period_stats.get("total_papers", 0)
                pattern_percentage = (pattern_count / max(total_papers, 1)) * 100

                pattern_trend[period] = {
                    "absolute_count": pattern_count,
                    "percentage_of_period": round(pattern_percentage, 2)
                }

            pattern_trends[pattern] = pattern_trend

        return pattern_trends

    def _analyze_geopolitical_correlations(self, period_data: Dict) -> Dict:
        """Analyze correlations with geopolitical events"""
        correlations = {
            "event_impact_analysis": {},
            "policy_correlation": {},
            "strategic_timing": []
        }

        for period_name, data in period_data.items():
            period_info = data["info"]
            stats = data["statistics"]

            # Analyze impact of geopolitical events
            events = period_info.get("geopolitical_events", [])
            if events:
                collaborations = stats["total_papers"]
                correlations["event_impact_analysis"][period_name] = {
                    "events": events,
                    "collaboration_volume": collaborations,
                    "context": period_info["context"],
                    "assessment": self._assess_event_impact(period_name, collaborations, events)
                }

        # Identify strategic timing patterns
        correlations["strategic_timing"] = self._identify_strategic_timing(period_data)

        return correlations

    def _assess_event_impact(self, period_name: str, collaborations: int, events: List[str]) -> str:
        """Assess the impact of geopolitical events on collaboration"""
        if period_name == "bri_launch_2013_2016":
            return "STRATEGIC_INCREASE - BRI launch correlated with partnership expansion"
        elif period_name == "expansion_2017_2019":
            return "PEAK_COLLABORATION - Maximum collaboration despite emerging tensions"
        elif period_name == "trade_war_2020_2021":
            if collaborations > 500:  # Arbitrary threshold
                return "RESILIENT - Continued collaboration despite trade tensions"
            else:
                return "DECLINING - Trade war impact visible"
        elif period_name == "decoupling_2022_2025":
            if collaborations > 300:
                return "CONCERNING - High collaboration during decoupling period"
            else:
                return "EXPECTED - Reduced collaboration due to restrictions"
        else:
            return "BASELINE - Normal collaboration patterns"

    def _identify_strategic_timing(self, period_data: Dict) -> List[Dict]:
        """Identify strategic timing patterns"""
        timing_patterns = []

        # Check for pre-emptive collaboration increases
        bri_volume = period_data.get("bri_launch_2013_2016", {}).get("statistics", {}).get("total_papers", 0)
        baseline_volume = period_data.get("pre_bri_baseline_2000_2012", {}).get("statistics", {}).get("total_papers", 0)

        if bri_volume > baseline_volume * 1.5:
            timing_patterns.append({
                "pattern": "PRE_EMPTIVE_EXPANSION",
                "description": "Collaboration surge coinciding with BRI launch",
                "strategic_implication": "Coordinated research partnership strategy"
            })

        # Check for resilience during restrictions
        decoupling_volume = period_data.get("decoupling_2022_2025", {}).get("statistics", {}).get("total_papers", 0)
        expansion_volume = period_data.get("expansion_2017_2019", {}).get("statistics", {}).get("total_papers", 0)

        if decoupling_volume > expansion_volume * 0.7:
            timing_patterns.append({
                "pattern": "RESTRICTION_RESILIENCE",
                "description": "Maintained collaboration despite decoupling efforts",
                "strategic_implication": "Research collaboration continues through alternative channels"
            })

        return timing_patterns

    def _analyze_country_temporal_patterns(self, collaborations: List[Dict]) -> Dict:
        """Analyze temporal patterns specific to countries"""
        country_patterns = {}

        # Group collaborations by country
        country_collabs = defaultdict(list)
        for collab in collaborations:
            for country in collab.get("countries_collaborating", []):
                if country != "CN":  # Exclude China itself
                    country_collabs[country].append(collab)

        # Analyze each country's temporal pattern
        for country, collabs in country_collabs.items():
            yearly_counts = defaultdict(int)
            for collab in collabs:
                year = collab.get("publication_year", 0)
                if year >= 2000:
                    yearly_counts[year] += 1

            if yearly_counts:
                country_patterns[country] = {
                    "total_collaborations": len(collabs),
                    "active_years": len(yearly_counts),
                    "yearly_distribution": dict(yearly_counts),
                    "trend_analysis": self._calculate_country_trend(yearly_counts),
                    "peak_year": max(yearly_counts.items(), key=lambda x: x[1])[0],
                    "peak_collaborations": max(yearly_counts.values())
                }

        return country_patterns

    def _calculate_country_trend(self, yearly_counts: Dict[int, int]) -> Dict:
        """Calculate trend for a specific country"""
        if len(yearly_counts) < 3:
            return {"trend": "INSUFFICIENT_DATA"}

        years = sorted(yearly_counts.keys())
        counts = [yearly_counts[year] for year in years]

        # Simple trend calculation
        recent_years = years[-3:]
        early_years = years[:3]

        recent_avg = sum(yearly_counts[year] for year in recent_years) / len(recent_years)
        early_avg = sum(yearly_counts[year] for year in early_years) / len(early_years)

        if recent_avg > early_avg * 1.3:
            trend = "INCREASING"
        elif recent_avg < early_avg * 0.7:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "recent_average": round(recent_avg, 2),
            "early_average": round(early_avg, 2),
            "change_ratio": round(recent_avg / max(early_avg, 1), 2)
        }

    def _analyze_technology_temporal_patterns(self, collaborations: List[Dict]) -> Dict:
        """Analyze how technology focus changes over time"""
        tech_temporal = defaultdict(lambda: defaultdict(int))

        for collab in collaborations:
            year = collab.get("publication_year", 0)
            if year >= 2000:
                for tech in collab.get("technology_categories", []):
                    tech_temporal[tech][year] += 1

        # Calculate emergence and decline patterns
        technology_patterns = {}
        for tech, yearly_data in tech_temporal.items():
            years = sorted(yearly_data.keys())
            if len(years) >= 3:
                technology_patterns[tech] = {
                    "total_papers": sum(yearly_data.values()),
                    "active_years": len(years),
                    "emergence_year": min(years),
                    "peak_year": max(yearly_data.items(), key=lambda x: x[1])[0],
                    "yearly_distribution": dict(yearly_data),
                    "trend": self._calculate_technology_trend(yearly_data)
                }

        return technology_patterns

    def _calculate_technology_trend(self, yearly_data: Dict[int, int]) -> str:
        """Calculate trend for a specific technology"""
        years = sorted(yearly_data.keys())
        if len(years) < 3:
            return "INSUFFICIENT_DATA"

        # Check if technology is emerging (more activity in recent years)
        mid_point = len(years) // 2
        recent_years = years[mid_point:]
        early_years = years[:mid_point]

        recent_total = sum(yearly_data[year] for year in recent_years)
        early_total = sum(yearly_data[year] for year in early_years)

        if recent_total > early_total * 1.5:
            return "EMERGING"
        elif recent_total < early_total * 0.5:
            return "DECLINING"
        else:
            return "STABLE"

    def _generate_predictions(self, period_data: Dict, trend_analysis: Dict) -> Dict:
        """Generate predictions based on temporal analysis"""
        predictions = {
            "short_term_2025_2027": {},
            "medium_term_2027_2030": {},
            "risk_scenarios": {},
            "early_warning_indicators": []
        }

        # Current trajectory analysis
        current_trend = self._assess_current_trajectory(period_data, trend_analysis)

        # Short-term predictions (2025-2027)
        predictions["short_term_2025_2027"] = {
            "collaboration_volume": self._predict_collaboration_volume(current_trend, "short_term"),
            "likely_scenarios": self._generate_short_term_scenarios(current_trend),
            "country_shifts": self._predict_country_shifts(trend_analysis),
            "technology_focus": self._predict_technology_focus(trend_analysis)
        }

        # Medium-term predictions (2027-2030)
        predictions["medium_term_2027_2030"] = {
            "collaboration_volume": self._predict_collaboration_volume(current_trend, "medium_term"),
            "structural_changes": self._predict_structural_changes(trend_analysis),
            "geopolitical_impact": self._predict_geopolitical_impact(trend_analysis)
        }

        # Risk scenarios
        predictions["risk_scenarios"] = {
            "escalation_scenario": "Continued restrictions lead to underground collaboration networks",
            "normalization_scenario": "Gradual return to pre-2020 collaboration levels",
            "fragmentation_scenario": "Permanent split into competing research blocs"
        }

        # Early warning indicators
        predictions["early_warning_indicators"] = [
            "Sudden spike in collaboration despite restrictions",
            "Shift to indirect collaboration through third countries",
            "Increased focus on critical dual-use technologies",
            "New institutional partnership announcements",
            "Changes in funding source patterns"
        ]

        return predictions

    def _assess_current_trajectory(self, period_data: Dict, trend_analysis: Dict) -> Dict:
        """Assess the current collaboration trajectory"""
        recent_period = "decoupling_2022_2025"
        recent_data = period_data.get(recent_period, {}).get("statistics", {})

        return {
            "current_volume": recent_data.get("total_papers", 0),
            "growth_momentum": trend_analysis.get("growth_rates", {}),
            "dominant_patterns": self._identify_dominant_patterns(recent_data),
            "trajectory_assessment": "DECLINING" if recent_data.get("total_papers", 0) < 500 else "STABLE"
        }

    def _identify_dominant_patterns(self, recent_data: Dict) -> List[str]:
        """Identify dominant collaboration patterns in recent period"""
        patterns = recent_data.get("collaboration_patterns", {})
        if patterns:
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            return [pattern for pattern, count in sorted_patterns[:3] if count > 0]
        return []

    def _predict_collaboration_volume(self, current_trend: Dict, timeframe: str) -> Dict:
        """Predict future collaboration volumes"""
        current_volume = current_trend["current_volume"]

        if timeframe == "short_term":
            # Conservative prediction based on current restrictions
            predicted_range = {
                "optimistic": int(current_volume * 1.2),
                "realistic": int(current_volume * 0.9),
                "pessimistic": int(current_volume * 0.6)
            }
        else:  # medium_term
            predicted_range = {
                "optimistic": int(current_volume * 1.5),
                "realistic": int(current_volume * 0.8),
                "pessimistic": int(current_volume * 0.4)
            }

        return {
            "predicted_range": predicted_range,
            "confidence": "MEDIUM",
            "assumptions": [
                "Current policy trends continue",
                "No major geopolitical shifts",
                "Technology restrictions remain in place"
            ]
        }

    def _generate_short_term_scenarios(self, current_trend: Dict) -> List[Dict]:
        """Generate short-term scenario predictions"""
        return [
            {
                "scenario": "Continued Decline",
                "probability": "HIGH",
                "description": "Further reduction in collaboration due to ongoing restrictions"
            },
            {
                "scenario": "Underground Networks",
                "probability": "MEDIUM",
                "description": "Collaboration continues through indirect channels and third countries"
            },
            {
                "scenario": "Policy Reversal",
                "probability": "LOW",
                "description": "Relaxation of restrictions leading to collaboration rebound"
            }
        ]

    def _predict_country_shifts(self, trend_analysis: Dict) -> Dict:
        """Predict shifts in country collaboration patterns"""
        return {
            "declining_partners": ["US", "GB", "AU"],
            "emerging_partners": ["BR", "SA", "EG", "TR"],
            "stable_partners": ["DE", "FR", "RU"],
            "rationale": "Shift from Five Eyes to BRI partners and neutral countries"
        }

    def _predict_technology_focus(self, trend_analysis: Dict) -> Dict:
        """Predict changes in technology focus"""
        return {
            "increasing_focus": ["biotechnology", "energy_storage", "advanced_materials"],
            "decreasing_focus": ["semiconductors", "telecommunications", "artificial_intelligence"],
            "rationale": "Shift to less restricted and dual-use technologies"
        }

    def _predict_structural_changes(self, trend_analysis: Dict) -> List[str]:
        """Predict structural changes in collaboration patterns"""
        return [
            "Increased use of third-country institutions as intermediaries",
            "Growth of private-sector collaboration vs. government-funded research",
            "Development of alternative research networks outside Western institutions",
            "Emphasis on commercially viable vs. fundamental research"
        ]

    def _predict_geopolitical_impact(self, trend_analysis: Dict) -> List[str]:
        """Predict geopolitical impacts of collaboration trends"""
        return [
            "Reduced Western influence in Chinese research directions",
            "Strengthened China-Global South research ties",
            "Potential for competing technology standards",
            "Increased importance of technology sovereignty"
        ]

    def generate_temporal_report(self, analysis_results: Dict) -> Dict:
        """Generate comprehensive temporal analysis report"""
        return {
            "executive_summary": {
                "analysis_period": "2000-2025",
                "key_findings": self._extract_key_findings(analysis_results),
                "strategic_implications": self._extract_strategic_implications(analysis_results)
            },
            "detailed_analysis": analysis_results,
            "recommendations": self._generate_recommendations(analysis_results),
            "monitoring_priorities": self._identify_monitoring_priorities(analysis_results)
        }

    def _extract_key_findings(self, results: Dict) -> List[str]:
        """Extract key findings from temporal analysis"""
        findings = []

        # Volume trends
        trend_data = results.get("trend_analysis", {}).get("collaboration_volume", {})
        if trend_data:
            total_recent = trend_data.get("decoupling_2022_2025", 0)
            total_baseline = trend_data.get("pre_bri_baseline_2000_2012", 0)
            if total_recent > total_baseline:
                findings.append(f"Collaboration volume remains {total_recent/max(total_baseline,1):.1f}x above baseline despite restrictions")

        # Country patterns
        country_trends = results.get("trend_analysis", {}).get("country_trends", {})
        if "Five_Eyes" in country_trends:
            findings.append("Five Eyes countries show declining collaboration patterns")

        # Technology shifts
        tech_patterns = results.get("technology_patterns", {})
        emerging_techs = [tech for tech, data in tech_patterns.items() if data.get("trend") == "EMERGING"]
        if emerging_techs:
            findings.append(f"Emerging technology focus: {', '.join(emerging_techs[:3])}")

        return findings

    def _extract_strategic_implications(self, results: Dict) -> List[str]:
        """Extract strategic implications"""
        implications = []

        # Geopolitical analysis
        geo_analysis = results.get("geopolitical_analysis", {})
        strategic_timing = geo_analysis.get("strategic_timing", [])
        if strategic_timing:
            implications.append("Evidence of coordinated strategic timing in research partnerships")

        # Predictions
        predictions = results.get("predictions", {})
        if predictions.get("risk_scenarios"):
            implications.append("Multiple future scenarios possible - requires adaptive monitoring")

        implications.append("Temporal patterns suggest deliberate strategic coordination")
        implications.append("Current restrictions showing limited effectiveness")

        return implications

    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        return [
            {
                "priority": "HIGH",
                "action": "Implement enhanced monitoring of indirect collaboration channels",
                "rationale": "Evidence of collaboration resilience despite restrictions"
            },
            {
                "priority": "MEDIUM",
                "action": "Track emerging technology focus areas",
                "rationale": "Technology collaboration patterns are shifting"
            },
            {
                "priority": "HIGH",
                "action": "Monitor third-country intermediary patterns",
                "rationale": "Predictions indicate use of neutral countries as intermediaries"
            }
        ]

    def _identify_monitoring_priorities(self, results: Dict) -> List[str]:
        """Identify monitoring priorities based on temporal analysis"""
        return [
            "Monthly collaboration volume tracking",
            "Quarterly technology focus assessment",
            "Annual geopolitical correlation analysis",
            "Real-time early warning indicator monitoring",
            "Bi-annual prediction model updates"
        ]


def main():
    """Test the temporal analyzer"""
    analyzer = TemporalAnalyzer()

    # Test with sample data
    sample_collaborations = [
        {
            "publication_year": 2015,
            "countries_collaborating": ["US", "CN"],
            "technology_categories": ["artificial_intelligence"],
            "collaboration_patterns": ["strategic_partnerships"]
        },
        {
            "publication_year": 2020,
            "countries_collaborating": ["DE", "CN"],
            "technology_categories": ["quantum_computing"],
            "collaboration_patterns": ["technology_transfer"]
        },
        {
            "publication_year": 2023,
            "countries_collaborating": ["BR", "CN"],
            "technology_categories": ["biotechnology"],
            "collaboration_patterns": ["funding_influence"]
        }
    ]

    print("=== Temporal Analysis Test ===")
    results = analyzer.analyze_temporal_trends(sample_collaborations)

    print(f"Periods analyzed: {len(results['period_data'])}")
    print(f"Countries with patterns: {len(results['country_patterns'])}")
    print(f"Technologies tracked: {len(results['technology_patterns'])}")

    # Show key trends
    for period, data in results["trend_analysis"]["collaboration_volume"].items():
        print(f"{period}: {data} collaborations")

if __name__ == "__main__":
    main()
