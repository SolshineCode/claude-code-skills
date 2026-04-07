---
name: gemini-collab
description: Delegate subtasks to Gemini (via Gemini CLI) to save Claude tokens. Gemini is a capable cloud model with free credits via Google subscription. Use for web research, large-file analysis, documentation generation, code review second opinions, and tasks where Gemini's 1M token context or Google ecosystem integration adds value. Less capable than Claude for complex reasoning but free and fast. TRIGGER when working on long autonomous tasks where parts can be offloaded.
allowed-tools: Bash, Read, Write, Glob, Grep
effort: high
---

# Gemini CLI Collaboration

You can delegate subtasks to Google's Gemini model via the locally installed Gemini CLI. Gemini runs in the cloud with free credits from the user's Google subscription — no API costs, no local GPU load.

**Gemini is less capable than Claude for complex reasoning, architecture decisions, and nuanced debugging.** But it's free, fast, has a 1M token context window, and excels at certain tasks. Use it to save Claude tokens on work that doesn't require Claude-level ability.

## When to Delegate to Gemini (vs Nemotron vs Claude)

### Gemini's Sweet Spots (prefer Gemini for these)
- **Large-file analysis** — 1M context means you can send entire codebases or massive logs without chunking
- **Documentation generation** — writing README sections, API docs, inline comments for large files
- **Code review / second opinion** — get a quick independent review before committing
- **Web-connected research** — Gemini has built-in Google Search grounding
- **Boilerplate and scaffolding** — generating repetitive code from patterns
- **Data transformation** — reformatting CSV/JSON, schema migrations, config conversions
- **Test generation** — writing unit tests for existing functions
- **Summarization** — condensing long documents, PRs, or discussions

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

## How to Call Gemini

### Basic headless call:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" \
  --prompt "YOUR PROMPT HERE" \
  --timeout 300
```

### With tool use (Gemini can read/write files, run commands):
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" \
  --prompt "YOUR PROMPT HERE" \
  --yolo \
  --cwd "/path/to/project"
```

### With specific model:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" \
  --prompt "YOUR PROMPT HERE" \
  --model gemini-2.5-flash
```

### Check readiness:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/gemini_client.py" --check-only
```

### Direct Gemini CLI (alternative):
```bash
gemini -p "YOUR PROMPT" -o text
gemini -p "YOUR PROMPT" --yolo          # with tool use auto-approved
gemini -p "YOUR PROMPT" -m gemini-2.5-pro  # use Pro model
```

## Model Selection

| Model | Best For | Notes |
|-------|----------|-------|
| `gemini-2.5-flash` (default) | Most tasks, fast | Good balance of speed and quality |
| `gemini-2.5-pro` | Complex reasoning, large context | Slower but higher quality |

## Collaboration Protocol

1. **Provide full context inline.** Gemini has no access to your conversation. Include:
   - All relevant code/data in the prompt
   - Clear instructions and expected output format
   - Constraints (language, style, framework conventions)

2. **Use `--yolo` carefully.** This lets Gemini read/write files and run commands autonomously. Only use when:
   - The task requires file system access (e.g., "read all .py files in src/ and generate type stubs")
   - You trust the operation is safe
   - Use `--sandbox` for untrusted operations

3. **Validate the output.** Always review before integrating:
   - Check code for correctness and style consistency
   - Verify factual claims (Gemini can hallucinate)
   - If output quality is poor, do it yourself — don't retry more than once

4. **Report the delegation.** Tell the user when you've used Gemini:
   - "Delegated test generation to Gemini (saved ~5K Claude tokens)"
   - Include Gemini's output with any needed corrections

## Example Delegation Patterns

### Generate tests for a file:
```bash
gemini -p "$(cat <<'EOF'
Read the following Python function and generate comprehensive pytest tests for it.
Include edge cases, error cases, and happy path tests. Output ONLY the test code.

```python
$(cat src/my_module.py)
```
EOF
)" -o text
```

### Summarize a large log file:
```bash
gemini -p "Summarize the errors and warnings in these Fly.io logs. Group by category. Be concise.

$(fly logs -n 200 2>/dev/null)" -o text
```

### Code review a diff:
```bash
gemini -p "Review this git diff for bugs, security issues, and style problems. Be concise, list only real issues.

$(git diff main...HEAD)" -o text
```

### Generate documentation:
```bash
gemini -p "Generate a README section describing this module's API. Use markdown. Include usage examples.

$(cat src/api.py)" -o text
```

## Piping File Content

For large files, pipe content via stdin combined with the prompt:
```bash
cat large_file.py | gemini -p "Analyze this code and list all public functions with their signatures and a one-line description."
```

## Limits

- **Cold start ~35-40s** — Gemini CLI loads extensions and MCP servers on startup. The first call in a session will be slow. Use `--timeout 120` minimum for cold calls; subsequent calls in the same minute are faster.
- **Requires internet** — cloud-based model, won't work offline
- **Auth required** — user must have run `gemini` interactively once to complete Google OAuth. If you get exit code 41, tell the user to run `! gemini` to authenticate.
- **Rate limits** — free tier has quota limits; if you hit them, fall back to Nemotron or do it yourself
- **Quality** — strong but not Claude-level for complex reasoning or nuanced tasks
- **Hallucination risk** — verify factual claims, especially about APIs or library behavior
- **No conversation memory** — each `-p` call is stateless; include all context every time
