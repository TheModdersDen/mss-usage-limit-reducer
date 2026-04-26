# `.agents/` — Agent-specific skill installations

This folder contains versions of the **usage-limit-reducer** skill formatted for each
supported AI coding assistant. Pick the sub-folder that matches the agent you use and
follow the instructions in the top-level `README.md` for how to install it.

| Folder | Agent | Instruction file | Diagnostic script |
|--------|-------|-----------------|-------------------|
| `claude/` | Anthropic Claude Code (CLI) | `SKILL.md` | `scripts/usage-report.py` |
| `cursor/` | Cursor AI (Composer) | `usage-limit-reducer.mdc` | `scripts/usage-report.py` |
| `github-copilot/` | GitHub Copilot (VS Code / Xcode / JetBrains) | `usage-limit-reducer.md` | `scripts/usage-report.py` |
| `gemini/` | Google Gemini Code Assist / Firebase Studio | `usage-limit-reducer.md` | `scripts/usage-report.py` |
| `grok/` | xAI Grok | `usage-limit-reducer.md` | `scripts/usage-report.py` |
| `universal/` | Any other agent — generic, agent-agnostic | `AGENTS.md` | `scripts/usage-report.py` |

All variants teach the same 11 rules for reducing wasted context tokens. Agent-specific
command references (e.g. `/compact` for Claude, `@workspace` for Copilot) are adapted
per folder, but the underlying advice is identical.

## Diagnostic scripts

Each folder contains a `scripts/usage-report.py` that works on **macOS, Linux, and
Windows 10+**:

```bash
# macOS / Linux
python3 .agents/<agent>/scripts/usage-report.py
python3 .agents/<agent>/scripts/usage-report.py --json   # machine-readable

# Windows (PowerShell or Command Prompt)
python .agents\<agent>\scripts\usage-report.py

# Universal (checks all agents at once)
python3 .agents/universal/scripts/usage-report.py
```

Claude Code's script is the only one that reads local token JSONL files and produces
actual usage statistics. All other scripts perform environment diagnostics and link
you to the appropriate online dashboard.

## Universal fallback

Copy `universal/AGENTS.md` to your project root as `AGENTS.md` — a broadly recognized
convention that many agents pick up automatically:

```bash
cp .agents/universal/AGENTS.md AGENTS.md
```
