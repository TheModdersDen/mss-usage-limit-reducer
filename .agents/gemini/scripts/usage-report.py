#!/usr/bin/env python3
"""
Google Gemini Code Assist / Firebase Studio diagnostic report.

Gemini Code Assist does not write per-turn token JSONL files locally, so this
script acts as a diagnostic tool: it checks for Gemini-specific context files
(GEMINI.md, ~/.gemini/), detects the VS Code Gemini extension, and guides you
to the Google Cloud Console for actual quota information.

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
# Platform-specific paths
# ---------------------------------------------------------------------------

def _gemini_user_dir() -> Path | None:
    """Return ~/.gemini if it exists."""
    candidate = Path.home() / ".gemini"
    return candidate if candidate.exists() else None


def _vscode_extensions_dir() -> Path | None:
    candidate = Path.home() / ".vscode" / "extensions"
    return candidate if candidate.exists() else None


def _vscode_executable() -> str | None:
    for name in ("code", "code-insiders", "codium", "code.cmd", "code.exe"):
        found = shutil.which(name)
        if found:
            return found
    system = platform.system()
    if system == "Darwin":
        paths = [
            Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
        ]
    elif system == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        prog = os.environ.get("ProgramFiles", "")
        paths = [
            Path(local) / "Programs" / "Microsoft VS Code" / "Code.exe" if local else None,
            Path(prog) / "Microsoft VS Code" / "Code.exe" if prog else None,
        ]
        paths = [p for p in paths if p]
    else:
        paths = [Path("/usr/share/code/code"), Path("/usr/bin/code")]
    for p in paths:
        if p.exists():
            return str(p)
    return None


def _find_gemini_extension(ext_dir: Path | None) -> list[str]:
    """List installed Gemini Code Assist extension folders."""
    if not ext_dir:
        return []
    keywords = ("google.cloudcode", "googlecloudtools", "gemini", "cloud-code")
    return [
        d.name for d in ext_dir.iterdir()
        if d.is_dir() and any(k in d.name.lower() for k in keywords)
    ]


# ---------------------------------------------------------------------------
# Context-file checks
# ---------------------------------------------------------------------------

def _find_context_files(cwd: Path) -> dict:
    """Scan for Gemini context files."""
    results = {}

    # Project-level
    gemini_md = cwd / "GEMINI.md"
    results["gemini_md_project"] = str(gemini_md) if gemini_md.exists() else None

    # User-level
    user_gemini = Path.home() / ".gemini" / "GEMINI.md"
    results["gemini_md_user"] = str(user_gemini) if user_gemini.exists() else None

    # Universal fallbacks
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

    vscode_exe = _vscode_executable()
    ext_dir = _vscode_extensions_dir()
    gemini_exts = _find_gemini_extension(ext_dir)
    gemini_user_dir = _gemini_user_dir()
    ctx = _find_context_files(cwd)

    if args.json:
        print(json.dumps({
            "platform": system,
            "vscode_installed": vscode_exe is not None,
            "vscode_executable": vscode_exe,
            "gemini_user_dir": str(gemini_user_dir) if gemini_user_dir else None,
            "gemini_extensions": gemini_exts,
            "project_dir": str(cwd),
            "context_files": ctx,
        }, indent=2))
        return 0

    # Text report
    sep = "-" * 72
    print("Google Gemini Code Assist — usage limit diagnostic")
    print(f"Platform: {system}  |  Project: {cwd}")
    print(sep)

    # VS Code installation
    if vscode_exe:
        print(f"VS Code executable : {vscode_exe}")
    else:
        print("VS Code executable : NOT FOUND")
    if ext_dir:
        print(f"Extensions dir     : {ext_dir}")
    print()

    # Gemini extension
    if gemini_exts:
        print(f"Gemini / Cloud Code extensions installed ({len(gemini_exts)}):")
        for ext in sorted(gemini_exts):
            print(f"  {ext}")
    else:
        print("Gemini / Cloud Code extensions : NONE FOUND")
        print("  Install from: https://marketplace.visualstudio.com/items"
              "?itemName=GoogleCloudTools.cloudcode")
    print()

    # ~/.gemini directory
    if gemini_user_dir:
        files = list(gemini_user_dir.iterdir())
        print(f"~/.gemini/ directory : {gemini_user_dir}  ({len(files)} file(s))")
        for f in sorted(files):
            print(f"  {f.name}")
    else:
        print("~/.gemini/ directory : NOT FOUND")
    print()

    # Context files
    print("Context files (reduce per-session token burn):")
    if ctx["gemini_md_project"]:
        print(f"  GEMINI.md (project) : {ctx['gemini_md_project']}")
    else:
        print("  GEMINI.md (project) : NOT FOUND  "
              "← create one to persist context across sessions")
    if ctx["gemini_md_user"]:
        print(f"  GEMINI.md (user)    : {ctx['gemini_md_user']}")
    else:
        print("  GEMINI.md (user)    : NOT FOUND  (~/.gemini/GEMINI.md)")
    if ctx["agents_md"]:
        print(f"  AGENTS.md           : {ctx['agents_md']}")
    else:
        print("  AGENTS.md           : NOT FOUND")
    print()

    # Quota info
    print("Quota & usage information:")
    print("  Gemini Code Assist does not store per-turn token counts locally.")
    print("  Check your quota at:")
    print("    Google Cloud Console → APIs & Services → Gemini Code Assist")
    print("    https://console.cloud.google.com/apis/api/cloudaicompanion.googleapis.com")
    print("  Firebase Studio:  https://idx.google.com  → Account settings")
    print()

    # Heuristics
    print("Heuristics:")
    if not ctx["gemini_md_project"] and not ctx["gemini_md_user"]:
        print("  - No GEMINI.md found at project or user level. Every new session will")
        print("    spend tokens re-establishing context.")
        print("    Create GEMINI.md at the project root with your role and conventions.")
    else:
        print("  - GEMINI.md present — good.")
    if not gemini_exts:
        print("  - No Gemini/Cloud Code extension detected. Install from the Marketplace.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
