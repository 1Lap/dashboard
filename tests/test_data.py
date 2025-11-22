"""
Test data generators for dashboard server tests.

This module provides factory functions to generate realistic test data
for telemetry, setup, and other racing-related data structures.

Usage:
    from tests.test_data import generate_telemetry, generate_setup

    # Generate with defaults
    telemetry = generate_telemetry()

    # Generate with custom values
    telemetry = generate_telemetry(lap=10, fuel=25.5)

    # Generate with overrides
    setup = generate_setup(suspension={'front_spring_rate': 130.0})

Features:
    - Realistic default values based on endurance racing data
    - Customizable via keyword arguments
    - Support for partial overrides (deep merge)
    - Timestamps automatically generated
    - Type-safe data structures

Notes:
    - All generators return dict (not classes/objects)
    - Timestamps use ISO 8601 format (UTC)
    - Tire data uses standard abbreviations (fl, fr, rl, rr)
    - Temperature values in Celsius
    - Pressure values in PSI
    - Fuel values in liters
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional


def generate_telemetry(
    lap: int = 1,
    position: int = 1,
    fuel: float = 50.0,
    fuel_capacity: float = 80.0,
    player_name: str = "Test Driver",
    car_name: str = "Test Car",
    track_name: str = "Test Track",
    session_type: str = "race",
    **overrides: Any
) -> Dict[str, Any]:
    """
    Generate sample telemetry data matching monitor output structure.

    Args:
        lap: Current lap number (default: 1)
        position: Current race position (default: 1)
        fuel: Current fuel in liters (default: 50.0)
        fuel_capacity: Tank capacity in liters (default: 80.0)
        player_name: Driver name (default: "Test Driver")
        car_name: Car/vehicle name (default: "Test Car")
        track_name: Track/circuit name (default: "Test Track")
        session_type: Session type (e.g., "practice", "qualifying", "race")
        **overrides: Any additional fields to override

    Returns:
        dict: Complete telemetry data structure

    Example:
        >>> telem = generate_telemetry(lap=5, fuel=30.5)
        >>> assert telem['lap'] == 5
        >>> assert telem['fuel'] == 30.5

        >>> # Full override
        >>> telem = generate_telemetry(
        ...     lap=10,
        ...     tire_pressures={'fl': 30.0, 'fr': 30.0, 'rl': 29.0, 'rr': 29.0}
        ... )

    Notes:
        - Timestamp is auto-generated (UTC)
        - Tire temps/pressures use realistic values
        - All temps in Celsius, pressures in PSI
    """
    data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'lap': lap,
        'position': position,
        'lap_time': 123.456,  # Lap time in seconds
        'fuel': fuel,
        'fuel_capacity': fuel_capacity,
        'tire_pressures': {
            'fl': 28.5,  # Front-left
            'fr': 28.7,  # Front-right
            'rl': 27.8,  # Rear-left
            'rr': 28.0   # Rear-right
        },
        'tire_temps': {
            'fl': 85.2,  # Celsius
            'fr': 86.1,
            'rl': 84.5,
            'rr': 85.0
        },
        'brake_temps': {
            'fl': 450.0,  # Celsius
            'fr': 455.0,
            'rl': 420.0,
            'rr': 425.0
        },
        'engine_water_temp': 92.5,  # Celsius
        'engine_oil_temp': 105.0,   # Celsius
        'track_temp': 28.5,  # Celsius
        'ambient_temp': 22.0,  # Celsius
        'player_name': player_name,
        'car_name': car_name,
        'track_name': track_name,
        'session_type': session_type,
        'speed': 180.5,  # km/h
        'rpm': 7500,
        'gear': 4,
    }

    # Apply any overrides
    data.update(overrides)
    return data


def generate_setup(
    suspension: Optional[Dict[str, Any]] = None,
    aerodynamics: Optional[Dict[str, Any]] = None,
    brakes: Optional[Dict[str, Any]] = None,
    **overrides: Any
) -> Dict[str, Any]:
    """
    Generate sample car setup data matching LMU REST API structure.

    Args:
        suspension: Override suspension settings (partial or full)
        aerodynamics: Override aero settings (partial or full)
        brakes: Override brake settings (partial or full)
        **overrides: Any additional top-level fields

    Returns:
        dict: Complete setup data structure

    Example:
        >>> # Default setup
        >>> setup = generate_setup()

        >>> # Override specific suspension values
        >>> setup = generate_setup(
        ...     suspension={'front_spring_rate': 130.0}
        ... )
        >>> assert setup['suspension']['front_spring_rate'] == 130.0
        >>> # Other suspension values use defaults

        >>> # Add custom section
        >>> setup = generate_setup(tires={'compound': 'soft'})

    Notes:
        - Partial overrides are merged with defaults
        - Values are realistic for GT3/LMP2 cars
        - Spring rates in N/mm, dampers in clicks
    """
    # Default setup values
    default_suspension = {
        'front_spring_rate': 120.5,  # N/mm
        'rear_spring_rate': 115.3,   # N/mm
        'front_damper': 8,  # Clicks
        'rear_damper': 7,   # Clicks
        'front_anti_roll_bar': 6,
        'rear_anti_roll_bar': 5,
        'front_ride_height': 45.0,  # mm
        'rear_ride_height': 55.0    # mm
    }

    default_aerodynamics = {
        'front_wing': 5,  # Clicks/settings
        'rear_wing': 8,
        'front_splitter': 3,
        'rear_diffuser': 4
    }

    default_brakes = {
        'brake_bias': 56.5,  # % front
        'brake_pressure': 85.0,  # %
        'front_brake_duct': 2,  # Clicks
        'rear_brake_duct': 2
    }

    # Merge provided overrides with defaults
    if suspension:
        default_suspension.update(suspension)
    if aerodynamics:
        default_aerodynamics.update(aerodynamics)
    if brakes:
        default_brakes.update(brakes)

    # Build complete setup
    data = {
        'suspension': default_suspension,
        'aerodynamics': default_aerodynamics,
        'brakes': default_brakes
    }

    # Apply any top-level overrides
    data.update(overrides)
    return data


def generate_session_data(
    session_id: Optional[str] = None,
    with_setup: bool = True,
    with_telemetry: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate complete session data structure.

    Args:
        session_id: Session UUID (auto-generated if None)
        with_setup: Include setup data (default: True)
        with_telemetry: Include telemetry data (default: True)
        **kwargs: Pass-through to telemetry/setup generators

    Returns:
        dict: Complete session data structure

    Example:
        >>> session = generate_session_data()
        >>> assert 'session_id' in session
        >>> assert 'setup' in session
        >>> assert 'telemetry' in session

        >>> # Session with only telemetry
        >>> session = generate_session_data(
        ...     with_setup=False,
        ...     lap=10,
        ...     fuel=25.0
        ... )

    Notes:
        - Mimics SessionManager.get_session() return structure
        - Useful for integration testing
    """
    import uuid

    if session_id is None:
        session_id = str(uuid.uuid4())

    data = {
        'session_id': session_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_update': datetime.now(timezone.utc).isoformat(),
    }

    if with_setup:
        data['setup'] = generate_setup()
        data['setup_timestamp'] = datetime.now(timezone.utc).isoformat()

    if with_telemetry:
        data['telemetry'] = generate_telemetry(**kwargs)

    return data


def generate_websocket_message(
    event: str,
    session_id: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate WebSocket message payload for testing.

    Args:
        event: Event name (e.g., 'telemetry_update', 'setup_data')
        session_id: Session UUID
        data: Event-specific data payload

    Returns:
        dict: WebSocket message structure

    Example:
        >>> msg = generate_websocket_message(
        ...     'telemetry_update',
        ...     'abc-123',
        ...     {'telemetry': generate_telemetry()}
        ... )

        >>> msg = generate_websocket_message(
        ...     'setup_data',
        ...     'abc-123',
        ...     {
        ...         'setup': generate_setup(),
        ...         'timestamp': datetime.now(timezone.utc).isoformat()
        ...     }
        ... )

    Notes:
        - Matches expected WebSocket event structure
        - Useful for testing event handlers
    """
    message = {
        'event': event,
        'session_id': session_id,
    }

    if data:
        message.update(data)

    return message


def generate_fuel_series(
    start_fuel: float = 80.0,
    fuel_per_lap: float = 2.5,
    num_laps: int = 10,
    capacity: float = 80.0
) -> list:
    """
    Generate a series of telemetry data showing fuel consumption.

    Args:
        start_fuel: Starting fuel in liters (default: 80.0)
        fuel_per_lap: Fuel consumed per lap (default: 2.5)
        num_laps: Number of laps to generate (default: 10)
        capacity: Fuel tank capacity (default: 80.0)

    Returns:
        list: List of telemetry dicts showing fuel progression

    Example:
        >>> fuel_data = generate_fuel_series(
        ...     start_fuel=80.0,
        ...     fuel_per_lap=2.5,
        ...     num_laps=5
        ... )
        >>> assert len(fuel_data) == 5
        >>> assert fuel_data[0]['fuel'] == 80.0
        >>> assert fuel_data[4]['fuel'] == 70.0

    Notes:
        - Useful for testing fuel calculations
        - Each lap decreases fuel linearly
        - Returns complete telemetry (not just fuel values)
    """
    series = []
    current_fuel = start_fuel

    for lap_num in range(1, num_laps + 1):
        telemetry = generate_telemetry(
            lap=lap_num,
            fuel=max(0.0, current_fuel),
            fuel_capacity=capacity
        )
        series.append(telemetry)
        current_fuel -= fuel_per_lap

    return series


def generate_multi_session(num_sessions: int = 3) -> list:
    """
    Generate multiple session data structures.

    Args:
        num_sessions: Number of sessions to generate (default: 3)

    Returns:
        list: List of complete session data dicts

    Example:
        >>> sessions = generate_multi_session(5)
        >>> assert len(sessions) == 5
        >>> # Each has unique session_id
        >>> session_ids = [s['session_id'] for s in sessions]
        >>> assert len(set(session_ids)) == 5

    Notes:
        - Each session has unique UUID
        - Useful for testing concurrent sessions
        - All sessions have full setup + telemetry
    """
    import uuid

    sessions = []
    for _ in range(num_sessions):
        session_id = str(uuid.uuid4())
        sessions.append(generate_session_data(session_id=session_id))

    return sessions
