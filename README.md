# Vanlife Dashboard

A native desktop assistant for organizing raw vanlife documentary footage
before it goes into DaVinci Resolve Studio for real editing. Built with
PySide6 (Qt), no browser, no web server, runs entirely on the local
machine.

The core idea: watch a clip, drop timestamped markers while scrubbing,
then either use the UI or ask a chat agent (local Ollama) to file it
into a destination folder. Every organize action copies the file and
verifies the copy against the source with a hash. **No video is ever
deleted by this app**, under any flow. Clips that aren't usable get
copied to a `Discard` folder instead of removed. A per-clip Markdown
document accumulates markers, chat notes, and organize history as the
clip gets worked on.

This is a human-in-the-loop tool. Nothing acts on its own, every
disk-mutating action needs explicit confirmation, and agents (chat,
auto-tagging, transcription) only respond to direct input.

## Status

Actively being built, phase by phase, with tests and a manual UI/UX
checklist gating each phase close. Currently through **Phase 2** of 13
(backend and data foundation). See [INSTRUCTIONS.md](INSTRUCTIONS.md)
for the full phase list and what's actually done versus still ahead.

## Stack

- Python 3.12, [PySide6](https://doc.qt.io/qtforpython-6/) for the UI
- SQLite for local state, no ORM
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for local transcription
- ffmpeg/ffprobe (external, must be on `PATH`) for proxies and thumbnails
- Local [Ollama](https://ollama.com/) for the chat agent and vision-model auto-tagging
- Reuses two modules from the sibling [SEEKERS_GHOSTS](https://github.com/TheSeeker713/SEEKERS_GHOSTS) repo via a `sys.path` bridge (`app.concurrency.SingleJobGate`, `_core.engine.prompts.ollama_generate`), everything else is self-contained

## Running it

Requires a local clone of `SEEKERS_GHOSTS` as a sibling-tree dependency
(see `vldash/config.py` for the exact path resolution, overridable via
the `VANLIFE_SEEKERS_GHOSTS_ROOT` environment variable), and Ollama
running locally for chat/tagging features once those phases land.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m vldash.main
```

## Project layout

```
vldash/            application package (note: not "app", see below)
  ui/               PySide6 widgets, themes, dialogs
  config.py          sys.path bridge, concurrency gates, shared paths
  db.py               SQLite schema and connection
  paths.py             the allow-listed filesystem choke point
  health.py             startup checks (roots, ffmpeg, Ollama)
docs/devlog/        dated build-log entries, one file per day
docs/design/         approved UI mockups kept as design references
.claude/rules/       durable agent rules, auto-loaded by Claude Code
```

The package is named `vldash`, not `app`. It started out as `app/` and
collided with the sibling repo's own `app/` package the moment the
`sys.path` bridge activated, `python -m app.main` caches `app` in
`sys.modules` as this project's package before the bridge can run, so
imports from the sibling repo failed. Renamed to avoid it.

## Contributing / agent instructions

[AGENTS.md](AGENTS.md) is the project's hard rules (what an AI agent
working here must never do). [INSTRUCTIONS.md](INSTRUCTIONS.md) is the
full phased build spec. [CLAUDE.md](CLAUDE.md) is the entry point
Claude Code actually auto-loads, which pulls in `AGENTS.md`.

---

_Mycelia Interactive LLC_
