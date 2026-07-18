# AIS Contact Tracker Module

Tracks nearby vessels via AIS (Signal K WebSocket) and logs contact/departure events to ship-log-search.

## Files

| File | Description |
|------|-------------|
| `ais-tracker.py` | AIS tracker — connects to Signal K, monitors vessels, logs events |
| `ais-simulator.py` | Fake AIS data generator for testing without hardware |

## Architecture

```
AIS Receiver  ──ws──>  ais-tracker.py  ──http──>  ship-log-search API
                                          ──ws──>  Oracle Relay
                            ↑
                      ais-simulator.py  (for dev)
```

## Configuration

The tracker accepts config via (in priority order): CLI args > env vars > JSON file > defaults.

### Config file (`config.json`)

```json
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
```

### Environment variables

- `AIS_SIGNALK_URL` — Signal K WebSocket URL
- `AIS_ORACLE_RELAY` — Oracle Relay URL
- `AIS_LOG_API` — Ship-log-search API URL
- `AIS_OUR_LAT`, `AIS_OUR_LON` — vessel position
- `AIS_CONTACT_RADIUS` — contact threshold in metres
- `AIS_DEPARTURE_RADIUS` — departure threshold in metres
- `AIS_CACHE_FILE` — vessel cache path

### CLI flags

```
--signal-k-url, --oracle-relay-url, --log-api-url,
--our-lat, --our-lon, --contact-radius, --departure-radius, --cache-file
```

## Usage

```bash
# Start the simulator (for testing without hardware)
python3 ais-simulator.py --port 9099 --vessels 5

# Start the tracker (connect to real AIS)
python3 ais-tracker.py

# Connect tracker to simulator (for dev)
python3 ais-tracker.py \
  --signal-k-url ws://localhost:9099 \
  --log-api-url http://localhost:8080/api/log
```

## Event Types

Tracker emits two event types:

### Contact (`ais-contact`)
Triggered when a vessel comes within `contact_radius_m` (default 500m) of our position.
Includes vessel name, MMSI, position, distance, speed, course.

### Departure (`ais-departure`)
Triggered when a vessel that was within range moves beyond `departure_radius_m` (default 1km).
Includes last known position and distance.

Both events are sent to:
1. `ship-log-search` API (`POST /api/log`)
2. `Oracle Relay` WebSocket (for real-time notifications)
