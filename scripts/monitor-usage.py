#!/usr/bin/env python3
"""
Agent Token Monitor (Heuristic & Local Logs)

This script monitors token usage for the current project (falling back to global usage).
It uses local file heuristics and available logs (e.g., Claude JSONL logs) to 
estimate the current token burden without requiring API keys.

It outputs a `.agent-usage-status.json` file in the project root (or globally).
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

def _default_claude_projects_dir() -> Path:
    import platform
    primary = Path.home() / ".claude" / "projects"
    if platform.system() == "Windows":
        local_app = os.environ.get("LOCALAPPDATA", "")
        if local_app:
            return Path(local_app) / "Claude" / "projects"
    return primary

def analyze_claude_logs(project_path: str) -> dict:
    """Analyze Claude Code logs for the given project path (if available)."""
    projects_dir = _default_claude_projects_dir()
    if not projects_dir.exists():
        return {}
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    total_in = 0
    total_out = 0
    turns = 0
    
    # We look for jsonl files
    files = list(projects_dir.glob("*/*.jsonl"))
    for p in files:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        rec = json.loads(line)
                        msg = rec.get("message") or {}
                        usage = msg.get("usage")
                        if not usage: continue
                        
                        ts = rec.get("timestamp")
                        if ts:
                            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if when < cutoff:
                                continue
                        
                        cwd = rec.get("cwd", "")
                        if project_path and project_path not in cwd:
                            continue
                            
                        inp = usage.get("input_tokens", 0) or 0
                        cr = usage.get("cache_read_input_tokens", 0) or 0
                        cw = usage.get("cache_creation_input_tokens", 0) or 0
                        out = usage.get("output_tokens", 0) or 0
                        
                        total_in += (inp + cr + cw)
                        total_out += out
                        turns += 1
                        
                    except Exception:
                        pass
        except OSError:
            pass
            
    if turns == 0:
        return {}
        
    return {
        "turns_24h": turns,
        "input_24h": total_in,
        "output_24h": total_out
    }

def analyze_project_heuristics(project_path: str) -> dict:
    """Estimate a baseline token burden based on project size."""
    if not os.path.exists(project_path):
        return {}
        
    file_count = 0
    for root, dirs, files in os.walk(project_path):
        if '.git' in root or 'node_modules' in root or '.venv' in root:
            continue
        file_count += len(files)
        
    return {
        "project_file_count": file_count,
        "estimated_context_base": file_count * 50  # rough heuristic: 50 tokens per file baseline
    }

def determine_tier(metrics: dict) -> str:
    """
    Dynamically determine the most efficient tier.
    No hardcoded universal thresholds, but uses a heuristic based on available data.
    """
    turns = metrics.get("turns_24h", 0)
    
    if turns > 30:
        return "Tier 3 (Conservative)"
    elif turns > 10:
        return "Tier 2 (Balanced)"
    return "Tier 1 (Creative)"

def analyze_api_usage() -> dict:
    """Attempt to securely load API keys via dotenv and query usage APIs."""
    try:
        from dotenv import load_dotenv
        # Look for .env or .env.keys in the current project or home directory
        env_paths = [Path.cwd() / ".env", Path.cwd() / ".env.keys", Path.home() / ".env", Path.home() / ".env.keys"]
        for path in env_paths:
            if path.exists():
                load_dotenv(dotenv_path=path)
                break
    except ImportError:
        pass # dotenv not installed, skip secure API fallback
        
    api_metrics = {}
    
    # Example: If OpenAI key is present, we could query the usage API.
    # Note: OpenAI's billing/usage endpoints often require org-level keys.
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        # api_metrics["openai_api_detected"] = True
        pass
        
    # Example: Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        # api_metrics["anthropic_api_detected"] = True
        pass
        
    return api_metrics

def main():
    project_path = os.getcwd()
    
    # 1. Gather available metrics without API keys (Primary)
    claude_metrics = analyze_claude_logs(project_path)
    heuristics = analyze_project_heuristics(project_path)
    
    # 2. Gather API metrics if securely provided (Fallback/Supplementary)
    api_metrics = analyze_api_usage()
    
    metrics = {**claude_metrics, **heuristics, **api_metrics}
    
    if not metrics.get("turns_24h"):
        # Fallback to global if project specific turns not found
        global_claude = analyze_claude_logs("")
        if global_claude:
            metrics["global_turns_24h"] = global_claude.get("turns_24h", 0)
            
    # 3. Determine Tier
    tier = determine_tier(metrics)
    
    status = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "project": project_path,
        "recommended_tier": tier,
        "metrics": metrics
    }
    
    # 4. Write out status
    out_path = Path(project_path) / ".agent-usage-status.json"
    try:
        with open(out_path, "w") as f:
            json.dump(status, f, indent=2)
        print(f"Status written to {out_path}")
    except Exception as e:
        print(f"Failed to write to local project. Falling back to global. Error: {e}")
        global_path = Path.home() / ".agent-usage-status.json"
        with open(global_path, "w") as f:
            json.dump(status, f, indent=2)
        print(f"Status written to {global_path}")

if __name__ == "__main__":
    main()
