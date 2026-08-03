# vanlife-dashboard — Project Law

Public Mycelia Interactive LLC repository. Default branch: `main`.
Workspace root: `D:\_Dev\AI-Setup\SEEKERS_GHOSTS\_test_project\vanlife-dashboard`
Public repo: `github.com/TheSeeker713/vanlife-dashboard`

This project has its own independent git repository, nested inside the SEEKERS_GHOSTS working tree but excluded from that repo's own git tracking (see SEEKERS_GHOSTS's `.gitignore`). It is not part of the SEEKERS_GHOSTS control-plane build.

---

## Project identity

vanlife-dashboard is a native desktop assistant-editor tool (PySide6/Qt, no browser, no web server) that helps organize raw vanlife-documentary footage before real post-production in DaVinci Resolve Studio. It reuses two proven modules from the sibling SEEKERS_GHOSTS repo (`app.concurrency.SingleJobGate`, `_core.engine.prompts.ollama_generate`) via `sys.path` import, but is otherwise a self-contained project with its own dependencies, its own database, and its own build history.

Core workflow: watch a clip, drop timestamped/tagged markers while scrubbing, then either use UI controls or a chat agent (local Ollama by default, optional Grok via OpenClaw) to file the clip into a destination folder or the `Discard` folder. Every organize action copies the file and verifies the copy against the source with a hash. A per-clip Markdown metadata document accumulates markers, chat notes, AI-suggested tags/transcript, and organize/verify history.

This is a human-in-the-loop tool. Agents (chat, auto-tagging, transcription) act only in direct response to user input and never re-trigger themselves.

---

## Hard rules

1. **No video is ever deleted, by any flow, under any circumstance.** This is a non-negotiable constraint from the project owner's household, not a technical preference. Clips that aren't usable for the documentary are copied into a `Discard` destination folder using the exact same copy-and-verify pipeline as any other organize action. The original source file is never removed by this app. If a future request asks for a delete capability, decline and point back to this rule; it does not get silently relaxed for convenience.

2. **Sandbox roots.** All filesystem reads/writes/deletes funnel through `paths.py::resolve_safe_path()`, resolved against the `roots` table (three seeded defaults plus any user-registered folders). Never touch a path outside a registered root. Never accept `root="project"` (read-only) as a write/copy/delete target.

3. **Three independent concurrency gates, one per GPU/CPU resource class.** `GATE` (Ollama: chat + VLM auto-tagging), `TRANSCODE_GATE` (ffmpeg proxy generation), `WHISPER_GATE` (local transcription, CPU by default). Never let two of these run simultaneously against the same resource; this machine has a documented crash history from sustained combined GPU/memory load (see SEEKERS_GHOSTS's `docs/SYSTEM_CRASH_LOG_IMPORTANT.md`).

4. **Human confirmation before every disk-mutating action.** Organize, discard, folder create/rename/delete: always a confirm step, whether triggered from the UI or from a chat action. `append_metadata_note` and `search_footage` are the only actions that apply immediately, because they are low-risk/reversible or read-only.

5. **Agents activate only on user input.** No scheduler, no APScheduler, no autonomous multi-step loop. One chat turn is one request/response. The resource watchdog's "soft shutdown" is a rule-based safety brake, not an autonomous agent action, and it only pauses new AI/transcode work, never deletes or mutates anything on disk.

6. **Verification before assertion.** Never report a step complete without actually checking: run the step's test, read its real output, confirm the claimed state matches. This project follows SEEKERS_GHOSTS's own documented lesson about false-positive completion claims. For any phase with a user-facing surface, this specifically includes Jeremy running the phase's UI/UX checklist himself, the agent's own screenshots and automated tests are necessary but not sufficient to close such a phase.

7. **Secrets.** Any API keys or credentials (e.g. for an optional OpenClaw/Grok backend) live in `.env` only, gitignored. `.env.example` ships with placeholders only.

8. **Verified, current dependencies.** Dependency versions are checked live against PyPI and pinned exactly in `requirements.txt`, not left as loose floors. Re-verify before pinning if significant time has passed since the last check.

---

## Development protocol (summary)

Full detail: [INSTRUCTIONS.md](INSTRUCTIONS.md) and [.claude/rules/phase-protocol.md](.claude/rules/phase-protocol.md) (auto-followed regardless of whether INSTRUCTIONS.md gets re-read).

- Inside a phase, run steps in sequence without waiting between steps.
- Each step: build → test → verify the test actually passed (check real output, not just exit code). A failed or unverified test means the step is incomplete, fix and re-test before moving on.
- Steps don't each get their own commit. Once every step in the phase is done, run the close-out sequence: **Cross-Check & Full Project Audit** (stale references, doc/code agreement, clean diff) → **re-run tests** (this phase plus a regression pass on prior phases) → **one commit and push** for the phase → **devlog entry** (voice rules in [.claude/rules/devlog-voice.md](.claude/rules/devlog-voice.md)) → **UI/UX checklist** for phases with a user-facing surface, run by Jeremy himself, not just the agent.
- After that sequence: **stop**. Report a phase summary. Wait for Jeremy's explicit go-ahead before starting the next phase.

---

## Read order (every session)

1. [AGENTS.md](AGENTS.md) (this file)
2. [INSTRUCTIONS.md](INSTRUCTIONS.md)
3. [.claude/rules/](.claude/rules/) (`phase-protocol.md`, `devlog-voice.md`) — durable rules, auto-followed even if 1 and 2 aren't re-read
4. Most recent entry under `docs/devlog/`

---

_Mycelia Interactive LLC — Keep At It, Always._
