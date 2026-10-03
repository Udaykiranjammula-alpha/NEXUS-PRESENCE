/**
 * NEXUS-PRESENCE Main Application Bootstrap
 * Author: Uday Kiran Jammula
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("==================================================");
    console.log("   NEXUS-PRESENCE: 3D AMBIENT WI-FI ENGINE        ");
    console.log("          Author: Uday Kiran Jammula              ");
    console.log("==================================================");

    const container = document.getElementById('threejs-container');
    if (!container) return;

    // 1. Initialize 3D Scene
    const sceneApp = new NexusScene(container, {
        width: NEXUS_CONFIG.ROOM.width,
        length: NEXUS_CONFIG.ROOM.length,
        height: NEXUS_CONFIG.ROOM.height,
        nodes: NEXUS_CONFIG.NODES
    });

    // 2. Initialize Telemetry State, UI, and Canvas Charts
    const telemetryStore = new NexusTelemetryStore(NEXUS_CONFIG.CHART_HISTORY_LENGTH);
    const ui = new NexusUI();
    const charts = new NexusCharts('rssi-chart-canvas', 'motion-chart-canvas');

    // Chart update loop (10 Hz)
    setInterval(() => {
        charts.render(telemetryStore);
    }, 100);

    // 3. Connect WebSocket Stream
    let serverActive = false;

    const wsClient = new NexusWebSocketClient(NEXUS_CONFIG.WS_URL, {
        onConnect: () => {
            serverActive = true;
            console.log("[APP] Connected to live backend streaming pipeline.");
        },
        onPacket: (packet) => {
            telemetryStore.ingest(packet);
            ui.update(packet);
            sceneApp.handleTelemetry(packet);
        },
        onDisconnect: () => {
            console.warn("[APP] Disconnected from backend server.");
        }
    });

    // 4. Bind UI Controls
    const btnDemo = document.getElementById('btn-toggle-demo');
    if (btnDemo) {
        btnDemo.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/demo/toggle', { method: 'POST' });
                const json = await res.json();
                console.log("[APP] Simulation toggle:", json);
            } catch (e) {
                // Standalone browser client fallback demo mode
                startClientSideDemo();
            }
        });
    }

    const btnCalibrate = document.getElementById('btn-calibrate');
    if (btnCalibrate) {
        btnCalibrate.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/calibrate', { method: 'POST' });
                const json = await res.json();
                alert("Empty-room baseline calibration executed successfully.");
            } catch (e) {
                alert("Backend server offline. Please start backend/server/main.py.");
            }
        });
    }

    const btnResetCam = document.getElementById('btn-reset-cam');
    if (btnResetCam) {
        btnResetCam.addEventListener('click', () => {
            sceneApp.cameraRig.camera.position.set(13, 10.5, 16);
            sceneApp.cameraRig.camera.lookAt(5, 1.2, 5);
            if (sceneApp.cameraRig.controls) {
                sceneApp.cameraRig.controls.target.set(5, 1.2, 5);
            }
        });
    }

    // 5. Automatic In-Browser Fallback Demo if backend is not yet started
    let localDemoInterval = null;
    let localDemoSimTime = 0;

    function startClientSideDemo() {
        if (localDemoInterval) return;
        console.log("[APP] Starting in-browser client-side demo mode.");
        
        localDemoInterval = setInterval(() => {
            localDemoSimTime += 0.05;
            const t = localDemoSimTime;
            
            // Generate figure-8 trajectory
            const px = 5.0 + 3.2 * Math.sin(t * 0.5);
            const py = 5.0 + 2.8 * Math.sin(t * 1.0);
            const speed = 0.85 + 0.15 * Math.cos(t * 0.8);
            let dir = Math.atan2(Math.cos(t * 1.0) * 2.8, Math.cos(t * 0.5) * 1.6);
            if (dir < 0) dir += 2 * Math.PI;

            const state = speed > 0.4 ? "MOVEMENT" : "LOW ACTIVITY";

            const syntheticPacket = {
                system_status: "ONLINE",
                timestamp: Date.now() / 1000,
                sensing_mode: "RSSI ONLY",
                global_motion_score: Math.min(speed / 1.5, 0.95),
                global_status: state,
                is_simulation: true,
                position_estimate: {
                    x: px,
                    y: py,
                    z: 0.0,
                    velocity: speed,
                    direction: dir,
                    movement: state,
                    confidence: 0.88
                },
                nodes: {
                    1: { node_id: 1, role: "MASTER", online: true, filtered_rssi: -42 + Math.sin(t)*3, deviation: 3.2, variance: 1.4, status: state, sensing_mode: "RSSI_ONLY", total_packets: 120 },
                    2: { node_id: 2, role: "SENSOR_A", online: true, filtered_rssi: -48 + Math.cos(t)*4, deviation: 4.1, variance: 2.1, status: state, sensing_mode: "RSSI_ONLY", total_packets: 120 },
                    3: { node_id: 3, role: "SENSOR_B", online: true, filtered_rssi: -45 + Math.sin(t*0.5)*3, deviation: 2.8, variance: 1.1, status: state, sensing_mode: "RSSI_ONLY", total_packets: 120 },
                    4: { node_id: 4, role: "SENSOR_C", online: true, filtered_rssi: -50 + Math.cos(t*0.7)*5, deviation: 5.0, variance: 2.8, status: state, sensing_mode: "RSSI_ONLY", total_packets: 120 }
                }
            };

            telemetryStore.ingest(syntheticPacket);
            ui.update(syntheticPacket);
            sceneApp.handleTelemetry(syntheticPacket);
        }, 50);
    }

    // Auto-trigger client demo after 2.5s if backend isn't sending frames
    setTimeout(() => {
        if (!serverActive) {
            console.log("[APP] Backend stream idle. Activating initial demonstration simulation.");
            startClientSideDemo();
        }
    }, 2000);
});
