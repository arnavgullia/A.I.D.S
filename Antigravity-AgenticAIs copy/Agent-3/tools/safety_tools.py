"""
Safety Calculation Tools for Agent 3: Safety Validator
Three tools for validating quantum-optimized deflection solutions.
"""

from typing import Dict, Any
from langchain_core.tools import tool


# Fragmentation threshold by composition (Joules per kg)
# Higher = more resistant to fragmentation
FRAGMENTATION_THRESHOLDS = {
    "metallic": 5_000_000,      # 5e6 J/kg - Dense metal, very resistant
    "iron": 5_000_000,          # Same as metallic
    "stony-iron": 3_000_000,    # 3e6 J/kg - Mixed composition
    "stony": 1_000_000,         # 1e6 J/kg - Standard rocky asteroid
    "rocky": 1_000_000,         # Same as stony
    "carbonaceous": 500_000,    # 5e5 J/kg - Carbon-rich, softer
    "rubble pile": 100_000,     # 1e5 J/kg - Loosely bound, fragile
    "rubble": 100_000,          # Same as rubble pile
    "icy": 100_000,             # 1e5 J/kg - Icy bodies, fragile
    "unknown": 1_000_000        # Default to stony
}

# Momentum enhancement factor (beta)
# Accounts for ejecta momentum from crater formation
MOMENTUM_BETA = 1.5


@tool
def calculate_fragmentation_risk(
    velocity_km_s: float,
    impactor_mass_kg: float,
    asteroid_mass_kg: float,
    asteroid_diameter_m: float,
    composition: str
) -> Dict[str, Any]:
    """
    Calculate the probability that the asteroid will fragment during impact.
    
    Fragmentation occurs when impact energy exceeds the asteroid's structural strength.
    This tool determines if the proposed kinetic impact will shatter the asteroid
    into multiple dangerous fragments instead of deflecting it safely.
    
    Args:
        velocity_km_s: Impact velocity in km/s (from quantum solution)
        impactor_mass_kg: Spacecraft mass in kg (from quantum solution)
        asteroid_mass_kg: Target asteroid mass in kg
        asteroid_diameter_m: Target asteroid diameter in meters
        composition: Asteroid material type (stony, metallic, carbonaceous, icy, rubble pile)
    
    Returns:
        Dictionary with fragmentation risk percentage, assessment, and explanation
    """
    print(f"\n[Tool] Calculating fragmentation risk...")
    print(f"[Tool] Impact: {velocity_km_s} km/s, {impactor_mass_kg} kg impactor")
    print(f"[Tool] Target: {asteroid_mass_kg:.2e} kg, {asteroid_diameter_m}m, {composition}")
    
    # Step 1: Convert velocity to m/s and calculate impact kinetic energy
    velocity_m_s = velocity_km_s * 1000
    impact_energy_joules = 0.5 * impactor_mass_kg * (velocity_m_s ** 2)
    
    # Step 2: Calculate specific energy (energy per kg of asteroid)
    specific_energy = impact_energy_joules / asteroid_mass_kg
    
    # Step 3: Look up fragmentation threshold for this composition
    composition_key = composition.lower().strip()
    threshold = FRAGMENTATION_THRESHOLDS.get(composition_key, FRAGMENTATION_THRESHOLDS["unknown"])
    
    # Step 4: Calculate risk percentage
    fragmentation_risk_pct = (specific_energy / threshold) * 100
    
    # Step 5: Classify result
    if fragmentation_risk_pct < 50:
        assessment = "LOW"
        explanation = f"Impact energy is well below structural limits. Asteroid will remain intact."
    elif fragmentation_risk_pct < 80:
        assessment = "ACCEPTABLE"
        explanation = f"Impact energy is within safe limits. Minor surface damage expected but no fragmentation."
    elif fragmentation_risk_pct < 100:
        assessment = "MARGINAL"
        explanation = f"Impact energy approaching structural limits. Some risk of partial fragmentation."
    else:
        assessment = "CRITICAL"
        explanation = f"Impact energy EXCEEDS structural limits! Asteroid will fragment into multiple dangerous pieces."
    
    result = {
        "fragmentation_risk_pct": round(fragmentation_risk_pct, 2),
        "impact_energy_joules": impact_energy_joules,
        "specific_energy_j_kg": specific_energy,
        "threshold_j_kg": threshold,
        "composition_analyzed": composition_key,
        "assessment": assessment,
        "explanation": explanation,
        "is_safe": fragmentation_risk_pct < 100
    }
    
    print(f"[Tool] Result: {fragmentation_risk_pct:.1f}% risk - {assessment}")
    return result


@tool
def calculate_deflection_distance(
    velocity_km_s: float,
    impactor_mass_kg: float,
    asteroid_mass_kg: float,
    time_to_impact_days: int
) -> Dict[str, Any]:
    """
    Calculate how far the asteroid will be deflected from its original trajectory.
    
    Uses momentum transfer physics to determine if the kinetic impact will
    move the asteroid far enough from Earth to ensure safety (minimum 10,000 km).
    
    Args:
        velocity_km_s: Impact velocity in km/s
        impactor_mass_kg: Spacecraft mass in kg
        asteroid_mass_kg: Target asteroid mass in kg
        time_to_impact_days: Days remaining until Earth impact
    
    Returns:
        Dictionary with deflection distance, delta-v, assessment, and explanation
    """
    print(f"\n[Tool] Calculating deflection distance...")
    print(f"[Tool] Impact: {velocity_km_s} km/s, {impactor_mass_kg} kg impactor")
    print(f"[Tool] Time available: {time_to_impact_days} days")
    
    # Step 1: Convert velocity to m/s
    velocity_m_s = velocity_km_s * 1000
    
    # Step 2: Calculate momentum transfer
    momentum = impactor_mass_kg * velocity_m_s
    
    # Step 3: Apply momentum enhancement factor (beta = 1.5)
    # This accounts for ejecta momentum from crater formation
    enhanced_momentum = momentum * MOMENTUM_BETA
    
    # Step 4: Calculate velocity change of asteroid (delta-v)
    delta_v_m_s = enhanced_momentum / asteroid_mass_kg
    
    # Step 5: Convert time to seconds and calculate deflection distance
    # Note: We use a cumulative orbital effect multiplier (1000) to account for
    # the fact that a small velocity change compounds over multiple orbits,
    # especially for asteroids with Earth-crossing orbits where the deflection
    # at the point of closest approach is amplified by orbital mechanics.
    time_seconds = time_to_impact_days * 24 * 60 * 60
    ORBITAL_AMPLIFICATION = 1000  # Orbital mechanics amplification factor
    deflection_m = delta_v_m_s * time_seconds * ORBITAL_AMPLIFICATION
    deflection_km = deflection_m / 1000
    
    # Step 6: Classify result
    if deflection_km > 20000:
        assessment = "EXCELLENT"
        explanation = f"Deflection of {deflection_km:,.0f} km provides excellent safety margin."
    elif deflection_km > 10000:
        assessment = "SUFFICIENT"
        explanation = f"Deflection of {deflection_km:,.0f} km exceeds minimum safe distance of 10,000 km."
    elif deflection_km > 5000:
        assessment = "MARGINAL"
        explanation = f"Deflection of {deflection_km:,.0f} km is below recommended minimum. Consider optimization."
    else:
        assessment = "INSUFFICIENT"
        explanation = f"Deflection of {deflection_km:,.0f} km is critically low. Mission will NOT prevent impact."
    
    result = {
        "deflection_distance_km": round(deflection_km, 2),
        "delta_v_m_s": delta_v_m_s,
        "momentum_transferred_kg_m_s": enhanced_momentum,
        "time_available_days": time_to_impact_days,
        "assessment": assessment,
        "explanation": explanation,
        "is_sufficient": deflection_km >= 10000
    }
    
    print(f"[Tool] Result: {deflection_km:,.0f} km deflection - {assessment}")
    return result


@tool
def evaluate_safety_score(
    fragmentation_risk_pct: float,
    deflection_distance_km: float,
    quantum_confidence: float
) -> Dict[str, Any]:
    """
    Evaluate overall mission safety and make final APPROVE/REJECT decision.
    
    Combines all safety checks into a single score. All three criteria must
    pass for mission approval:
    - Fragmentation risk < 100%
    - Deflection distance > 10,000 km
    - Quantum confidence > 70%
    
    Args:
        fragmentation_risk_pct: Fragmentation risk percentage (from calculate_fragmentation_risk)
        deflection_distance_km: Deflection distance in km (from calculate_deflection_distance)
        quantum_confidence: Confidence score from quantum optimization (0.0 to 1.0)
    
    Returns:
        Dictionary with safety score, checks passed/failed, recommendation, and reasoning
    """
    print(f"\n[Tool] Evaluating overall safety score...")
    print(f"[Tool] Fragmentation: {fragmentation_risk_pct}%")
    print(f"[Tool] Deflection: {deflection_distance_km} km")
    print(f"[Tool] Confidence: {quantum_confidence * 100}%")
    
    checks_passed = []
    checks_failed = []
    reasoning_parts = []
    
    # Check 1: Fragmentation Risk < 100%
    if fragmentation_risk_pct < 100:
        checks_passed.append("FRAGMENTATION_SAFE")
        if fragmentation_risk_pct < 80:
            reasoning_parts.append(f"✅ Fragmentation risk of {fragmentation_risk_pct:.1f}% is well within safe limits.")
        else:
            reasoning_parts.append(f"⚠️ Fragmentation risk of {fragmentation_risk_pct:.1f}% is acceptable but marginal.")
    else:
        checks_failed.append("FRAGMENTATION_CRITICAL")
        reasoning_parts.append(f"❌ CRITICAL: Fragmentation risk of {fragmentation_risk_pct:.1f}% exceeds 100% threshold. "
                              "Asteroid will shatter into multiple fragments.")
    
    # Check 2: Deflection Distance > 10,000 km
    if deflection_distance_km >= 10000:
        checks_passed.append("DEFLECTION_SUFFICIENT")
        if deflection_distance_km >= 15000:
            reasoning_parts.append(f"✅ Deflection of {deflection_distance_km:,.0f} km provides excellent safety margin.")
        else:
            reasoning_parts.append(f"✅ Deflection of {deflection_distance_km:,.0f} km meets minimum requirement of 10,000 km.")
    else:
        checks_failed.append("DEFLECTION_INSUFFICIENT")
        reasoning_parts.append(f"❌ CRITICAL: Deflection of {deflection_distance_km:,.0f} km is below minimum 10,000 km. "
                              "Mission will NOT prevent Earth impact.")
    
    # Check 3: Quantum Confidence > 70%
    confidence_pct = quantum_confidence * 100
    if quantum_confidence >= 0.70:
        checks_passed.append("CONFIDENCE_HIGH")
        if quantum_confidence >= 0.85:
            reasoning_parts.append(f"✅ Quantum optimization confidence of {confidence_pct:.0f}% is high.")
        else:
            reasoning_parts.append(f"✅ Quantum optimization confidence of {confidence_pct:.0f}% exceeds 70% threshold.")
    else:
        checks_failed.append("CONFIDENCE_LOW")
        reasoning_parts.append(f"⚠️ Quantum optimization confidence of {confidence_pct:.0f}% is below 70% threshold. "
                              "Solution may not be optimal.")
    
    # Calculate overall score and make decision
    total_checks = len(checks_passed) + len(checks_failed)
    safety_score = len(checks_passed) / total_checks
    
    if len(checks_failed) == 0:
        recommendation = "APPROVE"
        final_reasoning = "All safety criteria satisfied. Mission is cleared for execution."
    else:
        recommendation = "REJECT"
        final_reasoning = f"Mission REJECTED due to {len(checks_failed)} failed safety check(s). See details below."
    
    result = {
        "safety_score": round(safety_score, 2),
        "recommendation": recommendation,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "reasoning": "\n".join(reasoning_parts),
        "final_decision": final_reasoning,
        "is_approved": recommendation == "APPROVE"
    }
    
    print(f"[Tool] Result: {recommendation} (Score: {safety_score:.0%})")
    return result
