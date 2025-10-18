"""
Risk Assessment Helper for OpenAlex Analysis
Provides standardized risk assessment functions
"""

def assess_technology_risk(technologies, tech_config):
    """Assess risk level based on technology categories"""
    if not technologies:
        return "LOW"

    for risk_level in ["CRITICAL", "HIGH", "MEDIUM"]:
        critical_techs = tech_config.get("dual_use_technologies", {}).get(risk_level, [])
        if any(tech in critical_techs for tech in technologies):
            return risk_level

    return "LOW"

def assess_collaboration_risk(patterns):
    """Assess risk based on collaboration patterns"""
    high_risk_patterns = ["technology_transfer", "strategic_partnerships", "funding_influence"]

    if any(pattern in patterns for pattern in high_risk_patterns):
        return "HIGH"
    elif patterns:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_country_risk_score(country_stats):
    """Calculate overall risk score for a country"""
    # Placeholder for sophisticated risk calculation
    collaboration_count = country_stats.get("total_collaborations", 0)

    if collaboration_count > 1000:
        return "HIGH"
    elif collaboration_count > 100:
        return "MEDIUM"
    else:
        return "LOW"

if __name__ == "__main__":
    print("Risk Assessment Helper Ready")
