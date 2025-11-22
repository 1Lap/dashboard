"""
Pytest configuration and shared fixtures for dashboard server tests.
"""

import pytest
from datetime import datetime


@pytest.fixture
def sample_setup_data():
    """Sample car setup data from REST API."""
    return {
        "suspension": {
            "front_spring_rate": 120.5,
            "rear_spring_rate": 115.3,
            "front_damper": 8,
            "rear_damper": 7
        },
        "aerodynamics": {
            "front_wing": 5,
            "rear_wing": 8
        },
        "brakes": {
            "brake_bias": 56.5
        }
    }


@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data from monitor."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "lap": 5,
        "position": 2,
        "fuel": 45.3,
        "fuel_capacity": 80.0,
        "tire_pressures": {
            "fl": 28.5,
            "fr": 28.7,
            "rl": 27.8,
            "rr": 28.0
        },
        "tire_temps": {
            "fl": 85.2,
            "fr": 86.1,
            "rl": 84.5,
            "rr": 85.0
        },
        "brake_temps": {
            "fl": 450.0,
            "fr": 455.0,
            "rl": 420.0,
            "rr": 425.0
        },
        "engine_water_temp": 92.5,
        "track_temp": 28.5,
        "ambient_temp": 22.0
    }
