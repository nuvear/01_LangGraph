"""Shared classroom runtime: explicit live calls, tracing, and bounded file writes."""
from __future__ import annotations

import argparse
from contextvars import ContextVar
import json
import os
from pathlib import Path
import re
from typing import Any, Callable
from uuid import uuid4

from course_support.check_connections import values
from course_support.observability import BACKENDS, graph_tracing

ROOT = Path(__file__).resolve().parents[1]
_CONFIG: ContextVar[dict] = ContextVar("course_graph_config", default={})


def execution_config(thread_id: str | None = None) -> dict:
    """Copy the selected callbacks; optionally choose an isolated checkpoint thread."""
    config = {**_CONFIG.get(), "recursion_limit": 40}
    if thread_id is not None:
        config["configurable"] = {"thread_id": thread_id}
    return config


def get_model(*, live: bool, max_tokens: int = 768):
    """No silent fake model: callers must explicitly opt into a real paid request."""
    if not live:
        raise ValueError("This example needs --live for real Anthropic calls. Offline pytest uses explicit test doubles.")
    from langchain_anthropic import ChatAnthropic

    settings = values()
    key = settings.get("ANTHROPIC_API_KEY")
    model = settings.get("ANTHROPIC_MODEL")
    if not key or not model:
        raise ValueError("Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL in the local .env.")
    return ChatAnthropic(
        model=model, api_key=key, max_tokens=max_tokens,
        timeout=60, max_retries=1,
    )


def message_text(message: Any) -> str:
    """Read ordinary text without exposing provider internals or configuration."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


def output_directory(workdir: Path | str | None, lesson_id: str) -> Path:
    path = Path(workdir) if workdir is not None else ROOT / ".work" / "student-runs" / lesson_id.lower() / uuid4().hex[:8]
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_text(directory: Path | str, filename: str, content: str) -> Path:
    """Write a NEW text file beneath an explicit directory, never silently overwrite."""
    root = Path(directory).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.txt", filename):
        raise ValueError("Use a simple .txt filename: no directories, traversal, or absolute paths.")
    if ".." in filename:
        raise ValueError("Parent traversal is not allowed.")
    target = root / filename
    if target.is_symlink() or target.resolve().parent != root:
        raise ValueError("The output must remain within the selected directory.")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(content)
    return target


def run_cli(lesson_id: str, run_demo: Callable[..., dict]) -> None:
    parser = argparse.ArgumentParser(description=f"Run {lesson_id} teaching example.")
    parser.add_argument("--live", action="store_true", help="Allow real paid Anthropic requests.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--backend", choices=BACKENDS,
                        default={"S1": "langsmith", "S2": "langwatch"}.get(lesson_id, "none"))
    arguments = parser.parse_args()
    workdir = output_directory(arguments.output_dir, lesson_id)
    with graph_tracing(arguments.backend, name=f"LangGraph Course {lesson_id}") as config:
        token = _CONFIG.set(config)
        try:
            result = run_demo(live=arguments.live, workdir=workdir)
        finally:
            _CONFIG.reset(token)
    print(json.dumps({"lesson": lesson_id, "status": "passed", "live_api_enabled": arguments.live,
                      "backend": arguments.backend, "result": result}, indent=2, default=str))
