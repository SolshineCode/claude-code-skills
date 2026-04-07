#!/usr/bin/env python3
"""Gemini CLI wrapper for non-interactive delegation. Zero-dependency (stdlib only)."""

import argparse
import json
import os
import subprocess
import sys
import time


def gemini_is_available():
    """Check if Gemini CLI is installed and authenticated."""
    import shutil
    gemini_bin = shutil.which("gemini")
    if not gemini_bin:
        return False
    try:
        result = subprocess.run(
            [gemini_bin, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def call_gemini(
    prompt,
    model=None,
    output_format="text",
    yolo=False,
    sandbox=False,
    timeout_sec=300,
    cwd=None,
):
    """Call Gemini CLI in headless mode and return the output."""
    # On Windows, subprocess needs the .cmd shim or full path
    import shutil
    gemini_bin = shutil.which("gemini") or "gemini"
    cmd = [gemini_bin, "-p", prompt]

    if model:
        cmd.extend(["-m", model])

    if output_format:
        cmd.extend(["-o", output_format])

    if yolo:
        cmd.append("--yolo")

    if sandbox:
        cmd.append("-s")

    env = os.environ.copy()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=cwd,
            env=env,
        )

        if result.returncode == 41:
            print("ERROR: Gemini CLI not authenticated. Run 'gemini' interactively to log in.", file=sys.stderr)
            sys.exit(1)

        if result.returncode != 0:
            stderr_msg = result.stderr.strip() if result.stderr else f"exit code {result.returncode}"
            print(f"ERROR: Gemini CLI failed: {stderr_msg}", file=sys.stderr)
            sys.exit(1)

        output = result.stdout.strip()

        # Log stats to stderr
        print(f"[gemini] Response: {len(output)} chars", file=sys.stderr)

        return output

    except subprocess.TimeoutExpired:
        print(f"ERROR: Gemini CLI timed out after {timeout_sec}s", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: Gemini CLI not found. Install with: npm i -g @google/gemini-cli", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gemini CLI headless wrapper")
    parser.add_argument("--prompt", required=True, help="Prompt to send to Gemini")
    parser.add_argument("--model", default=None,
                        help="Model override (e.g., gemini-2.5-flash, gemini-2.5-pro)")
    parser.add_argument("--yolo", action="store_true",
                        help="Auto-approve all tool actions")
    parser.add_argument("--sandbox", action="store_true",
                        help="Run in sandbox mode (restricted file access)")
    parser.add_argument("--output-format", choices=["text", "json", "stream-json"],
                        default="text", help="Output format")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout in seconds (default: 300)")
    parser.add_argument("--cwd", default=None,
                        help="Working directory for Gemini")
    parser.add_argument("--check-only", action="store_true",
                        help="Check if Gemini CLI is available and exit")
    args = parser.parse_args()

    if args.check_only:
        ok = gemini_is_available()
        print("READY" if ok else "NOT_READY")
        sys.exit(0 if ok else 1)

    result = call_gemini(
        prompt=args.prompt,
        model=args.model,
        output_format=args.output_format,
        yolo=args.yolo,
        sandbox=args.sandbox,
        timeout_sec=args.timeout,
        cwd=args.cwd,
    )
    print(result)


if __name__ == "__main__":
    main()
