/**
 * NEXUS-PRESENCE Frontend Configuration
 * Author: Uday Kiran Jammula
 */

const NEXUS_CONFIG = {
    // WebSocket endpoint auto-detects current host
    WS_URL: (window.location.protocol === "https:" ? "wss://" : "ws://") + 
            (window.location.host || "localhost:8000") + "/ws/telemetry",

    // Default 3D Room geometry in meters
    ROOM: {
        width: 10.0,
        length: 10.0,
        height: 3.0
    },

    // Default ESP32 Physical Node Anchor Coordinates [x, y, z]
    NODES: {
        1: { id: 1, label: "MASTER #1", position: [0.0, 0.0, 2.0] },
        2: { id: 2, label: "SENSOR #2", position: [10.0, 0.0, 2.0] },
        3: { id: 3, label: "SENSOR #3", position: [0.0, 10.0, 2.0] },
        4: { id: 4, label: "SENSOR #4", position: [10.0, 10.0, 2.0] }
    },

    // Refresh rates and buffer lengths
    CHART_HISTORY_LENGTH: 60,
    HEARTBEAT_INTERVAL_MS: 3000
};

window.NEXUS_CONFIG = NEXUS_CONFIG;
