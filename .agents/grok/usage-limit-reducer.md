# Usage Limit Reducer — xAI Grok

Use this guidance when the user is hitting usage/rate limits, burning through tokens
fast, running a long conversation, or asks how to use Grok more efficiently.

Trigger phrases: "hit my limit", "running out of tokens", "usage limit", "save tokens",
"reduce usage", "am I wasting tokens", "this chat is getting long", "which model should
I use", "context is full".

---

## How to apply these instructions

Work through the steps in order. Skip any that clearly don't apply, but don't skip all.

### Step 1 — Measure usage

1. Direct the user to **x.ai** or the Grok dashboard to check their current usage and
   plan limits.
2. Note the model currently in use (Grok-3, Grok-3-mini, etc.) and the conversation
   length (number of exchanges in the current session).

### Step 2 — Diagnose the current session

Check three things:

1. **Conversation length.** If > 15–20 turns, history re-reading dominates token cost.
   - Start a **new conversation** (new chat window / new session).
   - Paste a one-paragraph summary as the very first message.

2. **System-prompt / instructions file presence.** If using Grok via the API or a
   custom tool, check whether a system prompt or project instructions file is in place.
   A universal fallback is `AGENTS.md` at the project root. If missing, Rule #6
   applies — offer to create one with the user's role, stack, and conventions.

3. **Model in use.** If the user is on `grok-3` for trivial tasks (formatting,
   renaming, grammar), Rule #8 applies — suggest switching to `grok-3-mini` or the
   lightest available Grok model for those tasks.

### Step 3 — Apply the rules that match

Pick the 2–4 most relevant rules.

| # | Rule | Grok action |
|---|------|-------------|
| 1 | Don't follow up to correct — restart | Start a new conversation; re-send an improved prompt |
| 2 | Fresh chat every 15–20 turns | New conversation + one-paragraph summary as first message |
| 3 | Batch questions into one message | Combine related asks into one message |
| 4 | Track actual token usage | x.ai dashboard or API usage endpoint |
| 5 | Reuse recurring context | Put it in a system prompt or `AGENTS.md` — not re-pasted each session |
| 6 | Set up memory / user preferences | Create/update `AGENTS.md` or the API system prompt with role, stack, conventions |
| 7 | Turn off features you don't use | Disable unused Grok tools/extensions (web search, code execution) if not needed |
| 8 | Use a lighter model for simple tasks | Switch to `grok-3-mini` or the lightest available model for routine tasks |
| 9 | Spread work across the day | Split long work into 2–3 sessions within Grok's rolling usage window |
| 10 | Work off-peak | Evenings and weekends may have lower congestion on shared xAI infrastructure |
| 11 | Enable paid plan / overage safety net | xAI SuperGrok / API plans include higher limits; check x.ai/api |

### Step 4 — Offer concrete next actions

End with a short ordered list. Examples:

- "This conversation is 25+ turns. Start a new chat and paste a one-paragraph summary."
- "No system prompt or `AGENTS.md` found. I can create one with your role and conventions — want me to?"
- "You're using Grok-3 for a formatting task. Switch to `grok-3-mini` for this."

Don't recite every rule. Match advice to what the session actually shows.

---

## What this does NOT do

- It does not silently switch models or edit settings. Recommend first, act on confirmation.
- It does not clear context without asking.
- It does not send any data anywhere.
