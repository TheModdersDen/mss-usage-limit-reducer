# usage-limit-reducer

Stop burning through your AI coding assistant's usage limit — for **Claude Code**,
**Cursor AI**, **GitHub Copilot**, **Google Gemini Code Assist / Firebase Studio**,
**Grok**, and any other agent that can follow a Markdown instruction file.

AI agents re-read the entire conversation on every turn. One developer measured it:
**98.5% of his tokens went to re-reading history, only 1.5% to generating
responses.** This skill diagnoses where your tokens are actually going and applies
11 rules for cutting usage — using real data where available (Claude Code JSONL logs)
or your agent's usage dashboard for other tools.

## What it does

When you trigger the skill, it:

1. **Measures** — runs `scripts/usage-report.py` against local logs (Claude Code) or
   directs you to your agent's usage dashboard.
2. **Diagnoses** the current session — conversation length, instructions-file presence,
   model in use.
3. **Applies** the 2–4 rules most relevant to what it finds. No dumping all 11 on you.
4. **Suggests** concrete next actions and acts only on confirmation.

## Install

### Claude Code

```bash
git clone <this-repo> ~/.claude/skills/usage-limit-reducer
```

Or, if you already cloned it elsewhere:

```bash
cp -r . ~/.claude/skills/usage-limit-reducer/
```

Restart Claude Code. It will show up in the skills list and auto-trigger on phrases like:

- "hit my limit" / "usage limit" / "running out of tokens"
- "save tokens" / "reduce usage" / "am I wasting tokens"
- "this chat is getting long"
- "which model should I use"

You can also invoke it directly: `/usage-limit-reducer`.

---

### Cursor AI (Composer)

Cursor reads project rules from `.cursor/rules/*.mdc` files.

1. Clone or download this repo.
2. Copy the Cursor rules file into your project:
   ```bash
   mkdir -p .cursor/rules
   cp .agents/cursor/usage-limit-reducer.mdc .cursor/rules/
   ```
3. For a **global** rule (applies to all projects), copy it to:
   ```bash
   mkdir -p ~/.cursor/rules
   cp .agents/cursor/usage-limit-reducer.mdc ~/.cursor/rules/
   ```
4. Restart Cursor. The rule will be available in Composer and will auto-trigger on the
   phrases listed in the file's `description` field.

**Alternative — `.cursorrules` (legacy format):**
```bash
cat .agents/cursor/usage-limit-reducer.mdc >> .cursorrules
```

---

### GitHub Copilot (VS Code · JetBrains · Xcode)

GitHub Copilot reads workspace-level instructions from `.github/copilot-instructions.md`.

**VS Code / JetBrains:**

1. Clone or download this repo.
2. Copy the Copilot instructions file into your project:
   ```bash
   mkdir -p .github
   cp .agents/github-copilot/usage-limit-reducer.md .github/copilot-instructions.md
   ```
   If `.github/copilot-instructions.md` already exists, append the content:
   ```bash
   cat .agents/github-copilot/usage-limit-reducer.md >> .github/copilot-instructions.md
   ```
3. Commit the file so all collaborators benefit.
4. In VS Code you can also add workspace-level inline instructions:
   - Open **Settings** → search for `github.copilot.chat.codeGeneration.instructions`
   - Add `{ "file": ".github/copilot-instructions.md" }` to the list.

**Xcode (via GitHub Copilot for Xcode):**

1. Install [GitHub Copilot for Xcode](https://github.com/github/CopilotForXcode) via
   the GitHub Copilot installer or directly from the repository.
2. Once installed, Copilot for Xcode reads the same `.github/copilot-instructions.md`
   from your repository root — follow the VS Code steps above.
3. Alternatively, paste the content of `.agents/github-copilot/usage-limit-reducer.md`
   into the **Custom Instructions** field in **Xcode → Settings → GitHub Copilot**.

> **Note:** Xcode does not have a built-in first-party AI coding assistant. GitHub
> Copilot for Xcode is currently the primary way to bring AI coding assistance into
> Xcode. Apple Intelligence features in Xcode are separate and do not currently support
> custom skill/instruction files.

---

### Google Gemini Code Assist / Firebase Studio (Google's AI-first IDE)

Gemini Code Assist reads project-level instructions from `GEMINI.md` at the project
root, and user-level instructions from `~/.gemini/GEMINI.md`.

**Firebase Studio (formerly Project IDX):**

1. Clone or download this repo.
2. Copy the Gemini instructions file into your project:
   ```bash
   cp .agents/gemini/usage-limit-reducer.md GEMINI.md
   ```
   If `GEMINI.md` already exists, append:
   ```bash
   cat .agents/gemini/usage-limit-reducer.md >> GEMINI.md
   ```
3. For **user-level** instructions (all projects):
   ```bash
   mkdir -p ~/.gemini
   cp .agents/gemini/usage-limit-reducer.md ~/.gemini/GEMINI.md
   ```
4. Open or reload your project in Firebase Studio / VS Code with Gemini Code Assist.
   The instructions will be picked up automatically.

---

### xAI Grok

Grok does not currently have a native IDE plugin with an instructions-file convention.
Use the universal fallback:

1. Copy the universal agent file into your project:
   ```bash
   cp .agents/universal/AGENT.md AGENTS.md
   ```
2. At the start of each Grok session, paste the content of `AGENTS.md` (or reference
   it) as a system prompt or first message.
3. For API usage, pass the content of `.agents/grok/usage-limit-reducer.md` as the
   `system` parameter in your API call.

---

### Any other agent (universal fallback)

For any agent not listed above:

```bash
cp .agents/universal/AGENT.md AGENTS.md
```

The `AGENTS.md` file at the project root is a broadly recognized convention for
AI agent instructions. Many modern agents (including OpenAI Codex, Amazon Q Developer,
and others) will pick it up automatically. If your agent doesn't, paste its content as
a system prompt or first message.

## Standalone: the token report

The script is useful on its own, outside the skill:

```bash
python3 ~/.claude/skills/usage-limit-reducer/scripts/usage-report.py --days 7
python3 ~/.claude/skills/usage-limit-reducer/scripts/usage-report.py --days 30 --project myrepo
python3 ~/.claude/skills/usage-limit-reducer/scripts/usage-report.py --json   # machine-readable
```

Example output:

```
Claude Code usage — last 7 day(s)
------------------------------------------------------------------------
Turns:        110
Input:        274 fresh  +  6.16M cache-read  +  934.3K cache-write
Output:       152.9K
Cache hit:    86.8% of input tokens came from cache
Estimated $:  ~$38.22 (API list prices; subscription is flat)

By model (top by cost):
  claude-opus-4-7     turns= 109  in=   274  out= 152.9K  cache_r= 6.16M (86.8%)  ~$38.22

Heuristics:
  - Cache hit is 86.8% — healthy.
  - Opus is 100% of spend. Consider Haiku (/model claude-haiku-4-5) for simple edits.
```

**What's read:** every JSONL file under `~/.claude/projects/`. **What leaves your machine:** nothing. No network calls.

**Pricing note:** the `$` figure uses API list prices as a relative-comparison tool. If you're on a Claude Code subscription plan, billing is flat — treat the number as "what this would cost on the API."

## The 11 rules, and what each maps to

| # | Rule | Claude Code action | Generic / other agent action |
|---|------|--------------------|------------------------------|
| 1 | Don't follow up to correct — restart | `/clear` + re-prompt | Start a new conversation with an improved prompt |
| 2 | Fresh chat every 15–20 turns | `/compact` or `/clear` + paste summary | New session + one-paragraph summary |
| 3 | Batch questions into one message | Combine related asks into one prompt | Same |
| 4 | Track actual token usage | **`scripts/usage-report.py`** — reads local JSONL logs | Agent's usage dashboard |
| 5 | Reuse recurring context | `CLAUDE.md`, skills, `.context/` | Agent's instructions file |
| 6 | Set up memory / user preferences | Create/update `CLAUDE.md` | Create/update the agent instructions file |
| 7 | Turn off features you don't use | Audit `~/.claude/settings.json` for unused MCPs/hooks | Disable unused IDE extensions and tool integrations |
| 8 | Use a lighter model for simple tasks | `/model claude-haiku-4-5` | Switch to the lightest available model in your agent |
| 9 | Spread work across the day | Split into 2–3 sessions (5-hour rolling window) | Same for most agent plans |
| 10 | Work off-peak | Peak is 5–11am PT / 8am–2pm ET weekdays | Evenings and weekends stretch shared-compute plans |
| 11 | Enable overage / pay-as-you-go | Settings → Usage on Claude Pro/Max | Check your agent's plan settings |

**Not fully implementable in any agent** (flagged honestly by the skill):

- Rule #1's "edit the original prompt" is a claude.ai / chat-UI-only feature. In IDEs the equivalent is clear + re-send.
- Rule #5's "upload to Projects" is web-only — use the agent's instructions file instead.
- Rule #11's overage toggle is plan-level.

## Layout

```
usage-limit-reducer/
├── SKILL.md                  # skill instructions (agent-agnostic, Claude Code first)
├── README.md                 # this file (for humans)
├── .agents/
│   ├── README.md             # index of agent-specific files
│   ├── claude/
│   │   └── SKILL.md          # original Claude Code skill (unchanged)
│   ├── cursor/
│   │   └── usage-limit-reducer.mdc   # Cursor AI Composer rules
│   ├── github-copilot/
│   │   └── usage-limit-reducer.md    # GitHub Copilot instructions
│   ├── gemini/
│   │   └── usage-limit-reducer.md    # Google Gemini Code Assist / Firebase Studio
│   ├── grok/
│   │   └── usage-limit-reducer.md    # xAI Grok
│   └── universal/
│       └── AGENT.md          # agent-agnostic fallback (use as AGENTS.md)
└── scripts/
    ├── usage-report.py       # local Claude Code token dashboard
    └── test_usage_report.py  # 16 unit + CLI tests
```

## Tests

```bash
python3 scripts/test_usage_report.py
```

Covers price lookups, aggregation math, `--days` cutoff, `--project` filter, malformed-JSONL handling, CLI text/JSON output, and a regression test for the `defaultdict(lambda: dict(totals))` shared-state bug.

## Credit

The 11 rules are from Dubi's article. This skill wires them into multiple AI coding
assistants with real measurement where available.
