#!/usr/bin/env python3
"""
GitHub Copilot diagnostic report — token usage & context health.

GitHub Copilot does not write per-turn token JSONL files locally, so this
script acts as a diagnostic tool: it detects your VS Code / Copilot
installation, checks for workspace-instruction files that affect token usage,
and guides you to the Copilot usage dashboard.

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
# Platform-specific VS Code / Copilot paths
# ---------------------------------------------------------------------------

def _vscode_extensions_dir() -> Path | None:
    """Return the VS Code extensions directory for the current OS."""
    candidate = Path.home() / ".vscode" / "extensions"
    return candidate if candidate.exists() else None


def _vscode_user_dir() -> Path | None:
    """Return the VS Code user data directory for the current OS."""
    system = platform.system()
    if system == "Darwin":
        candidate = (Path.home() / "Library" / "Application Support"
                     / "Code" / "User")
    elif system == "Windows":
        app_data = os.environ.get("APPDATA", "")
        candidate = Path(app_data) / "Code" / "User" if app_data else None
        if candidate is None:
            return None
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        base = Path(xdg) if xdg else Path.home() / ".config"
        candidate = base / "Code" / "User"
    return candidate if (candidate and candidate.exists()) else None


def _vscode_executable() -> str | None:
    """Find the VS Code executable, or return None."""
    for name in ("code", "code-insiders", "codium", "code.cmd", "code.exe"):
        found = shutil.which(name)
        if found:
            return found
    system = platform.system()
    if system == "Darwin":
        paths = [
            Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
            Path("/Applications/VSCodium.app/Contents/Resources/app/bin/codium"),
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
        paths = [
            Path("/usr/share/code/code"),
            Path("/usr/bin/code"),
            Path("/opt/visual-studio-code/code"),
        ]
    for p in paths:
        if p.exists():
            return str(p)
    return None


def _find_copilot_extension(ext_dir: Path | None) -> list[str]:
    """List installed Copilot extension folders."""
    if not ext_dir:
        return []
    return [
        d.name for d in ext_dir.iterdir()
        if d.is_dir() and d.name.startswith("github.copilot")
    ]


# ---------------------------------------------------------------------------
# Context-file checks
# ---------------------------------------------------------------------------

def _find_context_files(cwd: Path) -> dict:
    """Scan cwd for Copilot instruction files that reduce per-session token burn."""
    results = {}

    # Workspace instructions
    copilot_instr = cwd / ".github" / "copilot-instructions.md"
    results["copilot_instructions"] = (
        str(copilot_instr) if copilot_instr.exists() else None
    )

    # Universal fallbacks
    agents_md = cwd / "AGENTS.md"
    results["agents_md"] = str(agents_md) if agents_md.exists() else None

    claude_md = cwd / "CLAUDE.md"
    results["claude_md"] = str(claude_md) if claude_md.exists() else None

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
                    help="project directory to scan for instruction files")
    args = ap.parse_args()

    cwd = Path(args.cwd).resolve()
    system = platform.system()

    vscode_exe = _vscode_executable()
    ext_dir = _vscode_extensions_dir()
    user_dir = _vscode_user_dir()
    copilot_exts = _find_copilot_extension(ext_dir)
    ctx = _find_context_files(cwd)

    if args.json:
        print(json.dumps({
            "platform": system,
            "vscode_installed": vscode_exe is not None,
            "vscode_executable": vscode_exe,
            "vscode_user_dir": str(user_dir) if user_dir else None,
            "copilot_extensions": copilot_exts,
            "project_dir": str(cwd),
            "context_files": ctx,
        }, indent=2))
        return 0

    # Text report
    sep = "-" * 72
    print("GitHub Copilot — usage limit diagnostic")
    print(f"Platform: {system}  |  Project: {cwd}")
    print(sep)

    # VS Code installation
    if vscode_exe:
        print(f"VS Code executable : {vscode_exe}")
    else:
        print("VS Code executable : NOT FOUND (is VS Code installed?)")
    if user_dir:
        print(f"VS Code user dir   : {user_dir}")
    if ext_dir:
        print(f"Extensions dir     : {ext_dir}")
    else:
        print("Extensions dir     : NOT FOUND (~/.vscode/extensions)")
    print()

    # Copilot extensions
    if copilot_exts:
        print(f"Copilot extensions installed ({len(copilot_exts)}):")
        for ext in sorted(copilot_exts):
            print(f"  {ext}")
    else:
        print("Copilot extensions : NONE FOUND")
        print("  Install from: https://marketplace.visualstudio.com/items?itemName=GitHub.copilot")
    print()

    # Instruction files
    print("Instruction files (reduce per-session token burn):")
    if ctx["copilot_instructions"]:
        print(f"  .github/copilot-instructions.md : {ctx['copilot_instructions']}")
    else:
        print("  .github/copilot-instructions.md : NOT FOUND  "
              "← create one to persist context across sessions")
    if ctx["agents_md"]:
        print(f"  AGENTS.md                       : {ctx['agents_md']}")
    else:
        print("  AGENTS.md                       : NOT FOUND")
    if ctx["claude_md"]:
        print(f"  CLAUDE.md                       : {ctx['claude_md']}")
    print()

    # Quota / usage info
    print("Quota & usage information:")
    print("  GitHub Copilot does not store per-turn token counts locally.")
    print("  Check your usage at: https://github.com/settings/copilot")
    print("  (also: https://github.com/orgs/<org>/settings/copilot for Org plans)")
    print()

    # Heuristics
    print("Heuristics:")
    if not ctx["copilot_instructions"]:
        print("  - No .github/copilot-instructions.md found. Every new chat thread will")
        print("    spend tokens re-establishing your role and conventions. Create it now:")
        print("    mkdir -p .github && touch .github/copilot-instructions.md")
    else:
        print("  - copilot-instructions.md present — good.")
    if not copilot_exts:
        print("  - No Copilot extension detected. Install 'GitHub Copilot' and")
        print("    'GitHub Copilot Chat' from the VS Code Marketplace.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
