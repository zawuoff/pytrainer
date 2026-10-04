"""AI providers backed by CLIs the learner already pays for (no API keys needed).

- claude   -> Claude Code (`claude -p`), uses the Claude subscription
- codex    -> OpenAI Codex CLI (`codex exec`), uses the ChatGPT subscription
- opencode -> OpenCode (`opencode run`), uses OpenCode Go / Zen or any configured provider
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import db

EXTRA_PATHS = [
    Path.home() / ".local/bin",
    Path.home() / ".local/share/mise/shims",
    Path.home() / ".cargo/bin",
    Path.home() / ".bun/bin",
    Path.home() / ".npm-global/bin",
    Path("/usr/local/bin"),
]

PROVIDERS = {
    "claude": {"label": "Claude Code", "binary": "claude",
               "detail": "Uses your Claude Pro/Max subscription via the Claude Code CLI.",
               "models": ["sonnet", "opus", "haiku"], "default_model": "sonnet"},
    "codex": {"label": "Codex (ChatGPT)", "binary": "codex",
              "detail": "Uses your ChatGPT Plus/Pro subscription via the Codex CLI.",
              "models": [], "default_model": ""},
    "opencode": {"label": "OpenCode", "binary": "opencode",
                 "detail": "Uses OpenCode Go/Zen or whatever providers OpenCode is logged into.",
                 "models": [], "default_model": ""},
}


class AIError(Exception):
    pass


def _env() -> dict:
    env = dict(os.environ)
    parts = env.get("PATH", "").split(os.pathsep)
    for p in EXTRA_PATHS:
        if str(p) not in parts:
            parts.append(str(p))
    # mise installs live in per-tool dirs; add them if present
    mise = Path.home() / ".local/share/mise/installs"
    if mise.is_dir():
        for tool in ("claude", "codex", "opencode", "node"):
            for d in sorted(mise.glob(f"{tool}/*"), reverse=True):
                for cand in (d, d / "bin"):
                    if cand.is_dir() and str(cand) not in parts:
                        parts.append(str(cand))
    env["PATH"] = os.pathsep.join(p for p in parts if p)
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return env


def which(binary: str) -> str | None:
    return shutil.which(binary, path=_env()["PATH"])


def detect() -> list[dict]:
    out = []
    for key, p in PROVIDERS.items():
        path = which(p["binary"])
        models = list(p["models"])
        if key == "opencode" and path:
            try:
                cp = subprocess.run([path, "models"], capture_output=True, text=True,
                                    timeout=20, env=_env())
                models = [m.strip() for m in cp.stdout.splitlines() if "/" in m][:200]
            except (OSError, subprocess.SubprocessError):
                pass
        out.append({"id": key, "label": p["label"], "detail": p["detail"],
                    "installed": bool(path), "path": path, "models": models,
                    "default_model": p["default_model"]})
    return out


def current() -> dict:
    return db.get_setting("ai", {"provider": "none", "model": ""})


def enabled() -> bool:
    return current().get("provider", "none") != "none"


def _workdir() -> str:
    d = db.DATA_DIR / "ai-workdir"
    d.mkdir(parents=True, exist_ok=True)
    return str(d)


def complete(system: str, prompt: str, *, timeout: int = 240, provider: str | None = None,
             model: str | None = None) -> str:
    cfg = current()
    provider = provider or cfg.get("provider", "none")
    model = model if model is not None else cfg.get("model", "")
    if provider == "none":
        raise AIError("No AI provider connected. Connect one in Settings.")
    if provider not in PROVIDERS:
        raise AIError(f"Unknown provider {provider}")
    binary = which(PROVIDERS[provider]["binary"])
    if not binary:
        raise AIError(f"{PROVIDERS[provider]['label']} CLI not found on PATH.")
    try:
        if provider == "claude":
            return _claude(binary, system, prompt, model, timeout)
        if provider == "codex":
            return _codex(binary, system, prompt, model, timeout)
        return _opencode(binary, system, prompt, model, timeout)
    except subprocess.TimeoutExpired:
        raise AIError("The AI took too long to answer. Try again.") from None


def _claude(binary, system, prompt, model, timeout):
    cmd = [binary, "-p", "--output-format", "json", "--system-prompt", system,
           "--tools", "", "--no-session-persistence", "--strict-mcp-config"]
    if model:
        cmd += ["--model", model]
    cp = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout,
                        env=_env(), cwd=_workdir())
    try:
        data = json.loads(cp.stdout)
    except json.JSONDecodeError:
        raise AIError(_err("Claude Code", cp)) from None
    if data.get("is_error"):
        raise AIError(f"Claude Code error: {data.get('result') or data.get('subtype')}")
    return (data.get("result") or "").strip()


def _codex(binary, system, prompt, model, timeout):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "last.txt"
        cmd = [binary, "exec", "--skip-git-repo-check", "-s", "read-only", "--ephemeral",
               "--color", "never", "-o", str(out)]
        if model:
            cmd += ["-m", model]
        cmd.append("-")
        full = (f"<instructions>\n{system}\n</instructions>\n\n"
                "Do not run any commands or read any files; answer directly from the text below.\n\n"
                f"{prompt}")
        cp = subprocess.run(cmd, input=full, capture_output=True, text=True, timeout=timeout,
                            env=_env(), cwd=tmp)
        text = out.read_text().strip() if out.exists() else ""
        if not text:
            raise AIError(_err("Codex", cp))
        return text


def _opencode(binary, system, prompt, model, timeout):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [binary, "run", "--format", "json"]
        if model:
            cmd += ["-m", model]
        full = (f"<instructions>\n{system}\n</instructions>\n\n"
                "Do not use any tools; answer directly.\n\n" + prompt)
        prompt_file = Path(tmp) / "prompt.md"
        prompt_file.write_text(full)
        cmd += ["-f", str(prompt_file), "--", "Follow the instructions in the attached prompt.md exactly."]
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=_env(),
                            cwd=tmp, stdin=subprocess.DEVNULL)
        parts = []
        for line in cp.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "text":
                parts.append(ev.get("part", {}).get("text", ""))
        text = "".join(parts).strip()
        if not text:
            raise AIError(_err("OpenCode", cp))
        return text


def _err(name, cp) -> str:
    tail = (cp.stderr or cp.stdout or "").strip()[-600:]
    tail = re.sub(r"\x1b\[[0-9;]*m", "", tail)
    return f"{name} failed (exit {cp.returncode}). {tail}"


def complete_json(system: str, prompt: str, **kw) -> dict:
    """Ask for a single JSON object and parse it robustly."""
    system = system + ("\n\nRespond with ONLY one valid JSON object. No prose before or after, "
                       "no markdown code fences.")
    text = complete(system, prompt, **kw)
    return extract_json(text)


def extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    if start == -1:
        raise AIError("The AI did not return JSON.")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError as exc:
                    raise AIError(f"The AI returned malformed JSON: {exc}") from None
    raise AIError("The AI returned incomplete JSON.")
