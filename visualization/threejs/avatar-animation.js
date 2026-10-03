/**
 * Avatar Kinematic Walking & Idle Animation Controller
 * Author: Uday Kiran Jammula
 */

class NexusAvatarAnimation {
    constructor(avatar) {
        this.avatar = avatar;
        this.cycleTime = 0.0;
        this.currentSpeed = 0.0;
        this.currentState = "STABLE";
    }

    update(delta, state = "STABLE", velocity = 0.0) {
        this.currentState = state;
        this.currentSpeed = velocity;

        if (state === "STABLE" || velocity < 0.1) {
            this.animateIdle(delta);
        } else {
            this.animateWalk(delta, velocity);
        }
    }

    animateIdle(delta) {
        this.cycleTime += delta * 1.5;
        const breath = Math.sin(this.cycleTime);

        // Subtle breathing sway in chest and neck
        this.avatar.torso.rotation.x = breath * 0.03;
        this.avatar.neck.rotation.x = -breath * 0.02;

        // Limbs rest naturally
        this.avatar.leftShoulder.rotation.x = 0.05 + breath * 0.02;
        this.avatar.rightShoulder.rotation.x = 0.05 - breath * 0.02;
        this.avatar.leftElbow.rotation.x = -0.1;
        this.avatar.rightElbow.rotation.x = -0.1;

        this.avatar.leftHip.rotation.x = 0;
        this.avatar.rightHip.rotation.x = 0;
        this.avatar.leftKnee.rotation.x = 0;
        this.avatar.rightKnee.rotation.x = 0;
        this.avatar.pelvis.position.y = 0.85 + breath * 0.005;
    }

    animateWalk(delta, velocity) {
        // Stride frequency scales with velocity
        const strideRate = Math.min(Math.max(velocity * 4.5, 3.0), 8.5);
        this.cycleTime += delta * strideRate;

        const legSwing = Math.sin(this.cycleTime) * 0.65;
        const armSwing = -legSwing * 0.7; // Arms counter-swing opposite to legs

        // Alternating leg swing
        this.avatar.leftHip.rotation.x = legSwing;
        this.avatar.rightHip.rotation.x = -legSwing;

        // Knee bends naturally during backward stride
        this.avatar.leftKnee.rotation.x = legSwing < 0 ? Math.abs(legSwing) * 0.9 : 0.1;
        this.avatar.rightKnee.rotation.x = -legSwing < 0 ? Math.abs(legSwing) * 0.9 : 0.1;

        // Arm swings
        this.avatar.leftShoulder.rotation.x = armSwing;
        this.avatar.rightShoulder.rotation.x = -armSwing;
        this.avatar.leftElbow.rotation.x = -Math.abs(armSwing) * 0.4;
        this.avatar.rightElbow.rotation.x = -Math.abs(armSwing) * 0.4;

        // Subtle torso twist & vertical bounce
        this.avatar.torso.rotation.y = legSwing * 0.15;
        this.avatar.pelvis.position.y = 0.85 + Math.abs(Math.sin(this.cycleTime * 2.0)) * 0.04;
    }
}

window.NexusAvatarAnimation = NexusAvatarAnimation;
