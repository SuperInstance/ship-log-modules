#!/usr/bin/env python3
"""
Ship Log Module Installer

Browse, install, and manage ship-log-search modules.

Usage:
  shiplog install <module-name>   # Install a module
  shiplog modules                 # List installed modules
  shiplog search <query>          # Search available modules
  shiplog remove <module-name>    # Remove a module
  shiplog registry                # List all available modules
  shiplog info <module-name>      # Show module details

Config:
  export SHIPLOG_MODULES_DIR="$HOME/.local/share/shiplog/modules"
  export MODULE_REGISTRY="https://module-registry.casey-digennaro.workers.dev"
"""

import json
import os
import sys
import argparse
import urllib.request
from pathlib import Path

MODULES_DIR = Path(os.environ.get("SHIPLOG_MODULES_DIR", str(Path.home() / ".local" / "share" / "shiplog" / "modules")))
REGISTRY_URL = os.environ.get("MODULE_REGISTRY", "https://module-registry.casey-digennaro.workers.dev")

def fetch_registry(query=None, mtype=None):
    params = []
    if query: params.append(f"q={query}")
    if mtype: params.append(f"type={mtype}")
    url = f"{REGISTRY_URL}/api/modules?" + "&".join(params)
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()).get("modules", [])

def fetch_module(name):
    url = f"{REGISTRY_URL}/api/modules/{name}"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()).get("module", {})

def download_file(repo, path, filename):
    """Download a file from GitHub raw."""
    url = f"https://raw.githubusercontent.com/{repo}/main{path}{filename}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode()
    except Exception as e:
        print(f"  ⚠ Failed to download {filename}: {e}")
        return None

def cmd_install(args):
    """Install a module from the registry."""
    mod = fetch_module(args.name)
    if not mod:
        print(f"Module '{args.name}' not found in registry.")
        return

    if mod.get("status") == "planned":
        print(f"⚠ Module '{mod['name']}' is planned but not yet built.")
        print(f"   Description: {mod.get('description', '')}")
        return

    print(f"Installing: {mod['name']} v{mod.get('version', '0.1.0')}")
    print(f"  Type: {mod.get('type', 'widget')}")
    print(f"  Description: {mod.get('description', '')}")

    # Create module directory
    mod_dir = MODULES_DIR / mod["name"]
    mod_dir.mkdir(parents=True, exist_ok=True)

    # Write module manifest
    manifest = {
        "name": mod["name"],
        "type": mod.get("type", "widget"),
        "version": mod.get("version", "0.1.0"),
        "installed_at": str(Path().resolve()),
        "source": mod.get("repo", ""),
    }
    (mod_dir / "module.json").write_text(json.dumps(manifest, indent=2))

    # Download files based on module type
    repo = mod.get("repo", "")
    path = mod.get("path", "/")

    if mod.get("type") == "widget":
        # Download index.html
        html = download_file(repo, path, "index.html")
        if html:
            (mod_dir / "index.html").write_text(html)
            print(f"  ✅ Downloaded index.html ({len(html)} bytes)")
    elif mod.get("type") in ("data-source", "export", "integration"):
        # Try to download the main script
        script_name = f"{mod['name'].replace('-', '_')}.py"
        for candidate in [script_name, f"{mod['name']}.py", "main.py"]:
            code = download_file(repo, path, candidate)
            if code:
                (mod_dir / candidate).write_text(code)
                print(f"  ✅ Downloaded {candidate} ({len(code)} bytes)")
                break

    # Try README
    readme = download_file(repo, path, "README.md")
    if readme:
        (mod_dir / "README.md").write_text(readme)

    print(f"\n✅ Installed {mod['name']} to {mod_dir}")
    print(f"   Open {mod_dir} to use it.")

    if mod.get("type") == "widget":
        print(f"   Widget: open {mod_dir / 'index.html'} in a browser")
    elif mod.get("type") == "data-source":
        print(f"   Script: python3 {mod_dir}/*.py")

def cmd_modules(args):
    """List installed modules."""
    if not MODULES_DIR.exists():
        print("No modules installed. Use 'shiplog install <name>' to add one.")
        return

    installed = []
    for d in sorted(MODULES_DIR.iterdir()):
        manifest = d / "module.json"
        if manifest.exists():
            data = json.loads(manifest.read_text())
            installed.append(data)

    if not installed:
        print("No modules installed.")
        return

    print(f"Installed modules ({len(installed)}):")
    for m in installed:
        print(f"  {'🎨' if m.get('type') == 'widget' else '📡' if m.get('type') == 'data-source' else '📄'} "
              f"{m['name']:25} v{m.get('version', '?'):8} [{m.get('type', '?')}]")

def cmd_search(args):
    """Search the registry."""
    modules = fetch_registry(query=args.query)
    if not modules:
        print(f"No modules matching '{args.query}'")
        return

    print(f"Found {len(modules)} module(s):\n")
    for m in modules:
        icon = {"widget": "🎨", "data-source": "📡", "export": "📄", "integration": "🔗"}.get(m.get("type", ""), "")
        status = m.get("status", "?")
        badge = "✅" if status == "stable" else "📋" if status == "planned" else "🧪"
        print(f"  {icon} {badge} {m['name']:25} {m.get('description', '')[:60]}")

def cmd_remove(args):
    """Remove an installed module."""
    mod_dir = MODULES_DIR / args.name
    if not mod_dir.exists():
        print(f"Module '{args.name}' is not installed.")
        return

    import shutil
    shutil.rmtree(mod_dir)
    print(f"✅ Removed {args.name}")

def cmd_registry(args):
    """List all modules in the registry."""
    modules = fetch_registry()
    print(f"Module Registry ({len(modules)} modules):\n")

    by_type = {}
    for m in modules:
        by_type.setdefault(m.get("type", "other"), []).append(m)

    for mtype, mods in sorted(by_type.items()):
        icon = {"widget": "🎨", "data-source": "📡", "export": "📄", "integration": "🔗"}.get(mtype, "")
        print(f"  {icon} {mtype.upper()} ({len(mods)})")
        for m in mods:
            status = m.get("status", "?")
            badge = "✅" if status == "stable" else "📋" if status == "planned" else "🧪"
            print(f"    {badge} {m['name']:25} {m.get('description', '')[:55]}")
        print()

def cmd_info(args):
    """Show details for a specific module."""
    mod = fetch_module(args.name)
    if not mod:
        print(f"Module '{args.name}' not found.")
        return

    print(f"Name: {mod['name']}")
    print(f"Type: {mod.get('type', '?')}")
    print(f"Version: {mod.get('version', '?')}")
    print(f"Status: {mod.get('status', '?')}")
    print(f"Author: {mod.get('author', '?')}")
    print(f"Description: {mod.get('description', '')}")
    if mod.get("repo"):
        print(f"Repository: https://github.com/{mod['repo']}")
    if mod.get("tags"):
        print(f"Tags: {', '.join(mod['tags'])}")

def main():
    parser = argparse.ArgumentParser(description="Ship Log Module Manager")
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="Install a module")
    p_install.add_argument("name")

    sub.add_parser("modules", help="List installed modules")

    p_search = sub.add_parser("search", help="Search registry")
    p_search.add_argument("query")

    p_remove = sub.add_parser("remove", help="Remove a module")
    p_remove.add_argument("name")

    sub.add_parser("registry", help="Browse all available modules")

    p_info = sub.add_parser("info", help="Show module details")
    p_info.add_argument("name")

    args = parser.parse_args()
    if args.command == "install": cmd_install(args)
    elif args.command == "modules": cmd_modules(args)
    elif args.command == "search": cmd_search(args)
    elif args.command == "remove": cmd_remove(args)
    elif args.command == "registry": cmd_registry(args)
    elif args.command == "info": cmd_info(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
