---
name: gemini-collab
description: Delegate subtasks to Google's Gemini models via the Antigravity CLI (agy) to save Claude tokens. Antigravity is a capable cloud agent with free credits via a Google AI Pro subscription. Use for web research, large-file analysis, documentation generation, code review second opinions, and tasks where Gemini's long context window or Google ecosystem integration adds value. Less capable than Claude for complex reasoning but free and fast. TRIGGER when working on long autonomous tasks where parts can be offloaded.
allowed-tools: Bash, Read, Write, Glob, Grep
effort: high
---

# Antigravity CLI Collaboration

Delegate subtasks to Google's models via the **Antigravity CLI** (`agy`). Antigravity
runs in the cloud with free credits from a Google AI Pro subscription — no API costs,
no local GPU load.

> **The legacy `gemini` CLI is DEAD.** As of 2026-07-19 the standalone Gemini CLI
> (npm `@google/gemini-cli`) is unsupported and its login is blocked — Google requires
> Antigravity. Never install or invoke `gemini`; `agy` is the only engine in this
> skill. Direct headless `agy` calls were validated on Linux on 2026-07-19.

**Antigravity is less capable than Claude for complex reasoning, architecture
decisions, and nuanced debugging.** But it's free, fast, and excels at certain tasks.
Use it to save Claude tokens on work that doesn't require Claude-level ability.

## When to Delegate to Antigravity

### Sweet spots (prefer Antigravity for these)
- **Large-file analysis** — long context takes whole codebases or massive logs without chunking
- **Documentation generation** — README sections, API docs, inline comments for large files
- **Code review / second opinion** — quick independent review before committing
- **Web-connected research** — built-in Google Search grounding
- **Boilerplate and scaffolding** — repetitive code from patterns
- **Data transformation** — reformatting CSV/JSON, schema migrations, config conversions
- **Test generation** — unit tests for existing functions
- **Summarization** — condensing long documents, PRs, or discussions
- **Image generation** — but use the dedicated `nano-banana` skill for that

### Use a local model instead when
- No internet connection is available
- Privacy matters (data must stay local)
- The task is trivial and a local model is already loaded

### Keep for Claude when
- Complex multi-step reasoning across files
- Architecture and design decisions
- Security-sensitive code review
- Debugging subtle bugs
- Tasks requiring deep codebase context already in the conversation
- Anything the user specifically asked Claude to do

## Setup Check

```bash
agy --help >/dev/null && agy models
```

A model list (Gemini 3.5 Flash tiers, Gemini 3.1 Pro, ...) means auth is good. If it
prompts for login, stop and ask the user to authenticate interactively once — that is
their action, not yours.

## How to Call Antigravity (Linux/macOS)

Single-turn headless call:

```bash
timeout 300 agy -p "YOUR PROMPT HERE" \
  --model "Gemini 3.5 Flash (Medium)" \
  --dangerously-skip-permissions
```

- `-p/--print` runs non-interactively and prints the final response.
- **`--dangerously-skip-permissions` is required in print mode** — agy auto-denies
  tool permission prompts it cannot show, and the run dies with "a tool required the
  command permission" without it. (Alternatively, pre-configure allow-rules in agy's
  settings.json.)
- `--model` selects the agent model; see `agy models` for the current list. Flash
  tiers for routine work, `"Gemini 3.1 Pro (High)"` when quality matters.
- First call after boot is slower (workspace indexing); add `--print-timeout 5m0s`
  for cold calls.
- Run from a small, scoped working directory — never from the home-directory root,
  which agy may try to index wholesale.

### Running agy AGENTICALLY (multi-step tool-use)

`agy -p "<task>" --dangerously-skip-permissions` is not just one text turn: it runs a
full agentic loop (reads/writes files, runs shell commands, calls APIs) to completion,
then exits.

Pattern for a real multi-step job:

```bash
# 1. Scoped, SMALL work dir with a task spec.
mkdir -p ~/work/agy_job && cd ~/work/agy_job
#    Write TASK.md with the full instructions + URLs + recipe.
# 2. Secrets go in the ENV (inherited by agy) — NEVER inline in the prompt/argv.
export SOME_TOKEN='...'
# 3. Short prompt pointing at TASK.md; generous hard cap; run in background.
timeout 3600 agy -p "Read TASK.md in the current directory and carry out every step autonomously, end to end. Report what you did." \
  --dangerously-skip-permissions
```

Rules of thumb:
- **Prompt via a TASK.md file, not a giant argv string** — avoids argv length limits
  and quoting bugs.
- **Secrets in the environment**, never the prompt (prompts get logged).
- **ALWAYS verify the result yourself afterward** (inspect the files/repos it
  touched). Expect partial success on long autonomous chains; it may skip steps,
  hallucinate URLs, or stop early. Its final report is a claim to check, not ground
  truth.
- **Outputs may land in agy's sandbox, not your cwd** — if a claimed output file is
  missing, check `~/.gemini/antigravity-cli/scratch/` and the newest
  `~/.gemini/antigravity-cli/brain/<session-uuid>/` before declaring failure.
- Skip-permissions mode is powerful and autonomous. Scope the work dir, give bounded
  instructions, and don't hand it destructive capability you wouldn't run yourself.

### Windows note

On Windows, raw piped `agy --print` output has historically come back empty (agy
renders via an animated console "text drip" that needs a real TTY) and agy hangs when
launched from the home-directory root. The bundled `scripts/agy_pty.py` drives agy
under a ConPTY (requires `pywinpty`) and captures output reliably; use a high
`--idle` (600–900s) for agentic runs so tool-execution pauses don't cut the session
short. Linux/macOS pipes work directly and need none of this.

## Collaboration Protocol

1. **Provide full context inline.** Antigravity has no access to your conversation.
   Include all relevant code/data, clear instructions, the expected output format,
   and constraints (language, style, framework conventions).
2. **Use `--dangerously-skip-permissions` deliberately.** It lets Antigravity
   read/write files and run commands autonomously. Scope the working directory and
   keep instructions bounded.
3. **Validate the output.** Check code for correctness and style; verify factual
   claims (it can hallucinate). If quality is poor, do it yourself — don't retry
   more than once.
4. **Report the delegation.** Tell the user when you've used Antigravity and include
   the output with any needed corrections.

## Example Delegation Patterns

Generate tests for a file:

```bash
timeout 300 agy -p "Generate comprehensive pytest tests for the following Python module. Include edge cases, error cases, and happy path. Output ONLY the test code.

$(cat src/my_module.py)" --dangerously-skip-permissions
```

Summarize a large log:

```bash
timeout 300 agy -p "Summarize the errors and warnings in these logs. Group by category. Be concise.

$(tail -n 500 app.log)" --dangerously-skip-permissions
```

Code review a diff:

```bash
timeout 300 agy -p "Review this git diff for bugs, security issues, and style problems. Be concise, list only real issues.

$(git diff main...HEAD)" --dangerously-skip-permissions
```

## Limits

- **Requires internet** — cloud-based, won't work offline.
- **Rate limits** — Google AI Pro tier has quotas; if you hit them, fall back to a
  local model or do the task yourself.
- **Quality** — strong but not Claude-level for complex reasoning or nuance.
- **Hallucination risk** — verify factual claims, especially about APIs or library
  behavior.
- **No conversation memory** — each `-p` call is stateless; include all context
  every time.
- **Do NOT blanket-kill node processes** to clean up CLI shims — long-lived `node`
  processes are often MCP servers backing the running Claude session. Kill orphans
  by specific PID only.

## Attribution Note (for datasets / model cards)

If agy output feeds a dataset, data card, or publication, record the **actual served
model** for the run (per `agy models` naming, e.g. `gemini-3.5-flash` via
Antigravity), not a guess and not the model's self-report. Historic runs made with
the retired legacy `gemini` CLI served `gemini-2.5-flash` and should stay attributed
that way.

## Email / Messaging Safety

If the Antigravity environment has email or messaging access (e.g. inherited MCP
configs), treat sending as OFF-LIMITS in skip-permissions mode: autonomous agents
have sent real, unapproved emails in production under exactly this setup. Read-only
use (searching, summarizing threads, extracting info) is fine. Never pass a send
instruction to agy; if an email needs sending, draft it, show the user the exact
body, and let them send it.
