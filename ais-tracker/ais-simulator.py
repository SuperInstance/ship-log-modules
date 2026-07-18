#!/usr/bin/env python3
"""
ais-simulator.py — AIS Simulator for Signal K

Generates fake AIS vessel position reports near Sitka, AK, and broadcasts
them as Signal K delta messages over a local WebSocket server on port 9099.

Designed for testing ais-tracker.py without real AIS hardware.

Usage:
    python3 ais-simulator.py [--port 9099] [--vessels 5]
"""

import asyncio
import json
import math
import random
import signal
import sys
import time
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    print("This simulator requires the `websockets` library.")
    print("Install: pip install websockets")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

SITKA_LAT = 57.0531
SITKA_LON = -135.3348

# Radius of simulation area from Sitka harbour (in degrees, ~6km)
SPAWN_RADIUS_DEG = 0.06

# How often we broadcast vessel positions (seconds)
UPDATE_INTERVAL = 2.0

# Speed range in knots (converted to deg/s per tick)
KTS_TO_DEG_PER_TICK = 0.009  # rough: 1 kt ≈ 0.00045 deg/s * 2s tick = 0.0009 deg/tick at 2kt
# Actually let me use proper nautical mile conversion
# 1 NM = 1/60 degree ≈ 0.0166667 degrees
# 1 knot = 1 NM/hour = 1 NM/3600s
# 1 kt = 0.0166667/3600 deg/s ≈ 4.63e-6 deg/s
# Per 2s tick: 4.63e-6 * 2 = 9.26e-6 deg/tick per kt
KTS_TO_DEG_PER_TICK = 9.26e-6 * UPDATE_INTERVAL

# Course change probability per tick
COURSE_CHANGE_P = 0.02
SPEED_CHANGE_P = 0.01

# Vessel templates
VESSEL_TEMPLATES = [
    {"name": "ALASKA DRAGON", "mmsi": "367310420", "length": 28, "type": "Fishing"},
    {"name": "SITKA QUEEN",   "mmsi": "367123450", "length": 18, "type": "Fishing"},
    {"name": "NORTHERN LIGHT","mmsi": "367000001", "length": 14, "type": "Pleasure"},
    {"name": "ROYAL EAGLE",   "mmsi": "366987650", "length": 22, "type": "Trawler"},
    {"name": "SEA WOLF",      "mmsi": "367222000", "length": 12, "type": "Skiff"},
    # extras for -v > 5
    {"name": "BROWN BEAR",    "mmsi": "367444000", "length": 35, "type": "Research"},
    {"name": "SILVER SALMON", "mmsi": "367555111", "length": 9,  "type": "Pleasure"},
    {"name": "HALIBUT HOOKER","mmsi": "366666888", "length": 16, "type": "Fishing"},
]


# ─── Vessel Engine ────────────────────────────────────────────────────────────

class SimVessel:
    """A single simulated vessel navigating near Sitka."""

    def __init__(self, template):
        self.name = template["name"]
        self.mmsi = template["mmsi"]
        self.length = template["length"]
        self.type = template["type"]

        # Random spawn within the simulation area
        self.lat = SITKA_LAT + random.uniform(-SPAWN_RADIUS_DEG, SPAWN_RADIUS_DEG)
        self.lon = SITKA_LON + random.uniform(-SPAWN_RADIUS_DEG, SPAWN_RADIUS_DEG)

        # Initial course (degrees true) and speed (knots)
        self.cog_deg = random.uniform(0, 360)
        self.sog_kts = random.uniform(0.5, 8.0)
        self.cog_rad = math.radians(self.cog_deg)

        # Keep within simulation bounds
        self._center_lat = SITKA_LAT
        self._center_lon = SITKA_LON
        self._bound_deg = SPAWN_RADIUS_DEG * 1.8

        # Message sequence number
        self.seq = 0

    def update(self):
        """Advance position by one tick."""
        self.seq += 1

        # Occasionally change course
        if random.random() < COURSE_CHANGE_P:
            self.cog_deg = (self.cog_deg + random.uniform(-45, 45)) % 360
            self.cog_rad = math.radians(self.cog_deg)

        # Occasionally change speed
        if random.random() < SPEED_CHANGE_P:
            self.sog_kts = max(0.1, min(12.0, self.sog_kts + random.uniform(-1.5, 1.5)))

        # Move
        dlat = math.cos(self.cog_rad) * self.sog_kts * KTS_TO_DEG_PER_TICK
        # lon correction for latitude
        dlon = (math.sin(self.cog_rad) * self.sog_kts * KTS_TO_DEG_PER_TICK /
                math.cos(math.radians(self.lat)))

        self.lat += dlat
        self.lon += dlon

        # Contain within bounds by steering toward centre
        if abs(self.lat - self._center_lat) > self._bound_deg:
            self.cog_deg = 270 if self.lat > self._center_lat else 90
            self.cog_rad = math.radians(self.cog_deg)
        if abs(self.lon - self._center_lon) > self._bound_deg:
            self.cog_deg = 180 if self.lon > self._center_lon else 0
            self.cog_rad = math.radians(self.cog_deg)

    def to_signalk_delta(self):
        """Build a Signal K delta message for this vessel."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
              f"{datetime.now(timezone.utc).microsecond:06d}Z"
        uuid = f"urn:mrn:imo:mmsi:{self.mmsi}"

        return {
            "context": f"vessels.{uuid}",
            "updates": [
                {
                    "source": {
                        "label": "AIS-simulator",
                        "type": "AIS",
                        "mmsi": self.mmsi,
                    },
                    "timestamp": now,
                    "values": [
                        {
                            "path": "name",
                            "value": self.name,
                        },
                        {
                            "path": "navigation.position",
                            "value": {
                                "latitude": round(self.lat, 6),
                                "longitude": round(self.lon, 6),
                            },
                        },
                        {
                            "path": "navigation.speedOverGround",
                            "value": {
                                "value": round(self.sog_kts * 0.514444, 2),  # kts → m/s
                                "unit": "m/s",
                            },
                        },
                        {
                            "path": "navigation.courseOverGroundTrue",
                            "value": {
                                "value": round(self.cog_rad, 4),
                                "unit": "rad",
                            },
                        },
                    ],
                }
            ],
        }


# ─── Server ───────────────────────────────────────────────────────────────────

class AISSimulatorServer:
    """WebSocket server that broadcasts fake AIS data."""

    def __init__(self, host="0.0.0.0", port=9099, vessel_count=5):
        self.host = host
        self.port = port
        self.vessel_count = min(vessel_count, len(VESSEL_TEMPLATES))
        self.clients = set()
        self.vessels = []
        self._tick_task = None

    def create_vessels(self):
        templates = random.sample(VESSEL_TEMPLATES, self.vessel_count)
        self.vessels = [SimVessel(t) for t in templates]

    async def handler(self, websocket):
        self.clients.add(websocket)
        addr = websocket.remote_address
        print(f"[ais-simulator] Client connected: {addr}")
        try:
            async for msg in websocket:
                # We don't expect messages from clients, but handle pings gracefully
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"[ais-simulator] Client disconnected: {addr}")

    async def tick(self):
        """Periodically update vessel positions and broadcast."""
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)

            # Update all vessels
            for v in self.vessels:
                v.update()

            if not self.clients:
                continue

            # Build delta messages
            messages = [v.to_signalk_delta() for v in self.vessels]

            # Broadcast to all connected clients
            dead = set()
            for ws in self.clients:
                try:
                    for msg in messages:
                        await ws.send(json.dumps(msg))
                except websockets.exceptions.ConnectionClosed:
                    dead.add(ws)

            self.clients -= dead

    async def start(self):
        self.create_vessels()

        # Print vessel manifest
        print("╔══════════════════════════════════════════════╗")
        print("║         AIS Simulator                        ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║  Host: {self.host}:{self.port:<5}                              ║")
        print(f"║  Vessels: {self.vessel_count}                                        ║")
        print(f"║  Interval: {UPDATE_INTERVAL}s                                     ║")
        print("╠══════════════════════════════════════════════╣")
        print("║  Simulated Vessels:                           ║")
        for v in self.vessels:
            print(f"║    {v.name:20s} ({v.mmsi})  type={v.type:8s}       ║")
        print("╚══════════════════════════════════════════════╝")

        self._tick_task = asyncio.create_task(self.tick())

        async with websockets.serve(self.handler, self.host, self.port):
            print(f"[ais-simulator] Listening on ws://{self.host}:{self.port}")
            await asyncio.get_running_loop().create_future()  # run forever


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="AIS Simulator for Signal K")
    parser.add_argument("--port", "-p", type=int, default=9099,
                        help="WebSocket server port (default: 9099)")
    parser.add_argument("--vessels", "-v", type=int, default=5,
                        help="Number of simulated vessels (default: 5, max: 8)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Bind address (default: 0.0.0.0)")
    args = parser.parse_args()

    n = min(max(args.vessels, 1), len(VESSEL_TEMPLATES))
    if args.vessels > len(VESSEL_TEMPLATES):
        print(f"[ais-simulator] Note: capping to {len(VESSEL_TEMPLATES)} available templates",
              file=sys.stderr)

    server = AISSimulatorServer(host=args.host, port=args.port, vessel_count=n)

    # Graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def handle_signal(sig, frame):
        print("\n[ais-simulator] Shutting down...")
        loop.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        print("\n[ais-simulator] Goodbye!")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
