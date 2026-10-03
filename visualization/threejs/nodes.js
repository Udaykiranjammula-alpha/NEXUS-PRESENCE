/**
 * ESP32 Physical Node 3D Representations & RF Wave Emitters
 * Author: Uday Kiran Jammula
 */

class NexusNodes {
    constructor(scene, nodeConfigs = {}) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);

        this.nodeMeshes = {};
        this.pulseRings = {};

        // Default corner positions if not provided
        this.configs = Object.keys(nodeConfigs).length ? nodeConfigs : {
            1: { id: 1, label: "MASTER #1", position: [0.0, 0.0, 2.0] },
            2: { id: 2, label: "SENSOR #2", position: [10.0, 0.0, 2.0] },
            3: { id: 3, label: "SENSOR #3", position: [0.0, 10.0, 2.0] },
            4: { id: 4, label: "SENSOR #4", position: [10.0, 10.0, 2.0] }
        };

        this.buildNodes();
    }

    buildNodes() {
        for (const [idStr, cfg] of Object.entries(this.configs)) {
            const id = parseInt(idStr, 10);
            const pos = cfg.position;

            const nodeGroup = new THREE.Group();
            nodeGroup.position.set(pos[0], pos[2] || pos[1] || 2.0, pos[1] || pos[2] || 0.0);

            // 1. ESP32 PCB Enclosure
            const encGeo = new THREE.BoxGeometry(0.35, 0.15, 0.25);
            const encMat = new THREE.MeshStandardMaterial({
                color: id === 1 ? 0x1e293b : 0x0f172a,
                roughness: 0.4,
                metalness: 0.6
            });
            const enclosure = new THREE.Mesh(encGeo, encMat);
            nodeGroup.add(enclosure);

            // 2. Wi-Fi Antenna Mast
            const antGeo = new THREE.CylinderGeometry(0.015, 0.02, 0.4, 12);
            const antMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.5 });
            const antenna = new THREE.Mesh(antGeo, antMat);
            antenna.position.set(0.12, 0.25, 0);
            nodeGroup.add(antenna);

            // 3. Status Indicator LED
            const ledGeo = new THREE.SphereGeometry(0.035, 16, 16);
            const ledMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
            const led = new THREE.Mesh(ledGeo, ledMat);
            led.position.set(-0.1, 0.08, 0.08);
            nodeGroup.add(led);

            // 4. Expanding RF Wave Ring
            const ringGeo = new THREE.RingGeometry(0.2, 0.28, 32);
            const ringMat = new THREE.MeshBasicMaterial({
                color: id === 1 ? 0x00f0ff : 0x38bdf8,
                transparent: true,
                opacity: 0.6,
                side: THREE.DoubleSide
            });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2;
            ring.position.y = 0;
            nodeGroup.add(ring);

            this.pulseRings[id] = { mesh: ring, scale: 1.0 };
            this.nodeMeshes[id] = { group: nodeGroup, led: led, ledMat: ledMat };
            this.group.add(nodeGroup);
        }
    }

    updateTelemetry(nodeId, state) {
        if (!this.nodeMeshes[nodeId]) return;
        const { ledMat } = this.nodeMeshes[nodeId];

        if (!state.online) {
            ledMat.color.setHex(0xef4444); // Red: Offline
        } else if (state.status === "HIGH ACTIVITY") {
            ledMat.color.setHex(0xf59e0b); // Amber/Orange
        } else if (state.status === "MOVEMENT") {
            ledMat.color.setHex(0x00f0ff); // Cyan active
        } else {
            ledMat.color.setHex(0x10b981); // Emerald green stable
        }
    }

    animate(delta) {
        // Continuous subtle RF pulse ripple
        for (const id in this.pulseRings) {
            const item = this.pulseRings[id];
            item.scale += delta * 1.5;
            if (item.scale > 4.5) {
                item.scale = 0.5;
            }
            item.mesh.scale.set(item.scale, item.scale, item.scale);
            item.mesh.material.opacity = Math.max(0.0, 0.7 - (item.scale / 4.5));
        }
    }
}

window.NexusNodes = NexusNodes;
