---
name: nemotron-collab
description: Delegate subtasks to a local Nemotron model (via Ollama) to save Claude tokens. Use when you need file summarization, log analysis, boilerplate generation, code formatting, data extraction, or other grunt work that doesn't require Claude-level reasoning. TRIGGER when working on long autonomous tasks where parts can be offloaded.
allowed-tools: Bash, Read, Write, Glob, Grep
effort: high
---

# Local Nemotron 3 Collaboration

You have access to a local Nemotron 3 Nano 4B model running via Ollama. Use it to offload token-intensive grunt work during long autonomous tasks. This model has a 256K context window — much larger than typical small models.

**Nemotron is significantly less capable than both Claude and Gemini.** It's completely free (local), private (no data leaves the machine), works offline, and has zero latency for simple tasks. Use it ONLY for purely mechanical grunt work where accuracy of domain-specific content does not matter.

## CRITICAL: Known Quality Limitations (from real-world testing)

**Nemotron WILL hallucinate domain-specific terminology and technical details.** In testing, it:
- Expanded "SAE" as "Self-Attention" instead of "Sparse Autoencoder" in a research context
- Produced plausible-sounding but factually wrong technical definitions
- Generated text that looked correct at a glance but contained subtle inaccuracies

**Rules for safe delegation:**
1. **NEVER use Nemotron for content going into publications, papers, or documentation** where technical accuracy matters. Use Gemini or do it yourself.
2. **NEVER trust Nemotron's expansion of acronyms, technical terms, or domain jargon.** It will confidently hallucinate.
3. **NEVER use Nemotron for research analysis, literature review, or scientific reasoning.** The quality ceiling is too low.
4. **ALWAYS review every word** of Nemotron output before integrating it anywhere. Treat it as a rough draft that needs fact-checking, not a finished product.

## When to Delegate to Nemotron (vs Gemini vs Claude)

### Nemotron's ACTUAL Sweet Spots (strictly mechanical tasks)

**The sweet spot: "too annoying to script, too simple to waste Claude tokens on."**

- Reformatting code between styles (tabs→spaces, camelCase→snake_case, reindenting)
- Reshaping data (CSV→JSON, flattening nested structures, pivoting columns)
- Filling explicit templates with data (stamp out 20 similar test fixtures)
- Regex/pattern generation from clear examples
- Stripping/cleaning (remove comments, blank lines, HTML tags)
- Log extraction (find ERROR lines, extract timestamp + message — grep-like, not analytical)
- Generating test fixture data (dummy names, addresses, numbers)
- Any task where the output FORMAT matters more than content ACCURACY

### DO NOT Use Nemotron For (use Gemini or Claude instead)
- Writing documentation, READMEs, or any prose that will be published
- Explaining technical concepts (will hallucinate definitions)
- Research analysis or scientific reasoning
- Code review or architectural suggestions
- Any task requiring domain-specific knowledge
- Anything where a subtle factual error would be harmful
- Drafting text that will represent the user publicly

### Use Gemini Instead When
- The input is large (Gemini has 1M context vs Nemotron's 256K, and is faster)
- You need web search or Google ecosystem integration
- The task needs accurate, higher quality output (code review, documentation)
- Internet is available and speed matters
- Technical accuracy matters (Gemini is much more reliable on domain terms)

### Keep for Claude When
- Complex multi-step reasoning across files
- Architecture and design decisions
- Security-sensitive code
- Debugging subtle bugs
- Multi-file refactoring with interdependencies
- Anything requiring deep codebase context already in the conversation
- Anything the user specifically asked Claude to do

## How to Call Nemotron

```bash
python "${CLAUDE_SKILL_DIR}/scripts/nemotron_client.py" \
  --ensure-ready \
  --prompt "YOUR PROMPT HERE" \
  --system "YOU ARE A HELPFUL CODING ASSISTANT. Be concise." \
  --max-tokens 2048 \
  --temperature 0.3
```

The `--ensure-ready` flag auto-starts Ollama and pulls the model if needed — fully autonomous, no user intervention required.

### Check readiness without calling:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/nemotron_client.py" --check-only
```

## Collaboration Protocol

When delegating to Nemotron during autonomous work:

1. **Frame the task precisely.** Nemotron 4B is capable but not Claude. Give it:
   - Explicit instructions (not vague goals)
   - All necessary context inline (it has no access to your conversation)
   - Expected output format (JSON, markdown, code block, etc.)
   - Examples if the task is non-obvious

2. **Validate the output — hallucination rate on technical terms is non-trivial.** Nemotron WILL produce confident, plausible-sounding text that is factually wrong. You MUST:
   - Verify ALL technical terms, acronyms, and domain-specific claims against your own knowledge
   - Check code for syntax errors AND semantic correctness
   - Verify extracted data against the original source
   - If output contains any domain-specific reasoning, discard it and do it yourself
   - If output quality is poor, do it yourself — don't retry more than once

3. **Report the delegation.** Tell the user when you've used Nemotron:
   - "Delegated file summarization to local Nemotron (saved ~2K Claude tokens)"
   - Include Nemotron's output with light editing if needed

## System Prompts by Task Type

Use these proven system prompts:

**Code generation:**
```
You are a code generator. Output ONLY code, no explanations. Follow the spec exactly.
```

**Summarization:**
```
You are a summarizer. Read the content and produce a concise summary. Use bullet points. Max 10 bullets.
```

**Data extraction:**
```
You are a data extractor. Extract the requested fields from the input. Output valid JSON only, no markdown fences.
```

**Log analysis:**
```
You are a log analyzer. Identify errors, warnings, and anomalies. List each finding with the relevant log line.
```

## Multi-Step Delegation Pattern

For larger tasks, chain multiple Nemotron calls:

1. First call: have Nemotron analyze/plan the subtask
2. Review its plan, adjust if needed
3. Second call: have Nemotron execute based on the refined plan
4. Validate and integrate the result

## Important: Thinking Model

Nemotron 3 Nano is a **thinking model** — it generates an internal reasoning chain before producing its final response. The Ollama API returns both `content` (final answer) and `thinking` (chain-of-thought) fields.

**Implications for token budgets:**
- Thinking tokens consume `num_predict` budget. Use `--max-tokens 4096` (or higher) for complex tasks so the model has room for both thinking AND the actual response.
- If you get empty responses, the model ran out of tokens during its thinking phase. Increase `--max-tokens`.
- The `--show-thinking` flag prints the reasoning chain to stderr for debugging.

## Limits

- **256K context window** — much larger than most local models; you can send full files, but still be mindful of inference speed on large inputs
- **Quality ceiling** — it's a 4B model (MoE, 3.5B active params); expect competent but not brilliant output
- **Speed** — runs on GTX 1650 Ti with 4GB VRAM; ~1.8 tok/s on CPU (when GPU is busy), faster when GPU is free. Plan accordingly for large outputs. First call after model load is ~10x slower (cold start).
- **No tool use** — Nemotron can't read files or run commands; you must provide all context inline
- **GPU sharing** — the GTX 1650 Ti (4GB) may be in use by other processes. Before large inference jobs, check GPU usage with `nvidia-smi`. If VRAM is tight, Ollama will fall back to CPU automatically (slower but won't OOM or disrupt other work)
