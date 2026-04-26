# Usage Limit Reducer — Universal / Agent-Agnostic Version

**Goal:** Stop wasting context tokens. AI agents re-read the entire conversation on
every turn. One developer measured it: 98.5% of his tokens went to re-reading history;
only 1.5% generated responses. This guide diagnoses where tokens are actually going and
applies 11 rules that cut wasteful usage — applicable to any AI coding assistant.

## When to use this guide

Reach for it whenever you notice:

- "I'm hitting my usage/rate limit"
- "Tokens are running out / context is full"
- "This chat is getting really long"
- "The AI seems to be forgetting earlier context"
- "Which model should I use for this task?"
- "Am I wasting tokens / how do I use the AI more efficiently?"

---

## Step 1 — Measure actual usage

> Rule #4: you can't fix what you can't measure.

Run the bundled universal diagnostic script to get a snapshot of all detected agents
and context files on your system:

```bash
# macOS / Linux
python3 .agents/universal/scripts/usage-report.py

# Windows (PowerShell or Command Prompt)
python .agents\universal\scripts\usage-report.py
```

Flags: `--json` for machine-readable output, `--cwd /path` to scan a different
directory, `--days N` (default 7) and `--project <name>` for Claude Code log filtering.

**For Claude Code users:** the script also reads local JSONL logs and shows a full
token/cost breakdown for the last N days.

**For all other agents:** the script performs environment and file-system diagnostics
and directs you to the appropriate usage dashboard.

Key metrics to find:
- **Cache-hit ratio** — if available; < 60% means too many session restarts
- **Model in use** — are you using a heavyweight model for trivial tasks?
- **Conversation length** — how many turns / how many tokens in the current session?

---

## Step 2 — Diagnose the current session

Before applying rules, check three things:

1. **Conversation length.** If the session has many turns (typically 15–20+), the
   accumulated context re-reading cost dominates. Summarize and restart.

2. **Instructions/context file presence.** Most agents support a persistent instructions
   file at the project root:
   | Agent | File |
   |-------|------|
   | Claude Code | `CLAUDE.md` |
   | Cursor | `.cursorrules` or `.cursor/rules/` |
   | GitHub Copilot | `.github/copilot-instructions.md` |
   | Gemini Code Assist | `GEMINI.md` |
   | Universal fallback | `AGENTS.md` |

   If this file is missing, every new session burns several turns re-establishing your
   role, style, and project conventions.

3. **Model tier in use.** Are you running a large/expensive model for tasks that a
   smaller/faster model handles just as well (formatting, renaming, simple lookups)?

---

## Step 3 — Apply the rules that match

Pick the 2–4 rules most relevant to the current situation. Don't apply all 11 at once.

| # | Rule | Generic action |
|---|------|----------------|
| 1 | Don't follow up to correct — restart with a fixed prompt | Clear the conversation and re-send an improved prompt instead of piling on corrections |
| 2 | Fresh chat every 15–20 turns | Start a new conversation and paste a one-paragraph summary as the first message |
| 3 | Batch questions into one message | Combine related asks into one prompt; the agent often answers better with the full picture |
| 4 | Track actual token usage | Use your agent's usage dashboard or the bundled `scripts/usage-report.py` (Claude Code) |
| 5 | Reuse recurring context | Put it in your agent's instructions file (see table above) — not re-pasted each session |
| 6 | Set up memory / user preferences | Create or update the instructions file with your role, style, and project conventions |
| 7 | Turn off features you don't use | Disable unused extensions, MCP servers, or tool integrations that add tokens to every turn |
| 8 | Use a lighter model for simple tasks | Switch to the smallest model that can do the job (e.g. Haiku, GPT-4o-mini, Flash, etc.) |
| 9 | Spread work across the day | Usage windows are rolling (often 5 hours); split long work into 2–3 shorter sessions |
| 10 | Work off-peak | Shared-infrastructure agents may throttle during peak hours; evenings / weekends stretch your plan |
| 11 | Enable overage / pay-as-you-go as a safety net | If your plan allows it, turn on overage so you don't get cut off mid-task |

---

## Step 4 — Concrete next actions

End every diagnosis with a short, ordered action list. Examples:

- "This session is 35 turns long. Start a new conversation with a one-paragraph summary."
- "No instructions file found. Create `AGENTS.md` (or the agent-specific equivalent) with your role and project conventions."
- "You're using the largest model for a rename task. Switch to the lightest available model."
- "Disable the three MCP servers you haven't used this week."

---

## What this guide does NOT do

- It does not silently change your model or settings. Recommend first, act only on
  confirmation.
- It does not summarize-and-clear without asking — the user may have unsaved context.
- It does not send data anywhere. All measurement is local.

---

## Notes on agent-specific limitations

Some rules reference features that only exist in certain agents:

- **Rule #1 ("Edit your original prompt")** — only available in chat UIs that support
  message editing (claude.ai, ChatGPT web, etc.). In IDEs the equivalent is clear + re-send.
- **Rule #5 ("Upload to a Project")** — a claude.ai web UI feature. In IDEs, use the
  instructions file instead.
- **Rule #11 (Overage toggle)** — plan-level; mention it, don't try to toggle it from code.
