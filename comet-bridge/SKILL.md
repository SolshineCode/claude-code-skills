---
name: comet-bridge
description: "Guidelines for working with the Comet (Perplexity) agentic browser via the comet-bridge MCP server. Read this before using any mcp__comet-bridge__* tools. Covers connection, prompting patterns, known quirks, and lessons learned."
---

# Comet Bridge — Working with Perplexity's Agentic Browser

Comet is an autonomous agentic browser that handles web browsing independently. Use it instead of Claude in Chrome whenever possible to save context tokens.

## Security Considerations

**Read this before using Comet.**

1. **Remote debugging port exposes your browser.** Running Comet with `--remote-debugging-port=9222` means anything on your machine (or network, if not bound to localhost) can connect to and control the browser via Chrome DevTools Protocol. Only use this on trusted networks. Never on public WiFi.

2. **CDP gives full browser access.** The MCP server connected via CDP can read cookies, session tokens, and all page content from every tab. This is the same level of access as a browser extension with "all sites" permission. Understand the trust boundary.

3. **Comet sends page content to Perplexity servers.** When Comet processes a page, that content may be transmitted to Perplexity for AI processing. Do not use Comet to browse sensitive sites (banking, medical, email with sensitive content) unless you're comfortable with that data exposure.

4. **Browser control permission.** When Comet requests "Allow once" for browser control, it takes full control of a browser tab and can navigate anywhere, click anything, and fill forms. Always review what Comet is about to do before granting this permission unless you have established your own trust policy.

## Starting Comet

Comet must be running with `--remote-debugging-port=9222`. If `comet_connect` fails:

```bash
# Kill existing instances and restart with debug port
# Windows:
powershell -NoProfile -Command "Stop-Process -Name comet -Force -ErrorAction SilentlyContinue"
sleep 2
# Adjust path to your Comet installation:
"$LOCALAPPDATA/Perplexity/Comet/Application/comet.exe" --remote-debugging-port=9222 &
```

Then call `comet_connect`. If it still fails, wait 5 seconds and try again.

## Architecture & Limitations (comet-mcp v2.3.0)

The MCP server connects to Comet via Chrome DevTools Protocol (CDP) WebSocket, attached to the **main Perplexity tab**. This has key implications:

- **Research tasks work reliably** — Comet reads pages in its own context without needing browser control, so the CDP connection stays stable.
- **Action tasks (commenting, liking, messaging) crash the CDP connection** — When Comet gets "browser control" permission, it opens a NEW tab to navigate the target site. This destabilizes the WebSocket to the main Perplexity tab, causing readyState 3 (CLOSED) errors.
- **`newChat: true` is unreliable** — It runs a tab cleanup that closes agent browsing tabs and navigates to perplexity.ai. The React app hasn't hydrated when it tries to type, so `execCommand('insertText')` silently fails with "Prompt text not found" error.

**Bottom line: Use Comet for RESEARCH, use Claude in Chrome for ACTIONS.**

## Core Principles

1. **Trust Comet for research. It's capable.** Don't micromanage. Give it the full task and let it work.
2. **One big prompt beats five small ones.** Combine research, navigation, and analysis into a single detailed prompt.
3. **Delegate analysis, not just navigation.** Comet can screen results, make recommendations, and compile reports.
4. **Long timeouts.** 60s minimum for single-page tasks. 120-300s for multi-page research. Never use 15s timeouts.
5. **Don't over-poll.** Wait 60+ seconds before first poll.
6. **Prefer `newChat: false` with a throwaway "Hello" first.** `newChat: true` is unreliable.
7. **Use Comet for research, Chrome for actions.** The hybrid approach is the most reliable.

## Recommended Hybrid Workflow

1. **Research phase (Comet):** One big prompt to visit pages, read content, compile findings.
2. **Draft phase (Claude):** Based on Comet's research, draft actions and show user for approval.
3. **Action phase (Chrome):** Use Claude in Chrome to perform the approved actions.

## Known Behaviors

### Comet asks for confirmation before sending/posting
Solutions: Include "this is authorized" and "click Send/Submit immediately" in the prompt. If it still asks, respond with "Yes, confirmed. Do it now."

**NOTE:** Users should establish their own policy about whether to grant standing "Allow once" permission or review each browser control request individually.

### Input failures ("Prompt text not found")
**Workaround:** Send a throwaway prompt with `newChat: false` first, then your real task as a follow-up.

### Browser control crashes (CDP WebSocket dies)
**Workaround:** Don't use Comet for actions that need browser control. Use research-only mode, then Chrome for interactions.

### WebSocket disconnects (general)
Call `comet_connect` to reconnect. Previous context will be lost. Verify actions weren't already completed before resending.

## When to Use Comet vs Chrome

| Task | Comet | Chrome |
|------|-------|--------|
| Multi-page research | **Best choice** | Expensive (tokens) |
| Reading profiles/posts | **Best choice** | Fallback |
| Cross-platform research | **Best choice** | Can't do |
| Posting/commenting | **Crashes (CDP bug)** | **Use this** |
| Sending messages | **Crashes (CDP bug)** | **Use this** |
| Complex UI interactions | Less reliable | **Use this** |

## Token Savings

A typical research task via Chrome burns 50-100K tokens on screenshots and page content. Via Comet, Claude only sees the compiled results (a few hundred tokens).

## Source Code Reference

Package: `comet-mcp` v2.3.0 by hanzili (MIT)
- GitHub: https://github.com/hanzili/comet-mcp
