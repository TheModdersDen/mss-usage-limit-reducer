# Usage Limit Reducer — GitHub Copilot Instructions

Use this guidance when the user is hitting usage/rate limits, burning through tokens
fast, running a long conversation, or asks how to use GitHub Copilot more efficiently.

Trigger phrases: "hit my limit", "running out of tokens", "usage limit", "save tokens",
"reduce usage", "am I wasting tokens", "this chat is getting long", "which model should
I use", "context is full".

---

## How to apply these instructions

Work through the steps in order. Skip any that clearly don't apply, but don't skip all.

### Step 1 — Measure usage

1. Direct the user to **github.com/settings/copilot** (or account.github.com/copilot)
   to see their current usage and plan limits.
2. In VS Code, the current model is shown in the chat pane title bar or the model picker
   dropdown.
3. Note conversation length: how many exchanges are in the current chat thread?

### Step 2 — Diagnose the current session

Check three things:

1. **Conversation length.** If > 15–20 turns, history re-reading dominates token cost.
   In GitHub Copilot Chat:
   - Click the **"+"** (new chat) button to start a fresh thread.
   - Paste a one-paragraph summary as the first message of the new thread.

2. **Workspace instructions presence.** Check for `.github/copilot-instructions.md` in
   the repository root. If missing, Rule #6 applies — offer to create one with the
   user's role, stack, and conventions so every new session doesn't burn 3–5 turns
   on setup.

3. **Model in use.** Open the model picker in the Copilot Chat pane. If the user is on
   a large model (GPT-4o, Claude Opus, etc.) for trivial tasks (formatting, renaming,
   grammar), Rule #8 applies — suggest switching to `gpt-4o-mini` or `claude-haiku`
   for those tasks.

### Step 3 — Apply the rules that match

Pick the 2–4 most relevant rules.

| # | Rule | GitHub Copilot action |
|---|------|-----------------------|
| 1 | Don't follow up to correct — restart | Click "+" for a new chat thread; re-send an improved prompt |
| 2 | Fresh chat every 15–20 turns | New thread + one-paragraph summary as first message |
| 3 | Batch questions into one message | Combine related asks into one message; `@workspace` once covers the full picture |
| 4 | Track actual token usage | github.com/settings/copilot usage dashboard |
| 5 | Reuse recurring context | Put it in `.github/copilot-instructions.md` — not re-pasted each session |
| 6 | Set up memory / user preferences | Create/update `.github/copilot-instructions.md` with role, stack, conventions |
| 7 | Turn off features you don't use | Disable unused VS Code extensions and unused `@` agents (e.g. `@terminal`, `@vscode`) |
| 8 | Use a lighter model for simple tasks | Switch model in the chat pane dropdown to `gpt-4o-mini` or `claude-haiku` |
| 9 | Spread work across the day | Split long work into 2–3 sessions within Copilot's rolling usage window |
| 10 | Work off-peak | Evenings and weekends may have lower congestion on shared Copilot infrastructure |
| 11 | Enable Business/Enterprise plan safety net | Copilot Business/Enterprise includes higher limits; check github.com/features/copilot |

### Step 4 — Offer concrete next actions

End with a short ordered list. Examples:

- "This chat thread is 25+ turns. Click '+' for a new thread and paste a one-paragraph summary."
- "No `.github/copilot-instructions.md` found. I can create one with your role and conventions — want me to?"
- "You're using GPT-4o for a formatting task. Switch to `gpt-4o-mini` in the model picker."

Don't recite every rule. Match advice to what the session actually shows.

---

## What this does NOT do

- It does not silently switch models or edit settings. Recommend first, act on confirmation.
- It does not clear context without asking.
- It does not send any data anywhere.

---

## Installation note for repository maintainers

To activate these instructions for all Copilot users in a repository, copy the
relevant content into `.github/copilot-instructions.md`. For workspace-level
instructions in VS Code, add a `github.copilot.chat.codeGeneration.instructions`
entry in `.vscode/settings.json`. See the top-level `README.md` for full details.
