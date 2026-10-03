/**
 * Master Scene Coordinator for NEXUS-PRESENCE
 * Author: Uday Kiran Jammula
 */

class NexusScene {
    constructor(containerElement, config = {}) {
        this.container = containerElement;
        this.config = config;

        this.width = config.width || 10;
        this.length = config.length || 10;
        this.height = config.height || 3.0;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x06090e);
        this.scene.fog = new THREE.FogExp2(0x06090e, 0.035);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.1;
        this.container.appendChild(this.renderer.domElement);

        this.clock = new THREE.Clock();

        // Instantiate Subsystems
        this.cameraRig = new NexusCamera(this.container, {
            width: this.width, length: this.length, height: this.height
        });
        this.lighting = new NexusLighting(this.scene, {
            width: this.width, length: this.length, height: this.height
        });
        this.room = new NexusRoom(this.scene, {
            width: this.width, length: this.length, height: this.height
        });
        this.nodes = new NexusNodes(this.scene, config.nodes || {});
        this.signalRays = new NexusSignalRays(this.scene, config.nodes || {});

        this.avatar = new NexusHumanAvatar(this.scene);
        this.animation = new NexusAvatarAnimation(this.avatar);
        this.movementController = new NexusMovementController(this.avatar, this.animation);

        // Bind Resize Event
        window.addEventListener('resize', () => this.onResize());

        // Kick off loop
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    onResize() {
        if (!this.container || !this.renderer) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.cameraRig.onWindowResize();
        this.renderer.setSize(width, height);
    }

    handleTelemetry(packet) {
        if (!packet) return;

        // 1. Update avatar position and kinematics
        if (packet.position_estimate) {
            this.movementController.setTargetTelemetry(packet.position_estimate);
            this.signalRays.updateTarget(
                packet.position_estimate.x,
                packet.position_estimate.y,
                packet.position_estimate.z,
                packet.position_estimate.confidence,
                packet.nodes || {}
            );
        }

        // 2. Update sensor node statuses & indicators
        if (packet.nodes) {
            for (const [nid, nstate] of Object.entries(packet.nodes)) {
                this.nodes.updateTelemetry(parseInt(nid, 10), nstate);
            }
        }
    }

    animate() {
        requestAnimationFrame(this.animate);

        const delta = Math.min(this.clock.getDelta(), 0.1);

        this.cameraRig.update();
        this.nodes.animate(delta);
        this.movementController.update(delta);

        this.renderer.render(this.scene, this.cameraRig.camera);
    }
}

window.NexusScene = NexusScene;
