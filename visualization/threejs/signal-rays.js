/**
 * Dynamic RF Signal Rays, Beam Lines, and Spatial Target Indicators
 * Author: Uday Kiran Jammula
 */

class NexusSignalRays {
    constructor(scene, nodeConfigs = {}) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);

        this.lines = {};
        this.nodeConfigs = nodeConfigs;

        // Ground Target Marker & Confidence Radius Disc
        const discGeo = new THREE.RingGeometry(0.05, 0.8, 32);
        this.confidenceDiscMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.35,
            side: THREE.DoubleSide
        });
        this.confidenceDisc = new THREE.Mesh(discGeo, this.confidenceDiscMat);
        this.confidenceDisc.rotation.x = -Math.PI / 2;
        this.confidenceDisc.position.set(5, 0.02, 5);
        this.group.add(this.confidenceDisc);

        // Ground crosshair marker
        const crossGeo = new THREE.RingGeometry(0.02, 0.15, 16);
        const crossMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        this.targetCross = new THREE.Mesh(crossGeo, crossMat);
        this.targetCross.rotation.x = -Math.PI / 2;
        this.targetCross.position.set(5, 0.03, 5);
        this.group.add(this.targetCross);

        this.initRays();
    }

    initRays() {
        const lineMat = new THREE.LineDashedMaterial({
            color: 0x00f0ff,
            linewidth: 1,
            scale: 1,
            dashSize: 0.2,
            gapSize: 0.1,
            transparent: true,
            opacity: 0.45
        });

        for (let i = 1; i <= 4; i++) {
            const geom = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0, 2, 0),
                new THREE.Vector3(5, 1.0, 5)
            ]);
            const line = new THREE.Line(geom, lineMat.clone());
            this.lines[i] = line;
            this.group.add(line);
        }
    }

    updateTarget(targetX, targetY, targetZ, confidence = 0.85, nodeStates = {}) {
        // Floor marker positions (targetY in Three.js represents vertical height, targetX/Z are room ground)
        // Mapping: backend x -> Three.js x, backend y -> Three.js z, backend z -> Three.js y
        const avatarGroundPos = new THREE.Vector3(targetX, 0.02, targetY);
        this.confidenceDisc.position.set(targetX, 0.02, targetY);
        this.targetCross.position.set(targetX, 0.03, targetY);

        // Confidence radius sizing: higher confidence => tighter circle
        const radius = Math.max(0.3, 1.8 * (1.0 - confidence) + 0.4);
        this.confidenceDisc.scale.set(radius, radius, radius);

        const avatarTorsoPos = new THREE.Vector3(targetX, 1.0, targetY);

        // Update ray lines from each sensor node
        for (let i = 1; i <= 4; i++) {
            if (!this.lines[i]) continue;

            const cfg = this.nodeConfigs[i] || { position: [i % 2 === 0 ? 10 : 0, i > 2 ? 10 : 0, 2.0] };
            const nodePos = new THREE.Vector3(cfg.position[0], cfg.position[2] || 2.0, cfg.position[1]);

            const geom = this.lines[i].geometry;
            const positions = new Float32Array([
                nodePos.x, nodePos.y, nodePos.z,
                avatarTorsoPos.x, avatarTorsoPos.y, avatarTorsoPos.z
            ]);
            geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geom.computeBoundingSphere();

            // Adjust line opacity and color based on node status
            const nState = nodeStates[i];
            if (nState && nState.status === "MOVEMENT") {
                this.lines[i].material.color.setHex(0x00f0ff);
                this.lines[i].material.opacity = 0.8;
            } else if (nState && nState.status === "HIGH ACTIVITY") {
                this.lines[i].material.color.setHex(0xf59e0b);
                this.lines[i].material.opacity = 0.9;
            } else {
                this.lines[i].material.color.setHex(0x334155);
                this.lines[i].material.opacity = 0.25;
            }
        }
    }
}

window.NexusSignalRays = NexusSignalRays;
