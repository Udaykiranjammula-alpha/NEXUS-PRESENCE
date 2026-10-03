/**
 * Genuine Procedural 3D Humanoid Avatar (Low-Poly Articulated Rig)
 * Author: Uday Kiran Jammula
 */

class NexusHumanAvatar {
    constructor(scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);

        // Materials
        this.bodyMat = new THREE.MeshStandardMaterial({
            color: 0x1e293b,
            roughness: 0.35,
            metalness: 0.5
        });
        this.jointMat = new THREE.MeshStandardMaterial({
            color: 0x0f172a,
            roughness: 0.2,
            metalness: 0.8
        });
        this.visorMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff
        });
        this.accentMat = new THREE.MeshBasicMaterial({
            color: 0x38bdf8
        });

        this.buildHierarchy();
    }

    buildHierarchy() {
        // Root / Pelvis (Ground offset ~0.85m)
        this.pelvis = new THREE.Group();
        this.pelvis.position.y = 0.85;
        this.group.add(this.pelvis);

        // Pelvis geometry
        const pelvisMesh = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.16, 0.2), this.bodyMat);
        this.pelvis.add(pelvisMesh);

        // Torso / Spine
        this.torso = new THREE.Group();
        this.torso.position.y = 0.08;
        this.pelvis.add(this.torso);

        const chestMesh = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.45, 0.24), this.bodyMat);
        chestMesh.position.y = 0.22;
        this.torso.add(chestMesh);

        // Chest accent light strip
        const stripMesh = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.04, 0.25), this.accentMat);
        stripMesh.position.y = 0.32;
        this.torso.add(stripMesh);

        // Neck & Head
        this.neck = new THREE.Group();
        this.neck.position.y = 0.45;
        this.torso.add(this.neck);

        const headMesh = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.24, 0.22), this.bodyMat);
        headMesh.position.y = 0.14;
        this.neck.add(headMesh);

        // Visor
        const visorMesh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.08, 0.05), this.visorMat);
        visorMesh.position.set(0, 0.15, 0.12);
        this.neck.add(visorMesh);

        // --- ARMS ---
        // Left Arm (Pivot at shoulder)
        this.leftShoulder = new THREE.Group();
        this.leftShoulder.position.set(-0.24, 0.4, 0);
        this.torso.add(this.leftShoulder);

        const lUpperArm = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.28, 0.1), this.bodyMat);
        lUpperArm.position.y = -0.14;
        this.leftShoulder.add(lUpperArm);

        this.leftElbow = new THREE.Group();
        this.leftElbow.position.y = -0.28;
        this.leftShoulder.add(this.leftElbow);

        const lForearm = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.26, 0.09), this.bodyMat);
        lForearm.position.y = -0.13;
        this.leftElbow.add(lForearm);

        // Right Arm (Pivot at shoulder)
        this.rightShoulder = new THREE.Group();
        this.rightShoulder.position.set(0.24, 0.4, 0);
        this.torso.add(this.rightShoulder);

        const rUpperArm = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.28, 0.1), this.bodyMat);
        rUpperArm.position.y = -0.14;
        this.rightShoulder.add(rUpperArm);

        this.rightElbow = new THREE.Group();
        this.rightElbow.position.y = -0.28;
        this.rightShoulder.add(this.rightElbow);

        const rForearm = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.26, 0.09), this.bodyMat);
        rForearm.position.y = -0.13;
        this.rightElbow.add(rForearm);

        // --- LEGS ---
        // Left Leg (Pivot at hip)
        this.leftHip = new THREE.Group();
        this.leftHip.position.set(-0.11, -0.08, 0);
        this.pelvis.add(this.leftHip);

        const lThigh = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.4, 0.14), this.bodyMat);
        lThigh.position.y = -0.2;
        this.leftHip.add(lThigh);

        this.leftKnee = new THREE.Group();
        this.leftKnee.position.y = -0.4;
        this.leftHip.add(this.leftKnee);

        const lShin = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.38, 0.12), this.bodyMat);
        lShin.position.y = -0.19;
        this.leftKnee.add(lShin);

        const lFoot = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.2), this.jointMat);
        lFoot.position.set(0, -0.38, 0.04);
        this.leftKnee.add(lFoot);

        // Right Leg (Pivot at hip)
        this.rightHip = new THREE.Group();
        this.rightHip.position.set(0.11, -0.08, 0);
        this.pelvis.add(this.rightHip);

        const rThigh = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.4, 0.14), this.bodyMat);
        rThigh.position.y = -0.2;
        this.rightHip.add(rThigh);

        this.rightKnee = new THREE.Group();
        this.rightKnee.position.y = -0.4;
        this.rightHip.add(this.rightKnee);

        const rShin = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.38, 0.12), this.bodyMat);
        rShin.position.y = -0.19;
        this.rightKnee.add(rShin);

        const rFoot = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.2), this.jointMat);
        rFoot.position.set(0, -0.38, 0.04);
        this.rightKnee.add(rFoot);
    }
}

window.NexusHumanAvatar = NexusHumanAvatar;
