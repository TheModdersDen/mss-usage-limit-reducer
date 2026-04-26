#!/usr/bin/env python3
"""
Universal AI agent diagnostic report — token usage & context health.

Scans the current project and system for all known AI coding agents
(Claude Code, Cursor, GitHub Copilot, Gemini Code Assist, Grok) and
produces a consolidated report of what's installed, what context files
are present, and where to find quota information for each.

Supported platforms: macOS, Linux, Windows 10+

Usage:
    python3 usage-report.py          # full diagnostic
    python3 usage-report.py --json   # machine-readable output
    python3 usage-report.py --cwd /path/to/project
    python3 usage-report.py --days 7          # Claude Code: scan last N days
    python3 usage-report.py --project myrepo  # Claude Code: filter by project

Claude Code is the only agent that writes local token-usage JSONL files; for
all other agents, this script performs environment and file-system diagnostics
and directs you to the appropriate online dashboard.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


# ===========================================================================
# Claude Code — actual token-usage parsing
# ===========================================================================

CLAUDE_PRICES = {
    "claude-opus-4":     (15.0, 75.0, 18.75, 1.50),
    "claude-opus-4-1":   (15.0, 75.0, 18.75, 1.50),
    "claude-opus-4-5":   (15.0, 75.0, 18.75, 1.50),
    "claude-opus-4-6":   (15.0, 75.0, 18.75, 1.50),
    "claude-opus-4-7":   (15.0, 75.0, 18.75, 1.50),
    "claude-sonnet-4":   (3.0, 15.0, 3.75, 0.30),
    "claude-sonnet-4-5": (3.0, 15.0, 3.75, 0.30),
    "claude-sonnet-4-6": (3.0, 15.0, 3.75, 0.30),
    "claude-haiku-4-5":  (1.0, 5.0, 1.25, 0.10),
    "claude-3-5-sonnet": (3.0, 15.0, 3.75, 0.30),
    "claude-3-5-haiku":  (0.80, 4.0, 1.0, 0.08),
}


def _claude_price_for(model: str):
    key = model.lower()
    for known in CLAUDE_PRICES:
        if key.startswith(known):
            return CLAUDE_PRICES[known]
    return (0.0, 0.0, 0.0, 0.0)


def _zero_row():
    return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
            "turns": 0, "cost": 0.0}


def _iter_jsonl(paths):
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def _claude_collect(projects_dir: Path, cutoff: datetime, project_filter):
    totals = _zero_row()
    by_model = defaultdict(_zero_row)

    files = list(projects_dir.glob("*/*.jsonl"))
    for rec in _iter_jsonl(files):
        msg = rec.get("message") or {}
        usage = msg.get("usage")
        if not usage:
            continue
        ts = rec.get("timestamp")
        when = None
        if ts:
            try:
                when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                pass
        if when and when < cutoff:
            continue
        cwd = rec.get("cwd") or ""
        if project_filter and project_filter not in cwd:
            continue
        model = msg.get("model") or "(unknown)"

        inp = usage.get("input_tokens", 0) or 0
        out = usage.get("output_tokens", 0) or 0
        cr = usage.get("cache_read_input_tokens", 0) or 0
        cw = usage.get("cache_creation_input_tokens", 0) or 0
        pin, pout, pcw, pcr = _claude_price_for(model)
        cost = (inp * pin + out * pout + cw * pcw + cr * pcr) / 1_000_000

        for bucket in (totals, by_model[model]):
            bucket["input"] += inp
            bucket["output"] += out
            bucket["cache_read"] += cr
            bucket["cache_write"] += cw
            bucket["turns"] += 1
            bucket["cost"] += cost

    return totals, dict(by_model)


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def _claude_projects_dir() -> Path | None:
    primary = Path.home() / ".claude" / "projects"
    if primary.exists():
        return primary
    if platform.system() == "Windows":
        local_app = os.environ.get("LOCALAPPDATA", "")
        if local_app:
            win = Path(local_app) / "Claude" / "projects"
            if win.exists():
                return win
    return None


# ===========================================================================
# Installation / context-file detection helpers
# ===========================================================================

def _which_any(*names: str) -> str | None:
    for n in names:
        found = shutil.which(n)
        if found:
            return found
    return None


def _vscode_extensions_dir() -> Path | None:
    candidate = Path.home() / ".vscode" / "extensions"
    return candidate if candidate.exists() else None


def _extensions_matching(ext_dir: Path | None, keywords: list[str]) -> list[str]:
    if not ext_dir:
        return []
    return [
        d.name for d in ext_dir.iterdir()
        if d.is_dir() and any(k in d.name.lower() for k in keywords)
    ]


def _context_files(cwd: Path) -> dict:
    files = {
        "AGENTS.md":                     cwd / "AGENTS.md",
        "CLAUDE.md":                     cwd / "CLAUDE.md",
        "GEMINI.md":                     cwd / "GEMINI.md",
        ".cursorrules":                  cwd / ".cursorrules",
        ".github/copilot-instructions.md": cwd / ".github" / "copilot-instructions.md",
        ".cursor/rules/":                cwd / ".cursor" / "rules",
    }
    return {k: str(v) if (v.exists() if not str(v).endswith("/") else v.is_dir()) else None
            for k, v in files.items()}


# ===========================================================================
# Main
# ===========================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cwd", type=str, default=str(Path.cwd()))
    ap.add_argument("--days", type=int, default=7,
                    help="Claude Code: number of days to report (default 7)")
    ap.add_argument("--project", type=str, default=None,
                    help="Claude Code: substring match on project cwd")
    args = ap.parse_args()

    cwd = Path(args.cwd).resolve()
    system = platform.system()
    ext_dir = _vscode_extensions_dir()
    ctx = _context_files(cwd)

    # --- Claude Code ---
    claude_dir = _claude_projects_dir()
    claude_totals = None
    claude_by_model = {}
    if claude_dir:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
        claude_totals, claude_by_model = _claude_collect(claude_dir, cutoff, args.project)

    # --- Cursor ---
    cursor_exe = _which_any("cursor", "Cursor", "cursor.cmd")

    # --- VS Code / Copilot ---
    vscode_exe = _which_any("code", "code-insiders", "codium", "code.cmd", "code.exe")
    copilot_exts = _extensions_matching(ext_dir, ["github.copilot"])

    # --- Gemini ---
    gemini_exts = _extensions_matching(
        ext_dir, ["google.cloudcode", "googlecloudtools", "gemini", "cloud-code"])
    gemini_user_dir = Path.home() / ".gemini"

    # --- Grok / xAI ---
    xai_key = bool(os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY"))

    if args.json:
        result = {
            "platform": system,
            "project_dir": str(cwd),
            "context_files": ctx,
            "agents": {
                "claude_code": {
                    "logs_dir": str(claude_dir) if claude_dir else None,
                    "has_data": claude_totals is not None,
                    "totals": claude_totals,
                    "by_model": claude_by_model,
                },
                "cursor": {"executable": cursor_exe},
                "github_copilot": {
                    "vscode": vscode_exe,
                    "extensions": copilot_exts,
                },
                "gemini": {
                    "extensions": gemini_exts,
                    "user_dir": str(gemini_user_dir) if gemini_user_dir.exists() else None,
                },
                "grok": {"api_key_set": xai_key},
            },
        }
        print(json.dumps(result, indent=2))
        return 0

    sep = "-" * 72
    print("Universal AI agent diagnostic report")
    print(f"Platform: {system}  |  Project: {cwd}")
    print(sep)

    # Context files
    print("Context / instruction files present:")
    found_any = False
    for fname, fpath in ctx.items():
        status = "✓" if fpath else "✗"
        note = f"  {fpath}" if fpath else "  NOT FOUND"
        print(f"  {status}  {fname:<42}{note}")
        if fpath:
            found_any = True
    if not found_any:
        print("  ← None found. Create at least AGENTS.md (universal fallback).")
    print()

    # Claude Code
    print("── Claude Code ──────────────────────────────────────────────────")
    if claude_dir and claude_totals is not None:
        total_in = (claude_totals["input"] + claude_totals["cache_read"]
                    + claude_totals["cache_write"])
        cache_pct = (claude_totals["cache_read"] / total_in * 100) if total_in else 0.0
        print(f"  Logs dir  : {claude_dir}")
        print(f"  Window    : last {args.days} day(s)")
        print(f"  Turns     : {claude_totals['turns']:,}")
        print(f"  Input     : {_fmt_tokens(claude_totals['input'])} fresh  "
              f"+ {_fmt_tokens(claude_totals['cache_read'])} cache-read  "
              f"+ {_fmt_tokens(claude_totals['cache_write'])} cache-write")
        print(f"  Output    : {_fmt_tokens(claude_totals['output'])}")
        print(f"  Cache hit : {cache_pct:.1f}%")
        print(f"  Est. cost : ~${claude_totals['cost']:.2f} (API list prices)")
        if claude_by_model:
            top = sorted(claude_by_model.items(), key=lambda kv: kv[1]["cost"],
                         reverse=True)[:3]
            print(f"  Top models: " + ", ".join(m for m, _ in top))
        # Heuristic
        if claude_totals["turns"] and cache_pct < 60:
            print(f"  ⚠ Cache hit {cache_pct:.0f}% is low — try fewer session restarts.")
        opus_cost = sum(r["cost"] for m, r in claude_by_model.items()
                        if "opus" in m.lower())
        if claude_totals["cost"] and opus_cost / claude_totals["cost"] > 0.5:
            print(f"  ⚠ Opus is {opus_cost/claude_totals['cost']*100:.0f}% of spend — "
                  "consider /model claude-haiku-4-5 for simple tasks.")
    elif claude_dir:
        print(f"  Logs dir  : {claude_dir}  (no records in last {args.days} day(s))")
    else:
        print("  Not installed or no logs found.")
        print(f"  Expected  : {Path.home() / '.claude' / 'projects'}")
    print()

    # Cursor
    print("── Cursor AI ────────────────────────────────────────────────────")
    if cursor_exe:
        print(f"  Installed : {cursor_exe}")
    else:
        print("  Not found in PATH.  Install from https://cursor.com")
    print("  Quota     : https://cursor.com/settings (Settings → Account)")
    print()

    # Copilot
    print("── GitHub Copilot ───────────────────────────────────────────────")
    if vscode_exe:
        print(f"  VS Code   : {vscode_exe}")
    else:
        print("  VS Code   : not found in PATH")
    if copilot_exts:
        print(f"  Extensions: {', '.join(copilot_exts[:3])}")
    else:
        print("  Extensions: none found  (install github.copilot from Marketplace)")
    print("  Quota     : https://github.com/settings/copilot")
    print()

    # Gemini
    print("── Google Gemini Code Assist ────────────────────────────────────")
    if gemini_exts:
        print(f"  Extensions: {', '.join(gemini_exts[:3])}")
    else:
        print("  Extensions: none found  (install Cloud Code from Marketplace)")
    if gemini_user_dir.exists():
        print(f"  ~/.gemini/ : {gemini_user_dir}")
    print("  Quota     : https://console.cloud.google.com/apis/api/"
          "cloudaicompanion.googleapis.com")
    print()

    # Grok
    print("── xAI Grok ─────────────────────────────────────────────────────")
    print(f"  XAI_API_KEY : {'SET' if xai_key else 'NOT SET'}")
    print("  Quota       : https://console.x.ai")
    print("  No local IDE plugin — use AGENTS.md as system prompt.")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
