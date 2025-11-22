// WebSocket connection
let socket;

function initDashboard(sessionId) {
    // Connect to server
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);

        // Join session room
        socket.emit('join_session', {session_id: sessionId});
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });

    // Listen for setup updates
    socket.on('setup_update', (data) => {
        console.log('Setup update received:', data);
        updateSetup(data.setup);
    });

    // Listen for telemetry updates
    socket.on('telemetry_update', (data) => {
        updateTelemetry(data.telemetry);
    });
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (connected) {
        statusEl.textContent = '🟢 Connected';
        statusEl.className = 'status connected';
    } else {
        statusEl.textContent = '🔴 Disconnected';
        statusEl.className = 'status disconnected';
    }
}

function updateTelemetry(data) {
    // Session info
    setText('player-name', data.player_name || '-');
    setText('car-name', data.car_name || '-');
    setText('track-name', data.track_name || '-');
    setText('session-type', data.session_type || '-');
    setText('position', data.position > 0 ? `P${data.position}` : '-');
    setText('lap', data.lap || '-');

    // Fuel
    const fuel = data.fuel || 0;
    const fuelCapacity = data.fuel_capacity || 90;
    const fuelPercent = Math.round((fuel / fuelCapacity) * 100);
    setText('fuel', fuel.toFixed(1));
    setText('fuel-capacity', fuelCapacity.toFixed(1));
    setText('fuel-percent', fuelPercent);
    setWidth('fuel-bar', fuelPercent);

    // Estimate laps remaining (rough: 3L per lap)
    const fuelPerLap = 3.0;
    const lapsRemaining = Math.floor(fuel / fuelPerLap);
    setText('fuel-laps', lapsRemaining);

    // Tires
    updateTireData(data.tire_temps, 'tire-temp', '°C');
    updateTireData(data.tire_pressures, 'tire-psi', ' PSI');
    updateTireData(data.brake_temps, 'brake-temp', '°C');

    // Engine
    setText('engine-temp', data.engine_water_temp ? data.engine_water_temp.toFixed(1) : '-');

    // Weather
    setText('track-temp', data.track_temp ? data.track_temp.toFixed(1) : '-');
    setText('ambient-temp', data.ambient_temp ? data.ambient_temp.toFixed(1) : '-');
}

function updateTireData(tireObj, prefix, suffix) {
    if (!tireObj) return;

    const positions = ['fl', 'fr', 'rl', 'rr'];
    positions.forEach(pos => {
        const value = tireObj[pos];
        const text = value !== undefined ? value.toFixed(1) + suffix : '-';
        setText(`${prefix}-${pos}`, text);
    });
}

function updateSetup(setup) {
    const container = document.getElementById('setup-container');

    if (!setup || Object.keys(setup).length === 0) {
        container.innerHTML = '<p class="hint">No setup data available</p>';
        return;
    }

    // Display setup as nested structure
    container.innerHTML = '<pre>' + JSON.stringify(setup, null, 2) + '</pre>';
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function setWidth(id, percent) {
    const el = document.getElementById(id);
    if (el) el.style.width = percent + '%';
}
