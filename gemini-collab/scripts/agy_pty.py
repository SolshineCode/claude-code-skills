#!/usr/bin/env python3
"""Drive the Antigravity CLI (`agy --print`) through a ConPTY (pywinpty) so its
TTY-only "text drip" render is captured.

WHY THIS EXISTS
---------------
`agy` authenticates and generates responses fine from a subprocess (verified via
its own log: `Auth done received` -> `streamGenerateContent` -> a non-empty
`text_drip` of the answer). The earlier belief that "agy subprocess auth is
broken / returns empty" was WRONG. The real problem: `agy` only emits the
response to a real console via an animated "text drip"; a plain captured pipe
gets nothing and the process often hangs waiting on a console. Giving it a
pseudo-console (ConPTY via pywinpty) makes the output capturable and reliable.

A reader thread drains the PTY (pywinpty read() blocks), while the main thread
enforces a hard wall-clock cap plus an idle cutoff: once output stops arriving
for `--idle` seconds *after* some output has been seen, the drip is done and we
terminate the (otherwise lingering) agy process.

DEPENDENCY: pywinpty (`pip install pywinpty`). Already present in the user's
default python on this machine (winpty 2.0.15).

Usage:  echo "your prompt" | python agy_pty.py [--timeout 120] [--idle 4] [--cwd DIR]
Prompt is read from STDIN; the cleaned response is written to STDOUT.

NOTE: run `agy` from a small/empty CWD, never the home root (C:\\Users\\<user>),
or it hangs indexing the whole home workspace. The default cwd below is a
dedicated temp dir created on demand.
"""
import os
import re
import sys
import time
import threading
import argparse

try:
    import winpty  # pywinpty
except ImportError:
    sys.stderr.write(
        "ERROR: pywinpty not installed. Run `pip install pywinpty` "
        "(the agy ConPTY engine needs it).\n"
    )
    sys.exit(3)


def strip_ansi(s: str) -> str:
    s = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", s)   # OSC
    s = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", s)            # CSI
    s = re.sub(r"\x1b[()][0-9A-B]", "", s)                     # charset select
    s = re.sub(r"\x1b[=>]", "", s)
    return s.replace("\r", "")


PREAMBLE = (
    "Warning: True color", "Ripgrep is not available", "YOLO mode",
    "Loaded cached", "Tips for getting started", "data is collected",
)


def main():
    ap = argparse.ArgumentParser(description="Capture Antigravity (agy) via ConPTY")
    ap.add_argument("--timeout", type=int, default=120, help="hard wall-clock cap (s)")
    ap.add_argument("--idle", type=float, default=1.0,
                    help="stop this many s after the REAL answer stops growing. "
                         "Counted only once non-preamble content appears, so the "
                         "startup preamble->answer gap never triggers a premature cutoff.")
    ap.add_argument("--cwd", default=None,
                    help="working dir for agy (default: %LOCALAPPDATA%\\agy\\_runcwd). "
                         "Never the home root.")
    args = ap.parse_args()

    prompt = sys.stdin.read().strip()
    if not prompt:
        sys.stderr.write("ERROR: empty prompt on stdin\n")
        sys.exit(2)

    local = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    agy = os.path.join(local, "agy", "bin", "agy.exe")
    if not os.path.isfile(agy):
        sys.stderr.write(f"ERROR: agy not found at {agy}\n")
        sys.exit(4)

    cwd = args.cwd or os.path.join(local, "agy", "_runcwd")
    os.makedirs(cwd, exist_ok=True)

    # agy reads --print from argv. Neutralize embedded double-quotes so the
    # command line stays well-formed.
    safe_prompt = prompt.replace('"', "'")
    cmdline = (
        f'{agy} --print "{safe_prompt}" '
        f'--dangerously-skip-permissions --print-timeout {args.timeout}s'
    )

    pty = winpty.PtyProcess.spawn(cmdline, cwd=cwd, dimensions=(50, 200))

    buf = []
    last_data = [time.monotonic()]
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                data = pty.read(2048)
            except EOFError:
                break
            except Exception:
                break
            if data:
                buf.append(data)
                last_data[0] = time.monotonic()
            else:
                time.sleep(0.03)

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    def real_len():
        clean = strip_ansi("".join(buf))
        lines = [ln for ln in clean.splitlines() if not any(m in ln for m in PREAMBLE)]
        return len("\n".join(lines).strip())

    start = time.monotonic()
    last_real_grow = [None]   # time the real (non-preamble) answer last grew
    prev_real = 0
    while True:
        time.sleep(0.1)
        now = time.monotonic()
        if not pty.isalive():   # agy exited on its own — fastest path, done
            break
        if now - start > args.timeout:
            break
        rl = real_len()
        if rl > prev_real:
            prev_real = rl
            last_real_grow[0] = now
        # Idle cutoff counts only the REAL answer's silence, so the startup
        # preamble->answer gap can't end us early.
        if last_real_grow[0] is not None and (now - last_real_grow[0]) > args.idle:
            break

    stop.set()
    try:
        if pty.isalive():
            pty.terminate(force=True)
    except Exception:
        pass

    raw = "".join(buf)
    clean = strip_ansi(raw)
    lines = [ln for ln in clean.splitlines() if not any(m in ln for m in PREAMBLE)]
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).strip())
    if not out:
        sys.stderr.write(
            "ERROR: agy ConPTY produced no output. Check `agy` is logged in "
            "(run `agy` interactively once) and not rate-limited.\n"
        )
        sys.exit(1)
    sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()
