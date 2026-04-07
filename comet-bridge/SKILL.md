---
name: comet-bridge
description: "Guidelines for working with the Comet (Perplexity) agentic browser via the comet-bridge MCP server. Read this before using any mcp__comet-bridge__* tools. Covers connection, prompting patterns, known quirks, and lessons learned."
---

# Comet Bridge — Working with Perplexity's Agentic Browser

Comet is an autonomous agentic browser that handles web browsing independently. Use it instead of Claude in Chrome whenever possible to save context tokens.

## Starting Comet

Comet must be running with `--remote-debugging-port=9222`. If `comet_connect` fails:

```bash
# Kill existing instances and restart with debug port
powershell -NoProfile -Command "Stop-Process -Name comet -Force -ErrorAction SilentlyContinue"
sleep 2
"C:\Users\caleb\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222 &
```

Then call `comet_connect`. If it still fails, wait 5 seconds and try again.

## Architecture & Limitations (comet-mcp v2.3.0)

The MCP server connects to Comet via Chrome DevTools Protocol (CDP) WebSocket, attached to the **main Perplexity tab**. This has key implications:

- **Research tasks work reliably** — Comet reads pages in its own context without needing browser control, so the CDP connection stays stable.
- **Action tasks (commenting, liking, messaging) crash the CDP connection** — When Comet gets "browser control" permission, it opens a NEW tab to navigate the target site. This destabilizes the WebSocket to the main Perplexity tab, causing readyState 3 (CLOSED) errors.
- **`newChat: true` is unreliable** — It runs a tab cleanup that closes agent browsing tabs and navigates to perplexity.ai. The React app hasn't hydrated when it tries to type, so `execCommand('insertText')` silently fails → "Prompt text not found" error.

**Bottom line: Use Comet for RESEARCH, use Claude in Chrome for ACTIONS.**

## Core Principles

1. **Trust Comet for research. It's capable.** Don't micromanage. Give it the full task and let it work.

2. **One big prompt beats five small ones.** Combine research, navigation, and analysis into a single detailed prompt. Multiple small prompts lose context and risk input failures.

3. **Delegate analysis, not just navigation.** Comet can screen results, make recommendations, compare options, and compile reports. Tell it what you're trying to accomplish and let it figure out the approach.

4. **Long timeouts.** 60s minimum for single-page tasks. 120-300s for multi-page research. Never use 15s timeouts.

5. **Don't over-poll.** Wait 60+ seconds before first poll. Comet works faster when not interrupted. Only poll to check if a 2+ minute task is still progressing.

6. **Prefer `newChat: false` with a throwaway "Hello" first.** `newChat: true` is unreliable. Instead, send a short message with `newChat: false` to establish a session, then follow up with your real task.

7. **Use Comet for research, Chrome for actions.** Comet's CDP connection crashes when agent browsing opens new tabs. Use Comet to research profiles/posts/activity, then use Claude in Chrome to post comments, send messages, and like posts. This hybrid approach is the most reliable.

## Recommended Hybrid Workflow (LinkedIn)

1. **Research phase (Comet):** Send one big prompt asking Comet to visit profiles, read posts, and compile recommendations. This works reliably because it doesn't need browser control.
2. **Draft phase (Claude):** Based on Comet's research, draft messages/comments and show user for approval.
3. **Action phase (Chrome):** Use Claude in Chrome to navigate to specific LinkedIn posts and post the approved comments, send messages, or like posts. Chrome is reliable for these interactions.

This avoids the CDP crash that happens when Comet tries to use browser control for actions.

## Prompting Patterns That Work

### Research + analysis (best use case)
```
"Research [person/company]. Check their LinkedIn, recent posts, and X/Twitter.
Tell me: [specific fields you need]. Also check for [specific signals].
Recommend which [X] I should engage with first based on [criteria]."
```

### Batch research
```
"Do this for each of these [people/companies]: [list].
For each one, check their recent posts and compile results grouped by [category]."
```

### Follow-up extraction
When Comet's report is too long to see in one screenshot:
```
"From your report, just tell me: [specific question about the results]"
```
Follow-ups with `newChat: false` work more reliably than new chats.

## Known Behaviors

### Comet asks for confirmation before sending/posting
Comet has a safety policy and will often pause before clicking Send/Submit/Post. Solutions:
- Include "this is authorized" and "click Send/Submit immediately" in the original prompt
- If it still asks, respond with "Yes, confirmed. Do it now."
- It WILL execute the action. Don't assume it failed.

**IMPORTANT:** Caleb has given standing permission to always click "Allow once" when the browser control prompt appears. Do not ask the user — tell them to click it quickly if Claude cannot click it directly.

### Comet appears stuck but actually completed the action
Comet's UI sometimes shows "Listening..." or keeps the old response visible even after it successfully performed the action. **Always verify the actual page state** (via `comet_screenshot`) before concluding something didn't work.

### Input failures ("Prompt text not found")
**Root cause:** `newChat: true` closes tabs and navigates to perplexity.ai, but React hasn't hydrated when `execCommand('insertText')` runs. The text doesn't appear in the input, verification fails.

**Workaround:**
1. Send a short throwaway prompt with `newChat: false` (e.g., "Hello") to establish a session
2. Then send your real task as a follow-up with `newChat: false`
3. If that fails, kill Comet, restart with debug port, reconnect, and repeat

### Browser control crashes (CDP WebSocket dies)
**Root cause:** When Comet's agent gets browser control, it opens a new tab. The CDP WebSocket (connected to the main Perplexity tab) loses its connection because the tab structure changes.

**Pattern:** Ask with browser control → "Allow once" → WebSocket readyState 3 (CLOSED) → `comet_connect` fails or returns stale state.

**Workaround:** Don't use Comet for actions that need browser control. Use it for research only, then use Claude in Chrome for the actual interactions. See "Recommended Hybrid Workflow" above.

### WebSocket disconnects (general)
Comet's WebSocket can close mid-task. Fix: call `comet_connect` to reconnect. Previous conversation context will be lost. Before resending action tasks, verify the action wasn't already completed to avoid duplicates.

### Long browsing tasks
For multi-page research, Comet navigates autonomously. The step descriptions in `comet_poll` only show the last ~5 steps. Trust it's working if the URL is changing.

## When to Use Comet vs Chrome

| Task | Comet | Chrome |
|------|-------|--------|
| Multi-page research and compilation | **Best choice** | Expensive (tokens) |
| Reading profiles, posts, activity | **Best choice** | Fallback |
| Cross-platform research (LinkedIn + X + web) | **Best choice** | Can't do |
| Analysis and recommendations | **Best choice** | Can't do |
| Posting comments | **Crashes (CDP bug)** | **Use this** |
| Sending messages | **Crashes (CDP bug)** | **Use this** |
| Liking posts | **Crashes (CDP bug)** | **Use this** |
| Complex UI interactions (modals, dropdowns) | Less reliable | **Use this** |

## Token Savings

Comet's main value is keeping Claude's context clean for research. A typical research task via Chrome burns 50-100K tokens on screenshots and page content. Via Comet, Claude only sees the compiled results (a few hundred tokens). Use Comet for all research/reading and Chrome for actions.

## Source Code Reference

Package: `comet-mcp` v2.3.0 by hanzili (MIT)
- GitHub: https://github.com/hanzili/comet-mcp
- Installed at: `%LOCALAPPDATA%\npm-cache\_npx\e5496908d43a2422\node_modules\comet-mcp\`
- Key files: `dist/index.js` (MCP server), `dist/cdp-client.js` (CDP WebSocket), `dist/comet-ai.js` (input/typing)
- MCP logs: `%LOCALAPPDATA%\claude-cli-nodejs\Cache\C--Users-caleb\mcp-logs-comet-bridge\`
