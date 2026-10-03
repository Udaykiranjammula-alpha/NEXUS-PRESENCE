/**
 * Live Movement Controller & Kinematic Interpolator
 * Author: Uday Kiran Jammula
 */

class NexusMovementController {
    constructor(avatar, animation) {
        this.avatar = avatar;
        this.animation = animation;

        // Current rendered transforms
        this.currentPos = new THREE.Vector3(5.0, 0.0, 5.0);
        this.targetPos = new THREE.Vector3(5.0, 0.0, 5.0);
        this.currentHeading = 0.0;
        this.targetHeading = 0.0;

        this.velocity = 0.0;
        this.state = "STABLE";
        this.confidence = 0.85;

        // Interpolation smoothing weights (alpha per delta second)
        this.lerpRate = 5.0; // Higher = faster tracking, lower = smoother
    }

    setTargetTelemetry(telemetry) {
        if (!telemetry) return;

        // Note: Mapping backend coords (X: width, Y: length) to Three.js coords (X: width, Z: length)
        if (typeof telemetry.x === "number" && typeof telemetry.y === "number") {
            this.targetPos.set(telemetry.x, 0.0, telemetry.y);
        }

        if (typeof telemetry.direction === "number") {
            this.targetHeading = telemetry.direction;
        }

        if (typeof telemetry.velocity === "number") {
            this.velocity = telemetry.velocity;
        }

        if (telemetry.movement) {
            this.state = telemetry.movement;
        }

        if (typeof telemetry.confidence === "number") {
            this.confidence = telemetry.confidence;
        }
    }

    update(delta) {
        // 1. Smooth exponential position lerp
        const alpha = Math.min(delta * this.lerpRate, 1.0);
        this.currentPos.lerp(this.targetPos, alpha);
        this.avatar.group.position.copy(this.currentPos);

        // 2. Smooth shortest-arc rotational heading slerp
        let diff = this.targetHeading - this.currentHeading;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        this.currentHeading += diff * alpha;

        // In Three.js, rotation around Y axis orients avatar facing direction
        // Adjust angle offset so avatar faces along the vector
        this.avatar.group.rotation.y = -this.currentHeading + Math.PI / 2;

        // 3. Update limb kinematics
        this.animation.update(delta, this.state, this.velocity);
    }
}

window.NexusMovementController = NexusMovementController;
