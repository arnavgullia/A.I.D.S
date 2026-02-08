"""
Data Validator Tool for Agent 1.
Checks data quality and completeness.
"""

from typing import Dict, Any, List
from langchain_core.tools import tool


# Valid ranges for asteroid properties
VALID_RANGES = {
    "diameter": (0.1, 1000000),          # 10cm to 1000km
    "mass": (1e3, 1e21),                  # 1 ton to Moon-mass
    "velocity": (0.1, 100),               # 0.1 to 100 km/s
    "impact_probability": (0.0, 1.0),     # 0 to 100%
    "days_until_approach": (0, 100000),   # Up to ~273 years
    "semi_major_axis": (0.1, 50),         # 0.1 to 50 AU
    "eccentricity": (0.0, 0.99),          # Near-circular to highly elliptical
    "inclination": (0.0, 180.0),          # 0 to 180 degrees
    "albedo": (0.0, 1.0),                 # 0 to 100% reflective
    "rotation_period": (0.01, 10000),     # seconds to days
}

# Critical fields required for deflection planning
CRITICAL_FIELDS = ["id", "name", "mass", "velocity", "diameter", "impact_probability"]

# Important fields for complete analysis
IMPORTANT_FIELDS = ["composition", "days_until_approach", "semi_major_axis", "eccentricity"]


@tool
def data_validator_tool(asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate asteroid data for quality and completeness.
    
    Use this tool before sending data to Agent 2 or quantum system to ensure
    data quality. Checks for missing values, suspicious ranges, and completeness.
    
    Args:
        asteroid_data: Dictionary containing asteroid properties to validate
    
    Returns:
        Validation report including:
        - is_valid: Whether data passes all critical checks
        - confidence_score: Data quality score (0-100)
        - missing_critical: List of missing critical fields
        - missing_important: List of missing important fields
        - warnings: Any suspicious values detected
        - recommendations: Suggestions for data improvement
    """
    issues = []
    warnings = []
    missing_critical = []
    missing_important = []
    
    # Check for critical fields
    for field in CRITICAL_FIELDS:
        if field not in asteroid_data or asteroid_data[field] is None:
            missing_critical.append(field)
            issues.append(f"Missing critical field: {field}")
    
    # Check for important fields
    for field in IMPORTANT_FIELDS:
        if field not in asteroid_data or asteroid_data[field] is None:
            missing_important.append(field)
    
    # Validate value ranges
    for field, (min_val, max_val) in VALID_RANGES.items():
        if field in asteroid_data and asteroid_data[field] is not None:
            value = asteroid_data[field]
            if not isinstance(value, (int, float)):
                issues.append(f"Invalid type for {field}: expected number, got {type(value).__name__}")
            elif value < min_val or value > max_val:
                warnings.append({
                    "field": field,
                    "value": value,
                    "valid_range": f"{min_val} to {max_val}",
                    "message": f"Value {value} is outside expected range"
                })
    
    # Check for specific logical issues
    if "diameter" in asteroid_data and "mass" in asteroid_data:
        diameter = asteroid_data["diameter"]
        mass = asteroid_data["mass"]
        if diameter and mass:
            # Estimate density - should be 1000-8000 kg/m³ for asteroids
            volume = (4/3) * 3.14159 * ((diameter/2) ** 3)
            density = mass / volume
            if density < 500:
                warnings.append({
                    "field": "mass/diameter ratio",
                    "message": f"Implied density ({density:.0f} kg/m³) seems too low for an asteroid"
                })
            elif density > 10000:
                warnings.append({
                    "field": "mass/diameter ratio",
                    "message": f"Implied density ({density:.0f} kg/m³) seems too high - denser than iron"
                })
    
    # Check observation data quality indicators
    if "observation_arc_days" in asteroid_data:
        arc = asteroid_data["observation_arc_days"]
        if arc and arc < 30:
            warnings.append({
                "field": "observation_arc_days",
                "value": arc,
                "message": "Short observation arc - orbital predictions may be uncertain"
            })
    
    # Calculate confidence score
    confidence = 100.0
    
    # Deduct for missing critical fields (heavy penalty)
    confidence -= len(missing_critical) * 20
    
    # Deduct for missing important fields (lighter penalty)
    confidence -= len(missing_important) * 5
    
    # Deduct for warnings
    confidence -= len(warnings) * 3
    
    # Ensure score is in valid range
    confidence = max(0, min(100, confidence))
    
    # Determine overall validity
    is_valid = len(missing_critical) == 0 and confidence >= 50
    
    # Generate recommendations
    recommendations = []
    if missing_critical:
        recommendations.append(f"Obtain missing critical data: {', '.join(missing_critical)}")
    if missing_important:
        recommendations.append(f"Consider obtaining: {', '.join(missing_important)}")
    if any(w["field"] == "observation_arc_days" for w in warnings):
        recommendations.append("Request additional telescope observations to refine orbit")
    if confidence < 70:
        recommendations.append("Data quality is marginal - consider verification before deflection planning")
    
    return {
        "is_valid": is_valid,
        "confidence_score": round(confidence, 1),
        "status": "PASS" if is_valid else "FAIL",
        "data_completeness": {
            "critical_fields_present": len(CRITICAL_FIELDS) - len(missing_critical),
            "critical_fields_total": len(CRITICAL_FIELDS),
            "missing_critical": missing_critical if missing_critical else None,
            "missing_important": missing_important if missing_important else None
        },
        "warnings": warnings if warnings else None,
        "recommendations": recommendations if recommendations else ["Data quality is sufficient for analysis"],
        "safe_for_agent2": is_valid and confidence >= 60
    }
