/**
 * Resilient WebSocket Client for NEXUS-PRESENCE
 * Author: Uday Kiran Jammula
 */

class NexusWebSocketClient {
    constructor(url, callbacks = {}) {
        this.url = url;
        this.callbacks = callbacks;
        this.ws = null;
        this.reconnectInterval = 2500;
        this.isConnected = false;
        this.shouldReconnect = true;

        this.connect();
    }

    connect() {
        try {
            console.log(`[WS] Connecting to telemetry stream: ${this.url}`);
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log("[WS] Telemetry stream connected successfully.");
                this.isConnected = true;
                if (this.callbacks.onConnect) this.callbacks.onConnect();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (this.callbacks.onPacket) this.callbacks.onPacket(data);
                } catch (e) {
                    console.debug("[WS] Raw non-JSON payload:", event.data);
                }
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                if (this.callbacks.onDisconnect) this.callbacks.onDisconnect();
                if (this.shouldReconnect) {
                    setTimeout(() => this.connect(), this.reconnectInterval);
                }
            };

            this.ws.onerror = (err) => {
                console.warn("[WS] Telemetry connection error:", err);
                this.ws.close();
            };
        } catch (e) {
            console.error("[WS] Initialization exception:", e);
            if (this.shouldReconnect) {
                setTimeout(() => this.connect(), this.reconnectInterval);
            }
        }
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        }
    }
}

window.NexusWebSocketClient = NexusWebSocketClient;
