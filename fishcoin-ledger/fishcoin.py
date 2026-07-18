#!/usr/bin/env python3
"""
FishCoin Ledger — Tokenized vessel economy

A lightweight incentive system for crew engagement.
Crew earn FishCoin (🐟) for data-entry tasks that benefit the vessel.
Coins are tracked in a local ledger and can be redeemed for perks.

Usage:
  fishcoin earn Casey "Logged all catches for the day" 50
  fishcoin spend Casey "Bought coffee ashore" -200
  fishcoin balance Casey
  fishcoin leaderboard
  fishcoin history Casey
  fishcoin distribute   # Auto-distribute based on today's activity
  fishcoin reset        # New season / new ledger

Config:
  LEDGER_PATH defaults to ~/.local/share/shiplog/fishcoin.json
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

LEDGER_PATH = os.environ.get(
    "FISHCOIN_LEDGER",
    str(Path.home() / ".local" / "share" / "shiplog" / "fishcoin.json"),
)

# ── Rewards Table ────────────────────────────────────────
REWARDS = {
    "log_entry":       {"amount": 5,   "desc": "Log entry created"},
    "catch_report":    {"amount": 15,  "desc": "Catch logged with species + weight"},
    "maintenance":     {"amount": 25,  "desc": "Maintenance task completed"},
    "fuel_log":        {"amount": 10,  "desc": "Fuel entry logged"},
    "trip_plan":       {"amount": 20,  "desc": "Trip planned with waypoints"},
    "safety_check":    {"amount": 15,  "desc": "Pre-departure checklist completed"},
    "night_watch":     {"amount": 10,  "desc": "Night watch log entry"},
    "dawn_patrol":     {"amount": 10,  "desc": "Entry before 6 AM"},
    "streak_3":        {"amount": 50,  "desc": "3-day streak bonus"},
    "streak_7":        {"amount": 100, "desc": "7-day streak bonus"},
    "streak_30":       {"amount": 300, "desc": "30-day streak bonus"},
    "data_quality":    {"amount": 20,  "desc": "Entry with GPS coordinates + photo"},
    "first_of_season": {"amount": 100, "desc": "First catch of a new species this season"},
}

# ── Perks (redemption catalog) ───────────────────────────
PERKS = {
    "coffee":        {"cost": 200,  "desc": "Coffee ashore"},
    "beer":          {"cost": 150,  "desc": "Beer after shift"},
    "shower_first":  {"cost": 100,  "desc": "First shower at port"},
    "bunk_pick":     {"cost": 300,  "desc": "Pick your bunk next trip"},
    "shore_leave":   {"cost": 500,  "desc": "Extra hour shore leave"},
    "meal_pick":     {"cost": 50,   "desc": "Pick tonight's dinner"},
    "music_pick":    {"cost": 75,   "desc": "Pick the wheelhouse music"},
    "legend_status": {"cost": 2000, "desc": "Crew Legend title for the season"},
}


def load_ledger():
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH) as f:
            return json.load(f)
    return {"crew": {}, "history": [], "season": datetime.now(timezone.utc).year}


def save_ledger(data):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_balance(ledger, name):
    if name not in ledger["crew"]:
        ledger["crew"][name] = {"balance": 0, "earned_total": 0, "spent_total": 0}
    return ledger["crew"][name]


def cmd_earn(args):
    ledger = load_ledger()
    crew = get_balance(ledger, args.name)

    crew["balance"] += args.amount
    crew["earned_total"] = crew.get("earned_total", 0) + args.amount

    ledger["history"].append({
        "name": args.name,
        "type": "earn",
        "amount": args.amount,
        "reason": args.reason,
        "ts": time.time(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    })

    save_ledger(ledger)

    fish = "🐟" * min(5, max(1, args.amount // 10))
    print(f"{fish} {args.name} earned {args.amount} FishCoin")
    print(f"   Reason: {args.reason}")
    print(f"   Balance: {crew['balance']} 🐟")


def cmd_spend(args):
    ledger = load_ledger()
    crew = get_balance(ledger, args.name)

    if crew["balance"] < args.amount:
        print(f"❌ Insufficient balance. {args.name} has {crew['balance']} 🐟, needs {args.amount}.")
        return

    crew["balance"] -= args.amount
    crew["spent_total"] = crew.get("spent_total", 0) + args.amount

    ledger["history"].append({
        "name": args.name,
        "type": "spend",
        "amount": -args.amount,
        "reason": args.reason,
        "ts": time.time(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    })

    save_ledger(ledger)
    print(f"💰 {args.name} spent {args.amount} FishCoin")
    print(f"   Reason: {args.reason}")
    print(f"   Balance: {crew['balance']} 🐟")


def cmd_balance(args):
    ledger = load_ledger()
    crew = get_balance(ledger, args.name)

    print(f"🐟 FishCoin Balance: {args.name}")
    print(f"   Current: {crew['balance']}")
    print(f"   Total earned: {crew.get('earned_total', 0)}")
    print(f"   Total spent: {crew.get('spent_total', 0)}")


def cmd_leaderboard(args):
    ledger = load_ledger()

    if not ledger["crew"]:
        print("No FishCoin transactions yet.")
        return

    sorted_crew = sorted(
        ledger["crew"].items(),
        key=lambda x: x[1].get("earned_total", 0),
        reverse=True
    )

    print(f"🏆 FishCoin Leaderboard — Season {ledger['season']}")
    print(f"{'Rank':<6}{'Crew':<20}{'Balance':<12}{'Earned':<12}{'Spent':<10}")
    print("─" * 60)

    medals = ["🥇", "🥈", "🥉"]
    for i, (name, data) in enumerate(sorted_crew):
        medal = medals[i] if i < 3 else f"{i+1}."
        print(f"{medal:<6}{name:<20}{data['balance']:<12}{data.get('earned_total', 0):<12}{data.get('spent_total', 0):<10}")


def cmd_history(args):
    ledger = load_ledger()

    history = [h for h in ledger["history"] if h["name"] == args.name]
    if not history:
        print(f"No transactions for {args.name}.")
        return

    print(f"📜 FishCoin History: {args.name}\n")

    balance = 0
    for h in history[-20:]:
        date = h.get("date", "????")
        if h["type"] == "earn":
            balance += h["amount"]
            sign = "+"
            icon = "🐟"
        else:
            balance += h["amount"]
            sign = ""
            icon = "💰"
        print(f"  {date} {icon} {sign}{abs(h['amount']):>5}  {h['reason'][:40]:<40}  Balance: {balance}")


def cmd_perks(args):
    print("🛒 FishCoin Perk Catalog\n")
    for key, perk in sorted(PERKS.items(), key=lambda x: x[1]["cost"]):
        print(f"  {perk['cost']:>5} 🐟  {perk['desc']}")
    print(f"\nRedeem: fishcoin spend <name> \"{args.name if hasattr(args,'name') else 'perk'}\" <amount>")


def cmd_rewards(args):
    print("💰 FishCoin Reward Table\n")
    print(f"{'Action':<25}{'Reward':<10}{'Description'}")
    print("─" * 60)
    for key, reward in sorted(REWARDS.items(), key=lambda x: -x[1]["amount"]):
        print(f"  {key:<25}{reward['amount']:>4} 🐟   {reward['desc']}")


def cmd_distribute(args):
    """Auto-distribute FishCoin based on today's ship-log activity."""
    ledger = load_ledger()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Load log entries from offline-sync DB
    db_path = os.environ.get(
        "DB_PATH",
        str(Path.home() / ".local" / "share" / "shiplog" / "local.db"),
    )

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        entries = conn.execute(
            "SELECT * FROM logs WHERE date(timestamp) = ? ORDER BY timestamp",
            (today,)
        ).fetchall()
        conn.close()
    except Exception:
        entries = []

    if not entries:
        print(f"No log entries for {today}. Nothing to distribute.")
        return

    distributions = {}
    for entry in entries:
        # Extract author from metadata or default to "Captain"
        meta = json.loads(entry["metadata"] or "{}")
        author = meta.get("author", "Captain")
        category = entry["category"] or "observation"

        # Determine reward
        reward_key = "log_entry"
        if category == "catch":
            reward_key = "catch_report"
        elif category == "maintenance":
            reward_key = "maintenance"
        elif category == "navigation":
            reward_key = "log_entry"

        reward = REWARDS.get(reward_key, REWARDS["log_entry"])
        distributions[author] = distributions.get(author, 0) + reward["amount"]

    total = 0
    for name, amount in distributions.items():
        crew = get_balance(ledger, name)
        crew["balance"] += amount
        crew["earned_total"] = crew.get("earned_total", 0) + amount
        ledger["history"].append({
            "name": name,
            "type": "earn",
            "amount": amount,
            "reason": f"Auto-distribution for {today} activity",
            "ts": time.time(),
            "date": today,
        })
        total += amount
        print(f"🐟 {name}: +{amount} FishCoin")

    save_ledger(ledger)
    print(f"\nTotal distributed: {total} 🐟 to {len(distributions)} crew member(s)")


def cmd_reset(args):
    if not args.confirm:
        print("⚠ This will reset all FishCoin balances. Pass --confirm to proceed.")
        return

    ledger = load_ledger()
    old_season = ledger["season"]

    # Archive
    archive_path = LEDGER_PATH.replace(".json", f"_season_{old_season}.json")
    with open(archive_path, "w") as f:
        json.dump(ledger, f, indent=2)

    ledger = {"crew": {}, "history": [], "season": datetime.now(timezone.utc).year}
    save_ledger(ledger)

    print(f"✅ New season started. Previous season ({old_season}) archived to {archive_path}")


def main():
    parser = argparse.ArgumentParser(description="🐟 FishCoin — Vessel Crew Economy")
    sub = parser.add_subparsers(dest="command")

    p_earn = sub.add_parser("earn", help="Award FishCoin")
    p_earn.add_argument("name")
    p_earn.add_argument("reason")
    p_earn.add_argument("amount", type=int)

    p_spend = sub.add_parser("spend", help="Spend FishCoin")
    p_spend.add_argument("name")
    p_spend.add_argument("reason")
    p_spend.add_argument("amount", type=int)

    p_bal = sub.add_parser("balance", help="Check balance")
    p_bal.add_argument("name")

    sub.add_parser("leaderboard", help="Crew leaderboard")
    sub.add_parser("perks", help="View perk catalog")
    sub.add_parser("rewards", help="View reward table")
    sub.add_parser("distribute", help="Auto-distribute based on today's logs")

    p_hist = sub.add_parser("history", help="Transaction history")
    p_hist.add_argument("name")

    p_reset = sub.add_parser("reset", help="Start new season")
    p_reset.add_argument("--confirm", action="store_true")

    args = parser.parse_args()

    if args.command == "earn": cmd_earn(args)
    elif args.command == "spend": cmd_spend(args)
    elif args.command == "balance": cmd_balance(args)
    elif args.command == "leaderboard": cmd_leaderboard(args)
    elif args.command == "perks": cmd_perks(args)
    elif args.command == "rewards": cmd_rewards(args)
    elif args.command == "distribute": cmd_distribute(args)
    elif args.command == "history": cmd_history(args)
    elif args.command == "reset": cmd_reset(args)
    else: parser.print_help()


if __name__ == "__main__":
    main()
