/**
 * 3D Room Geometry and Environment Builder
 * Author: Uday Kiran Jammula
 */

class NexusRoom {
    constructor(scene, options = {}) {
        this.scene = scene;
        this.width = options.width || 10;
        this.length = options.length || 10;
        this.height = options.height || 3.0;

        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.buildRoom();
    }

    buildRoom() {
        // Floor with high-tech grid
        const floorGeo = new THREE.PlaneGeometry(this.width, this.length);
        const floorMat = new THREE.MeshStandardMaterial({
            color: 0x0a0e17,
            roughness: 0.8,
            metalness: 0.2
        });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.position.set(this.width / 2, 0, this.length / 2);
        floor.receiveShadow = true;
        this.group.add(floor);

        // Grid overlay
        const gridHelper = new THREE.GridHelper(Math.max(this.width, this.length), 20, 0x00f0ff, 0x1f2937);
        gridHelper.position.set(this.width / 2, 0.01, this.length / 2);
        this.group.add(gridHelper);

        // Outer Wireframe Bounding Volume
        const boxGeo = new THREE.BoxGeometry(this.width, this.height, this.length);
        const edges = new THREE.EdgesGeometry(boxGeo);
        const lineMat = new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.35 });
        const wireBox = new THREE.LineSegments(edges, lineMat);
        wireBox.position.set(this.width / 2, this.height / 2, this.length / 2);
        this.group.add(wireBox);

        // Translucent holographic boundary walls
        const wallMat = new THREE.MeshPhysicalMaterial({
            color: 0x031728,
            transparent: true,
            opacity: 0.15,
            roughness: 0.3,
            transmission: 0.8,
            side: THREE.DoubleSide
        });

        // Back wall (Z = 0)
        const backWall = new THREE.Mesh(new THREE.PlaneGeometry(this.width, this.height), wallMat);
        backWall.position.set(this.width / 2, this.height / 2, 0);
        this.group.add(backWall);

        // Left wall (X = 0)
        const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(this.length, this.height), wallMat);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.position.set(0, this.height / 2, this.length / 2);
        this.group.add(leftWall);

        // Coordinate axes markings
        this.createAxisLabels();
    }

    createAxisLabels() {
        // Subtle origin indicator
        const originGeo = new THREE.SphereGeometry(0.08, 16, 16);
        const originMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
        const originMarker = new THREE.Mesh(originGeo, originMat);
        originMarker.position.set(0, 0.05, 0);
        this.group.add(originMarker);
    }
}

window.NexusRoom = NexusRoom;
