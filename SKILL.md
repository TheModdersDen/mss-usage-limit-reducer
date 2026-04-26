---
name: usage-limit-reducer
description: Use when the user is hitting usage/rate limits, burning through tokens fast, running a long conversation, or asks how to use AI coding assistants more efficiently. Triggers on phrases like "hit my limit", "running out of tokens", "usage limit", "save tokens", "reduce usage", "am I wasting tokens", "this chat is getting long", "which model should I use", "context is full". Diagnoses the current session, runs a real token-usage report from local logs (Claude Code), and applies 11 rules for reducing AI token usage.
---

# Usage Limit Reducer

Apply the 11 rules for cutting AI token usage. AI coding assistants re-read the entire
conversation on every turn — 98.5% of tokens often go to re-reading history rather
than generating responses. Diagnose where the user's tokens are going and apply the
rules that actually move the needle.

> **Agent note:** This skill was originally written for Claude Code. Claude-specific
> commands (e.g. `/compact`, `/model`) are listed first; equivalent actions for other
> agents (Cursor, GitHub Copilot, Gemini, Grok) follow in parentheses where they differ.
> Agent-specific files live in `.agents/<agent>/` if you prefer a version without the
> Claude references.

## How to run this skill

Do the steps in order. Skip any step that clearly doesn't apply, but don't skip all of
them — the value is in matching rules to what the user is actually doing.

### Step 1 — Run the real token-usage report

Rule #4: "you can't fix what you can't measure."

**Claude Code** already writes every token, model, and timestamp to
`~/.claude/projects/<project>/<session>.jsonl`. Run the bundled script to show the
breakdown (use the absolute path to `scripts/usage-report.py` inside this skill's
directory):

```bash
python3 <SKILL_DIR>/scripts/usage-report.py --days 7
```

Flags: `--days N` (default 7), `--project <substring>` to scope by cwd, `--json` for
machine-readable output. Share the headline numbers — cache-hit% and model mix are the
two that matter most.

- **Low cache-hit% (< ~60%)** → too many fresh chats or cache-busting edits; Rule #2 applies.
- **High large-model share** for routine work → Rule #8 applies.

**Other agents:** direct the user to their agent's usage dashboard (Cursor Settings →
Account, github.com/settings/copilot, Google Cloud Console, x.ai dashboard, etc.).

### Step 2 — Diagnose the current session

Before advising, check three things:

1. **Conversation length.** If this session already has many turns, rule #2 applies
   directly.
   - *Claude Code:* suggest `/compact` (summarize in place) or `/clear` then paste a
     one-paragraph summary as the first message of the new chat.
   - *Other agents:* start a new chat/session and paste the summary.

2. **Instructions file presence.** Check the project root for the agent's context file:

   | Agent | File |
   |-------|------|
   | Claude Code | `CLAUDE.md` (and `~/.claude/CLAUDE.md`) |
   | Cursor | `.cursorrules` or `.cursor/rules/*.mdc` |
   | GitHub Copilot | `.github/copilot-instructions.md` |
   | Gemini Code Assist | `GEMINI.md` |
   | Universal fallback | `AGENTS.md` |

   If missing, rule #6 applies — offer to create one with the user's role, style, and
   project conventions so every new session doesn't burn 3–5 messages on setup.

3. **Model in use.** If the user is on a large/expensive model for trivial tasks
   (grammar, formatting, short answers, quick renames), rule #8 applies.
   - *Claude Code:* `/model claude-haiku-4-5`
   - *Cursor:* switch in the Composer model picker to `cursor-small` or `claude-haiku-4-5`
   - *GitHub Copilot:* switch to `gpt-4o-mini` or `claude-haiku` in the chat model picker
   - *Gemini:* switch to `gemini-1.5-flash` or `gemini-2.0-flash-lite`
   - *Grok:* switch to `grok-3-mini`

### Step 3 — Apply the rules that match

Pick the 2–4 rules most relevant to what the user is doing right now. Don't dump all
11 on them. For each rule: (a) what to do, (b) why it works, (c) the concrete next
action.

| # | Rule | Claude Code action | Generic / other agent action |
|---|------|--------------------|------------------------------|
| 1 | Don't follow up to correct — restart | `/clear` + re-prompt | Start a new conversation with an improved prompt |
| 2 | Fresh chat every 15–20 turns | `/compact` to summarize, or `/clear` + paste summary | New session + one-paragraph summary as first message |
| 3 | Batch questions into one message | Combine related asks into one prompt | Same |
| 4 | Track actual token usage | `scripts/usage-report.py` | Agent's usage dashboard |
| 5 | Reuse recurring context | Put in `CLAUDE.md`, skills, or `.context/` | Put in the agent's instructions file |
| 6 | Set up memory / user preferences | Create/update `CLAUDE.md` | Create/update the agent-specific instructions file |
| 7 | Turn off features you don't use | Audit `~/.claude/settings.json` for unused MCPs, hooks | Disable unused IDE extensions and tool integrations |
| 8 | Use a lighter model for simple tasks | `/model claude-haiku-4-5` | Switch to the lightest available model |
| 9 | Spread work across the day | 5-hour rolling window; split into 2–3 sessions | Same concept applies to most agent plans |
| 10 | Work off-peak | Peak is 5–11am PT / 8am–2pm ET weekdays | Evenings and weekends stretch shared-compute plans |
| 11 | Enable overage / pay-as-you-go | Settings → Usage on Claude Pro/Max plans | Check your agent's plan settings |

### Step 4 — Offer concrete next actions

End with a short, ordered list of what to do *now*, based on the diagnosis. Examples:

- "Run `/compact` — this conversation is 40+ turns." *(Claude Code)*
- "Start a new chat session and paste a summary — this thread is 40+ turns." *(other agents)*
- "I can create a `CLAUDE.md` (or `AGENTS.md`) with your preferences — want me to?"
- "Switch to Haiku for this rename: `/model claude-haiku-4-5`." *(Claude Code)*

Don't recite every rule. Don't lecture. Match the advice to what the session actually
shows.

## Rules not fully implementable in any agent

- **Rule #1 ("Edit your prompt")** — only available in chat UIs that support message
  editing (claude.ai, ChatGPT web, etc.). In IDEs the equivalent is clear + re-send.
- **Rule #5 ("Upload to Projects")** — a claude.ai web UI feature; use the
  instructions file instead.
- **Rule #11 (Overage toggle)** — plan-level; mention it, don't try to implement it.

## What this skill does NOT do

- It does not silently change the user's model or settings. Recommend, then act only
  on confirmation.
- It does not summarize-and-clear without asking — the user may have unsaved context.
- It does not send data anywhere. The usage report is strictly local.
