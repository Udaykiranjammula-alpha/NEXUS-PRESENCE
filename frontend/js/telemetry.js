/**
 * Telemetry State Manager & Buffer Store
 * Author: Uday Kiran Jammula
 */

class NexusTelemetryStore {
    constructor(maxHistory = 60) {
        this.maxHistory = maxHistory;
        this.latestPacket = null;
        
        // Rolling histories for charts
        this.rssiHistory = { 1: [], 2: [], 3: [], 4: [] };
        this.motionHistory = [];
        this.timestamps = [];
    }

    ingest(packet) {
        this.latestPacket = packet;
        const now = packet.timestamp || (Date.now() / 1000);

        this.timestamps.push(now);
        if (this.timestamps.length > this.maxHistory) this.timestamps.shift();

        // Push motion score
        this.motionHistory.push(packet.global_motion_score || 0.0);
        if (this.motionHistory.length > this.maxHistory) this.motionHistory.shift();

        // Push RSSI per node
        if (packet.nodes) {
            for (let i = 1; i <= 4; i++) {
                const n = packet.nodes[i];
                const val = n ? (n.filtered_rssi || n.raw_rssi || -70) : -70;
                this.rssiHistory[i].push(val);
                if (this.rssiHistory[i].length > this.maxHistory) this.rssiHistory[i].shift();
            }
        }
    }

    getNodeState(nodeId) {
        if (!this.latestPacket || !this.latestPacket.nodes) return null;
        return this.latestPacket.nodes[nodeId] || null;
    }

    getPositionEstimate() {
        if (!this.latestPacket) return null;
        return this.latestPacket.position_estimate || null;
    }
}

window.NexusTelemetryStore = NexusTelemetryStore;
