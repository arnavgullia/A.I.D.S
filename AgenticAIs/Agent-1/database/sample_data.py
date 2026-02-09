"""
Sample asteroid data for Project Aegis.
Includes realistic data for testing and demonstration.
"""

import sqlite3
from .models import init_database, get_db_path, drop_database


# Sample asteroids with realistic data
SAMPLE_ASTEROIDS = [
    {
        "id": "APO2026",
        "name": "Apophis-2026",
        "diameter": 340,
        "mass": 6.1e10,  # ~61 billion kg
        "velocity": 30.73,
        "composition": "stony",
        "impact_probability": 0.92,
        "days_until_approach": 180,
        "semi_major_axis": 0.9224,
        "eccentricity": 0.1911,
        "inclination": 3.33,
        "discovery_date": "2004-06-19",
        "last_observation": "2026-01-15",
        "observation_arc_days": 7880,
        "absolute_magnitude": 19.7,
        "albedo": 0.30,
        "rotation_period": 30.4,
        "spectral_type": "Sq",
        "is_potentially_hazardous": 1,
        "notes": "PRIMARY THREAT - Potential Earth impact in 2026. High priority target for deflection."
    },
    {
        "id": "BENNU101",
        "name": "Bennu",
        "diameter": 492,
        "mass": 7.329e10,
        "velocity": 28.0,
        "composition": "carbonaceous",
        "impact_probability": 0.08,
        "days_until_approach": 2920,  # ~8 years
        "semi_major_axis": 1.1264,
        "eccentricity": 0.2037,
        "inclination": 6.03,
        "discovery_date": "1999-09-11",
        "last_observation": "2026-01-20",
        "observation_arc_days": 9627,
        "absolute_magnitude": 20.19,
        "albedo": 0.046,
        "rotation_period": 4.297,
        "spectral_type": "B",
        "is_potentially_hazardous": 1,
        "notes": "Well-studied by OSIRIS-REx mission. Sample returned in 2023. Rubble pile structure."
    },
    {
        "id": "ATLAS2025",
        "name": "Atlas-2025",
        "diameter": 280,
        "mass": 3.2e10,
        "velocity": 25.5,
        "composition": "stony-iron",
        "impact_probability": 0.45,
        "days_until_approach": 120,
        "semi_major_axis": 1.458,
        "eccentricity": 0.412,
        "inclination": 12.7,
        "discovery_date": "2024-03-15",
        "last_observation": "2026-01-28",
        "observation_arc_days": 684,
        "absolute_magnitude": 20.5,
        "albedo": 0.18,
        "rotation_period": 8.2,
        "spectral_type": "S",
        "is_potentially_hazardous": 1,
        "notes": "Recently discovered. Trajectory refinement ongoing. MEDIUM-HIGH threat classification."
    },
    {
        "id": "DIDYMOS",
        "name": "Didymos",
        "diameter": 780,
        "mass": 5.32e11,
        "velocity": 23.8,
        "composition": "stony",
        "impact_probability": 0.001,
        "days_until_approach": 1460,  # ~4 years
        "semi_major_axis": 1.6444,
        "eccentricity": 0.3836,
        "inclination": 3.41,
        "discovery_date": "1996-04-11",
        "last_observation": "2026-01-10",
        "observation_arc_days": 10862,
        "absolute_magnitude": 18.16,
        "albedo": 0.15,
        "rotation_period": 2.26,
        "spectral_type": "Xk",
        "is_potentially_hazardous": 1,
        "notes": "Binary asteroid system. Successfully deflected by NASA DART mission in 2022. Test target."
    },
    {
        "id": "RYUGU",
        "name": "Ryugu",
        "diameter": 900,
        "mass": 4.5e11,
        "velocity": 19.2,
        "composition": "carbonaceous",
        "impact_probability": 0.0001,
        "days_until_approach": 5840,  # ~16 years
        "semi_major_axis": 1.1896,
        "eccentricity": 0.1903,
        "inclination": 5.88,
        "discovery_date": "1999-05-10",
        "last_observation": "2025-12-20",
        "observation_arc_days": 9722,
        "absolute_magnitude": 19.26,
        "albedo": 0.045,
        "rotation_period": 7.63,
        "spectral_type": "Cg",
        "is_potentially_hazardous": 1,
        "notes": "Studied by Hayabusa2 mission. Diamond-shaped rubble pile. Sample returned in 2020."
    },
    {
        "id": "EROS433",
        "name": "Eros",
        "diameter": 16840,  # 16.84 km - quite large!
        "mass": 6.687e15,
        "velocity": 24.36,
        "composition": "stony",
        "impact_probability": 0.0,
        "days_until_approach": 3650,  # ~10 years
        "semi_major_axis": 1.458,
        "eccentricity": 0.2226,
        "inclination": 10.83,
        "discovery_date": "1898-08-13",
        "last_observation": "2026-01-25",
        "observation_arc_days": 46538,
        "absolute_magnitude": 11.16,
        "albedo": 0.25,
        "rotation_period": 5.27,
        "spectral_type": "S",
        "is_potentially_hazardous": 0,
        "notes": "First NEA discovered. Studied by NEAR Shoemaker mission. No current impact risk."
    },
    {
        "id": "TOUTATIS",
        "name": "Toutatis",
        "diameter": 2450,
        "mass": 5.0e13,
        "velocity": 29.45,
        "composition": "stony",
        "impact_probability": 0.0,
        "days_until_approach": 2555,  # ~7 years
        "semi_major_axis": 2.5129,
        "eccentricity": 0.6295,
        "inclination": 0.45,
        "discovery_date": "1989-01-04",
        "last_observation": "2026-01-18",
        "observation_arc_days": 13528,
        "absolute_magnitude": 15.3,
        "albedo": 0.13,
        "rotation_period": 176.0,  # Very slow tumbling rotation
        "spectral_type": "Sk",
        "is_potentially_hazardous": 1,
        "notes": "Tumbling rotation. Imaged by Chang'e 2 flyby. No impact risk in foreseeable future."
    },
    {
        "id": "PHAETHON",
        "name": "Phaethon",
        "diameter": 5100,
        "mass": 1.4e14,
        "velocity": 35.0,  # High velocity!
        "composition": "rocky",
        "impact_probability": 0.0,
        "days_until_approach": 730,  # ~2 years
        "semi_major_axis": 1.2712,
        "eccentricity": 0.8898,  # Very eccentric orbit
        "inclination": 22.26,
        "discovery_date": "1983-10-11",
        "last_observation": "2026-01-22",
        "observation_arc_days": 15443,
        "absolute_magnitude": 14.6,
        "albedo": 0.122,
        "rotation_period": 3.604,
        "spectral_type": "B",
        "is_potentially_hazardous": 1,
        "notes": "Parent body of Geminid meteor shower. Target of DESTINY+ mission. Blue-colored asteroid."
    },
    {
        "id": "HERMES",
        "name": "Hermes",
        "diameter": 400,
        "mass": 2.0e10,
        "velocity": 26.8,
        "composition": "stony",
        "impact_probability": 0.15,
        "days_until_approach": 365,
        "semi_major_axis": 1.6552,
        "eccentricity": 0.6244,
        "inclination": 6.07,
        "discovery_date": "1937-10-28",
        "last_observation": "2026-01-05",
        "observation_arc_days": 32199,
        "absolute_magnitude": 17.5,
        "albedo": 0.15,
        "rotation_period": 13.9,
        "spectral_type": "S",
        "is_potentially_hazardous": 1,
        "notes": "Lost for 66 years after discovery. Binary asteroid. Historically significant NEA."
    },
    {
        "id": "ORPHEUS",
        "name": "Orpheus",
        "diameter": 348,
        "mass": 6.5e10,
        "velocity": 31.2,
        "composition": "iron",
        "impact_probability": 0.68,
        "days_until_approach": 90,
        "semi_major_axis": 1.209,
        "eccentricity": 0.323,
        "inclination": 2.68,
        "discovery_date": "2025-08-20",
        "last_observation": "2026-01-30",
        "observation_arc_days": 163,
        "absolute_magnitude": 19.2,
        "albedo": 0.35,
        "rotation_period": 4.1,
        "spectral_type": "M",
        "is_potentially_hazardous": 1,
        "notes": "URGENT - Iron composition makes deflection more challenging. HIGH threat priority."
    }
]


def populate_database():
    """Populate the database with sample asteroid data."""
    # Initialize fresh database
    drop_database()
    init_database()
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO asteroids (
            id, name, diameter, mass, velocity, composition,
            impact_probability, days_until_approach, semi_major_axis,
            eccentricity, inclination, discovery_date, last_observation,
            observation_arc_days, absolute_magnitude, albedo, rotation_period,
            spectral_type, is_potentially_hazardous, notes
        ) VALUES (
            :id, :name, :diameter, :mass, :velocity, :composition,
            :impact_probability, :days_until_approach, :semi_major_axis,
            :eccentricity, :inclination, :discovery_date, :last_observation,
            :observation_arc_days, :absolute_magnitude, :albedo, :rotation_period,
            :spectral_type, :is_potentially_hazardous, :notes
        )
    """
    
    for asteroid in SAMPLE_ASTEROIDS:
        cursor.execute(insert_query, asteroid)
    
    conn.commit()
    conn.close()
    
    print(f"Populated database with {len(SAMPLE_ASTEROIDS)} asteroids:")
    for a in SAMPLE_ASTEROIDS:
        threat = "HIGH" if a["impact_probability"] > 0.5 else "MEDIUM" if a["impact_probability"] > 0.1 else "LOW"
        print(f"  - {a['name']}: {a['diameter']}m, {threat} threat ({a['impact_probability']*100:.1f}% impact prob)")


if __name__ == "__main__":
    populate_database()
