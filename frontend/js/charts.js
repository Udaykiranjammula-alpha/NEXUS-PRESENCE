/**
 * High-Performance Canvas Telemetry Charts
 * Author: Uday Kiran Jammula
 */

class NexusCharts {
    constructor(rssiCanvasId, motionCanvasId) {
        this.rssiCanvas = document.getElementById(rssiCanvasId);
        this.motionCanvas = document.getElementById(motionCanvasId);

        if (this.rssiCanvas) this.setupCanvas(this.rssiCanvas);
        if (this.motionCanvas) this.setupCanvas(this.motionCanvas);

        this.nodeColors = {
            1: '#38bdf8', // Cyan/Sky
            2: '#10b981', // Emerald
            3: '#a855f7', // Purple
            4: '#f59e0b'  // Amber
        };
    }

    setupCanvas(canvas) {
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
    }

    render(telemetryStore) {
        if (this.rssiCanvas) this.drawRssiChart(telemetryStore.rssiHistory);
        if (this.motionCanvas) this.drawMotionChart(telemetryStore.motionHistory);
    }

    drawRssiChart(rssiData) {
        const ctx = this.rssiCanvas.getContext('2d');
        const rect = this.rssiCanvas.getBoundingClientRect();
        const w = rect.width;
        const h = rect.height;

        ctx.clearRect(0, 0, w, h);

        // Draw grid lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let y = 20; y < h; y += 25) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }

        // Domain: -90 dBm to -30 dBm
        const minDb = -90;
        const maxDb = -30;

        for (let nid = 1; nid <= 4; nid++) {
            const series = rssiData[nid] || [];
            if (series.length < 2) continue;

            ctx.strokeStyle = this.nodeColors[nid];
            ctx.lineWidth = 1.5;
            ctx.beginPath();

            const step = w / (NEXUS_CONFIG.CHART_HISTORY_LENGTH - 1);
            for (let i = 0; i < series.length; i++) {
                const val = series[i];
                const normalizedY = 1.0 - ((val - minDb) / (maxDb - minDb));
                const py = Math.max(4, Math.min(h - 4, normalizedY * h));
                const px = i * step;

                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
        }
    }

    drawMotionChart(motionData) {
        const ctx = this.motionCanvas.getContext('2d');
        const rect = this.motionCanvas.getBoundingClientRect();
        const w = rect.width;
        const h = rect.height;

        ctx.clearRect(0, 0, w, h);

        // Draw threshold lines (Movement threshold at ~0.6)
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.2)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        const threshY = h * 0.4;
        ctx.beginPath();
        ctx.moveTo(0, threshY);
        ctx.lineTo(w, threshY);
        ctx.stroke();
        ctx.setLineDash([]);

        if (motionData.length < 2) return;

        // Area gradient
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        grad.addColorStop(0, 'rgba(0, 240, 255, 0.35)');
        grad.addColorStop(1, 'rgba(0, 240, 255, 0.0)');

        ctx.fillStyle = grad;
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 2;

        ctx.beginPath();
        const step = w / (NEXUS_CONFIG.CHART_HISTORY_LENGTH - 1);
        ctx.moveTo(0, h);

        for (let i = 0; i < motionData.length; i++) {
            const val = motionData[i]; // 0.0 to 1.0
            const py = h - (val * (h - 8)) - 4;
            const px = i * step;
            ctx.lineTo(px, py);
        }

        ctx.lineTo((motionData.length - 1) * step, h);
        ctx.closePath();
        ctx.fill();

        // Stroke line on top
        ctx.beginPath();
        for (let i = 0; i < motionData.length; i++) {
            const val = motionData[i];
            const py = h - (val * (h - 8)) - 4;
            const px = i * step;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.stroke();
    }
}

window.NexusCharts = NexusCharts;
