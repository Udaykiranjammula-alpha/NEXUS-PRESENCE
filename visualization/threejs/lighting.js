/**
 * Studio Lighting Rig for NEXUS-PRESENCE
 * Author: Uday Kiran Jammula
 */

class NexusLighting {
    constructor(scene, roomDimensions = { width: 10, length: 10, height: 3 }) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);

        const cx = roomDimensions.width / 2;
        const cy = roomDimensions.height;
        const cz = roomDimensions.length / 2;

        // Soft ambient fill
        const ambient = new THREE.AmbientLight(0x0e1b2a, 1.2);
        this.group.add(ambient);

        // Directional overhead key light
        const mainLight = new THREE.DirectionalLight(0xd4e5ff, 1.4);
        mainLight.position.set(cx + 4, cy + 6, cz + 3);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 1024;
        mainLight.shadow.mapSize.height = 1024;
        mainLight.shadow.bias = -0.001;
        this.group.add(mainLight);

        // Subtle cyan rim light for tech aesthetic
        const rimLight = new THREE.DirectionalLight(0x00f0ff, 0.8);
        rimLight.position.set(cx - 6, cy + 2, cz - 6);
        this.group.add(rimLight);

        // Center ceiling warm emitter
        const ceilingPoint = new THREE.PointLight(0x4095ff, 0.9, 15, 1.5);
        ceilingPoint.position.set(cx, cy - 0.2, cz);
        this.group.add(ceilingPoint);
    }
}

window.NexusLighting = NexusLighting;
