# Usage Limit Reducer — ChatGPT

Use this guidance when hitting usage/rate limits (e.g., GPT-4o usage limits), burning through conversation context, or when asking how to use ChatGPT more efficiently.

Trigger phrases: "hit my limit", "running out of tokens", "usage limit", "save tokens", "reduce usage", "am I wasting tokens", "this chat is getting long", "context is full".

---

## General Agent Guidelines

As an AI, you must self-regulate your usage to prevent burning the user's token limits unnecessarily:
1. **No Infinite Loops:** If you fail a task or test 3 times in a row, STOP and ask the user for help. Do not keep retrying the same approach.
2. **Limit Complex Sub-tasks:** Only tackle complex parallel tasks if explicitly asked. 
3. **Self-Monitor Turns:** Keep track of how many turns have elapsed in the current session.
4. **Self-Estimate Context (Primary Tracker):** On every 5th turn, estimate your current context token usage by calculating roughly (Total Words in Chat * 1.33) or (Total Characters / 4). If the estimate exceeds 30,000 tokens (or your known context limit), alert the user and suggest restarting the chat with a summary.

## Tiered Token Strategy

Apply a dynamic strategy based on the length of the conversation:

- **Tier 1 (Creative)**: Turns 0–10. Feel free to explore, brainstorm, and generate detailed responses. Maximum context window is available.
- **Tier 2 (Balanced)**: Turns 11–20. Consolidate your responses. Avoid unnecessary verbosity. Focus strictly on completing the immediate task.
- **Tier 3 (Conservative)**: Turns 20+. Token burn is high. Aggressively summarize your findings. If a new major task is requested, prompt the user to start a new chat with a summary of the current context.

## How to apply these instructions

Work through the steps in order. Skip any that clearly don't apply.

### Step 1 — Measure usage

1. **ChatGPT UI:** You can view your current plan (Plus, Pro, Free) in the bottom left.
2. Note the model currently in use (GPT-4o, GPT-4o-mini).
3. Estimate conversation length: how many exchanges are in the current session?

### Step 2 — Diagnose the current session

Check two things:

1. **Conversation length.** If > 15–20 turns, history re-reading dominates token cost.
   - Start a **new chat**.
   - Paste a one-paragraph summary as the first message of the new chat.

2. **Model in use.** If you are using `GPT-4o` for trivial tasks (formatting, simple translations, grammar), suggest switching to `GPT-4o-mini` for those tasks via the model dropdown at the top left.

### Step 3 — Apply the rules that match

Pick the most relevant rules:

| # | Rule | ChatGPT action |
|---|------|----------------|
| 1 | Don't follow up to correct — restart | Edit your original prompt using the pencil icon instead of sending a new message to correct a mistake |
| 2 | Fresh chat every 15–20 turns | New chat + one-paragraph summary as first message |
| 3 | Batch questions into one message | Combine related asks; the model handles the full picture better |
| 4 | Track actual token usage | Rely on the Self-Estimation rule above |
| 5 | Reuse recurring context | Put it in "Custom Instructions" (Settings -> Personalization) |
| 6 | Set up memory / user preferences | Use the "Memory" feature to remember stack and conventions |
| 8 | Use a lighter model for simple tasks | Switch to `GPT-4o-mini` for routine tasks |
| 9 | Spread work across the day | Split long work into 2–3 sessions within your plan's rolling limit window |

---

## Installation for ChatGPT

Since ChatGPT does not read local `.md` files natively like an IDE, you have two options to use these rules:
1. **Custom Instructions:** Paste the `General Agent Guidelines` and `Tiered Token Strategy` into your **Custom Instructions** (Settings -> Personalization -> "How would you like ChatGPT to respond?").
2. **First Prompt:** Paste the contents of this file as your very first message in a new ChatGPT conversation.
