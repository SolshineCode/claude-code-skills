# Claude Code Skills

A collection of custom skills for [Claude Code](https://claude.ai/claude-code) (Anthropic's CLI agent). Each skill is a self-contained `SKILL.md` file that teaches Claude how to handle a specific complex task.

## Skills

### Application & Legal
| Skill | Description |
|-------|-------------|
| **borrower-defense** | Borrower Defense to Repayment application assistant. Full pipeline: evidence gathering via Gmail, audio transcription, narrative drafting, human-writing polish, StudentAid.gov portal automation, strategic review. |

### Writing & Content
| Skill | Description |
|-------|-------------|
| **human-writing-check** | AI writing detection and removal based on Wikipedia's comprehensive detection guide. Scans for banned words, structural patterns, style tells, and rewrites to sound human. |

### Networking & Outreach
| Skill | Description |
|-------|-------------|
| **linkedin-os** | Automated LinkedIn networking system. Job search campaigns (25 connections/week, follow-up sequences, referral requests) and VC networking campaigns. Uses Claude in Chrome. |

### AI Delegation
| Skill | Description |
|-------|-------------|
| **gemini-collab** | Delegate to Google's Gemini via CLI. Gmail API access, web research, large-file analysis, documentation generation. Free with Google subscription. |
| **nemotron-collab** | Delegate to local Nemotron model via Ollama. Zero-cost, zero-latency for file summarization, log analysis, boilerplate generation. |

### Browser Automation
| Skill | Description |
|-------|-------------|
| **comet-bridge** | Perplexity's Comet agentic browser via MCP. Connection patterns, known quirks, hybrid workflow (Comet for research, Chrome for actions). Includes security considerations. |

### Image Generation
| Skill | Description |
|-------|-------------|
| **nano-banana** | Image generation via Gemini CLI. Blog images, thumbnails, icons, diagrams, illustrations, photos. Routes all image requests through Gemini. |

### Autonomous Work
| Skill | Description |
|-------|-------------|
| **deep-work** | Autonomous multi-hour task execution. For when you want to hand off a large task and walk away. Manages its own planning, execution, and progress tracking. |
| **commercialize** | Take a technology concept from idea to market-ready assets. Patent drafts, scientific publications, product design, business strategy, all built out in a dedicated GitHub repo. |

## Installation

Copy any skill directory into `~/.claude/skills/` and Claude Code will auto-detect it:

```bash
# Single skill
cp -r borrower-defense ~/.claude/skills/

# All skills
cp -r */ ~/.claude/skills/
```

Then invoke with `/skill-name` in Claude Code (e.g., `/borrower-defense`), or Claude will auto-trigger based on conversation context.

## Prerequisites by Skill

| Skill | Requires |
|-------|----------|
| borrower-defense | Gemini CLI (authed), Claude in Chrome, ffmpeg, FSA ID |
| human-writing-check | None |
| linkedin-os | Claude in Chrome |
| gemini-collab | Gemini CLI (authed) |
| nemotron-collab | Ollama with Nemotron model |
| comet-bridge | Comet browser, comet-mcp |
| nano-banana | Gemini CLI |
| deep-work | None |
| commercialize | GitHub CLI |

## Creating Your Own Skills

A skill is just a directory with a `SKILL.md` file inside `~/.claude/skills/`. The SKILL.md should contain:

1. A description of when to trigger the skill
2. Step-by-step instructions for Claude to follow
3. Code patterns, command templates, and known gotchas
4. Examples of expected inputs and outputs

Claude Code reads the SKILL.md when the skill is invoked and follows it as a detailed playbook.

## License

MIT
