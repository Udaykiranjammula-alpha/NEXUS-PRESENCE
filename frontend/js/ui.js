/**
 * Dashboard UI State Dispatcher & DOM Synchronizer
 * Author: Uday Kiran Jammula
 */

class NexusUI {
    constructor() {
        this.dom = {
            systemStatusBadge: document.getElementById('system-status-badge'),
            sensingModeBadge: document.getElementById('sensing-mode-badge'),
            simBadge: document.getElementById('sim-mode-badge'),
            
            // Person tracking metrics
            posX: document.getElementById('metric-pos-x'),
            posY: document.getElementById('metric-pos-y'),
            posZ: document.getElementById('metric-pos-z'),
            velocity: document.getElementById('metric-velocity'),
            direction: document.getElementById('metric-direction'),
            movement: document.getElementById('metric-movement'),
            confidenceVal: document.getElementById('metric-confidence-val'),
            confidenceFill: document.getElementById('metric-confidence-fill'),

            // Node cards
            nodes: {
                1: this.getNodeElements(1),
                2: this.getNodeElements(2),
                3: this.getNodeElements(3),
                4: this.getNodeElements(4)
            }
        };
    }

    getNodeElements(id) {
        return {
            statusPill: document.getElementById(`node-${id}-status`),
            rssi: document.getElementById(`node-${id}-rssi`),
            packets: document.getElementById(`node-${id}-packets`),
            csi: document.getElementById(`node-${id}-csi`),
            dev: document.getElementById(`node-${id}-dev`)
        };
    }

    update(packet) {
        if (!packet) return;

        // 1. Top Badges
        if (this.dom.sensingModeBadge) {
            this.dom.sensingModeBadge.textContent = packet.sensing_mode || "RSSI ONLY";
            if ((packet.sensing_mode || "").includes("CSI")) {
                this.dom.sensingModeBadge.className = "badge badge-csi";
            } else {
                this.dom.sensingModeBadge.className = "badge";
            }
        }

        if (this.dom.simBadge) {
            this.dom.simBadge.style.display = packet.is_simulation ? "inline-flex" : "none";
        }

        if (this.dom.systemStatusBadge) {
            const isOnline = packet.system_status === "ONLINE";
            this.dom.systemStatusBadge.className = `badge ${isOnline ? 'badge-online' : 'badge-offline'}`;
            this.dom.systemStatusBadge.innerHTML = `<span class="pulse-dot"></span> ${packet.system_status}`;
        }

        // 2. Person Tracking HUD
        const pos = packet.position_estimate;
        if (pos) {
            if (this.dom.posX) this.dom.posX.textContent = `${pos.x.toFixed(2)} m`;
            if (this.dom.posY) this.dom.posY.textContent = `${pos.y.toFixed(2)} m`;
            if (this.dom.posZ) this.dom.posZ.textContent = `${pos.z.toFixed(2)} m`;
            if (this.dom.velocity) this.dom.velocity.textContent = `${pos.velocity.toFixed(2)} m/s`;
            
            if (this.dom.direction) {
                const deg = Math.round((pos.direction * 180) / Math.PI);
                this.dom.direction.textContent = `${deg}°`;
            }

            if (this.dom.movement) {
                this.dom.movement.textContent = pos.movement;
                if (pos.movement === "HIGH ACTIVITY") {
                    this.dom.movement.style.color = "var(--accent-amber)";
                } else if (pos.movement === "MOVEMENT") {
                    this.dom.movement.style.color = "var(--accent-cyan)";
                } else {
                    this.dom.movement.style.color = "var(--accent-emerald)";
                }
            }

            if (this.dom.confidenceVal) {
                const confPercent = Math.round(pos.confidence * 100);
                this.dom.confidenceVal.textContent = `${confPercent}%`;
                if (this.dom.confidenceFill) {
                    this.dom.confidenceFill.style.width = `${confPercent}%`;
                }
            }
        }

        // 3. Node Cards
        if (packet.nodes) {
            for (let i = 1; i <= 4; i++) {
                const n = packet.nodes[i];
                const elems = this.dom.nodes[i];
                if (!elems) continue;

                if (!n || !n.online) {
                    if (elems.statusPill) {
                        elems.statusPill.className = "badge badge-offline";
                        elems.statusPill.textContent = "OFFLINE";
                    }
                    if (elems.rssi) elems.rssi.textContent = "-- dBm";
                    if (elems.packets) elems.packets.textContent = "0";
                    if (elems.csi) elems.csi.textContent = "DISABLED";
                    if (elems.dev) elems.dev.textContent = "0.0 dB";
                } else {
                    if (elems.statusPill) {
                        elems.statusPill.className = "badge badge-online";
                        elems.statusPill.textContent = n.status || "ONLINE";
                    }
                    if (elems.rssi) elems.rssi.textContent = `${n.filtered_rssi || n.raw_rssi} dBm`;
                    if (elems.packets) elems.packets.textContent = `${n.total_packets || 0}`;
                    if (elems.csi) elems.csi.textContent = (n.sensing_mode === "CSI_RSSI") ? "ACTIVE" : "RSSI_ONLY";
                    if (elems.dev) elems.dev.textContent = `Δ ${n.deviation || 0.0} dB`;
                }
            }
        }
    }
}

window.NexusUI = NexusUI;
