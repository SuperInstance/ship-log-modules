#!/usr/bin/env python3
"""
Ship Log Export — CSV/TSV export of log entries.

Usage:
  python3 export.py --from 2026-07-01 --to 2026-07-31
  python3 export.py --all
  python3 export.py --category catch
  python3 export.py --format tsv

Config:
  export SHIPLOG_URL="https://ship-log-search.casey-digennaro.workers.dev"
"""

import csv
import json
import os
import sys
import argparse
import urllib.request
from datetime import datetime

SHIPLOG_URL = os.environ.get("SHIPLOG_URL", "https://ship-log-search.casey-digennaro.workers.dev")

def fetch_entries(from_date=None, to_date=None, category=None, limit=500):
    params = [f"k={limit}"]
    if from_date: params.append(f"from={from_date}T00:00:00Z")
    if to_date: params.append(f"to={to_date}T23:59:59Z")
    if category: params.append(f"category={category}")
    url = f"{SHIPLOG_URL}/api/timeline?" + "&".join(params)
    
    print(f"Fetching: {url}", file=sys.stderr)
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    return data.get("results", [])

def export(entries, fmt="csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    ext = "csv" if fmt == "csv" else "tsv"
    filename = f"shiplog_export_{timestamp}.{ext}"
    
    fieldnames = ["date", "time", "category", "text", "lat", "lon", "location_name", "id"]
    delimiter = "," if fmt == "csv" else "\t"
    
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        for entry in entries:
            m = entry.get("metadata", {})
            ts = m.get("timestamp", "")
            date_part = ts[:10] if ts else ""
            time_part = ts[11:19] if ts else ""
            writer.writerow({
                "date": date_part,
                "time": time_part,
                "category": m.get("category", ""),
                "text": m.get("text", ""),
                "lat": m.get("lat", ""),
                "lon": m.get("lon", ""),
                "location_name": m.get("location_name", ""),
                "id": entry.get("id", ""),
            })
    
    print(f"✅ Exported {len(entries)} entries to {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Export ship log entries")
    parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--category", "-c", choices=["catch", "maintenance", "weather", "observation", "navigation"])
    parser.add_argument("--all", action="store_true", help="Export all entries")
    parser.add_argument("--format", "-f", choices=["csv", "tsv"], default="csv")
    parser.add_argument("--limit", "-n", type=int, default=500)
    parser.add_argument("--output", "-o", default=None, help="Output filename")
    
    args = parser.parse_args()
    
    entries = fetch_entries(
        from_date=args.from_date,
        to_date=args.to_date,
        category=args.category,
        limit=args.limit,
    )
    
    if not entries:
        print("No entries found matching filters.")
        return
    
    filename = export(entries, args.format)
    if args.output:
        os.rename(filename, args.output)
        print(f"   Renamed to: {args.output}")

if __name__ == "__main__":
    main()
