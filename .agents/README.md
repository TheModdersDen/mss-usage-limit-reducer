# `.agents/` — Agent-specific skill installations

This folder contains versions of the **usage-limit-reducer** skill formatted for each
supported AI coding assistant. Pick the sub-folder that matches the agent you use and
follow the instructions in the top-level `README.md` for how to install it.

| Folder | Agent |
|--------|-------|
| `claude/` | Anthropic Claude Code (CLI) |
| `cursor/` | Cursor AI (Composer) |
| `github-copilot/` | GitHub Copilot (VS Code / Xcode / JetBrains) |
| `gemini/` | Google Gemini Code Assist / Firebase Studio |
| `grok/` | xAI Grok |
| `universal/` | Any other agent — generic, agent-agnostic instructions |

All variants teach the same 11 rules for reducing wasted context tokens. Agent-specific
command references (e.g. `/compact` for Claude, `@workspace` for Copilot) are adapted
per folder, but the underlying advice is identical.
