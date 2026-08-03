"""Startup health checks: each default root reachable, ffmpeg/ffprobe on
PATH, Ollama connectivity. Pure functions, independently testable, kept
separate from how the UI displays their results (main_window.py wires
these into the status bar as a non-blocking badge, never a dialog that
blocks launch)."""
from __future__ import annotations

import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import paths

OLLAMA_URL = "http://127.0.0.1:11434/api/tags"
OLLAMA_TIMEOUT_S = 2.0


@dataclass
class CheckResult:
    name: str
    ok: bool
    message: str


def check_roots() -> list[CheckResult]:
    results = []
    for key in paths.get_roots():
        try:
            resolved = paths.resolve_safe_path(key)
            results.append(CheckResult(f"root:{key}", True, f"{key} reachable at {resolved}"))
        except paths.RootUnavailable as exc:
            results.append(CheckResult(f"root:{key}", False, str(exc)))
    return results


def check_ffmpeg() -> CheckResult:
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return CheckResult("ffmpeg", True, f"ffmpeg at {ffmpeg_path}, ffprobe at {ffprobe_path}")
    missing = [n for n, p in (("ffmpeg", ffmpeg_path), ("ffprobe", ffprobe_path)) if not p]
    return CheckResult("ffmpeg", False, f"not on PATH: {', '.join(missing)}")


def check_ollama() -> CheckResult:
    try:
        req = urllib.request.Request(OLLAMA_URL, method="GET")
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_S):
            return CheckResult("ollama", True, "Ollama reachable at 127.0.0.1:11434")
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return CheckResult("ollama", False, f"Ollama unavailable: {exc}")


def run_all_checks() -> list[CheckResult]:
    results = list(check_roots())
    results.append(check_ffmpeg())
    results.append(check_ollama())
    return results
