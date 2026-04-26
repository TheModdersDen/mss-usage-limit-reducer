# Usage Limit Reducer — Google Gemini Code Assist / Firebase Studio

Use this guidance when the user is hitting usage/rate limits, burning through tokens
fast, running a long conversation, or asks how to use Gemini Code Assist more
efficiently.

Trigger phrases: "hit my limit", "running out of tokens", "usage limit", "save tokens",
"reduce usage", "am I wasting tokens", "this chat is getting long", "which model should
I use", "context is full".

---

## How to apply these instructions

Work through the steps in order. Skip any that clearly don't apply, but don't skip all.

### Step 1 — Measure usage

Run the bundled Gemini diagnostic script:

```bash
# macOS / Linux
python3 .agents/gemini/scripts/usage-report.py

# Windows (PowerShell or Command Prompt)
python .agents\gemini\scripts\usage-report.py
```

Add `--json` for machine-readable output. The script checks for `GEMINI.md`,
`~/.gemini/`, the Cloud Code VS Code extension, and links you to your quota
dashboard.

For live quota numbers:

1. **Google Cloud Console → APIs & Services → Gemini Code Assist** usage page.
2. **idx.google.com** (Firebase Studio) → Account settings for quota information.
3. Note the model currently in use (shown in the chat or settings pane).
4. Estimate conversation length: how many exchanges are in the current session?

### Step 2 — Diagnose the current session

Check three things:

1. **Conversation length.** If > 15–20 turns, history re-reading dominates token cost.
   In Gemini Code Assist or Firebase Studio:
   - Start a **new chat session** from the sidebar.
   - Paste a one-paragraph summary as the first message of the new session.

2. **Context/instructions file presence.** Check for `GEMINI.md` at the project root
   or `~/.gemini/GEMINI.md` for user-level instructions. If missing, Rule #6 applies —
   offer to create one with the user's role, stack, and conventions so every new session
   doesn't burn 3–5 turns on setup.

3. **Model in use.** Check the model selector. If the user is on `gemini-1.5-pro` or
   `gemini-2.0-pro-exp` for trivial tasks (formatting, renaming, grammar), Rule #8
   applies — suggest switching to `gemini-1.5-flash` or `gemini-2.0-flash-lite` for
   those tasks.

### Step 3 — Apply the rules that match

Pick the 2–4 most relevant rules.

| # | Rule | Gemini Code Assist / Firebase Studio action |
|---|------|---------------------------------------------|
| 1 | Don't follow up to correct — restart | Start a new chat session; re-send an improved prompt |
| 2 | Fresh chat every 15–20 turns | New session + one-paragraph summary as first message |
| 3 | Batch questions into one message | Combine related asks; Gemini handles the full picture better in one turn |
| 4 | Track actual token usage | Google Cloud Console → Gemini Code Assist quota page |
| 5 | Reuse recurring context | Put it in `GEMINI.md` at project root — not re-pasted each session |
| 6 | Set up memory / user preferences | Create/update `GEMINI.md` with role, stack, coding conventions |
| 7 | Turn off features you don't use | Disable unused IDE extensions and unused Gemini plugins/tools |
| 8 | Use a lighter model for simple tasks | Switch to `gemini-1.5-flash` or `gemini-2.0-flash-lite` in the model selector |
| 9 | Spread work across the day | Split long work into 2–3 sessions within the quota window |
| 10 | Work off-peak | Evenings and weekends may have lower congestion on shared Gemini infrastructure |
| 11 | Enable paid plan / overage safety net | Gemini Code Assist Standard/Enterprise includes higher quotas; check cloud.google.com/gemini/docs/codeassist |

### Step 4 — Offer concrete next actions

End with a short ordered list. Examples:

- "This session is 30+ turns. Start a new chat and paste a one-paragraph summary."
- "No `GEMINI.md` found. I can create one with your role and conventions — want me to?"
- "You're using Gemini 1.5 Pro for a rename. Switch to `gemini-1.5-flash` in the model selector."

Don't recite every rule. Match advice to what the session actually shows.

---

## What this does NOT do

- It does not silently switch models or edit settings. Recommend first, act on confirmation.
- It does not clear context without asking.
- It does not send any data anywhere.

---

## Installation for Firebase Studio (Google's AI-first IDE)

Firebase Studio (formerly Project IDX) supports custom AI instructions. Place
`GEMINI.md` at your project root, or copy the content of this file into your project's
`GEMINI.md` to make these guidelines available in every Gemini chat session. See the
top-level `README.md` for full setup details.
