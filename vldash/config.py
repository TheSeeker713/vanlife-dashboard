"""Project configuration: sys.path bridge to SEEKERS_GHOSTS, the three
concurrency gates, and shared paths.

The three gates live here, not in agent_core.py, specifically so media.py
(Phase 4, needs TRANSCODE_GATE) and transcribe.py (Phase 11, needs
WHISPER_GATE) can import just the gate they need without pulling in the
chat-specific module that doesn't get built until Phase 8.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
PROXY_CACHE_DIR = DATA_DIR / "proxies"
LOG_PATH = DATA_DIR / "app.log"

DEFAULT_OLLAMA_MODEL = "hermes3:8b"

# --- sys.path bridge to the sibling SEEKERS_GHOSTS repo ---------------------

_env_root = os.environ.get("VANLIFE_SEEKERS_GHOSTS_ROOT")
SEEKERS_GHOSTS_ROOT = Path(_env_root) if _env_root else PROJECT_ROOT.parent.parent

_sentinel = SEEKERS_GHOSTS_ROOT / "app" / "concurrency.py"
if not _sentinel.exists():
    raise ImportError(
        f"expected SEEKERS_GHOSTS root at {SEEKERS_GHOSTS_ROOT} "
        f"(sentinel file not found: {_sentinel}); "
        f"set the VANLIFE_SEEKERS_GHOSTS_ROOT environment variable to override"
    )
if str(SEEKERS_GHOSTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SEEKERS_GHOSTS_ROOT))

from app.concurrency import GATE, SingleJobGate  # noqa: E402

TRANSCODE_GATE = SingleJobGate()
WHISPER_GATE = SingleJobGate()

# --- resource watchdog starting thresholds (Error handling & resilience) ----
# Starting configuration, not tuned yet, see the plan's own risk note: these
# need empirical adjustment once the app has run real workloads.
WATCHDOG_WARNING_VRAM_PCT = 85
WATCHDOG_CRITICAL_VRAM_PCT = 95
WATCHDOG_POLL_SECONDS = 5
