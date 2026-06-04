#!/usr/bin/env python3
"""Gemini headless wrapper for non-interactive delegation. Zero-dependency (stdlib only).

PRIMARY path: the legacy `gemini` CLI (npm .CMD shim) driven via STDIN in
interactive mode. The legacy `gemini` CLI is authenticated and works reliably,
and is the default for general tasks/labeling.

Why STDIN (not `-p`): `gemini -m <model> -p "<prompt>"` (prompt as argv) only
works for SHORT prompts (~under 1-2k chars); larger prompts silently return
empty. Piping the prompt via STDIN with no `-p` flag is reliable for prompts of
ANY size.

ANTIGRAVITY path (`--engine agy`): the Antigravity CLI (`agy`), serving
Gemini 3.5 Flash. agy auth is NOT broken (the earlier belief that it "returns
empty / not authenticated" was wrong — its log shows auth + a real API call +
a generated response). The catch: agy only emits its answer to a real console
via an animated "text drip", so a plain pipe captures nothing. The `agy_pty.py`
helper drives agy under a ConPTY (pywinpty) so the output is captured reliably.
`auto` uses gemini first and falls back to the agy ConPTY path.
"""

import argparse
import os
import shutil
import subprocess
import sys


# Preamble / warning lines emitted by the gemini CLI on stdout before the real
# response. These are stripped from the captured output.
_PREAMBLE_MARKERS = (
    "Warning: True color",
    "Ripgrep is not available",
    "YOLO mode",
    "Loaded cached",
)

DEFAULT_MODEL = "gemini-2.5-flash"


def _resolve_gemini() -> str | None:
    """Locate the legacy gemini binary. On Windows this is an npm .CMD shim
    (e.g. C:/Users/<user>/AppData/Roaming/npm/gemini.CMD). shutil.which finds
    it; subprocess.run with the resolved path can execute it."""
    return shutil.which("gemini")


def _resolve_agy() -> str | None:
    """Locate the agy binary. On Windows, the installer puts it in
    $LOCALAPPDATA/agy/bin/agy.exe and ensures it's on the user PATH (may
    require a shell restart for `shutil.which` to find it)."""
    explicit = shutil.which("agy")
    if explicit:
        return explicit
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidate = os.path.join(local, "agy", "bin", "agy.exe")
        if os.path.isfile(candidate):
            return candidate
    return None


def _strip_preamble(text: str) -> str:
    """Remove gemini CLI preamble/warning lines from stdout, returning only the
    real response content."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if any(marker in line for marker in _PREAMBLE_MARKERS):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def gemini_is_available() -> bool:
    """Check if a working Gemini engine is available.

    Primary signal: the legacy `gemini` binary produces non-empty output for a
    tiny stdin prompt (proves it's installed AND authenticated). Falls back to
    checking that the agy binary at least runs `--version`.
    """
    gemini_bin = _resolve_gemini()
    if gemini_bin:
        try:
            result = subprocess.run(
                [gemini_bin, "-m", DEFAULT_MODEL],
                input="Reply with one word: OK",
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=60,
            )
            if result.returncode == 0 and _strip_preamble(result.stdout):
                return True
        except Exception:
            pass

    agy_bin = _resolve_agy()
    if agy_bin:
        try:
            result = subprocess.run(
                [agy_bin, "--version"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    return False


def _call_gemini_stdin(prompt, model, timeout_sec, cwd):
    """Primary path: drive the legacy `gemini` CLI via STDIN."""
    gemini_bin = _resolve_gemini()
    if not gemini_bin:
        return None  # signal caller to try fallback

    cmd = [gemini_bin, "-m", model or DEFAULT_MODEL]
    env = os.environ.copy()

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec + 30,
        cwd=cwd,
        env=env,
    )

    if result.returncode != 0:
        stderr_msg = result.stderr.strip() if result.stderr else f"exit code {result.returncode}"
        print(f"ERROR: gemini CLI failed: {stderr_msg}", file=sys.stderr)
        sys.exit(1)

    output = _strip_preamble(result.stdout or "")

    if not output:
        print(
            "ERROR: gemini CLI returned empty output after stripping preamble. "
            "Likely cause: not authenticated or rate-limited. Run `gemini` "
            "interactively to verify login, then retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[gemini] Response: {len(output)} chars", file=sys.stderr)
    return output


def _call_agy(prompt, yolo, sandbox, timeout_sec, cwd):
    """Antigravity path: drive `agy --print` through a ConPTY (pywinpty).

    `agy` only emits its response to a real console via an animated "text drip";
    a plain captured pipe gets nothing (this — NOT broken auth — is why naive
    `agy --print` from a subprocess looked empty). The `agy_pty.py` helper gives
    it a pseudo-console so the output is captured reliably. Prompt is piped to
    the helper via STDIN; it returns the cleaned response on STDOUT.
    """
    agy_bin = _resolve_agy()
    if not agy_bin:
        print(
            "ERROR: neither gemini nor agy CLI found. Install the legacy gemini "
            "CLI (`npm i -g @google/gemini-cli`) or the Antigravity CLI.",
            file=sys.stderr,
        )
        sys.exit(1)

    helper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agy_pty.py")
    if not os.path.isfile(helper):
        print(f"ERROR: agy ConPTY helper not found at {helper}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, helper, "--timeout", str(timeout_sec)]
    if cwd:
        cmd += ["--cwd", cwd]
    # yolo/sandbox no longer apply: the ConPTY helper always runs agy with
    # --dangerously-skip-permissions (required so print mode doesn't block on an
    # interactive permission prompt). They are accepted for API stability only.

    env = os.environ.copy()
    try:
        result = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout_sec + 30, cwd=cwd, env=env,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: Antigravity (agy ConPTY) timed out after {timeout_sec}s", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        stderr_msg = result.stderr.strip() if result.stderr else f"exit code {result.returncode}"
        print(f"ERROR: Antigravity (agy ConPTY) failed: {stderr_msg}", file=sys.stderr)
        sys.exit(1)

    output = (result.stdout or "").strip()
    if not output:
        print(
            "ERROR: Antigravity (agy ConPTY) returned empty output. Check `agy` "
            "is logged in (run it interactively once) and not rate-limited.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[agy] Response: {len(output)} chars", file=sys.stderr)
    return output


def call_gemini(
    prompt,
    model=None,
    output_format="text",
    yolo=False,
    sandbox=False,
    timeout_sec=300,
    cwd=None,
    engine="auto",
):
    """Call a Gemini engine in headless mode and return the output.

    engine:
        "auto"   -> try legacy gemini (stdin) first, fall back to agy
        "gemini" -> force legacy gemini (stdin) only
        "agy"    -> force Antigravity CLI only

    The `output_format` arg is accepted for API stability with the prior
    wrapper but is currently ignored.
    """
    try:
        if engine in ("auto", "gemini"):
            out = _call_gemini_stdin(prompt, model, timeout_sec, cwd)
            if out is not None:
                return out
            if engine == "gemini":
                print("ERROR: gemini CLI not found.", file=sys.stderr)
                sys.exit(1)
            # engine == "auto" and gemini missing -> fall through to agy
        return _call_agy(prompt, yolo, sandbox, timeout_sec, cwd)
    except subprocess.TimeoutExpired:
        print(f"ERROR: Gemini CLI timed out after {timeout_sec}s", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gemini headless wrapper (legacy gemini via stdin, agy fallback)")
    parser.add_argument("--prompt", required=False, help="Prompt to send to Gemini")
    parser.add_argument("--model", default=None,
                        help=f"Model override (default: {DEFAULT_MODEL})")
    parser.add_argument("--engine", choices=["auto", "gemini", "agy"], default="auto",
                        help="Backend engine: auto (default), gemini (legacy stdin), or agy (Antigravity)")
    parser.add_argument("--yolo", action="store_true",
                        help="Auto-approve all tool actions (agy fallback only: maps to --dangerously-skip-permissions)")
    parser.add_argument("--sandbox", action="store_true",
                        help="Run in sandbox mode (agy fallback only)")
    parser.add_argument("--output-format", choices=["text", "json", "stream-json"],
                        default="text", help="Output format (currently ignored)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout in seconds (default: 300)")
    parser.add_argument("--cwd", default=None,
                        help="Working directory")
    parser.add_argument("--check-only", action="store_true",
                        help="Check if a Gemini engine is available and exit")
    args = parser.parse_args()

    if args.check_only:
        ok = gemini_is_available()
        print("READY" if ok else "NOT_READY")
        sys.exit(0 if ok else 1)

    if not args.prompt:
        parser.error("--prompt is required unless using --check-only")

    result = call_gemini(
        prompt=args.prompt,
        model=args.model,
        output_format=args.output_format,
        yolo=args.yolo,
        sandbox=args.sandbox,
        timeout_sec=args.timeout,
        cwd=args.cwd,
        engine=args.engine,
    )
    print(result)


if __name__ == "__main__":
    main()
