# Claude Code Skills

Custom skills for [Claude Code](https://claude.ai/claude-code) -- Anthropic's agentic CLI. Each skill is a `SKILL.md` playbook that teaches Claude how to handle a complex, multi-step task autonomously.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/SolshineCode/claude-code-skills.git
cd claude-code-skills

# Install one skill
cp -r skill-tsa ~/.claude/skills/

# Install all skills
cp -r */ ~/.claude/skills/

# Use it in Claude Code
# Type: /skill-tsa all
```

That's it. Claude Code auto-detects any `SKILL.md` in `~/.claude/skills/`. No config needed.

---

## Skills

### skill-tsa
**Security scanner for Claude Code skills.**

Scan any skill for malicious commands, prompt injection, data exfiltration, obfuscated code, and scope creep before you install it.

```
/skill-tsa borrower-defense          # scan one skill
/skill-tsa all                       # scan every installed skill
/skill-tsa https://github.com/x/y   # scan a remote repo BEFORE installing
```

Checks 5 categories: dangerous commands (rm -rf, curl|sh, eval), prompt injection (role hijacking, hidden instructions, consent fabrication), data exfiltration (credential theft, sending files to external URLs), suspicious patterns (obfuscated code, hidden text), and scope creep (a "formatter" skill that reads your email).

**Requires:** Nothing. Works on any machine with Claude Code.

---

### human-writing-check
**Detect and remove AI writing tells.**

Based on [Wikipedia's Signs of AI Writing guide](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Scans text for banned words ("delve", "tapestry", "landscape"), structural patterns (rule of three, em dashes, not-just-X-but-Y), style tells (synonym cycling, uniform paragraphs), and tone issues (universal positivity, vague attributions).

Use it on blog posts, articles, documentation, LinkedIn messages, legal documents, or anything you're publishing under your name.

```
/human-writing-check              # review the most recent text Claude drafted
/human-writing-check myfile.md    # review a specific file
```

Gives a numbered violation list, rewrites the entire text to sound human, then does a second pass. Reports the most common tells so you can watch for them in future drafts.

**Requires:** Nothing.

---

### gemini-collab
**Delegate tasks to Google's Gemini to save Claude tokens.**

Gemini is free (with Google subscription), has a 1M token context, and can do web research, Gmail API access, large-file analysis, documentation generation, and code review. Less capable than Claude for complex reasoning but great for grunt work.

The killer feature: **Gemini CLI has Gmail API access.** When run with `--yolo`, it can search, read, and export emails programmatically. This is faster and more reliable than browser automation for any email-related task.

```python
# Headless call
python "~/.claude/skills/gemini-collab/scripts/gemini_client.py" \
  --prompt "Summarize the errors in these logs" --timeout 300

# With file system access
python "~/.claude/skills/gemini-collab/scripts/gemini_client.py" \
  --prompt "Search Gmail for emails from example.com and save them" \
  --yolo --cwd /path/to/output
```

**Requires:** Gemini CLI installed and authenticated. Run `gemini` interactively once to complete Google OAuth before first use.

---

### nemotron-collab
**Delegate tasks to a local Nemotron model via Ollama.**

Zero cost, zero latency, fully private. Good for file summarization, log analysis, boilerplate generation, code formatting, data extraction. Use when you don't need internet access and want to keep data local.

**Requires:** Ollama installed with a Nemotron model pulled.

---

### comet-bridge
**Working with Perplexity's Comet agentic browser.**

Comet is an AI browser that can autonomously research topics, read pages, and compile findings. This skill documents how to connect it via MCP, what works vs what crashes, and the recommended hybrid workflow.

The key insight: **use Comet for research, Chrome for actions.** Comet's CDP connection crashes when it tries to post comments, send messages, or click buttons. But for reading and analyzing web content across multiple sites, it's 10x cheaper than Chrome automation (50-100K tokens saved per research task).

Includes security considerations for remote debugging port exposure and data transmission to Perplexity servers.

**Requires:** Comet browser (Perplexity desktop app), comet-mcp npm package.

---

### borrower-defense
**Borrower Defense to Repayment application assistant.**

Guides you through filing a federal BDTR application to discharge student loans when your school committed misconduct (fraud, misrepresentation, disability discrimination, broken programs, etc.).

Handles the entire pipeline across 8 phases:
1. Intake interview (structured questions about your situation)
2. Evidence gathering (Gmail search via Gemini, audio transcription guidance, FERPA request drafting)
3. Narrative drafting (sworn statement with portal character restrictions)
4. Human-writing check (mandatory AI-writing decontamination)
5. Portal form filling (JS-accelerated automation of StudentAid.gov's 7-step form)
6. Evidence upload checklist (manual step, with exact file locations)
7. Strategic positioning review (legal standard analysis by loan period, evidence strength)
8. Handoff (session notes, memory, calendar reminders, post-submission checklist)

Built from a real application session. Includes hard-won lessons about the portal's aggressive timeouts, character restrictions, React form quirks, and session management.

**Requires:** Gemini CLI (authed for Gmail), Claude in Chrome, ffmpeg (for audio compression), FSA ID account at StudentAid.gov.

---

### linkedin-os
**Automated LinkedIn networking system.**

Two campaign types:
- **Job Search:** 25 personalized connection requests per week, follow-up sequences on day 3/7/14, referral requests after building context.
- **VC Networking:** Build relationships with investors over weeks, share traction and insights, eventually request intro meetings.

Uses Claude in Chrome for all LinkedIn interactions. Includes message templates, status tracking, and daily/weekly workflows.

**Requires:** Claude in Chrome browser extension, LinkedIn account.

---

### nano-banana
**Image generation via Gemini CLI.**

Routes all image generation requests through Gemini. Handles blog featured images, YouTube thumbnails, icons, diagrams, patterns, illustrations, photos, and visual assets. Use whenever you need Claude to create any visual content.

**Requires:** Gemini CLI.

---

### deep-work
**Autonomous multi-hour task execution.**

For when you want to hand off a large, complex task and walk away. Claude manages its own planning, execution, and progress tracking without asking questions. Use for tasks that would take a human multiple hours of focused work.

```
/deep-work "Refactor the authentication system to use JWT tokens"
/deep-work "Write comprehensive tests for the API layer"
```

**Requires:** Nothing.

---

### commercialize
**Take a technology from idea to market-ready assets.**

Creates a dedicated GitHub repo and builds out: patent application drafts, scientific publication drafts, product design documents, business strategy, market analysis. Use when you have a technical concept and want everything needed to bring it to market.

```
/commercialize "Novel approach to X using Y"
```

**Requires:** GitHub CLI (`gh`).

---

## How Skills Work

A Claude Code skill is just a folder with a `SKILL.md` file inside `~/.claude/skills/`. When you type `/skill-name` or Claude detects a matching conversation topic, it reads the SKILL.md and follows it as a detailed playbook.

```
~/.claude/skills/
  my-skill/
    SKILL.md          # Required. The playbook Claude follows.
    scripts/          # Optional. Helper scripts the skill references.
    references/       # Optional. Templates, examples, docs.
```

Skills can reference other skills (borrower-defense uses gemini-collab and human-writing-check). They can include scripts that Claude executes. They can have any structure as long as SKILL.md is at the root.

## Security

Run `/skill-tsa` on any skill before installing it. See the [skill-tsa](#skill-tsa) section above.

Skills have the same access as Claude Code itself -- they can read/write files, run commands, and access the internet. A malicious skill could exfiltrate data, delete files, or manipulate Claude's behavior via prompt injection. Only install skills from sources you trust, and scan them first.

## License

MIT

---

### investor-materials
**Create investor-facing fundraising materials.**

Adapted from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT).

Builds pitch decks, one-pagers, investor memos, financial models, use-of-funds tables, and accelerator applications. Enforces a single source of truth so traction metrics, raise size, team bios, and milestones stay consistent across every document you hand an investor.

```
/investor-materials     # start building or revising any investor asset
```

**Requires:** Nothing.

---

### investor-outreach
**Draft investor communication that gets replies.**

Adapted from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT).

Writes cold emails, warm intro blurbs, follow-ups, and post-meeting updates for VCs, angels, and accelerators. Enforces real personalization and a direct ask. Hard-bans filler phrases ("I'd love to connect", "excited to share", generic thesis praise).

```
/investor-outreach     # write or refine any investor-facing message
```

**Requires:** Nothing.

---

### frontend-slides
**Create zero-dependency, animation-rich HTML presentations.**

Adapted from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT). Inspired by work by [@zarazhangrui](https://github.com/zarazhangrui).

Generates self-contained HTML presentations from scratch, converts PPT/PPTX files via python-pptx, or enhances existing HTML decks. Enforces viewport-fit (every slide in one viewport, no internal scrolling) as a hard gate. Includes visual style discovery via preview files so non-designers don't need to describe preferences in the abstract.

```
/frontend-slides       # new deck, PPTX conversion, or deck enhancement
```

**Requires:** `python-pptx` for PPTX conversion (optional, falls back to manual workflow).

---

### investor-pitch-deck
**End-to-end YC-style pitch deck orchestrator.**

Locally authored. Wires together `investor-materials`, `frontend-slides`, `investor-outreach`, and `/human-writing-check` into a single workflow. Three modes:

- **Greenfield** — build a fresh deck from a startup description
- **Refactor** — tighten and YC-ify an existing deck
- **Mining** — strip an old/external deck for raw copy and assets, build a completely new structure from them

Produces an HTML deck (via `frontend-slides`) or Marp Markdown (CLI-exportable to PPTX/PDF), runs a writing quality pass, and optionally generates outreach emails from the same canonical facts.

```
/investor-pitch-deck   # start the full pitch deck workflow
```

**Requires:** `investor-materials`, `frontend-slides` (both in this repo). `investor-outreach` and `human-writing-check` are optional extensions.
