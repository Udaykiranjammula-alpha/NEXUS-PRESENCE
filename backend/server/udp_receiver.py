"""
Async UDP Receiver for ESP32 Sensor Telemetry
Author: Uday Kiran Jammula
"""

import asyncio
import json
import logging
from typing import Callable, Optional
from backend.models.telemetry import RawNodeTelemetry

logger = logging.getLogger("nexus.udp")

class ESP32TelemetryProtocol(asyncio.DatagramProtocol):
    def __init__(self, packet_callback: Callable[[RawNodeTelemetry], None]):
        self.packet_callback = packet_callback
        self.transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
        logger.info("[UDP] ESP32 Telemetry Protocol listener established.")

    def datagram_received(self, data: bytes, addr):
        try:
            payload_str = data.decode("utf-8").strip()
            # In case multiple JSON objects were coalesced
            for line in payload_str.splitlines():
                line = line.strip()
                if not line:
                    continue
                data_dict = json.loads(line)
                telemetry = RawNodeTelemetry(**data_dict)
                self.packet_callback(telemetry)
        except Exception as e:
            logger.debug(f"[UDP] Packet parse error from {addr}: {e}")

    def error_received(self, exc):
        logger.error(f"[UDP] Error received on socket: {exc}")

    def connection_lost(self, exc):
        logger.info("[UDP] Listener connection closed.")

async def start_udp_listener(host: str, port: int, callback: Callable[[RawNodeTelemetry], None]):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ESP32TelemetryProtocol(callback),
        local_addr=(host, port)
    )
    return transport, protocol
