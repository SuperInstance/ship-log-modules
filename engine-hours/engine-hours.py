#!/usr/bin/env python3
"""
Engine Hours Tracker — tracks engine runtime and maintenance intervals.

Runs on the boat's nav computer. Listens to Signal K for engine RPM data.
Accumulates hours. Alerts when maintenance is due.

Usage:
  python3 engine-hours.py track     # Start tracking (daemon)
  python3 engine-hours.py status    # Show current hours and maintenance status
  python3 engine-hours.py log       # Add a manual engine hour reading
  python3 engine-hours.py service   # Record a service event

Config:
  export SIGNALK_URL="ws://localhost:3000/signalk/v1/stream?subscribe=self"
  export DB_PATH="$HOME/.local/share/shiplog/engine.db"

Maintenance schedule (edit below):
  OIL_CHANGE_HOURS = 100
  FILTER_CHANGE_HOURS = 200
  IMPELLER_HOURS = 500
  MAJOR_SERVICE_HOURS = 1000
"""

import sqlite3
import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", str(Path.home() / ".local" / "share" / "shiplog" / "engine.db"))
SIGNALK_URL = os.environ.get("SIGNALK_URL", "ws://localhost:3000/signalk/v1/stream?subscribe=self")

MAINTENANCE_SCHEDULE = {
    "oil_change": {"interval_hours": 100, "label": "Oil Change", "critical": True},
    "fuel_filter": {"interval_hours": 200, "label": "Fuel Filter Replacement", "critical": False},
    "impeller": {"interval_hours": 500, "label": "Raw Water Impeller", "critical": True},
    "transmission_fluid": {"interval_hours": 250, "label": "Transmission Fluid Change", "critical": False},
    "zinc_anodes": {"interval_hours": 100, "label": "Zinc Anode Inspection", "critical": False},
    "major_service": {"interval_hours": 1000, "label": "Major Engine Service", "critical": True},
    "injector_service": {"interval_hours": 1500, "label": "Injector Service/Cleaning", "critical": False},
    "valve_adjust": {"interval_hours": 800, "label": "Valve Clearance Adjustment", "critical": False},
}

RPM_THRESHOLD = 100  # above this = engine running

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS engine_state (
            id INTEGER PRIMARY KEY DEFAULT 1,
            total_hours REAL DEFAULT 0,
            last_rpm REAL DEFAULT 0,
            engine_running INTEGER DEFAULT 0,
            last_update TEXT,
            last_started TEXT,
            last_stopped TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS service_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT NOT NULL,
            performed_at_hours REAL NOT NULL,
            performed_at TEXT NOT NULL,
            notes TEXT
        )
    """)
    # Ensure state row exists
    conn.execute("INSERT OR IGNORE INTO engine_state (id) VALUES (1)")
    conn.commit()
    return conn

def get_state(conn):
    return conn.execute("SELECT * FROM engine_state WHERE id = 1").fetchone()

def cmd_track(args):
    """Daemon: listen to Signal K and accumulate engine hours."""
    try:
        import websocket
    except ImportError:
        print("Install websocket-client: pip install websocket-client")
        sys.exit(1)

    conn = get_db()
    state = get_state(conn)

    last_tick = time.time()
    accumulated_hours = state["total_hours"]
    was_running = False

    def on_message(ws, message):
        nonlocal last_tick, accumulated_hours, was_running
        try:
            data = json.loads(message)
            for update in data.get("updates", []):
                for v in update.get("values", []):
                    if v["path"] == "propulsion.main.revolutions":
                        rpm = v.get("value", 0) or 0
                        now = time.time()
                        dt = (now - last_tick) / 3600  # hours
                        is_running = rpm > RPM_THRESHOLD

                        if is_running:
                            accumulated_hours += dt

                        # Check for engine start/stop transitions
                        if is_running and not was_running:
                            print(f"[{datetime.now().isoformat()}] Engine STARTED (RPM: {rpm:.0f})")
                            conn.execute("UPDATE engine_state SET last_started = ? WHERE id = 1",
                                       (datetime.now(timezone.utc).isoformat(),))
                            conn.commit()
                        elif not is_running and was_running:
                            print(f"[{datetime.now().isoformat()}] Engine STOPPED. Total hours: {accumulated_hours:.2f}")
                            conn.execute("UPDATE engine_state SET last_stopped = ? WHERE id = 1",
                                       (datetime.now(timezone.utc).isoformat(),))

                        was_running = is_running
                        last_tick = now

                        # Update DB every minute
                        conn.execute("""
                            UPDATE engine_state
                            SET total_hours = ?, last_rpm = ?, engine_running = ?,
                                last_update = ?
                            WHERE id = 1
                        """, (accumulated_hours, rpm, int(is_running),
                              datetime.now(timezone.utc).isoformat()))
                        conn.commit()

                        # Check maintenance alerts
                        check_maintenance(conn, accumulated_hours)

        except (json.JSONDecodeError, KeyError):
            pass

    def on_open(ws):
        print(f"🔧 Engine hours tracker started. Current total: {accumulated_hours:.2f}h")
        print(f"   Listening to: {SIGNALK_URL}")
        print(f"   Maintenance intervals: {', '.join(f'{k}={v[\"interval_hours\"]}h' for k,v in MAINTENANCE_SCHEDULE.items())}")
        print()

    ws = websocket.WebSocketApp(SIGNALK_URL, on_open=on_open, on_message=on_message)
    ws.run_forever(reconnect=5)

def check_maintenance(conn, total_hours):
    """Check if any maintenance is due and print alerts."""
    for service_type, info in MAINTENANCE_SCHEDULE.items():
        last_service = conn.execute(
            "SELECT performed_at_hours FROM service_log WHERE service_type = ? ORDER BY id DESC LIMIT 1",
            (service_type,)
        ).fetchone()

        last_hours = last_service["performed_at_hours"] if last_service else 0
        hours_since = total_hours - last_hours
        hours_until = info["interval_hours"] - hours_since

        if hours_until <= 0:
            icon = "🚨" if info["critical"] else "⚠️"
            print(f"{icon} MAINTENANCE DUE: {info['label']} (overdue by {-hours_until:.1f}h)")

def cmd_status(args):
    """Show engine hours and maintenance status."""
    conn = get_db()
    state = get_state(conn)
    total = state["total_hours"]

    running = "🔴 RUNNING" if state["engine_running"] else "⚪ STOPPED"
    print(f"Engine Hours Tracker")
    print(f"  Status: {running}")
    print(f"  Total hours: {total:.2f}")
    print(f"  Current RPM: {state['last_rpm']:.0f}" if state["last_rpm"] else "  Current RPM: 0")
    if state["last_started"]:
        print(f"  Last started: {state['last_started'][:19]}")
    if state["last_stopped"]:
        print(f"  Last stopped: {state['last_stopped'][:19]}")
    print()

    print(f"Maintenance Schedule:")
    for service_type, info in MAINTENANCE_SCHEDULE.items():
        last_service = conn.execute(
            "SELECT performed_at_hours, performed_at FROM service_log "
            "WHERE service_type = ? ORDER BY id DESC LIMIT 1",
            (service_type,)
        ).fetchone()

        if last_service:
            last_hours = last_service["performed_at_hours"]
            last_date = last_service["performed_at"][:10]
            hours_since = total - last_hours
            hours_until = info["interval_hours"] - hours_since

            if hours_until <= 0:
                status = f"🚨 OVERDUE by {-hours_until:.1f}h"
            elif hours_until <= info["interval_hours"] * 0.1:
                status = f"⚠️  Due soon ({hours_until:.1f}h left)"
            else:
                status = f"✅ {hours_until:.1f}h remaining"
            print(f"  {info['label']:35} {status}  (last: {last_hours:.1f}h on {last_date})")
        else:
            hours_until = info["interval_hours"] - total
            if hours_until <= 0:
                print(f"  {info['label']:35} 🚨 NEVER SERVICED (overdue by {-hours_until:.1f}h)")
            else:
                print(f"  {info['label']:35} ⏳ {hours_until:.1f}h until first service")

    conn.close()

def cmd_log(args):
    """Manually set engine hours (for reconciling with physical hour meter)."""
    conn = get_db()
    conn.execute("UPDATE engine_state SET total_hours = ? WHERE id = 1", (args.hours,))
    conn.execute("UPDATE engine_state SET last_update = ? WHERE id = 1",
                (datetime.now(timezone.utc).isoformat(),))
    conn.commit()
    print(f"✅ Engine hours set to {args.hours:.2f}h")

def cmd_service(args):
    """Record a service event."""
    conn = get_db()
    state = get_state(conn)
    total_hours = state["total_hours"]

    if args.service_type not in MAINTENANCE_SCHEDULE:
        print(f"Unknown service type: {args.service_type}")
        print(f"Available: {', '.join(MAINTENANCE_SCHEDULE.keys())}")
        return

    conn.execute(
        "INSERT INTO service_log (service_type, performed_at_hours, performed_at, notes) VALUES (?, ?, ?, ?)",
        (args.service_type, args.hours or total_hours,
         datetime.now(timezone.utc).isoformat(), args.notes or "")
    )
    conn.commit()
    label = MAINTENANCE_SCHEDULE[args.service_type]["label"]
    print(f"✅ Service recorded: {label} at {args.hours or total_hours:.2f}h")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Engine Hours Tracker")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("track", help="Start tracking (daemon)")
    sub.add_parser("status", help="Show hours and maintenance")

    p_log = sub.add_parser("log", help="Set total engine hours")
    p_log.add_argument("hours", type=float, help="Total engine hours")

    p_svc = sub.add_parser("service", help="Record a service event")
    p_svc.add_argument("service_type", help=f"Type: {', '.join(MAINTENANCE_SCHEDULE.keys())}")
    p_svc.add_argument("--hours", type=float, default=None, help="Hours at service (default: current)")
    p_svc.add_argument("--notes", default="")

    args = parser.parse_args()
    if args.command == "track": cmd_track(args)
    elif args.command == "status": cmd_status(args)
    elif args.command == "log": cmd_log(args)
    elif args.command == "service": cmd_service(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
