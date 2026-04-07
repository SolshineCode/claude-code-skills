#!/usr/bin/env python3
"""Local Nemotron client via Ollama. Zero-dependency (stdlib only)."""

import argparse
import io
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "nemotron-3-nano:4b"


def ollama_is_running():
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except Exception:
        return False


def model_is_available(model):
    try:
        resp = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5)
        data = json.loads(resp.read())
        return any(m["name"] == model for m in data.get("models", []))
    except Exception:
        return False


def ensure_ollama_ready(model):
    """Start Ollama and pull model if needed. Returns True if ready."""
    if not ollama_is_running():
        print("[nemotron] Starting Ollama...", file=sys.stderr)
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        for _ in range(30):
            time.sleep(1)
            if ollama_is_running():
                break
        else:
            print("ERROR: Ollama failed to start after 30s", file=sys.stderr)
            return False

    if not model_is_available(model):
        print(f"[nemotron] Pulling {model}...", file=sys.stderr)
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            print(f"ERROR: Failed to pull {model}: {result.stderr}", file=sys.stderr)
            return False

    return True


def call_nemotron(prompt, system="", model=DEFAULT_MODEL, max_tokens=2048, temperature=0.3):
    """Call local Nemotron via Ollama's OpenAI-compatible API."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
            msg = data.get("message", {})
            content = msg.get("content", "")
            thinking = msg.get("thinking", "")
            # Include timing info on stderr for the orchestrator
            total_ns = data.get("total_duration", 0)
            eval_count = data.get("eval_count", 0)
            if total_ns:
                think_note = f" ({len(thinking)} chars thinking)" if thinking else ""
                print(
                    f"[nemotron] {eval_count} tokens in {total_ns/1e9:.1f}s "
                    f"({eval_count/(total_ns/1e9):.1f} tok/s){think_note}",
                    file=sys.stderr,
                )
            return content, thinking
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"ERROR: Ollama HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Local Nemotron via Ollama")
    parser.add_argument("--prompt", required=True, help="User prompt")
    parser.add_argument("--system", default="", help="System prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--ensure-ready", action="store_true",
                        help="Auto-start Ollama and pull model if needed")
    parser.add_argument("--show-thinking", action="store_true",
                        help="Also print the model's thinking chain to stderr")
    parser.add_argument("--check-only", action="store_true",
                        help="Just check if Ollama + model are ready, exit 0/1")
    args = parser.parse_args()

    # Force UTF-8 output on Windows (cp1252 can't handle Unicode from LLM)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    if args.check_only:
        ok = ollama_is_running() and model_is_available(args.model)
        print("READY" if ok else "NOT_READY")
        sys.exit(0 if ok else 1)

    if args.ensure_ready:
        if not ensure_ollama_ready(args.model):
            sys.exit(1)

    content, thinking = call_nemotron(
        prompt=args.prompt,
        system=args.system,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
    print(content)

    if args.show_thinking and thinking:
        print(f"\n[thinking]\n{thinking}\n[/thinking]", file=sys.stderr)


if __name__ == "__main__":
    main()
