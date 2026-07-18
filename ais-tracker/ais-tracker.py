#!/usr/bin/env python3
"""
ais-tracker.py — AIS Contact Tracker

Connects to a local Signal K WebSocket, monitors AIS vessel positions,
and logs contact/departure events to ship-log-search API and Oracle Relay.

Usage:
    python3 ais-tracker.py [--config config.json]

Config file (CLI args or env vars override JSON):
    {
        "signal_k_url": "ws://localhost:3000/signalk/v1/stream",
        "oracle_relay_url": "wss://oracle-relay.casey-digennaro.workers.dev/room/casey-fishing",
        "log_api_url": "http://localhost:8080/api/log",
        "our_lat": 57.0531,
        "our_lon": -135.3348,
        "contact_radius_m": 500,
        "departure_radius_m": 1000,
        "cache_file": "/tmp/ais-vessel-cache.json",
        "self_vessel_name": "Casey's Boat"
    }
"""

import json
import math
import os
import signal
import sys
import time
import argparse
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

# Try websocket-client (primary), fall back to websockets
try:
    from websocket import WebSocketApp as WSApp
    HAS_WEBSOCKET_CLIENT = True
except ImportError:
    try:
        import websockets
        HAS_WEBSOCKET_CLIENT = False
    except ImportError:
        HAS_WEBSOCKET_CLIENT = False

try:
    import urllib.request as urlrequest
    import urllib.error as urlerror
except ImportError:
    urlrequest = None


# ─── Haversine ────────────────────────────────────────────────────────────────

def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance in metres between two (lat, lon) points."""
    R = 6_371_000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─── Vessel Cache ─────────────────────────────────────────────────────────────

class VesselCache:
    """Persistent JSON-backed cache of known vessels (MMSI → info + state)."""

    def __init__(self, path):
        self.path = path
        self._data = {}
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self._data, f, indent=2)
        os.replace(tmp, self.path)

    def get(self, mmsi, default=None):
        return self._data.get(mmsi, default)

    def set(self, mmsi, **fields):
        entry = self._data.setdefault(mmsi, {})
        entry.update(fields)
        entry["last_seen_utc"] = datetime.now(timezone.utc).isoformat()

    def transition(self, mmsi, new_state):
        entry = self._data.setdefault(mmsi, {})
        old = entry.get("state", "unknown")
        entry["state"] = new_state
        entry["last_seen_utc"] = datetime.now(timezone.utc).isoformat()
        return old

    def items(self):
        return self._data.items()


# ─── API / Relay Senders ─────────────────────────────────────────────────────

def send_to_ship_log_api(api_url, text, category, lat, lon, location_name=""):
    """POST a log entry to ship-log-search API (fire-and-forget)."""
    if not api_url or not urlrequest:
        return False
    payload = {
        "text": text,
        "category": category,
        "lat": lat,
        "lon": lon,
        "location_name": location_name or str(round(lat, 4)) + "," + str(round(lon, 4)),
    }
    data = json.dumps(payload).encode("utf-8")
    try:
        req = urlrequest.Request(
            api_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlrequest.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as exc:
        print(f"[ais-tracker] API POST failed: {exc}", file=sys.stderr)
        return False


def send_to_oracle_relay(ws, event_dict):
    """Send a JSON event to the Oracle Relay WebSocket (fire-and-forest)."""
    if not ws:
        return False
    try:
        ws.send(json.dumps(event_dict))
        return True
    except Exception as exc:
        print(f"[ais-tracker] Oracle relay send failed: {exc}", file=sys.stderr)
        return False


# ─── Signal K Delta Parsing ───────────────────────────────────────────────────

def parse_self_position(msg, self_uuid_hint=None):
    """Extract own ship position from a Signal K delta message.
    
    Returns (lat, lon) or None.
    """
    ctx = msg.get("context", "")
    updates = msg.get("updates", [])
    if not updates:
        return None

    # Self vessel usually has a well-known context or the path "navigation.position"
    # We look at the very first update's values
    for update in updates:
        values = update.get("values", [])
        for v in values:
            path = v.get("path", "")
            if path == "navigation.position" or path == "position":
                val = v.get("value", {})
                lat = val.get("latitude")
                lon = val.get("longitude")
                if lat is not None and lon is not None:
                    return (float(lat), float(lon))
    return None


def parse_ais_targets(msg, known_mmsis=None):
    """Extract AIS vessel reports from a Signal K delta.

    Each AIS target typically has a self-describing context like:
        vessels.urn:mrn:imo:mmsi:366987654
    and values containing navigation.position, name, etc.

    Yields dicts with keys: mmsi, name, lat, lon, sog, cog
    """
    if known_mmsis is None:
        known_mmsis = {}

    ctx = msg.get("context", "")
    updates = msg.get("updates", [])

    # Try to extract MMSI from context
    ctx_mmsi = _extract_mmsi_from_context(ctx)

    for update in updates:
        values = update.get("values", [])
        source = update.get("source", {})
        source_mmsi = source.get("mmsi")

        # Collect all values into a flat dict keyed by path
        flat = {}
        for v in values:
            flat[v["path"]] = v["value"]

        position = flat.get("navigation.position") or flat.get("position")
        if not position:
            continue

        lat = _to_float(position.get("latitude"))
        lon = _to_float(position.get("longitude"))
        if lat is None or lon is None:
            continue

        mmsi = source_mmsi or ctx_mmsi or _mmsi_from_vessel_name(flat.get("name", ""))
        if not mmsi:
            continue

        name = flat.get("name", "")
        if isinstance(name, dict):
            name = name.get("value", "")
        name = str(name).strip()
        if not name:
            name = known_mmsis.get(str(mmsi), {}).get("name", f"MMSI-{mmsi}")

        sog_val = flat.get("navigation.speedOverGround")
        if isinstance(sog_val, dict):
            sog_val = sog_val.get("value", sog_val)
        sog = _to_float(sog_val)

        cog_val = flat.get("navigation.courseOverGroundTrue")
        if isinstance(cog_val, dict):
            cog_val = cog_val.get("value", cog_val)
        cog = _to_float(cog_val)

        yield {
            "mmsi": str(mmsi),
            "name": name,
            "lat": lat,
            "lon": lon,
            "sog": sog,
            "cog": cog,
            "timestamp": msg.get("timestamp", datetime.now(timezone.utc).isoformat()),
        }


def _extract_mmsi_from_context(context):
    if not context:
        return None
    # patterns: vessels.urn:mrn:imo:mmsi:366987654
    #           vessels.urn:mrn:signalk:uuid:... (no mmsi here)
    parts = context.split(":")
    for i, p in enumerate(parts):
        if p == "mmsi" and i + 1 < len(parts):
            try:
                mmsi = parts[i + 1].split(".")[0].split(",")[0]
                if mmsi.isdigit():
                    return mmsi
            except (IndexError, ValueError):
                pass
    return None


def _mmsi_from_vessel_name(name):
    """Last-resort hash of vessel name for simulator vessels without real MMSI."""
    if not name:
        return None
    h = hashlib.md5(name.encode()).hexdigest()[:10]
    return f"0{h}"


def _to_float(val):
    if val is None:
        return None
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None


# ─── Config ───────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "signal_k_url": "ws://localhost:3000/signalk/v1/stream",
    "oracle_relay_url": "wss://oracle-relay.casey-digennaro.workers.dev/room/casey-fishing",
    "log_api_url": "http://localhost:8080/api/log",
    "our_lat": 57.0531,
    "our_lon": -135.3348,
    "contact_radius_m": 500,
    "departure_radius_m": 1000,
    "cache_file": "/tmp/ais-vessel-cache.json",
    "self_vessel_name": "Casey's Boat",
}


def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    if path:
        try:
            with open(path) as f:
                cfg.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"[ais-tracker] Warning: could not load config {path}: {exc}", file=sys.stderr)
    # env overrides
    env_map = {
        "AIS_SIGNALK_URL": "signal_k_url",
        "AIS_ORACLE_RELAY": "oracle_relay_url",
        "AIS_LOG_API": "log_api_url",
        "AIS_OUR_LAT": "our_lat",
        "AIS_OUR_LON": "our_lon",
        "AIS_CONTACT_RADIUS": "contact_radius_m",
        "AIS_DEPARTURE_RADIUS": "departure_radius_m",
        "AIS_CACHE_FILE": "cache_file",
        "AIS_VESSEL_NAME": "self_vessel_name",
    }
    for env_key, cfg_key in env_map.items():
        val = os.environ.get(env_key)
        if val is not None:
            if cfg_key in ("our_lat", "our_lon", "contact_radius_m", "departure_radius_m"):
                try:
                    cfg[cfg_key] = float(val)
                except ValueError:
                    pass
            else:
                cfg[cfg_key] = val

    return cfg


# ─── Main Loop (websocket-client based) ───────────────────────────────────────

def run_tracker_ws_client(cfg):
    """Run tracker using the `websocket-client` library."""
    cache = VesselCache(cfg["cache_file"])
    contact_radius = cfg["contact_radius_m"]
    departure_radius = cfg["departure_radius_m"]
    our_lat = cfg["our_lat"]
    our_lon = cfg["our_lon"]
    self_name = cfg["self_vessel_name"]

    oracle_ws = None  # filled once connected
    oracle_connected = False

    def connect_oracle():
        nonlocal oracle_ws, oracle_connected
        if not cfg.get("oracle_relay_url"):
            return
        try:
            if oracle_ws:
                try:
                    oracle_ws.close()
                except Exception:
                    pass
            from websocket import create_connection
            oracle_ws = create_connection(cfg["oracle_relay_url"], timeout=10)
            oracle_connected = True
            print(f"[ais-tracker] Connected to Oracle Relay: {cfg['oracle_relay_url']}")
        except Exception as exc:
            print(f"[ais-tracker] Oracle Relay connection failed: {exc}", file=sys.stderr)
            oracle_connected = False

    connect_oracle()

    def on_message(ws, message):
        nonlocal our_lat, our_lon
        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            return

        # --- 1. Update own position from stream ---
        self_pos = parse_self_position(msg)
        if self_pos:
            our_lat, our_lon = self_pos
            # print(f"[ais-tracker] Self position updated: {our_lat:.4f}, {our_lon:.4f}")

        # --- 2. Process AIS targets ---
        for vessel in parse_ais_targets(msg, known_mmsis=cache._data):
            mmsi = vessel["mmsi"]
            vlat, vlon = vessel["lat"], vessel["lon"]
            vname = vessel["name"]

            dist = haversine_m(our_lat, our_lon, vlat, vlon)
            old_state = cache.transition(mmsi, "in_range" if dist <= departure_radius else "out_of_range")

            # Update cache with latest info
            cache.set(mmsi,
                      name=vname,
                      lat=vlat,
                      lon=vlon,
                      sog=vessel.get("sog"),
                      cog=vessel.get("cog"),
                      dist_m=round(dist, 1),
                      )

            now_utc = datetime.now(timezone.utc).isoformat()
            loc_name = f"near {vname}"
            event = None

            # --- CONTACT EVENT (within contact_radius) ---
            if dist <= contact_radius and old_state != "in_range":
                text = (
                    f"🛥️ AIS CONTACT: {vname} ({mmsi}) "
                    f"at {vlat:.4f},{vlon:.4f} "
                    f"distance {dist:.0f}m "
                    f"SOG {vessel.get('sog', '?'):s} kts"
                    if isinstance(vessel.get('sog'), str) else
                    f"🛥️ AIS CONTACT: {vname} ({mmsi}) "
                    f"at {vlat:.4f},{vlon:.4f} "
                    f"distance {dist:.0f}m "
                    f"SOG {vessel.get('sog') or '?'} kts"
                )
                event = {
                    "type": "contact",
                    "text": text,
                    "category": "ais-contact",
                    "lat": vlat,
                    "lon": vlon,
                    "location_name": loc_name,
                    "vessel_mmsi": mmsi,
                    "vessel_name": vname,
                    "distance_m": round(dist, 1),
                    "own_lat": our_lat,
                    "own_lon": our_lon,
                    "timestamp": now_utc,
                }
                print(f"[ais-tracker] 🛥️ CONTACT: {vname} at {dist:.0f}m")

            # --- DEPARTURE EVENT (was in_range, now > departure_radius) ---
            elif dist > departure_radius and old_state == "in_range":
                text = (
                    f"🚩 AIS DEPARTURE: {vname} ({mmsi}) "
                    f"last seen at {vlat:.4f},{vlon:.4f} "
                    f"distance {dist:.0f}m"
                )
                event = {
                    "type": "departure",
                    "text": text,
                    "category": "ais-departure",
                    "lat": vlat,
                    "lon": vlon,
                    "location_name": loc_name,
                    "vessel_mmsi": mmsi,
                    "vessel_name": vname,
                    "distance_m": round(dist, 1),
                    "own_lat": our_lat,
                    "own_lon": our_lon,
                    "timestamp": now_utc,
                }
                print(f"[ais-tracker] 🚩 DEPARTURE: {vname} at {dist:.0f}m")

            if event:
                # Fire-and-forget to ship-log-search API
                send_to_ship_log_api(
                    cfg["log_api_url"],
                    event["text"],
                    event["category"],
                    event["lat"],
                    event["lon"],
                    event.get("location_name", ""),
                )
                # Fire-and-forget to Oracle Relay
                if oracle_ws and oracle_connected:
                    send_to_oracle_relay(oracle_ws, event)

        # Periodic save
        cache.save()

    def on_error(ws, error):
        print(f"[ais-tracker] WebSocket error: {error}", file=sys.stderr)

    def on_close(ws, close_status_code, close_msg):
        print(f"[ais-tracker] Signal K disconnected ({close_status_code}: {close_msg})", file=sys.stderr)
        # reconnect logic in the outer loop

    def on_open(ws):
        print(f"[ais-tracker] Connected to Signal K: {cfg['signal_k_url']}")
        print(f"[ais-tracker] Contact radius: {contact_radius}m | Departure radius: {departure_radius}m")
        print(f"[ais-tracker] Starting position: {our_lat:.4f}, {our_lon:.4f}")

    # Reconnect loop
    while True:
        ws = WSApp(
            cfg["signal_k_url"],
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        # Run with 10s ping interval, no timeout
        ws.run_forever(ping_interval=10, ping_timeout=5, reconnect=5)
        print("[ais-tracker] Signal K disconnected. Reconnecting in 5s...", file=sys.stderr)
        time.sleep(5)


# ─── Alternative: websockets library runner ────────────────────────────────────

async def run_tracker_websockets(cfg):
    """Run tracker using the `websockets` async library."""
    import asyncio
    import websockets

    cache = VesselCache(cfg["cache_file"])
    contact_radius = cfg["contact_radius_m"]
    departure_radius = cfg["departure_radius_m"]
    our_lat = cfg["our_lat"]
    our_lon = cfg["our_lon"]
    oracle_ws = None

    async def connect_oracle():
        nonlocal oracle_ws
        if not cfg.get("oracle_relay_url"):
            return
        try:
            oracle_ws = await websockets.connect(cfg["oracle_relay_url"])
            print(f"[ais-tracker] Connected to Oracle Relay: {cfg['oracle_relay_url']}")
        except Exception as exc:
            print(f"[ais-tracker] Oracle Relay connection failed: {exc}", file=sys.stderr)
            oracle_ws = None

    await connect_oracle()

    while True:
        try:
            async with websockets.connect(cfg["signal_k_url"]) as ws:
                print(f"[ais-tracker] Connected to Signal K: {cfg['signal_k_url']}")
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    # Self position
                    self_pos = parse_self_position(msg)
                    if self_pos:
                        our_lat, our_lon = self_pos

                    # AIS targets
                    for vessel in parse_ais_targets(msg, known_mmsis=cache._data):
                        mmsi = vessel["mmsi"]
                        vlat, vlon = vessel["lat"], vessel["lon"]
                        vname = vessel["name"]

                        dist = haversine_m(our_lat, our_lon, vlat, vlon)
                        old_state = cache.transition(mmsi, "in_range" if dist <= departure_radius else "out_of_range")

                        cache.set(mmsi, name=vname, lat=vlat, lon=vlon,
                                  sog=vessel.get("sog"), cog=vessel.get("cog"),
                                  dist_m=round(dist, 1))

                        now_utc = datetime.now(timezone.utc).isoformat()
                        loc_name = f"near {vname}"
                        event = None

                        if dist <= contact_radius and old_state != "in_range":
                            text = (
                                f"🛥️ AIS CONTACT: {vname} ({mmsi}) "
                                f"at {vlat:.4f},{vlon:.4f} "
                                f"distance {dist:.0f}m"
                            )
                            event = {
                                "type": "contact", "text": text,
                                "category": "ais-contact", "lat": vlat, "lon": vlon,
                                "location_name": loc_name, "vessel_mmsi": mmsi,
                                "vessel_name": vname, "distance_m": round(dist, 1),
                                "own_lat": our_lat, "own_lon": our_lon, "timestamp": now_utc,
                            }
                            print(f"[ais-tracker] 🛥️ CONTACT: {vname} at {dist:.0f}m")

                        elif dist > departure_radius and old_state == "in_range":
                            text = (
                                f"🚩 AIS DEPARTURE: {vname} ({mmsi}) "
                                f"last seen at {vlat:.4f},{vlon:.4f} "
                                f"distance {dist:.0f}m"
                            )
                            event = {
                                "type": "departure", "text": text,
                                "category": "ais-departure", "lat": vlat, "lon": vlon,
                                "location_name": loc_name, "vessel_mmsi": mmsi,
                                "vessel_name": vname, "distance_m": round(dist, 1),
                                "own_lat": our_lat, "own_lon": our_lon, "timestamp": now_utc,
                            }
                            print(f"[ais-tracker] 🚩 DEPARTURE: {vname} at {dist:.0f}m")

                        if event:
                            send_to_ship_log_api(cfg["log_api_url"], event["text"],
                                                 event["category"], event["lat"], event["lon"],
                                                 event.get("location_name", ""))
                            if oracle_ws:
                                try:
                                    await oracle_ws.send(json.dumps(event))
                                except Exception:
                                    oracle_ws = None
                                    await connect_oracle()

                    cache.save()

        except (websockets.exceptions.ConnectionClosed, OSError) as exc:
            print(f"[ais-tracker] Signal K disconnect: {exc}. Reconnecting in 5s...", file=sys.stderr)
            cache.save()
            await asyncio.sleep(5)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AIS Contact Tracker")
    parser.add_argument("--config", "-c", help="Path to config JSON file")
    parser.add_argument("--signal-k-url", help="Signal K WebSocket URL")
    parser.add_argument("--oracle-relay-url", help="Oracle Relay WebSocket URL")
    parser.add_argument("--log-api-url", help="Ship-log-search API URL")
    parser.add_argument("--our-lat", type=float, help="Our vessel latitude")
    parser.add_argument("--our-lon", type=float, help="Our vessel longitude")
    parser.add_argument("--contact-radius", type=float, help="Contact radius in metres")
    parser.add_argument("--departure-radius", type=float, help="Departure radius in metres")
    parser.add_argument("--cache-file", help="Vessel cache file path")
    args = parser.parse_args()

    cfg = load_config(args.config)

    # CLI overrides
    cli_map = {
        "signal_k_url": "signal-k-url",
        "oracle_relay_url": "oracle-relay-url",
        "log_api_url": "log-api-url",
        "our_lat": "our-lat",
        "our_lon": "our-lon",
        "contact_radius_m": "contact-radius",
        "departure_radius_m": "departure-radius",
        "cache_file": "cache-file",
    }
    for cfg_key, cli_arg in cli_map.items():
        val = getattr(args, cli_arg.replace("-", "_"), None)
        if val is not None:
            cfg[cfg_key] = val

    print("╔══════════════════════════════════════════════╗")
    print("║         AIS Contact Tracker                  ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Signal K:     {cfg['signal_k_url']:<33}║")
    print(f"║  Oracle Relay: {cfg.get('oracle_relay_url','(none)'):<33}║")
    print(f"║  API:          {cfg['log_api_url']:<33}║")
    print(f"║  Position:     {cfg['our_lat']:.4f}, {cfg['our_lon']:.4f}                        ║")
    print(f"║  Contact:      {cfg['contact_radius_m']:.0f}m                                    ║")
    print(f"║  Departure:    {cfg['departure_radius_m']:.0f}m                                    ║")
    print(f"║  Cache:        {cfg['cache_file']:<33}║")
    print("╚══════════════════════════════════════════════╝")

    # Graceful shutdown
    shutdown = False

    def handle_signal(sig, frame):
        nonlocal shutdown
        print("\n[ais-tracker] Shutting down...")
        shutdown = True
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if not HAS_WEBSOCKET_CLIENT:
        import asyncio
        asyncio.run(run_tracker_websockets(cfg))
    else:
        run_tracker_ws_client(cfg)


if __name__ == "__main__":
    main()
