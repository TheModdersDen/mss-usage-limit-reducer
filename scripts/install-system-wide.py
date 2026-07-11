#!/usr/bin/env python3
"""
Install System-Wide Usage Monitor

This script attempts to:
1. Schedule `monitor-usage.py` to run hourly (via crontab or schtasks).
2. Append a reference to the usage monitor in global agent config files.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def setup_scheduler(monitor_script_path: str):
    print("Setting up background scheduler...")
    sys_plat = platform.system()
    
    if sys_plat == "Windows":
        task_name = "AgentUsageMonitor"
        cmd = f'schtasks /Create /SC HOURLY /TN {task_name} /TR "python \\"{monitor_script_path}\\"" /F'
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Successfully created Windows Scheduled Task: {task_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create scheduled task. Error: {e.stderr.decode('utf-8', errors='ignore')}")
            print("You may need to run this script as Administrator.")
    else:
        # Unix/Linux/Mac
        cron_job = f"0 * * * * /usr/bin/env python3 {monitor_script_path} > /dev/null 2>&1"
        try:
            # Get current crontab
            current_cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            cron_content = current_cron.stdout if current_cron.returncode == 0 else ""
            
            if monitor_script_path not in cron_content:
                cron_content += f"\n{cron_job}\n"
                process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
                process.communicate(cron_content)
                print("Successfully added to crontab.")
            else:
                print("Cron job already exists.")
        except Exception as e:
            print(f"Failed to setup crontab: {e}")

def append_global_configs(skill_dir: Path):
    print("Updating global agent configurations...")
    
    # Text to append to global files
    injection_text = f"""
---
# Usage Limit Reducer (System-wide)
Please check `~/.agent-usage-status.json` or run `{skill_dir}/scripts/monitor-usage.py` to determine your current token usage tier before proceeding with heavy tasks.
Read full rules in `{skill_dir}/.agents/universal/AGENTS.md`.
---
"""
    
    home = Path.home()
    
    configs = [
        home / ".gemini" / "config" / "AGENTS.md",
        home / ".claude" / "CLAUDE.md",
        home / ".cursorrules" # some users keep a global one in home
    ]
    
    for cfg in configs:
        if cfg.exists():
            try:
                content = cfg.read_text(encoding="utf-8")
                if "Usage Limit Reducer" not in content:
                    with open(cfg, "a", encoding="utf-8") as f:
                        f.write(injection_text)
                    print(f"Updated {cfg}")
                else:
                    print(f"Already installed in {cfg}")
            except Exception as e:
                print(f"Could not update {cfg}: {e}")
        else:
            print(f"Config not found (skipping): {cfg}")
            
    print("\nNote: For agent-specific scheduling like Antigravity's /schedule, please run that command inside your agent's chat window.")

def main():
    skill_dir = Path(__file__).parent.parent.absolute()
    monitor_script = skill_dir / "scripts" / "monitor-usage.py"
    
    if not monitor_script.exists():
        print(f"Error: {monitor_script} not found.")
        sys.exit(1)
        
    setup_scheduler(str(monitor_script))
    append_global_configs(skill_dir)
    print("\nInstallation complete.")

if __name__ == "__main__":
    main()
