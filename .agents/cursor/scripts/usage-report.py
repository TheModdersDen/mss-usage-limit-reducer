#!/usr/bin/env python3
"""
Cursor AI diagnostic report — token usage & context health.

Cursor does not write per-turn token JSONL files the way Claude Code does, so
this script acts as a diagnostic tool: it detects your Cursor installation,
checks for context/rules files that affect token usage, and guides you to the
Cursor usage dashboard for actual quota information.

Supported platforms: macOS, Linux, Windows 10+

Usage:
    python3 usage-report.py          # full diagnostic
    python3 usage-report.py --json   # machine-readable output
    python3 usage-report.py --cwd /path/to/project
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Platform-specific Cursor config roots
# ---------------------------------------------------------------------------

def _cursor_config_dir() -> Path | None:
    """Return the Cursor user config directory for the current OS, or None."""
    system = platform.system()
    if system == "Darwin":
        candidate = Path.home() / "Library" / "Application Support" / "Cursor" / "User"
    elif system == "Windows":
        app_data = os.environ.get("APPDATA", "")
        candidate = Path(app_data) / "Cursor" / "User" if app_data else None
        if candidate is None:
            return None
    else:
        # Linux / other POSIX
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        base = Path(xdg) if xdg else Path.home() / ".config"
        candidate = base / "Cursor" / "User"

    return candidate if candidate.exists() else None


def _cursor_extensions_dir() -> Path | None:
    """Return the Cursor extensions directory for the current OS, or None."""
    system = platform.system()
    if system == "Darwin":
        candidate = Path.home() / ".cursor" / "extensions"
    elif system == "Windows":
        candidate = Path.home() / ".cursor" / "extensions"
    else:
        candidate = Path.home() / ".cursor" / "extensions"
    return candidate if candidate.exists() else None


def _cursor_executable() -> str | None:
    """Find the Cursor executable, or return None."""
    for name in ("cursor", "Cursor", "cursor.cmd"):
        found = shutil.which(name)
        if found:
            return found
    # Common install paths
    system = platform.system()
    if system == "Darwin":
        candidates = [
            Path("/Applications/Cursor.app/Contents/MacOS/Cursor"),
        ]
    elif system == "Windows":
        local_app = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            Path(local_app) / "Programs" / "cursor" / "Cursor.exe" if local_app else None,
        ]
        candidates = [c for c in candidates if c]
    else:
        candidates = [
            Path.home() / ".local" / "share" / "cursor" / "cursor",
            Path("/opt/cursor/cursor"),
            Path("/usr/local/bin/cursor"),
        ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ---------------------------------------------------------------------------
# Context-file checks
# ---------------------------------------------------------------------------

def _find_context_files(cwd: Path) -> dict:
    """Scan cwd for Cursor context/rules files that reduce per-session token burn."""
    results = {}

    # Modern: .cursor/rules/*.mdc
    rules_dir = cwd / ".cursor" / "rules"
    if rules_dir.is_dir():
        mdc_files = list(rules_dir.glob("*.mdc"))
        results["cursor_rules_dir"] = str(rules_dir)
        results["cursor_rules_files"] = [str(f.name) for f in mdc_files]
    else:
        results["cursor_rules_dir"] = None
        results["cursor_rules_files"] = []

    # Legacy: .cursorrules
    legacy = cwd / ".cursorrules"
    results["cursorrules_file"] = str(legacy) if legacy.exists() else None

    # Universal fallback
    agents_md = cwd / "AGENTS.md"
    results["agents_md"] = str(agents_md) if agents_md.exists() else None

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--cwd", type=str, default=str(Path.cwd()),
                    help="project directory to scan for context files")
    args = ap.parse_args()

    cwd = Path(args.cwd).resolve()
    system = platform.system()

    cursor_exe = _cursor_executable()
    config_dir = _cursor_config_dir()
    ext_dir = _cursor_extensions_dir()
    ctx = _find_context_files(cwd)

    if args.json:
        print(json.dumps({
            "platform": system,
            "cursor_installed": cursor_exe is not None,
            "cursor_executable": cursor_exe,
            "cursor_config_dir": str(config_dir) if config_dir else None,
            "cursor_extensions_dir": str(ext_dir) if ext_dir else None,
            "project_dir": str(cwd),
            "context_files": ctx,
        }, indent=2))
        return 0

    # Text report
    sep = "-" * 72
    print("Cursor AI — usage limit diagnostic")
    print(f"Platform: {system}  |  Project: {cwd}")
    print(sep)

    # Installation
    if cursor_exe:
        print(f"Cursor executable : {cursor_exe}")
    else:
        print("Cursor executable : NOT FOUND (is Cursor installed?)")
    if config_dir:
        print(f"Cursor config dir : {config_dir}")
    else:
        print("Cursor config dir : NOT FOUND")
    if ext_dir:
        ext_count = len(list(ext_dir.iterdir()))
        print(f"Extensions dir    : {ext_dir}  ({ext_count} extension(s))")
    else:
        print("Extensions dir    : NOT FOUND")
    print()

    # Context files
    print("Context / rules files (reduce per-session token burn):")
    if ctx["cursor_rules_files"]:
        print(f"  .cursor/rules/   : {len(ctx['cursor_rules_files'])} file(s) — "
              f"{', '.join(ctx['cursor_rules_files'])}")
    else:
        print("  .cursor/rules/   : NOT FOUND  ← create one to save tokens on every session")
    if ctx["cursorrules_file"]:
        print(f"  .cursorrules     : {ctx['cursorrules_file']}")
    else:
        print("  .cursorrules     : NOT FOUND  (legacy format, .cursor/rules/ preferred)")
    if ctx["agents_md"]:
        print(f"  AGENTS.md        : {ctx['agents_md']}")
    else:
        print("  AGENTS.md        : NOT FOUND")
    print()

    # Quota / usage info
    print("Quota & usage information:")
    print("  Cursor does not store per-turn token counts locally.")
    print("  Check your usage quota at: https://cursor.com/settings")
    print("  (Settings → Account → Usage & Billing)")
    print()

    # Heuristics
    print("Heuristics:")
    if not ctx["cursor_rules_files"] and not ctx["cursorrules_file"]:
        print("  - No rules file found. Every new Composer session will spend tokens")
        print("    re-establishing context. Create .cursor/rules/project.mdc with your")
        print("    role, stack, and coding conventions to save tokens on every session.")
    else:
        print("  - Rules file present — good. Each new session inherits this context.")
    if not ctx["agents_md"]:
        print("  - No AGENTS.md found. Consider creating one as a universal fallback")
        print("    for other agents (GitHub Copilot, Gemini, etc.).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
