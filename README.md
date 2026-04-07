# Claude Code Skills

A collection of custom skills for [Claude Code](https://claude.ai/claude-code) (Anthropic's CLI agent). Each skill is a self-contained `SKILL.md` file that teaches Claude how to handle a specific complex task.

## Skills

### borrower-defense
**Borrower Defense to Repayment Application Assistant.** Guides users through filing a BDTR application on StudentAid.gov to discharge federal student loans when their school engaged in misconduct. Handles the full pipeline: intake interview, Gmail evidence gathering (via Gemini CLI), audio transcription guidance, narrative drafting, human-writing polish, portal form filling via browser automation, and strategic positioning review.

Dependencies: `gemini-collab`, `human-writing-check`, Claude in Chrome extension, ffmpeg

### human-writing-check
**AI Writing Detection and Removal.** Reviews drafted text for signs of AI-generated writing based on [Wikipedia's Signs of AI Writing guide](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) and fixes every violation. Covers banned words, structural patterns, style tells, and tone issues. Essential for any prose that will be published or submitted under someone's name.

### gemini-collab
**Gemini CLI Collaboration.** Delegates subtasks to Google's Gemini model via the locally installed Gemini CLI. Includes a Python wrapper script for headless calls. Key use case: Gmail API access for searching/exporting emails programmatically (faster and more reliable than browser automation for email tasks).

### comet-bridge
**Comet (Perplexity) Agentic Browser.** Guidelines for working with the Comet browser via comet-mcp. Covers connection, prompting patterns, known quirks (CDP crashes on action tasks, newChat reliability issues), and the recommended hybrid workflow (Comet for research, Chrome for actions).

## Installation

Copy any skill directory into `~/.claude/skills/` and Claude Code will auto-detect it:

```bash
cp -r borrower-defense ~/.claude/skills/
```

Then invoke with `/borrower-defense` in Claude Code, or Claude will auto-trigger based on the skill's trigger conditions.

## Prerequisites

Some skills require external tools:
- **Gemini CLI**: `npm install -g @anthropic-ai/gemini-cli` (or however installed). Must run `gemini` interactively once to complete Google OAuth.
- **Claude in Chrome**: Browser extension from claude.ai/chrome
- **ffmpeg**: `winget install ffmpeg` (Windows) or `brew install ffmpeg` (Mac)
- **Comet browser**: Perplexity's desktop browser with `--remote-debugging-port=9222`

## License

MIT
