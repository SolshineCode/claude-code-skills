---
name: colab-gpu
description: "Use this skill when any task requires a cloud GPU (T4), running ML experiments, NLA evaluations, or interpretability research on Google Colab. Covers fully autonomous setup via Chrome automation: opening Colab, selecting T4 GPU, connecting the runtime, bridging via colab-mcp, running cells, and monitoring. Read this before using any mcp__colab-mcp__* tools. Compatible as a sub-task within /deep-work."
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Colab GPU — Fully Autonomous T4 Session via Chrome + colab-mcp

This skill is fully autonomous. **Do not ask the user to open Chrome, connect a runtime, or perform any manual step.** Claude handles all of it via the Chrome MCP tools and colab-mcp bridge. This skill integrates cleanly as a sub-task inside a `/deep-work` session.

## ⛔ CRITICAL RULES — read before doing anything (hard-won 2026-06-17)

1. **ACCOUNT IS A HARD GATE.** Colab/Drive must run as **caleb.deleeuw@gmail.com** and NEVER any other Google account. Verify the *rendered* account (Step 0.5) **before** opening any notebook AND again right before running any cell. If it is not caleb.deleeuw@gmail.com, STOP and switch — never proceed "hoping it's right." This has gone wrong repeatedly; treat a wrong account as a blocking failure, not a warning.

2. **NEVER call `open_colab_browser_connection` synchronously while the Colab frontend is NOT yet connected.** It is a *blocking* call that is supposed to time out at 60 s but in practice can hang the entire Claude session for HOURS (observed: 1h57m). The ONLY safe time to call it is *after* you have already driven a controlled tab to the magic URL and clicked Accept — then it returns `true` instantly. See Step 3 for the non-hanging protocol. If you ever see "Waiting for user to connect in Colab - will wait for 60s" sitting for more than ~90 s, the call is hung — it must be interrupted.

3. **Prefer the pure browser-automation path (Step 3-ALT) for unattended deep-work.** colab-mcp's connection handshake (token capture + command-palette token paste + blocking tool) is fragile and has caused hangs and crashes. Driving the Colab notebook UI directly with claude-in-chrome (type into cells, run, read output) has **no token, no dialog, no blocking call, no MCP-server dependency** — it is the robust default. Use colab-mcp only when its connect is confirmed working and you want nicer cell I/O.

### ✅ WORKING fully-automated connection recipe (2026-06-17 — the breakthrough)

The colab-mcp connection CAN be established with zero human steps using a **background sub-agent to hold the blocking call** (the deadlock was: the connect tool must be in-flight for the handshake, but it hangs the caller — so run it in a backgrounded Agent). The command-palette token paste is NOT needed when you drive the magic-URL frontend tab yourself. Exact recipe that worked end-to-end (connected, added a cell, ran it, read clean output):

1. **Account gate** (Step 0.5): controlled tab on Colab as caleb.deleeuw@gmail.com (`?authuser=1` here).
2. **Select T4 GPU runtime BEFORE connecting anything** (order matters: changing the runtime type *after* the MCP is connected restarts the kernel and DROPS the MCP — redo required). ✅ **Fully automatable (verified 2026-06-17, got Tesla T4)** — see "Autonomously selecting T4" below. The whole trick: Colab `goog` menu buttons open on **mousedown+mouseup**, NOT `.click()`/ref-click; the accelerator is an `mwc-radio` with `value="GPU,T4"` in shadow DOM; Save is a real dialog button (`find`→ref click works). Do this FIRST so the runtime is T4 before the MCP handshake.
3. **Trigger capture**: `rm` the capture file, call `open_colab_browser_connection` ONCE to fire `webbrowser.open_new` and write `colab_mcp_url.txt` (it then hangs — fine, you'll background the real one). Read the token+port from the file.
4. **Connect the (T4) runtime** (kernel must be live or the proxy never completes): `document.querySelector('colab-connect-button').shadowRoot.querySelector('#connect').click()`, wait ~25 s for "Connected".
5. **Navigate the controlled tab to the magic URL** with authuser: `…/empty.ipynb?authuser=1#mcpProxyToken=<tok>&mcpProxyPort=<port>`. This loads the frontend holding the token.
6. **Launch a BACKGROUND sub-agent** (`Agent` tool, `run_in_background: true`) whose sole job: ToolSearch-load `mcp__colab-mcp__open_colab_browser_connection` and call it once, report the boolean. This call starts the server's proxy client and waits; with the frontend loaded + runtime connected, the websocket completes and it **returns `true` within seconds** (observed 6 s). The hang is isolated in the sub-agent and never freezes the main session.
7. On `RESULT: true`, the notebook tools unlock for the whole session. ToolSearch `colab mcp notebook cell` → use `add_code_cell` / `run_code_cell` / `get_cells` / `update_cell`. `run_code_cell` returns outputs as clean JSON (stdout + tracebacks) — the whole reason to use colab-mcp.

If the sub-agent's call does NOT return quickly: the runtime wasn't connected (redo step 3) or the magic-URL frontend tab isn't loaded (redo step 4). As a manual fallback, the command-palette token paste (Step 3b) also establishes it.

### Autonomously selecting T4 GPU (verified working 2026-06-17 — got Tesla T4)

**The root cause of every "menu won't work" failure: Colab's `goog-menu-button`s open on `mousedown`+`mouseup`, NOT on `.click()` or a synthetic/ref click.** (`find` was misleading — it returns menu items even when the menu is *closed*, because Colab keeps them in the DOM hidden.) Once you dispatch mousedown+mouseup, the menu opens and items activate the same way.

Do all of this via `javascript_tool` (the dialog is `mwc-dialog` + Material web components in shadow DOM, so JS shadow-piercing is the reliable path; `find`→ref works for the final Save button):

1. **Open the Runtime menu + click "Change runtime type"** — one atomic JS call (do both synchronously so the menu can't close between):
   ```js
   const fire=(el,t)=>{const r=el.getBoundingClientRect();el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window,clientX:r.x+5,clientY:r.y+5,button:0}));};
   const vis=el=>el&&el.offsetParent!==null;
   const b=document.getElementById('runtime-menu-button');
   if(![...document.querySelectorAll('.goog-menu')].some(vis)){ fire(b,'mousedown'); fire(b,'mouseup'); }   // mousedown+mouseup, NOT click
   const item=[...document.querySelectorAll('.goog-menuitem')].filter(vis).find(e=>/change runtime type/i.test(e.textContent||''));
   fire(item,'mouseover'); fire(item,'mousedown'); fire(item,'mouseup');                                    // activates the item
   ```
   (Calling mousedown+mouseup on the button again *toggles it closed* — guard with the `.goog-menu` visible check.)
2. **Select T4** — the accelerator options are `mwc-radio` elements (shadow DOM) with values: `""`(CPU), `GPU,T4`, `GPU,H100`, `GPU,G4`, `GPU,A100`, `GPU,L4`, `TPU,V5E1`, `TPU,V6E1`. Pierce shadow roots, pick `GPU,T4`:
   ```js
   const all=[]; const walk=(r,d)=>{if(d>8)return;for(const el of r.querySelectorAll('*')){if(el.tagName.toLowerCase()==='mwc-radio')all.push(el);if(el.shadowRoot)walk(el.shadowRoot,d+1);}}; walk(document,0);
   const t4=all.find(r=>r.getAttribute('value')==='GPU,T4'); t4.click(); t4.checked=true; t4.dispatchEvent(new Event('change',{bubbles:true}));
   ```
3. **Click Save**: `find` query "Save button in the runtime type dialog" → `computer left_click` by its `ref` (a normal real click works here — it's a dialog button, not a goog menu item). The connect button then reads "Reconnect T4".
4. **Connect the T4 runtime**: shadow-DOM click `document.querySelector('colab-connect-button').shadowRoot.querySelector('#connect').click()`; wait ~25 s for "Connected". (If a "runtime disconnected" `mwc-dialog` is showing from a timeout, this reconnect dismisses it.)
5. Proceed to the MCP connection (capture → magic URL → background-agent connect). Verified end-to-end: `torch.cuda.get_device_name(0)` → `Tesla T4`, 15 GB.

### Verified findings (2026-06-17 live run) — trust these over older text below
- **Capture WORKS** with the absolute-python `BROWSER` env (got a real token). The earlier "capture never fired" was bare-`python`-not-on-PATH.
- **Account:** on this machine `?authuser=1` = caleb.deleeuw@gmail.com (index 0 = the WRONG `cl8.dl8.888@gmail.com`). `?authuser=<email>` was IGNORED; probe by index and match the email. **Carry `?authuser=1` in EVERY Colab URL, including the magic URL** (`…/empty.ipynb?authuser=1#mcpProxyToken=…`) or it reverts to the wrong account.
- **Runtime connect:** the `find`→ref click and raw-coordinate clicks MISSED (dpr). What worked: JS shadow-DOM click — `document.querySelector('colab-connect-button').shadowRoot.querySelector('#connect').click()`. Wait ~20–30 s; "Connected" when `shadowRoot` text contains "Connected" (RAM/Disk text is in a child element).
- **colab-mcp connect: NOT an Accept button.** The fully-automated path (magic-URL frontend + background-agent connect) needs no dialog and IS confirmed end-to-end headless. The command-palette token paste (Step 3b) is only a manual fallback.
- **`open_colab_browser_connection` still hangs** despite `MCP_TOOL_TIMEOUT=90000` (progress messages defeat the idle timeout) — observed 11 min. Only call it once the frontend is already connected.
- **dpr ≈ 1.25** → calibrate every coordinate click (`*1.25`), or use ref/shadow-DOM clicks instead.
- **Cell editor & output are largely opaque to main-frame JS** (cross-origin/iframe): `get_page_text` and JS `textContent` return nothing useful. Read cell output via `find` ("Cell N output region") → its `ref`. Typed code is subject to the editor auto-closing brackets/quotes — verify or prefer a paste/JS-set method.

## Step 0: Load Chrome Tools (Always First)

Chrome tools are deferred — they must be fetched before use. Do this in one ToolSearch call:

```
ToolSearch query: "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__javascript_tool"
```

Also load the colab-mcp tool at this point so you know it's available:

```
ToolSearch query: "select:mcp__colab-mcp__open_colab_browser_connection"
```

If ToolSearch returns "No matching deferred tools found" for colab-mcp, the MCP server has exited (this happens after a failed or interrupted connection attempt). The user must restart Claude Code to bring the server back — tell them to do so and then resume from Step 0.

## Step 0.5: Verify Google Account — HARD GATE (do not skip, do not proceed on failure)

Colab must run as **caleb.deleeuw@gmail.com**. Chrome is signed into multiple accounts and defaults to the wrong one. This step is a gate: you may not move to Step 1 until the active account is verified to be caleb.deleeuw@gmail.com.

**Why this keeps failing:** the account index (`authuser=N`) is NOT stable across sessions, so hardcoding `authuser=0` is unreliable. The robust method is: read the *actual rendered* account email, and switch by matching the email text — never assume.

1. Navigate the controlled tab to `https://colab.research.google.com/`.
2. Detect the active account email from the Colab account button (top-right). Use `mcp__claude-in-chrome__find` for "Google account button / avatar showing email", or JS:
   ```javascript
   // The account button's aria-label contains the active email
   const btn = document.querySelector('a[aria-label*="@"], [aria-label*="Google Account"]');
   (btn && btn.getAttribute('aria-label')) || document.body.innerText.match(/[\w.+-]+@gmail\.com/)?.[0] || 'UNKNOWN'
   ```
3. **If it shows `caleb.deleeuw@gmail.com` → proceed to Step 1.**
4. **If it shows any other account or UNKNOWN → switch (do NOT proceed):**
   - Try forcing the account by email in the URL first: navigate to `https://colab.research.google.com/?authuser=caleb.deleeuw@gmail.com`, then re-run step 2 to confirm. Google honors `authuser=<email>` when that account is signed in.
   - If still wrong, click the account avatar (top-right) to open the switcher, screenshot, and click the row whose text is exactly `caleb.deleeuw@gmail.com`. Then re-verify.
   - To discover the right index deterministically, probe `?authuser=0`, `?authuser=1`, `?authuser=2` and read the rendered email after each; use the one that resolves to caleb.deleeuw@gmail.com.
   - If that account isn't signed in at all: open the sign-in page and tell the user "Please sign into caleb.deleeuw@gmail.com in the Chrome tab, then tell me when done" — **do NOT enter credentials yourself** (prohibited).
5. **Re-verify the account again right before running any cell** (Step 4) — a runtime reconnect or new tab can silently land on the wrong account.

## Step 1: Find or Open a Colab Notebook

Call `mcp__claude-in-chrome__tabs_context_mcp` to check open tabs.

- If a tab already shows `colab.research.google.com` **and** the account is `caleb.deleeuw@gmail.com`, use it.
- Otherwise navigate the current tab to `https://colab.research.google.com/`.

When the notebook picker appears, open an existing notebook (e.g., "scratchpad") rather than creating a new one — creating a new notebook requires Drive storage quota, which may be full. Click an existing recent notebook.

If the user provided a specific notebook URL, navigate to that URL directly instead.

**Wait for page load**: After navigating, call `mcp__claude-in-chrome__read_page` once to confirm the Colab editor has loaded (look for "Runtime" in the page content). If not loaded after 5s, read again — do not proceed to runtime steps until the editor is visible.

## Step 2: Ensure T4 Runtime

### Detect current runtime state

Inject JS to read runtime state from the Colab DOM:

```javascript
// Detect if runtime is already connected and what accelerator is active
const toolbar = document.querySelector('.connected-button, .connect-button');
const connectedState = document.querySelector('[data-resource-connected="true"]') 
  || document.title.toLowerCase().includes('connected')
  || !!document.querySelector('.connected-button');
const gpuIndicator = document.querySelector('.runtime-type-icon, .colab-resource-type');
({
  connected: !!connectedState,
  toolbarText: toolbar ? toolbar.textContent.trim() : null,
  gpuText: gpuIndicator ? gpuIndicator.textContent.trim() : null
})
```

Use `mcp__claude-in-chrome__javascript_tool` to run this. Interpret the result:
- If already connected and T4 confirmed (toolbar shows RAM/disk usage, title shows "Connected"): skip to Step 3.
- If connected but GPU type unknown: proceed anyway — T4 is the free default when GPU acceleration is on.
- If not connected: proceed through runtime type selection below.

### Select T4 GPU (if runtime not yet connected)

⚠ The old `.click()`-based approach here did NOT work — Colab `goog` menu buttons open on **mousedown+mouseup**, and the accelerator is an `mwc-radio` in shadow DOM. Use the **verified working method in "Autonomously selecting T4 GPU"** (in the ⛔ CRITICAL RULES section near the top). Summary: fire mousedown+mouseup on `#runtime-menu-button`, activate the "Change runtime type" `.goog-menuitem`, select the shadow-DOM `mwc-radio[value="GPU,T4"]`, `find`→ref click Save, then shadow-DOM-click connect. Verified 2026-06-17 → Tesla T4 15 GB.

**If T4 is unavailable** (Colab warns GPU units are exhausted): pick whatever GPU value is offered (`GPU,L4`, `GPU,A100`, …) — do not block the workflow. Log the actual GPU from `nvidia-smi` later.

### Connect the runtime

After setting the runtime type, click Connect:

```javascript
const connectBtn = Array.from(document.querySelectorAll('button, [role="button"]'))
  .find(b => b.textContent.trim() === 'Connect' || b.textContent.trim() === 'Reconnect');
if (connectBtn) connectBtn.click();
'clicked Connect'
```

**Wait for connection**: Poll `mcp__claude-in-chrome__read_page` every 10 seconds for up to 60 seconds until the page shows RAM/disk usage bars or "Connected" in the title. If still not connected at 60s, try clicking Connect once more and wait another 30s. If still failing, take a screenshot via `mcp__claude-in-chrome__computer` and diagnose from the visual state.

## Step 3: Bridge via colab-mcp (deterministic mechanism)

### How colab-mcp actually works (read this — it's the whole reason this is solvable)

Source: `colab_mcp/session.py` + `websocket_server.py` (v1.0.1). When you call `open_colab_browser_connection`:

1. The server has already started a **WebSocket server on `localhost:<random port>`** with a random **token** (`secrets.token_urlsafe(16)`). Port + token are **stable for the server's whole lifetime**.
2. If a Colab frontend is already connected → returns `true` immediately.
3. Otherwise it calls `webbrowser.open_new("https://colab.research.google.com/notebooks/empty.ipynb#mcpProxyToken=<token>&mcpProxyPort=<port>")` and **blocks up to 60 s** waiting for a Colab page (origin must be colab) to open that websocket and authenticate with the token. On success → `true`; on 60 s timeout → `false`.

The "Connect to a local Colab MCP server / Accept" prompt is Colab asking permission to open that localhost websocket. **It lives in a cross-origin Colab iframe, so JS cannot click it** — only coordinate clicks in a tab you control work. And `webbrowser.open_new` opens the magic URL in the **default browser's main window, which is NOT in the claude-in-chrome tab group** — so you can't drive that tab.

### One-time setup (already done on this machine; verify before relying on it)

The fix is to redirect `webbrowser.open_new` to **capture the magic URL to a file** instead of opening an uncontrollable tab, so you can navigate your *controlled* group tab to it. This is configured once in `~/.claude.json` by adding to the `colab-mcp` server's `env`:

```json
"env": { "BROWSER": "C:/Python314/python C:/Users/caleb/.claude/colab_url_capture.py %s" }
```

with capture script `~/.claude/colab_url_capture.py`:

```python
import sys
url = sys.argv[1] if len(sys.argv) > 1 else "NOURL"
open(r"C:\Users\caleb\.claude\colab_mcp_url.txt", "w", encoding="utf-8").write(url)
```

**Two critical gotchas (both verified 2026-06-17):**
- Use an **ABSOLUTE python path** (`C:/Python314/python`), NOT bare `python`. The MCP server subprocess's PATH may not include python, so a bare `python` in BROWSER silently fails and the capture file is never written — the single most common reason "capture never fired." (Find the path with `which python`.)
- Use **forward slashes** in both paths — Python's `webbrowser` runs the value through `shlex.split`, which eats backslashes.
- After editing `~/.claude.json`, **Claude Code must be restarted** for the colab-mcp server to respawn with the new env. One-time cost. The env must exist on **every** colab-mcp scope (top-level `mcpServers` AND any `projects.<path>.mcpServers`) — whichever scope serves the session is the one that needs it.

Verify setup exists (checks both scopes): 
```bash
python -c "import json; c=json.load(open(r'C:/Users/caleb/.claude.json')); print('top:', (c.get('mcpServers',{}).get('colab-mcp') or {}).get('env')); [print(p, (pc.get('mcpServers',{}).get('colab-mcp') or {}).get('env')) for p,pc in c.get('projects',{}).items() if (pc.get('mcpServers') or {}).get('colab-mcp')]"
```
If missing, add it (Python: load JSON, set `env` on each colab-mcp scope, dump) and tell the user to restart Claude Code once.

**Confirm the capture actually works after restart, BEFORE relying on it** (independent of the hang-prone tool): run the exact command webbrowser would run —
```bash
"C:/Python314/python" "C:/Users/caleb/.claude/colab_url_capture.py" "TESTURL" && cat C:/Users/caleb/.claude/colab_mcp_url.txt   # must print TESTURL
```
That proves the script+path; the env-reaching-the-subprocess part is only testable post-restart via Step 3a.

### 3a: Trigger the URL capture (first connection call) — ⚠ HANG RISK, read fully

`webbrowser.open_new` (which writes the capture file) fires at the *very start* of this call, so **the capture file appears within ~1 s**. The DANGER is what comes after: the server middleware then `await`s the frontend connection, and although it has a 60 s timeout, it has been observed **NOT to respect it and hang the Claude session for hours**. You cannot interrupt your own synchronous MCP call.

⚠ **`MCP_TOOL_TIMEOUT` does NOT reliably bound this call (verified 2026-06-17).** It is set to 90000 in `settings.json`, and the *first* call of a session did abort at 90 s — but a later call **hung 11+ minutes** before the user killed it. The tool streams `report_progress` ("Waiting for user to connect…") notifications, and those appear to reset/defeat the idle timeout. **Therefore: NEVER call `open_colab_browser_connection` as a way to *wait* for a connection.** The only safe time to call it is AFTER the frontend is already connected (Step 3c), when it returns instantly. To merely *trigger the capture*, you still have to make one call — make it ONCE, watch the capture file appear within ~1–2 s, and be ready for the user to interrupt it (it will not return on its own). This is exactly why Step 3-ALT (no colab-mcp) is the recommended default.

```
Bash: rm -f C:/Users/caleb/.claude/colab_mcp_url.txt
mcp__colab-mcp__open_colab_browser_connection      # aborts at MCP_TOOL_TIMEOUT (~90s) or returns false; capture file already written
Bash: cat C:/Users/caleb/.claude/colab_mcp_url.txt  # must contain the real magic URL; if EMPTY/missing, capture is broken → do NOT retry the hang-prone call, fix capture (3a-setup) or use Step 3-ALT
```

If the capture file is empty/missing after this call, the BROWSER env never fired in the server subprocess (absolute-python-path or restart issue, see setup above). Stop here — repeating the call just risks another multi-hour hang. Fix the env and restart, or switch to Step 3-ALT.

### 3b: Connect via the command palette + token paste (THE REAL MECHANISM — there is NO "Accept" button)

⚠ **Correction (verified 2026-06-17): the current colab-mcp version does NOT show a one-click "Accept" dialog.** Navigating to the magic URL shows an *instructions* panel that merely **displays the token** (format `<token>&<port>`, e.g. `AbCd1234ExampleToken&51950`) and tells you to connect via the command palette. Earlier skill versions said "click Accept" — that was wrong and wasted hours.

The token+port come from the capture file (Step 3a) — you do NOT need to navigate to the magic URL at all; you just need a Colab notebook tab with a **connected runtime**. The real flow:

1. **Parse token+port** from `colab_mcp_url.txt`: the URL `…#mcpProxyToken=<TOK>&mcpProxyPort=<PORT>` → the paste value is `<TOK>&<PORT>`.
2. **Ensure the runtime is connected** (Step 2) — the MCP proxy needs a live kernel or the connection never completes.
3. **Open the command palette** in the notebook tab → **Tools menu → Command palette** (`Ctrl+Shift+P` keydown does not register through automation). ⚠ goog menus open on **mousedown+mouseup**, not `.click()` — use the `fire()` helper from "Autonomously selecting T4 GPU" above:
   ```js
   const fire=(el,t)=>{const r=el.getBoundingClientRect();el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window,clientX:r.x+5,clientY:r.y+5,button:0}));};
   const b=document.getElementById('tools-menu-button'); fire(b,'mousedown'); fire(b,'mouseup');
   const it=[...document.querySelectorAll('.goog-menuitem')].filter(e=>e.offsetParent).find(e=>/command palette/i.test(e.textContent)); fire(it,'mouseover'); fire(it,'mousedown'); fire(it,'mouseup');
   ```
   (NOTE: this whole command-palette path is the MANUAL fallback only — the magic-URL + background-agent recipe at the top connects with no palette at all.)
4. In the palette, type **`Connect to a local Colab MCP server`**, select it (Enter). A small **token form** appears.
5. **Paste/type the `<TOK>&<PORT>` value** into the form and click **Connect**.
6. THEN — and only then — call `mcp__colab-mcp__open_colab_browser_connection` (Step 3c): with the frontend now connected it returns `true` instantly (no hang).

⚠ **This step is genuinely hard to fully automate** and is NOT yet confirmed working end-to-end headless: Colab's command-palette overlay and the token form render in contexts that resist synthetic JS clicks, and `Ctrl+Shift+P` via the automation key event did not open the palette in testing. The reliable levers are (a) opening the palette via the Tools-menu JS clicks above, (b) typing into the focused palette/form via the keyboard `type` action, and (c) coordinate clicks **calibrated by devicePixelRatio** (see note below). If you cannot complete it autonomously, this is the ONE place a ~15-second human action is acceptable: ask the user to run the palette command and paste the token (it is already displayed in their tab), then proceed with everything else automated. For truly zero-touch deep-work, prefer **Step 3-ALT**.

**devicePixelRatio calibration (critical for ALL coordinate clicks):** this machine renders at **dpr ≈ 1.25**, so the `computer` tool's pixel coordinates are JS/CSS coordinates **× dpr**. A button at CSS `(x,y)` from `getBoundingClientRect` must be clicked at `(x*1.25, y*1.25)`. Uncalibrated coordinate clicks silently miss — which is why menu/button clicks failed until ref-based or shadow-DOM clicks were used. Prefer `find`→`ref` clicks and JS shadow-DOM `.click()` (both coordinate-free); use raw coordinates only when calibrated.

### 3c: Confirm connection

Call the tool again — now that the frontend is connected it returns `true` immediately and unlocks the notebook-editing tools:

```
mcp__colab-mcp__open_colab_browser_connection      # returns true
```

Then discover the unlocked tools:

```
ToolSearch query: "colab mcp notebook cell execute"
```

Use these MCP notebook tools for all cell interactions — do NOT click cells manually via Chrome when the MCP tools are available.

### Failure recovery

- **Tool returns false on 3c too**: the Accept click missed. Re-screenshot, the dialog should still be visible (it persists after the 60 s server timeout), re-click Accept, retry 3c.
- **Capture file empty/missing after 3a**: the BROWSER env isn't active — the server was started before the config edit. Confirm the env (verify command above) and restart Claude Code.
- **colab-mcp tool not loadable via ToolSearch**: the server process is down. Restart Claude Code; the BROWSER env persists in config so the new server is already instrumented.
- **Never call `open_colab_browser_connection` without the BROWSER env set** — it will open an uncontrollable main-window tab and you'll be stuck (the original failure mode).

## Step 3-ALT: Robust path — drive Colab via browser automation (NO colab-mcp) ⭐ default for unattended deep-work

When colab-mcp's capture isn't confirmed working, or you simply want zero hang/Accept/token risk, **skip Step 3 entirely** and operate the notebook through claude-in-chrome. There is no localhost websocket, no Accept dialog, no blocking tool, no MCP-server dependency — so nothing can hang the session or require a human mid-run. Trade-off: cell I/O is via the DOM rather than a clean API, so it's a bit more verbose, but it is reliable.

**Account gate still applies** (Step 0.5) — verify caleb.deleeuw@gmail.com first.

- **Write code into a cell**: focus the last code cell and type. Find the cell input with `find` ("code cell input area") or JS; click it, then:
  ```
  mcp__claude-in-chrome__computer { action: "left_click", ref: "<cell ref>", tabId: <tab> }
  mcp__claude-in-chrome__computer { action: "type", text: "import torch; print(torch.cuda.get_device_name(0))", tabId: <tab> }
  ```
  For multi-line code, prefer setting the cell via the Colab/Monaco editor model in JS, or type line-by-line. Avoid characters the editor auto-closes (it auto-inserts closing brackets/quotes) — paste-style `type` is usually fine.
- **Run the cell**: `mcp__claude-in-chrome__computer { action: "key", text: "ctrl+Return", tabId: <tab> }` (run in place) or `shift+Return` (run + next).
- **Read the output**: poll `mcp__claude-in-chrome__get_page_text` or `read_page` (filter the cell's output area) until the result/text appears; or screenshot for visual confirmation. Detect "still running" via the cell's spinner/`[*]` execution indicator.
- **New cell**: `key "alt+Return"` (Colab: run cell and insert below) or click the "+ Code" button.
- **To add a new code cell programmatically** when the toolbar is awkward, use the Colab keyboard shortcut: click a cell, press `Escape` then `b` (insert cell below).

This path covers Steps 4–7 the same way — type each cell, run, read output. Use it as the spine of deep-work GPU runs; reach for colab-mcp (Step 3) only as an optimization once its capture is verified.

## Step 4: Set Up the Notebook

Add and run a GPU verification cell first:

```python
import torch, subprocess
print("CUDA available:", torch.cuda.is_available())
print("Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free',
                         '--format=csv,noheader'], capture_output=True, text=True)
print(result.stdout)
```

Parse the output to confirm GPU type and available VRAM before launching heavy workloads.

### Install dependencies

Run pip installs in a dedicated early cell:

```python
!pip install -q <packages>
```

The `-q` flag reduces noise. Run this cell and wait for completion before adding workload cells.

### Mount Google Drive (always do this before long runs)

```python
from google.colab import drive
drive.mount('/content/drive')
```

This ensures outputs persist across session disconnects. Save all outputs under `/content/drive/MyDrive/colab-runs/<experiment-name>/`.

## Step 5: Run the Experiment

Add code cells for the actual work. Rules for autonomous long runs:

- **Unbuffered output**: use `python -u` or prepend `import os; os.environ['PYTHONUNBUFFERED']='1'` so per-step prints flush immediately.
- **Checkpoints**: set `save_interval` proportional to step time. If each step takes ~3 min, checkpoint every 50 steps (first checkpoint at ~2.5h, not 5h).
- **Output paths**: always write to `/content/drive/MyDrive/colab-runs/<run-name>/` — never `/tmp/` (ephemeral) alone.
- **One cell per logical phase**: setup → install → data → train → eval. Easier to re-run individual phases if a cell fails.

## Step 6: Monitor GPU During Run

After starting a long-running cell, monitor with periodic checks. Do NOT poll every turn — minimum 30s between reads for tasks expected to take minutes.

Add a monitoring cell (run it while training runs in another cell via `%%capture` or notebook background):

```python
!nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader
```

**Stall detection**: if GPU utilization is 0% across two consecutive monitor polls AND output files aren't growing, the job has stalled. Diagnose from the cell output (last log line), fix the issue, re-run from the last checkpoint.

For runs expected to take 30+ minutes: set a CronCreate timer instead of polling the whole time, estimating completion time (err later not earlier).

## Step 7: Retrieve Results

When cells complete:
1. Read cell output directly via the unlocked colab-mcp output tool.
2. Verify outputs were saved to Drive.
3. Follow the data mandate: commit result files immediately — do not leave them only in Colab. Either download via the Colab files panel (JS click) or push directly from a notebook cell:

```python
import subprocess
subprocess.run(['git', 'add', 'results/'], cwd='/content/MyRepo')
subprocess.run(['git', 'commit', '-m', 'Add eval results from Colab T4 run'], cwd='/content/MyRepo')
subprocess.run(['git', 'push'], cwd='/content/MyRepo')
```

## NLA / NLAttack Specific Flow

```python
# Cell 1: Clone and install
!git clone https://github.com/SolshineCode/NLAttack /content/NLAttack
!pip install -q -r /content/NLAttack/requirements.txt

# Cell 2: Run from repo root (CRITICAL — relative imports break otherwise)
import os
os.chdir('/content/NLAttack')
!python -u eval.py --config configs/default.yaml 2>&1 | tee /content/drive/MyDrive/colab-runs/nla-$(date +%Y%m%d_%H%M)/run.log

# Cell 3: Save artifacts immediately
!cp report.json /content/drive/MyDrive/colab-runs/nla-$(date +%Y%m%d_%H%M)/
!cp activations.npz /content/drive/MyDrive/colab-runs/nla-$(date +%Y%m%d_%H%M)/
```

## T4 Limits & Fallback

| Limit | Detail |
|-------|--------|
| VRAM | ~15 GB on T4 |
| Session max | ~12 hours before forced disconnect |
| Free tier quota | May throttle after heavy use — accept whatever GPU is assigned |
| Idle disconnect | Colab disconnects after ~90 min idle; mount Drive before long runs |

If the session is forcibly disconnected mid-run, reconnect (Step 2–3), check Drive for the latest checkpoint, and resume from there.

## Error Recovery (Autonomous)

| Symptom | Fix |
|---------|-----|
| `open_colab_browser_connection` returns false | JS poller didn't click Accept in time; retry the parallel JS+MCP call pair once |
| colab-mcp tool unavailable / server disconnected | Server exited after failed attempt — tell user to restart Claude Code; resume from Step 0 |
| Wrong Google account on Colab | Navigate to accounts.google.com, switch to caleb.deleeuw@gmail.com, then reload Colab |
| Runtime won't connect after 90s | Take a screenshot, check for Google sign-in prompt; if signed into wrong account, do account switch |
| T4 not available dialog | Accept the offered GPU, log actual type from `nvidia-smi`, continue |
| CUDA OOM mid-run | Add `torch.cuda.empty_cache()` before the OOM step; reduce batch size by 50%; rerun from last checkpoint |
| Cell hangs with no output | Check if it's waiting on Drive mount auth; if so, take a screenshot and check for an auth dialog |
| Drive mount auth dialog | Take a screenshot with `mcp__claude-in-chrome__computer`, click "Connect to Google Drive" → permit in the popup |

## Integration with /deep-work

When used as a sub-task inside `/deep-work`:
1. Load this skill's Chrome tools (Step 0) at the start of the parent deep-work session — don't re-load each sub-task.
2. Call Steps 1–3 once at session start to set up the Colab connection.
3. Steps 4–7 repeat per experiment as the deep-work plan progresses.
4. Deep-work's "never ask questions" principle applies here too — make GPU/config decisions autonomously, document them in cell comments.

## Source

- colab-mcp: https://github.com/googlecolab/colab-mcp
- MCP bridge tool: `mcp__colab-mcp__open_colab_browser_connection`
- Post-connection tools discovered via: `ToolSearch query: "colab mcp notebook cell"`
