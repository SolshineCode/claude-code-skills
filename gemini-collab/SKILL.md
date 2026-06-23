---
name: gemini-collab
description: Delegate subtasks to Google's Gemini 3.5 Flash (and other Google models) via Antigravity CLI to save Claude tokens. Antigravity is a capable cloud model with free credits via Google AI Pro subscription. Use for web research, large-file analysis, documentation generation, code review second opinions, and tasks where Gemini's long context window or Google ecosystem integration adds value. Less capable than Claude for complex reasoning but free and fast. TRIGGER when working on long autonomous tasks where parts can be offloaded.
allowed-tools: Bash, Read, Write, Glob, Grep
effort: high
---

# Antigravity CLI Collaboration (formerly gemini-cli)

You can delegate subtasks to Google's models via the locally installed **Antigravity CLI** (`agy`). Antigravity runs in the cloud with free credits from the user's Google AI Pro subscription — no API costs, no local GPU load.

**Antigravity is the successor to the now-deprecated `gemini` CLI** (2026-05-23). The legacy `gemini` binary still works briefly but is scheduled to stop working this month. Default model: **Gemini 3.5 Flash (Medium)**.

**Antigravity is less capable than Claude for complex reasoning, architecture decisions, and nuanced debugging.** But it's free, fast, and excels at certain tasks. Use it to save Claude tokens on work that doesn't require Claude-level ability.

## When to Delegate to Antigravity (vs Nemotron vs Claude)

### Antigravity's Sweet Spots (prefer Antigravity for these)
- **Large-file analysis** — large context means you can send entire codebases or massive logs without chunking
- **Documentation generation** — writing README sections, API docs, inline comments for large files
- **Code review / second opinion** — get a quick independent review before committing
- **Web-connected research** — Antigravity has built-in Google Search grounding
- **Boilerplate and scaffolding** — generating repetitive code from patterns
- **Data transformation** — reformatting CSV/JSON, schema migrations, config conversions
- **Test generation** — writing unit tests for existing functions
- **Summarization** — condensing long documents, PRs, or discussions
- **Bulk labeling for ML datasets** — fast tier (`gemini-2.5-flash`) labels at ~36 rows/sec via parallelized subprocess

### Use Nemotron Instead When
- No internet connection is available
- GPU is free and you want zero-latency for simple tasks
- Privacy matters (data stays local)
- The task is very simple (< 100 tokens output)

### Keep for Claude When
- Complex multi-step reasoning across files
- Architecture and design decisions
- Security-sensitive code review
- Debugging subtle bugs
- Tasks requiring deep codebase context already in the conversation
- Anything the user specifically asked Claude to do

## Authentication & engine (load-bearing — read this first)

**Two working engines on this Windows machine (verified 2026-06-03):**

1. **Legacy `gemini` CLI via STDIN — the DEFAULT for general tasks/labeling.** Authenticated, fast, reliable. Resolve it with `shutil.which("gemini")` (it's an npm `.CMD` shim at `…/AppData/Roaming/npm/gemini`). `subprocess.run` with the resolved path executes it.
2. **Antigravity `agy` (Gemini 3.5 Flash) via a ConPTY — use `--engine agy` when you specifically want Antigravity / Gemini 3.5 Flash.** See the ConPTY note below.

### Legacy gemini specifics
- **Use STDIN, not `-p` argv, for large prompts.** `gemini -m gemini-2.5-flash -p "<prompt>"` is unreliable for large prompts (observed to silently return empty above ~1–2k chars on some runs). Piping via STDIN in interactive mode with NO `-p` flag is reliable for ANY size:
  ```python
  subprocess.run([gemini_bin, "-m", "gemini-2.5-flash"],
                 input=prompt, capture_output=True, text=True,
                 encoding="utf-8", errors="replace", timeout=...)
  ```
- **Strip the preamble.** stdout starts with warning lines that must be removed before use: lines containing `Warning: True color`, `Ripgrep is not available`, `YOLO mode`, `Loaded cached`. Real content (often wrapped in a ```json fence for structured prompts) follows. The wrapper strips these automatically.
- **Nondeterminism:** the gemini CLI occasionally ignores a terse instruction and emits a verbose off-script answer. Validate output; retry once if it's clearly not an answer.

### CORRECTED: `agy` auth is NOT broken — it's a TTY-output problem (2026-06-03)
Earlier versions of this skill claimed "`agy` subprocess auth FAILS / returns empty." **That diagnosis was wrong.** Direct inspection of agy's own log (`--log-file`) during a subprocess `--print` call shows:
- `Auth done received` → **auth succeeds**
- `…/v1internal:streamGenerateContent` → **the real model API is called**
- `text_drip.go: Drip stopped: length=N` → **a non-empty response is generated**

The response is real; it just never reaches a captured pipe because **`agy` renders its answer only to a real console via an animated "text drip."** A plain pipe gets nothing and the process often hangs waiting on a console. **The fix is a pseudo-console (ConPTY).** `scripts/agy_pty.py` drives `agy --print` under a ConPTY via **pywinpty** and captures the output reliably (verified: correct answers across many consecutive single-process calls; model self-identifies as "Antigravity… built by Google DeepMind", backend label `Gemini 3.5 Flash (Medium)`).
- **Dependency:** `pywinpty` (present in the default python here; install with `pip install pywinpty` if missing).
- **Run agy from a small/empty CWD, never the home root** (`C:\Users\<user>`) — it hangs indexing the whole home workspace. `agy_pty.py` defaults its cwd to `%LOCALAPPDATA%\agy\_runcwd`.
- **`agy --print` must include `--dangerously-skip-permissions`** or print mode blocks on an interactive permission prompt. `agy_pty.py` always adds it.

The `gemini_client.py` wrapper handles all of the above. Call it with `--prompt`; it returns the response. Force a backend with `--engine gemini` (legacy stdin, default-preferred) or `--engine agy` (Antigravity via ConPTY).

## How to Call Antigravity

### Basic headless call (preferred):
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" \
  --prompt "YOUR PROMPT HERE" \
  --timeout 300
```

The wrapper defaults to the legacy `gemini` CLI via STDIN (works for prompts of any size, strips the warning preamble automatically) and falls back to `agy` only if `gemini` isn't found. Default model: `gemini-2.5-flash`. For large/structured prompts, prefer passing the prompt via a temp file or `--prompt "$(cat prompt.txt)"` — the wrapper pipes it through STDIN internally so size is not a concern.

### Force a backend engine:
```bash
# Force legacy gemini (default-preferred):
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" --prompt "..." --engine gemini
# Use Antigravity / Gemini 3.5 Flash (driven under a ConPTY — works reliably):
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" --prompt "..." --engine agy
```

### Antigravity (Gemini 3.5 Flash) via ConPTY:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" \
  --prompt "YOUR PROMPT HERE" \
  --engine agy --timeout 90
```

The `agy` engine always runs with `--dangerously-skip-permissions` (required for non-interactive print mode) under a ConPTY. `--yolo`/`--sandbox` are accepted for API stability but ignored on this path. The `--engine agy` wrapper path is tuned for a SINGLE-TURN text answer (short idle cutoff). For a real multi-step AGENTIC run (download/parse/upload, file edits, shell), do NOT use the wrapper — call `agy_pty.py` directly with a high idle (see next section). One call per process — the helper spawns a fresh `agy` each time.

### Running `agy` AGENTICALLY (multi-step tool-use) — verified 2026-06-22

`agy --print "<task>" --dangerously-skip-permissions` is NOT just one text turn: it runs a full
agentic loop (reads/writes files, runs shell commands, calls APIs) to completion, then exits.
Earlier docs calling it "prompt→response only" were wrong.

**The gotcha that truncates agentic runs:** `agy_pty.py`'s default `--idle 1` terminates `agy` as
soon as its visible output stops growing for 1s. During a real task `agy` pauses output every time
it executes a tool (a download, a parse) — so the idle cutoff kills it right after its first
narration line (e.g. "I will start by listing the directory…"). That's why agentic runs looked
like they "went agentic and returned nothing."

**To drive a full agentic task to completion:**
```bash
# 1. Scoped, SMALL work dir with a task spec (never run agy from the home root).
mkdir -p /c/Users/caleb/work/agy_job
#    write /c/Users/caleb/work/agy_job/TASK.md with the full instructions + URLs + recipe.
# 2. Put secrets in the ENV (inherited by the spawned agy) — NEVER inline them in the prompt/argv.
export HF_TOKEN='...'; export PYTHONIOENCODING=utf-8 PYTHONUTF8=1
# 3. Short prompt that points agy at TASK.md; HIGH --idle so tool pauses don't cut it off,
#    HIGH --timeout as the hard cap. The loop exits naturally when agy finishes (pty.isalive()=False).
echo "Read TASK.md in the current directory and carry out every step autonomously, end to end. Report what you did." \
  | python "${CLAUDE_SKILL_DIR}/scripts/agy_pty.py" --idle 900 --timeout 3600 --cwd /c/Users/caleb/work/agy_job
```

Rules of thumb:
- **Idle ≥ the longest expected tool pause** (downloads/parses): 600–900s is safe; the default 1s is only for single-turn text.
- **Timeout = hard wall-clock cap** for the whole task (e.g. 3600s). Run it `run_in_background`.
- **Prompt via a TASK.md file, not a giant argv string** — avoids Windows argv length limits and the helper's quote-neutralization mangling. Keep the stdin prompt to one line: "read TASK.md and execute."
- **Secrets go in the environment**, never in the prompt (it's logged and embedded in argv).
- **ALWAYS verify the result yourself afterward** (inspect the repo / files it touched). `agy` is Gemini 3.5 Flash — expect partial success on long autonomous chains; it may skip steps, hallucinate URLs, or stop early. Treat its final report as a claim to check, not ground truth.
- This is powerful + autonomous (skip-permissions). Scope the work dir, give bounded instructions, and don't hand it destructive capability you wouldn't run yourself.

### Direct CLI (alternative):
```bash
# PREFERRED — legacy gemini via stdin (any prompt size):
printf '%s' "YOUR PROMPT" | gemini -m gemini-2.5-flash
# Antigravity (Gemini 3.5 Flash) — needs a ConPTY, so go through the helper:
echo "YOUR PROMPT" | python "${CLAUDE_SKILL_DIR}/scripts/agy_pty.py" --timeout 90
# (Raw `agy --print "..."` into a pipe returns empty — TTY-only drip output. Use winpty/ConPTY.)
```

## Model Selection

- **Legacy `gemini` engine (default):** serves `gemini-2.5-flash`. Pass `--model` to override (note `gemini-3.5-flash` is NOT valid on the legacy CLI — 404).
- **Antigravity `agy` engine (`--engine agy`):** serves Gemini 3.5 Flash (Medium). Other models (3.5 Pro, etc.) are selected via plugins or the interactive `/model` slash command, not a CLI flag. For most labeling/research tasks the default is correct.

## Collaboration Protocol

1. **Provide full context inline.** Antigravity has no access to your conversation. Include:
   - All relevant code/data in the prompt
   - Clear instructions and expected output format
   - Constraints (language, style, framework conventions)

2. **Use `--dangerously-skip-permissions` carefully.** This lets Antigravity read/write files and run commands autonomously. Only use when:
   - The task requires file system access (e.g., "read all .py files in src/ and generate type stubs")
   - You trust the operation is safe
   - Use `--sandbox` for untrusted operations

3. **Validate the output.** Always review before integrating:
   - Check code for correctness and style consistency
   - Verify factual claims (Antigravity can hallucinate)
   - If output quality is poor, do it yourself — don't retry more than once

4. **Report the delegation.** Tell the user when you've used Antigravity:
   - "Delegated test generation to Antigravity (saved ~5K Claude tokens)"
   - Include the output with any needed corrections

## Example Delegation Patterns

### Generate tests for a file:
```bash
"$LOCALAPPDATA/agy/bin/agy.exe" --print "$(cat <<'EOF'
Read the following Python function and generate comprehensive pytest tests for it.
Include edge cases, error cases, and happy path tests. Output ONLY the test code.

```python
$(cat src/my_module.py)
```
EOF
)"
```

### Summarize a large log file:
```bash
"$LOCALAPPDATA/agy/bin/agy.exe" --print "Summarize the errors and warnings in these Fly.io logs. Group by category. Be concise.

$(fly logs -n 200 2>/dev/null)"
```

### Code review a diff:
```bash
"$LOCALAPPDATA/agy/bin/agy.exe" --print "Review this git diff for bugs, security issues, and style problems. Be concise, list only real issues.

$(git diff main...HEAD)"
```

### Generate documentation:
```bash
"$LOCALAPPDATA/agy/bin/agy.exe" --print "Generate a README section describing this module's API. Use markdown. Include usage examples.

$(cat src/api.py)"
```

## Limits

- **Auth** — both engines are authenticated on this machine, no extra setup needed. Legacy `gemini` is the default; `--engine agy` reaches Antigravity (Gemini 3.5 Flash) via the ConPTY helper (`scripts/agy_pty.py`, needs `pywinpty`). agy auth is fine — the only reason naive `agy --print` looks empty is its TTY-only "text drip" output, which the ConPTY helper solves.
- **Do NOT blanket-kill node processes.** Some guides advise `Get-Process node | Stop-Process -Force` to clear orphaned gemini shims. On this machine long-lived `node` processes are MCP servers (comet-bridge, claude-in-chrome) and killing them all breaks the running Claude session. Kill orphaned shims by specific PID only.
- **Cold start time** — Antigravity CLI loads workspace context on startup; first call in a session is slower. Use `--print-timeout 5m0s` minimum for cold calls.
- **Requires internet** — cloud-based model, won't work offline
- **Rate limits** — Google AI Pro tier has quota limits; if you hit them, fall back to Nemotron or do it yourself. (Note: the old gemini-cli `gemini-2.5-pro` model hit a 19h quota wall during the 2026-05-23 bulk labeling run; the `gemini-2.5-flash` alias was on a separate, much larger Flash quota.)
- **Quality** — strong but not Claude-level for complex reasoning or nuanced tasks
- **Hallucination risk** — verify factual claims, especially about APIs or library behavior
- **No conversation memory** — each `--print` call is stateless; include all context every time

## Provenance Note (2026-05-23)

**CORRECTED 2026-06-02 (was wrong before):** the legacy `gemini -m gemini-2.5-flash` CLI serves **`gemini-2.5-flash`**, NOT "Gemini 3.5 Flash". Verified empirically via the CLI's own usage telemetry (`gemini ... --output-format json` → `stats.models` keys the request under `gemini-2.5-flash`, the billed/served model — not a self-report). As of June 2026 the Gemini API lists `gemini-2.5-flash` and `gemini-3.5-flash` as **separate stable models**; the alias is NOT silently upgraded. The "Gemini 3.5 Flash (Medium)" label belongs to the **Antigravity (`agy`) CLI** — a *different* tool/model from the legacy-CLI labeler. Do not trust model self-reports OR the agy banner when recording the **legacy-CLI** labeler. **Record `gemini-2.5-flash` as the labeler in any data card / model card / publication that used the legacy `gemini` CLI.** (Update 2026-06-03: `agy` IS reachable from a subprocess after all — via the ConPTY helper — and its backend label is confirmed `Gemini 3.5 Flash (Medium)`. So if you deliberately label via `--engine agy`, record **`gemini-3.5-flash` (Antigravity)** instead. The two engines serve different models; attribute to whichever you actually ran.)

## Migration Status (2026-05-23)

- **Legacy `gemini-cli`** (npm `@google/gemini-cli`) was slated for deprecation in 2026-05 but **is still authenticated and working as of 2026-06-03** — it remains the wrapper's default engine. Watch for it to stop; if it does, switch the default to `--engine agy`.
- **Antigravity CLI** (`agy.exe`, `$LOCALAPPDATA/agy/bin/`) is the forward path, reachable via `--engine agy` (ConPTY helper `scripts/agy_pty.py`).
- **Wrapper script:** `scripts/gemini_client.py` — `--engine gemini` (legacy stdin, default) or `--engine agy` (Antigravity via ConPTY). `auto` tries gemini then falls back to agy.

## Gmail via Antigravity: Warnings

Antigravity has Gmail MCP access (inherited from the prior gemini-cli MCP config) and can READ email threads well. Use it for inbox research and summarization.

**CRITICAL — Gmail SEND is dangerous with Antigravity in `--dangerously-skip-permissions` mode:**
- Antigravity in skip-permissions mode WILL autonomously execute gmail_sender.py and send emails without user approval if it decides to. This happened in production with the prior gemini-cli and caused two unauthorized midnight emails to an Anthropic recruiter.
- **Always get explicit user approval before any send operation.** Show the exact formatted email body. Never pass a send command to Antigravity until the user says "go."
- **Newline handling is buggy:** When passing email body as a shell argument, `\n` is passed as a literal backslash-n unless `json.loads(f'"{body}"')` is used in the script. Always verify formatting before sending — test with a draft or BCC first.
- **Safe Antigravity Gmail use:** reading threads, searching inbox, extracting contact info, summarizing correspondence history.
- **Unsafe Antigravity Gmail use:** autonomous sends, any email with formatted content like bullet points or paragraphs (prone to garbling).
