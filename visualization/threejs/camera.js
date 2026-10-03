/**
 * Camera Setup & Controls for NEXUS-PRESENCE
 * Author: Uday Kiran Jammula
 */

class NexusCamera {
    constructor(container, roomDimensions = { width: 10, length: 10, height: 3 }) {
        this.container = container;
        const aspect = container.clientWidth / container.clientHeight;
        
        this.camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 100);
        
        // Position camera diagonally elevated looking at room center
        const cx = roomDimensions.width / 2;
        const cy = roomDimensions.height / 2;
        const cz = roomDimensions.length / 2;
        
        this.camera.position.set(cx + 8, cy + 9, cz + 11);
        this.target = new THREE.Vector3(cx, 1.2, cz);
        this.camera.lookAt(this.target);

        // OrbitControls if loaded
        if (typeof THREE.OrbitControls !== "undefined") {
            this.controls = new THREE.OrbitControls(this.camera, container);
            this.controls.target.copy(this.target);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.maxPolarAngle = Math.PI / 2 - 0.05; // Don't clip under floor
            this.controls.minDistance = 2.0;
            this.controls.maxDistance = 28.0;
        }
    }

    update() {
        if (this.controls) {
            this.controls.update();
        }
    }

    onWindowResize() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.aspect = aspect;
        this.camera.updateProjectionMatrix();
    }
}

window.NexusCamera = NexusCamera;
