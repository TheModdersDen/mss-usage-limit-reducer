#!/usr/bin/env python3
"""
xAI Grok diagnostic report — token usage & context health.

Grok does not have a native IDE plugin with local log files, so this script
acts as a diagnostic tool: it checks for context/instruction files, detects
relevant environment variables, and guides you to the xAI dashboard for
quota information.

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
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Context-file checks
# ---------------------------------------------------------------------------

def _find_context_files(cwd: Path) -> dict:
    """Scan for instruction files relevant to Grok sessions."""
    results = {}

    # Universal fallback (most likely to be used with Grok)
    agents_md = cwd / "AGENTS.md"
    results["agents_md"] = str(agents_md) if agents_md.exists() else None

    # Other common context files
    for name in ("CLAUDE.md", "GEMINI.md", ".cursorrules"):
        p = cwd / name
        results[name.lower().replace(".", "_")] = str(p) if p.exists() else None

    copilot_instr = cwd / ".github" / "copilot-instructions.md"
    results["copilot_instructions"] = (
        str(copilot_instr) if copilot_instr.exists() else None
    )

    return results


def _check_env() -> dict:
    """Check for Grok / xAI environment variables."""
    env_keys = ("XAI_API_KEY", "GROK_API_KEY", "GROK_MODEL", "XAI_BASE_URL")
    return {
        k: ("SET (hidden)" if os.environ.get(k) else "NOT SET")
        for k in env_keys
    }


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

    ctx = _find_context_files(cwd)
    env = _check_env()

    if args.json:
        print(json.dumps({
            "platform": system,
            "project_dir": str(cwd),
            "context_files": ctx,
            "environment": env,
        }, indent=2))
        return 0

    # Text report
    sep = "-" * 72
    print("xAI Grok — usage limit diagnostic")
    print(f"Platform: {system}  |  Project: {cwd}")
    print(sep)

    # Environment variables
    print("Environment variables:")
    for k, v in env.items():
        print(f"  {k:<20} : {v}")
    print()

    # Context files
    print("Context / instruction files:")
    if ctx["agents_md"]:
        print(f"  AGENTS.md                       : {ctx['agents_md']}  ✓ (primary for Grok)")
    else:
        print("  AGENTS.md                       : NOT FOUND  "
              "← create one; paste it as the system prompt in Grok sessions")
    for key, label in [
        ("claude_md", "CLAUDE.md"),
        ("gemini_md", "GEMINI.md"),
        ("cursorrules", ".cursorrules"),
        ("copilot_instructions", ".github/copilot-instructions.md"),
    ]:
        val = ctx.get(key)
        if val:
            print(f"  {label:<32}: {val}")
    print()

    # Quota info
    print("Quota & usage information:")
    print("  Grok does not store per-turn token counts locally.")
    print("  Check your usage at: https://x.ai  (account → usage)")
    print("  API quota:           https://console.x.ai")
    print()
    print("  To use Grok via API with instructions:")
    print('    - Pass the content of AGENTS.md as the "system" parameter')
    print("    - Example (Python):")
    print("        from openai import OpenAI")
    print('        client = OpenAI(api_key=os.environ["XAI_API_KEY"],')
    print('                        base_url="https://api.x.ai/v1")')
    print("        with open('AGENTS.md') as f: system = f.read()")
    print('        client.chat.completions.create(model="grok-3-mini",')
    print('            messages=[{"role":"system","content":system},')
    print('                      {"role":"user","content":"..."}])')
    print()

    # Heuristics
    print("Heuristics:")
    if not ctx["agents_md"]:
        print("  - No AGENTS.md found. Without a persistent context file, every Grok")
        print("    session will spend tokens re-establishing your role and conventions.")
        print("    Run:  cp .agents/universal/AGENTS.md AGENTS.md")
    else:
        print("  - AGENTS.md present — use it as your Grok system prompt.")
    if env["XAI_API_KEY"] == "NOT SET":
        print("  - XAI_API_KEY not set. For API usage, set it in your shell profile:")
        if system == "Windows":
            print("      setx XAI_API_KEY your_key_here")
        else:
            print("      echo 'export XAI_API_KEY=your_key_here' >> ~/.bashrc")

    return 0


if __name__ == "__main__":
    sys.exit(main())
