#!/usr/bin/env python3
"""
weather-feed.py — Weather feed module for ship-log-search

Fetches NOAA marine weather forecasts and NDBC buoy data,
logs current conditions as 'weather' entries and active marine
alerts as 'weather_alert' entries to the ship-log-search API.

Usage:
  python3 weather-feed.py                          One-shot (cron-friendly)
  python3 weather-feed.py --daemon                 Continuous runner
  python3 weather-feed.py --dry-run                Preview without sending
  python3 weather-feed.py --lat 57.05 --lon -135.33

Environment variables:
  SHIP_LOG_API_URL   — ship-log-search base URL     (default: http://localhost:8080)
  SHIP_LOG_KEY       — API key (X-Log-Key header)   (default: '')
  WEATHER_LAT        — Latitude                     (default: 57.053)
  WEATHER_LON        — Longitude                    (default: -135.33)
  WEATHER_INTERVAL   — Check interval in hours      (default: 6)
  NDBC_STATION_ID    — NDBC buoy station ID         (default: 46083)
"""

import json
import os
import sys
import argparse
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Constants ────────────────────────────────────────────────────────────────

USER_AGENT = 'ShipLogWeatherFeed/1.0 (ship-log-search)'
NWS_API_BASE = 'https://api.weather.gov'

DEFAULT_LAT = 57.053
DEFAULT_LON = -135.33
DEFAULT_INTERVAL = 6  # hours
DEFAULT_NDBC_STATION = '46083'  # Sitka, AK buoy

# ── Helpers ──────────────────────────────────────────────────────────────────


def fetch_json(url, timeout=15):
    """Fetch and decode JSON from a URL with proper headers."""
    req = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_text(url, timeout=10):
    """Fetch plain text from a URL."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8')


def timestamp_now():
    """Return current UTC time as ISO 8601."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def timestamp_human():
    """Return current UTC time as human-readable string."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


# ── NWS API ──────────────────────────────────────────────────────────────────


def get_nws_points(lat, lon):
    """
    Fetch NWS /points/{lat},{lon} and extract relevant URLs.

    Returns a dict with forecast URLs, zone info, and location name,
    or None if the coordinates are outside NWS coverage (404).
    """
    url = f'{NWS_API_BASE}/points/{lat},{lon}'
    try:
        data = fetch_json(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f'  [WARN] No NWS points data for {lat},{lon} — '
                  'coordinates may be outside US waters')
            return None
        raise

    props = data['properties']
    rel = props.get('relativeLocation', {}).get('properties', {})
    city = rel.get('city', '')
    state = rel.get('state', '')
    location_name = ', '.join(filter(None, [city, state])) or f'{lat}, {lon}'

    return {
        'forecast':         props.get('forecast'),
        'forecast_hourly':  props.get('forecastHourly'),
        'forecast_grid':    props.get('forecastGridData'),
        'marine_forecast':  props.get('marineForecast'),
        'forecast_zone':    props.get('forecastZone'),
        'marine_zone':      props.get('marineZone'),
        'maritime_zone':    props.get('maritimeZone'),
        'cwa':              props.get('cwa'),
        'location_name':    location_name,
        'city':             city,
        'state':            state,
    }


def get_forecast_periods(forecast_url):
    """
    Fetch forecast periods from any NWS forecast URL
    (land zone, marine zone, hourly, etc.).

    Returns a list of period dicts, or empty list on failure.
    """
    if not forecast_url:
        return []
    try:
        data = fetch_json(forecast_url)
        return data.get('properties', {}).get('periods', [])
    except Exception as e:
        print(f'  [WARN] Forecast fetch failed ({forecast_url}): {e}')
        return []


def format_period(period):
    """Format a single forecast period into a readable summary line."""
    name = period.get('name', '')
    temp = period.get('temperature', '?')
    unit = period.get('temperatureUnit', 'F')
    wind = period.get('windSpeed', '') or ''
    wind_dir = period.get('windDirection', '') or ''
    detail = period.get('detailedForecast', period.get('shortForecast', ''))

    parts = [f'{name}: {temp}°{unit}']
    if wind_dir and wind:
        parts.append(f'Wind {wind_dir} {wind}')
    elif wind:
        parts.append(f'Wind {wind}')

    # Include the short forecast — often contains wave/wind info
    short = period.get('shortForecast', '')
    if short:
        parts.append(short)

    # Only include detailed forecast if it's concise
    if detail and len(detail) < 250 and detail != short:
        parts.append(f'({detail})')

    return ' | '.join(parts)


def get_active_alerts(lat, lon):
    """Fetch active NWS alerts for a point."""
    url = f'{NWS_API_BASE}/alerts/active?point={lat},{lon}'
    try:
        data = fetch_json(url)
    except Exception as e:
        print(f'  [WARN] Failed to fetch alerts: {e}')
        return []
    return [a['properties'] for a in data.get('features', [])]


def is_marine_advisory(alert):
    """Return True if the alert is a marine hazard (small craft, gale, etc.)."""
    event = alert.get('event', '').lower()
    keywords = [
        'small craft', 'gale', 'storm warning', 'hazardous seas',
        'heavy freezing spray', 'marine', 'seas',
    ]
    return any(kw in event for kw in keywords)


# ── NDBC Buoy Data ───────────────────────────────────────────────────────────


def get_ndbc_data(station_id):
    """
    Fetch and parse NDBC buoy real-time data.
    Returns the latest observation as a dict, or None on failure.
    """
    url = f'https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt'
    try:
        text = fetch_text(url)
        return _parse_ndbc(text)
    except Exception as e:
        print(f'  [WARN] NDBC station {station_id} unavailable: {e}')
        return None


def _parse_ndbc(text):
    """
    Parse NDBC standard meteorological data format.

    Lines are space-delimited.  'MM' marks missing values.
    Line 1 = column headers (e.g. YY MM DD hh mm WDIR WSPD …)
    Line 2 = units comment (skip — e.g. yr mo dy hr mn degT m/s …)
    Line 3+ = data rows, most recent first.
    """
    lines = text.strip().split('\n')
    if len(lines) < 3:
        return None

    # Line 1: column names
    headers = lines[0].strip().split()
    # Line 3: most recent data row (skip line 2 == units)
    data = lines[2].strip().split()

    if len(headers) != len(data):
        return None

    result = {}
    for h, v in zip(headers, data):
        h = h.lstrip('#')  # first header may start with #YY
        try:
            if v == 'MM':
                result[h] = None
            elif '.' in v:
                result[h] = float(v)
            else:
                result[h] = int(v)
        except (ValueError, IndexError):
            result[h] = v
    return result


def format_ndbc(ndbc):
    """Format NDBC buoy readings into a readable string."""
    if not ndbc:
        return ''

    parts = ['📡 NDBC Buoy:']
    m = ndbc  # shorthand

    if m.get('WDIR') is not None:
        parts.append(f'Wind Dir: {m["WDIR"]}°')
    if m.get('WSPD') is not None:
        parts.append(f'Wind: {m["WSPD"]} m/s')
    if m.get('GST') is not None:
        parts.append(f'Gust: {m["GST"]} m/s')
    if m.get('WVHT') is not None:
        parts.append(f'Waves: {m["WVHT"]} m')
    if m.get('DPD') is not None:
        parts.append(f'Period: {m["DPD"]} s')
    if m.get('PRES') is not None:
        parts.append(f'Pressure: {m["PRES"]} mb')
    if m.get('ATMP') is not None:
        parts.append(f'Air: {m["ATMP"]}°C')
    if m.get('WTMP') is not None:
        parts.append(f'Water: {m["WTMP"]}°C')

    return ' | '.join(parts)


# ── Ship-log-search API ──────────────────────────────────────────────────────


def send_entry(entry, api_url, api_key, dry_run=False):
    """
    POST a log entry to the ship-log-search API.

    Returns parsed response on success, None on failure.
    """
    if dry_run:
        print(f'  [DRY-RUN] Would POST: {json.dumps(entry, indent=2)}')
        return True

    url = f'{api_url.rstrip("/")}/api/log'
    body = json.dumps(entry).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': 'application/json',
        'X-Log-Key': api_key,
        'User-Agent': USER_AGENT,
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f'  [ERROR] API HTTP {e.code}: {err_body}')
        return None
    except urllib.error.URLError as e:
        print(f'  [ERROR] API unreachable: {e.reason}')
        return None


# ── Entry builders ───────────────────────────────────────────────────────────


def build_weather_entry(urls, periods, ndbc, alerts, lat, lon):
    """
    Build a 'weather' category entry from of all fetched data.
    """
    now = timestamp_human()
    loc = urls.get('location_name', f'{lat}, {lon}') if urls else f'{lat}, {lon}'

    # Determine which forecast source we used
    source_tag = 'marine' if (urls and urls.get('marine_forecast')) else 'land'

    lines = [f'🌤 Weather Report — {loc} — {now}']

    # ── Current conditions ──
    current = periods[0] if periods else None
    if current:
        lines.append(f'\n📍 Current:')
        lines.append(f'   {format_period(current)}')

    # ── Next period ──
    if len(periods) > 1:
        lines.append(f'\n🔮 Next:')
        for p in periods[1:3]:  # show next two periods
            lines.append(f'   {format_period(p)}')

    # ── Extended outlook ──
    if len(periods) > 3:
        lines.append(f'\n📋 Extended forecast:')
        for p in periods[3:6]:
            name = p.get('name', '')
            temp = p.get('temperature', '?')
            unit = p.get('temperatureUnit', 'F')
            short = p.get('shortForecast', '')
            wind = p.get('windSpeed', '')
            wdir = p.get('windDirection', '')
            lines.append(f'   • {name}: {temp}°{unit}, {short}, {wdir} {wind}')

    # Show forecast source
    lines.append(f'\n   (Source: NWS {source_tag} forecast)')

    # ── NDBC buoy ―───────────────────────────────────────────────────────────
    if ndbc:
        ndbc_str = format_ndbc(ndbc)
        if ndbc_str:
            lines.append(f'\n{ndbc_str}')

    # ── Marine alerts ──
    marine = [a for a in alerts if is_marine_advisory(a)]
    if marine:
        lines.append('')
        for a in marine:
            event = a.get('event', 'Unknown Alert')
            sev = a.get('severity', '')
            headline = a.get('headline', '')
            lines.append(f'⚠️  ⚠️ MARINE ALERT: {event} ({sev})')
            if headline:
                lines.append(f'   {headline}')

    # ── Other alerts (brief) ──
    other = [a for a in alerts if not is_marine_advisory(a)]
    if other:
        for a in other[:3]:
            event = a.get('event', 'Unknown')
            sev = a.get('severity', '')
            lines.append(f'\n⚠️  Weather Alert: {event} ({sev})')

    return {
        'text': '\n'.join(lines),
        'category': 'weather',
        'lat': lat,
        'lon': lon,
        'location_name': loc,
    }


def build_alert_entry(alert, lat, lon, location):
    """Build a 'weather_alert' category entry for an active marine alert."""
    event = alert.get('event', 'Unknown Warning')
    severity = alert.get('severity', '')
    headline = alert.get('headline', event)
    description = alert.get('description', '')
    instruction = alert.get('instruction', '')
    expires = alert.get('expires', '')

    lines = [
        f'🚨 WEATHER ALERT: {event}',
        f'Severity: {severity}',
        f'{headline}',
    ]

    if description:
        # Keep description manageable
        desc = description[:800]
        if len(description) > 800:
            desc += '\n[... truncated]'
        lines.append(f'\n{desc}')

    if instruction:
        lines.append(f'\nInstructions: {instruction}')

    if expires:
        lines.append(f'\nExpires: {expires}')

    return {
        'text': '\n'.join(lines),
        'category': 'weather_alert',
        'lat': lat,
        'lon': lon,
        'location_name': location,
    }


# ── Main cycle ───────────────────────────────────────────────────────────────


def run_cycle(lat, lon, api_url, api_key, ndbc_station, dry_run=False, verbose=False):
    """
    Execute one complete weather check / log cycle:

      1. Fetch NWS /points/ metadata
      2. Fetch marine (preferred) or land-zone forecast
      3. Fetch NDBC buoy data as fallback augmentation
      4. Check for active alerts
      5. Build and send 'weather' entry
      6. If marine alerts active, send 'weather_alert' entries
    """
    now = timestamp_human()
    loc_display = f'{lat}, {lon}'
    print(f'  ─── Cycle @ {now} ───')

    # ── Step 1: NWS points ──
    print(f'  [1/6] NWS /points/…')
    urls = get_nws_points(lat, lon)

    periods = []
    source_label = 'N/A'

    if urls:
        loc_display = urls.get('location_name', loc_display)

        # ── Step 2: Forecast ──
        # Prefer marine forecast for coastal/marine positions
        if urls.get('marine_forecast'):
            print(f'  [2/6] Marine forecast…')
            periods = get_forecast_periods(urls['marine_forecast'])
            source_label = 'marine'

        if not periods and urls.get('forecast'):
            print(f'  [2/6] Land-zone forecast…')
            periods = get_forecast_periods(urls['forecast'])
            source_label = 'land'

        if not periods and urls.get('forecast_hourly'):
            print(f'  [2/6] Hourly forecast (sampled)…')
            hly = get_forecast_periods(urls['forecast_hourly'])
            if hly:
                # Sample every 3 hours for next 12 hours
                periods = [hly[i] for i in range(0, min(len(hly), 12), 3)]
                for i, p in enumerate(periods):
                    p['name'] = f'+{i * 3}h'
                source_label = 'hourly'
    else:
        print(f'  [1/6] No NWS coverage — using NDBC only')

    n_periods = len(periods)
    print(f'         Got {n_periods} forecast periods ({source_label})')

    # ── Step 3: NDBC buoy ──
    print(f'  [3/6] NDBC station {ndbc_station}…')
    ndbc = get_ndbc_data(ndbc_station)
    if ndbc:
        print(f'         OK — {format_ndbc(ndbc)}')
    else:
        print(f'         Unavailable')

    # ── Step 4: Alerts ──
    print(f'  [4/6] Active alerts…')
    alerts = get_active_alerts(lat, lon)
    n_marine = sum(1 for a in alerts if is_marine_advisory(a))
    print(f'         {len(alerts)} total, {n_marine} marine advisory')

    # ── Step 5: Weather log entry ──
    print(f'  [5/6] Sending weather entry…')
    entry = build_weather_entry(urls, periods, ndbc, alerts, lat, lon)
    result = send_entry(entry, api_url, api_key, dry_run)
    if result:
        print(f'  ✅  Weather entry logged')
    else:
        print(f'  ❌  Weather entry FAILED')

    # ── Step 6: Alert log entries ──
    marine_alerts = [a for a in alerts if is_marine_advisory(a)]
    if marine_alerts:
        print(f'  [6/6] Logging {len(marine_alerts)} marine alert(s)…')
    for a in marine_alerts:
        alert_entry = build_alert_entry(a, lat, lon, loc_display)
        evt = a.get('event', 'Unknown')
        result = send_entry(alert_entry, api_url, api_key, dry_run)
        status = '✅' if result else '❌'
        print(f'  {status}  Alert: {evt}')

    if not marine_alerts:
        print(f'  [6/6] No marine alerts to log')

    print()

    return periods, ndbc, alerts


# ── CLI ──────────────────────────────────────────────────────────────────────


def parse_args(argv=None):
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description='Weather feed module for ship-log-search',
    )

    p.add_argument('--daemon', action='store_true',
                   help='Run continuously in a loop')
    p.add_argument('--dry-run', action='store_true',
                   help='Preview entries without sending')
    p.add_argument('--verbose', '-v', action='store_true',
                   help='Show extra detail')

    # Position
    default_lat = float(os.environ.get('WEATHER_LAT', DEFAULT_LAT))
    default_lon = float(os.environ.get('WEATHER_LON', DEFAULT_LON))
    p.add_argument('--lat', type=float, default=default_lat,
                   help=f'Latitude (default: {default_lat})')
    p.add_argument('--lon', type=float, default=default_lon,
                   help=f'Longitude (default: {default_lon})')

    # Interval
    default_int = float(os.environ.get('WEATHER_INTERVAL', DEFAULT_INTERVAL))
    p.add_argument('--interval', type=float, default=default_int,
                   help=f'Check interval in hours (default: {default_int})')

    # NDBC
    default_ndbc = os.environ.get('NDBC_STATION_ID', DEFAULT_NDBC_STATION)
    p.add_argument('--ndbc-station', type=str, default=default_ndbc,
                   help=f'NDBC station ID (default: {default_ndbc})')

    # API
    default_api_url = os.environ.get('SHIP_LOG_API_URL',
                                      'http://localhost:8080')
    p.add_argument('--api-url', type=str, default=default_api_url,
                   help=f'API base URL (default: {default_api_url})')
    p.add_argument('--api-key', type=str,
                   default=os.environ.get('SHIP_LOG_KEY', ''),
                   help='API key (X-Log-Key header)')

    return p.parse_args(argv)


def main():
    args = parse_args()

    banner = f'''
{'=' * 64}
  Ship Log — Weather Feed
  Position:   {args.lat}, {args.lon}
  API:        {args.api_url}
  NDBC:       {args.ndbc_station}
  Interval:   {args.interval}h
  Mode:       {'daemon' if args.daemon else 'one-shot'}
              {'DRY RUN' if args.dry_run else 'live'}
{'=' * 64}
'''
    print(banner.strip())

    kwargs = {
        'lat': args.lat,
        'lon': args.lon,
        'api_url': args.api_url,
        'api_key': args.api_key,
        'ndbc_station': args.ndbc_station,
        'dry_run': args.dry_run,
        'verbose': args.verbose,
    }

    if args.daemon:
        print(f'Entering daemon loop (every {args.interval}h)…\n')
        while True:
            run_cycle(**kwargs)
            print(f'Sleeping {args.interval} hour(s)…\n')
            time.sleep(args.interval * 3600)
    else:
        run_cycle(**kwargs)


if __name__ == '__main__':
    main()
