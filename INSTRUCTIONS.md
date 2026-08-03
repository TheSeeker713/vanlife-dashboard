# vanlife-dashboard — Build Instructions

Companion to [AGENTS.md](AGENTS.md). This file is the executable build spec: protocol, devlog rules, and phased steps with tests.

Workspace: `D:\_Dev\AI-Setup\SEEKERS_GHOSTS\_test_project\vanlife-dashboard`
Public repo: `github.com/TheSeeker713/vanlife-dashboard`
Default branch: `main`

---

## PHASE_STEP_PROTOCOL

Full detail: [.claude/rules/phase-protocol.md](.claude/rules/phase-protocol.md), which is followed automatically regardless of whether this file gets re-read. Summary:

Within a phase, execute steps (N.1, N.2, N.3...) in sequence without waiting for human input between them. Each step: build the deliverable, test it, verify the test actually passed (check real output/state, don't assume a clean exit code means success). A failed or unverified test means the step isn't done, fix it before moving to the next step. Steps do not each get their own commit, the phase commits once, after the close-out sequence below.

Once every step in the phase is built and individually tested, run the close-out sequence before anything is committed:

1. **Cross-Check & Full Project Audit** — grep for stale references to anything renamed/removed this phase, confirm `AGENTS.md`/`INSTRUCTIONS.md`/the plan doc still agree with what was actually built, confirm no stray test/debug artifacts are staged, review the full diff about to be committed.
2. **Re-run tests** — the phase's own automated tests plus a quick regression pass against prior phases' tests, not just the newest step.
3. **Commit and push** — one commit for the phase (a couple more only if the audit surfaced real fixes needed), pushed to `main`.
4. **Devlog entry**, per the spec below.
5. **UI/UX checklist** (phases with a user-facing surface only) — see the dedicated section below. The phase is not closed and the next phase does not start until Jeremy has run the checklist himself and confirmed, not merely accepted the agent's own report. Phases with no user-facing surface get a lighter functional-verification note instead, stated explicitly rather than silently skipped.

Stop after step 5. Do not start the next phase. Report a phase summary and wait for Jeremy's explicit go-ahead before continuing.

---

## Devlog spec

- **Location:** `docs/devlog/{YYYY-MM-DD}devlog.md`
- One file per calendar day. Create it on the first entry of that day. Append for every subsequent phase closed that day.
- Devlogs are tracked in git. Never gitignore them.
- Every phase-close commit and push is paired with a devlog entry, timestamped with date and time.
- **Voice rules:** the full canonical spec lives in [.claude/rules/devlog-voice.md](.claude/rules/devlog-voice.md) (research grounding, full "never use" list, full "always do" list). Read it before writing an entry, don't rely on memory of it. Short version: written entirely in first person as Jeremy Robards, CTO and CAIO of Mycelia Interactive LLC, never narrated *about* him in the third person. Not written as an AI, not written as a status report. No em dashes. No "not X, but Y" contrast framing. No inflated verbs (delve, underscore, showcase, foster, leverage, boast). Anchored in at least one real, specific detail (a real filename, a real error, a real number) per entry, not summarized in the abstract.
- Each entry must be detailed and explicit about what was actually built or debugged, not vague. It should read like someone who understands the system explaining their own work.

**Entry shape (guidance, not a rigid template):**

```markdown
### HH:MM - Phase N: <short title>

I ...
```

---

## UI/UX Checklist requirement

Every phase that changes what the user sees or interacts with needs a concrete, phase-specific checklist Jeremy runs by hand before the phase counts as closed. The agent's own screenshots and automated tests are necessary but not sufficient, they catch structural bugs, not whether the thing actually feels right to use.

**How to build one:** derive each item directly from that phase's Build/Test descriptions above, phrased as an action plus an expected result ("Click X, confirm Y happens"), not a vague "check that it works." Keep it short enough to actually run through in a few minutes, not a full QA pass. Generate it fresh at that phase's real close-out, against what was actually built, not written in advance for phases that haven't landed yet, a checklist written against a guess goes stale the moment the real UI differs.

Phases with no user-facing surface (pure backend/governance, e.g. Phase 0, most of Phase 2) get a lighter functional checklist instead of a UI/UX one, or skip this step with that noted explicitly rather than silently.

### Worked example: Phase 1 (retroactive)

Phase 1 shipped before this requirement existed. This is the checklist Jeremy is running now, after the fact, to close that gap, and the template every later phase's checklist follows the shape of:

- [ ] Launch the app. Confirm it opens light-themed, Sort page active by default.
- [ ] Click the Canvas tab in the page-bar. Confirm it switches cleanly and the active-tab underline moves to Canvas.
- [ ] Click Media Bin's maximize icon (`⤢`). Confirm Chat, Metadata, Player, and Timeline all hide and Media Bin fills the Sort page.
- [ ] Click the same icon again (`⤥`). Confirm everything restores to its prior layout.
- [ ] Click Media Bin's collapse icon. Confirm it shrinks to a thin strip at the left edge instead of disappearing.
- [ ] Click the collapsed strip. Confirm it expands back to its previous width.
- [ ] Collapse the Chat drawer. Confirm Metadata stays open, they're independent, not linked.
- [ ] Collapse Metadata. Confirm Chat is unaffected.
- [ ] Open View menu, click Toggle Theme. Confirm it switches to dark cleanly, no flash of unstyled widgets.
- [ ] Toggle back to light from the same menu item.
- [ ] Resize the window and drag a splitter to change panel widths, close the app, relaunch it. Confirm geometry, theme, current page, and panel widths/collapsed-states all come back exactly as left.
- [ ] Press F1 (and separately `?`). Confirm the shortcuts cheat sheet opens and closes cleanly.
- [ ] Open Help > Navigate. Confirm the tour lists every real panel (Media Bin, Player, Timeline, Chat, Metadata, Canvas page).
- [ ] Open Help > About. Confirm the app name, version, and author line are correct.
- [ ] Hover/click a few disabled menu items (things not built yet). Confirm they're inert, no crash, no console error.

---

## Shared rules (all phases)

- No video file is ever deleted by this app, under any flow, at any phase. If a step seems to need deletion, stop and re-read [AGENTS.md](AGENTS.md) Hard Rule 1 rather than building it.
- All filesystem access funnels through `paths.py::resolve_safe_path()`. No step adds a filesystem operation that bypasses it.
- Secrets only in `.env` (gitignored). `.env.example` ships with placeholders only.
- Verification before assertion: after push, confirm the remote actually has what's claimed (`git fetch origin main` / `git log origin/main` or equivalent) before reporting a step done.
- Dependency versions are pinned exactly in `requirements.txt`, verified live against PyPI, not left as loose floors.

---

## PHASE 0: Project setup and governance

**Goal:** Stand up the project skeleton, its own venv, its own public repo, and the documents that guide every phase after this one. No feature code in this phase.

### Step 0.1 — Directory skeleton and virtual environment

**Build:** Create the project folder structure (`vldash/`, `vldash/ui/`, `data/`, `data/proxies/`, `docs/devlog/`) and a dedicated venv at the project root (`python -m venv .venv`).

**Test:** All folders exist. `.venv\Scripts\python.exe --version` runs and reports a Python 3 interpreter distinct from any already-active environment.

### Step 0.2 — Pin and install dependencies

**Build:** Verify latest stable versions live against PyPI for `PySide6`, `python-dotenv`, `PyYAML`, `faster-whisper`, `psutil`, `nvidia-ml-py` (provides `pynvml`). Write `requirements.txt` with exact pins. Install into `.venv`.

**Test:** `.venv\Scripts\python.exe -m pip freeze` lists every package at exactly the pinned version. No package installed outside `.venv` (system/global Python untouched).

### Step 0.3 — gitignore, both repos

**Build:** Write this project's own `.gitignore` (`.venv/`, `__pycache__/`, `data/*.sqlite*`, `data/app.log`, `data/proxies/`, `.env`). Add `/_test_project/vanlife-dashboard/` to SEEKERS_GHOSTS's own `.gitignore` so the outer private repo never tracks this nested one.

**Test:** `git status` inside SEEKERS_GHOSTS does not show `_test_project/vanlife-dashboard/` as untracked or embedded-repo content. `git check-ignore` in each repo confirms the right rule matches.

### Step 0.4 — AGENTS.md and INSTRUCTIONS.md

**Build:** Write this project's own `AGENTS.md` (project identity, hard rules, protocol summary, read order) and this `INSTRUCTIONS.md`, modeled on SEEKERS_GHOSTS's own files but scoped to this project.

**Test:** Both files exist, are non-empty, and both explicitly state the no-deletion hard rule and the phase/step/devlog protocol.

### Step 0.5 — Public GitHub repository

**Build:** `git init`, confirm exact repo name/account/visibility with Jeremy in chat (a real, publicly-visible action), then `gh repo create` the confirmed public repository with `main` as default branch, add the remote, push the initial commit.

**Test:** The repo is reachable at its GitHub URL. `git remote -v` in the local project points at it. `git log origin/main` after push shows the initial commit.

### Step 0.6 — Phase 0 closure

**Build:** Final commit covering anything not yet committed in 0.1 to 0.5. Write the first `docs/devlog/{date}devlog.md` entry covering the whole phase.

**Test:** `git status` is clean. `git fetch origin main` then `git log origin/main` shows the closing commit. Devlog file exists with a real first-person entry, no em dashes, correct author byline.

**STOP after Phase 0.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 1: Design and UX scaffolding (redone)

**Goal:** A themed, correctly laid out shell every later phase fills in, not improvised as features get built. This phase was built once already as a flat multi-dock layout and it didn't hold up visually, empty boxy panels, wrong proportions, a tab strip landing at the bottom of its group instead of the top. Redone against a click-through HTML mockup validated before any Qt code was touched, grounded in DaVinci Resolve's page-bar structure and Morphic Studio's full-page spatial Canvas.

### Step 1.1 — Palette and both theme stylesheets

**Build:** `vldash/ui/palette.py` (shared hex constants: warm amber/terracotta accent, semantic tag colors, both light and dark surface tokens). `vldash/ui/light_theme.qss` (default) and `vldash/ui/dark_theme.qss`, both built together from the same palette, not "one now, one later."

**Test:** Launching a minimal `QApplication` with `light_theme.qss` applied shows a consistent light theme, no unstyled default-grey widgets mixed in. Swapping in `dark_theme.qss` at runtime shows a consistent dark theme with the same layout.

### Step 1.2 — MainWindow shell: page-bar, Sort page, Canvas page placeholder

**Build:** `vldash/ui/main_window.py`: `QMainWindow` with a top page-bar (`Sort` / `Canvas` tabs) driving a page stack. Sort page: Media Bin (left, placeholder content), Player (center, placeholder), Timeline strip (slim, directly under Player), Chat drawer and Metadata drawer stacked on the right (independent, not tabbed together). Canvas page: placeholder full-page content, reachable via its page-bar tab. Menu bar scaffolded with the full roster (File, Edit, View, Clip, Canvas, Tools, Help); the theme toggle lives in the View menu, not as a page-bar icon, since it's an optional setting, not a headline control. Items present even if disabled until their feature phase lands.

**Test:** App launches light-themed to the shell. Page-bar switches between Sort and Canvas correctly. Every panel and every menu item from the roster is present (even if inert). No crash on launch.

### Step 1.3 — Drawer component, layout persistence, shortcut cheat sheet

**Build:** `vldash/ui/drawer.py`: reusable collapsible-panel component with docked/collapsed states (Media Bin additionally gets a maximized state), used by Media Bin, Chat, and Metadata rather than three hand-rolled implementations. `QSettings`-backed `saveState()`/`restoreState()` for layout, including which drawers are collapsed and Media Bin's current state. `Help > Shortcuts` (and `?`/F1) opens a cheat sheet overlay listing the shortcut roster (populated as later phases add real shortcuts).

**Test:** Media Bin's collapse (`⟨`/`⟩`) and maximize (`⤢`) both work and can be combined with the other panels correctly (maximizing Media Bin hides Chat/Metadata/Timeline as expected). Chat and Metadata collapse independently of each other. Resize/collapse a panel, switch to Canvas and back, close and relaunch the app, confirm the arrangement (including drawer/maximize states) persisted. Cheat sheet opens and closes cleanly.

**STOP after Phase 1.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 2: Backend and data foundation

**Goal:** The database, the path allow-list, the sys.path wiring to SEEKERS_GHOSTS, and startup health checks.

### Step 2.1 — sys.path wiring and gates

**Build:** `vldash/config.py`: sentinel-checked `sys.path.insert` to the SEEKERS_GHOSTS root, import `GATE` from `app.concurrency`, define `TRANSCODE_GATE` and `WHISPER_GATE` as independent `SingleJobGate` instances.

**Test:** A throwaway script imports `config` and confirms all three gates exist and are distinct instances, and that `import app` resolves to the sibling repo's `app` package (has a `concurrency` submodule), not this project's own package. This project's package was originally named `app/` too and the collision was real and immediate: `python -m app.main` caches `app` in `sys.modules` as *this* project's package before any sys.path insert can run, so `from app.concurrency import GATE` fails with `ModuleNotFoundError` every time. Confirmed by actually running it, not by inspection. Renamed this project's package to `vldash/` per the pre-agreed fallback; the test above is what a clean run now looks like.

### Step 2.2 — Database schema

**Build:** `vldash/db.py`: full schema (`clips`, `markers`, `chat_messages`, `organize_events`, `note_phrases`, `roots`, `canvas_boards`, `canvas_regions`, `canvas_cards`, `ai_analysis`, `transcripts`, `footage_search` FTS5), `init_db()`, default `roots` seed (source, dest, project).

**Test:** Fresh `init_db()` creates every table. `roots` has exactly 3 rows with `is_default=1`. Re-running `init_db()` does not duplicate the seed.

### Step 2.3 — Path allow-list

**Build:** `vldash/paths.py::resolve_safe_path(root_key, relative)`, resolving against the live `roots` table, raising `PathViolation` on any traversal outside the resolved root.

**Test:** Real entries list correctly under all 3 default roots. A `..`-style relative path raises `PathViolation`, not a silent escape.

### Step 2.4 — Logging and startup health checks

**Build:** Rotating `data/app.log`. Startup checks: each default root reachable, `ffmpeg`/`ffprobe` on `PATH`, Ollama connectivity (non-blocking status badge).

**Test:** Healthy case: app launches clean, all checks pass. Unhealthy case: temporarily rename a root folder, confirm a clear in-app error, not a crash or silent empty tree; restore the folder afterward.

**STOP after Phase 2.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 3: Media Bin panel

**Goal:** Real, working directory browsing for the 3 default roots, presented as a Resolve-style Media Pool rather than a bare file tree, wired into the Phase 1 Sort page.

### Step 3.1 — Grid/Filmstrip/List views for the 3 default roots

**Build:** `vldash/ui/media_bin_panel.py`: Grid (default)/Filmstrip/List view toggle for Source (read-only), Destination (browse + create/rename/delete), Project (read-only), all routed through `resolve_safe_path`. `media.py`/ffmpeg don't exist yet, so grid cells use a file-type placeholder graphic, not a blank box and not a real thumbnail yet, that lands in Phase 4.

**Test:** Real directory entries render for all 3 roots against the actual `J:` and `D:` paths, in all 3 view modes. Dest-side create/rename works. Deleting a non-empty dest folder is refused with a clear error, not a recursive wipe.

**STOP after Phase 3.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 4: Video playback and proxies

**Goal:** Smooth playback of real high-bitrate footage via lazily generated proxies.

### Step 4.1 — ffprobe wrapper

**Build:** `vldash/media.py::probe(path)`, capturing `duration_seconds`/`fps` into the `clips` row on first open.

**Test:** Run against a real `.MOV` from `Clips\`, confirm correct duration/fps captured.

### Step 4.2 — Proxy generation

**Build:** `ensure_proxy(clip, quality)` for `720p`/`1080p`/`4k`, NVENC hardware encode with `libx264` CPU fallback, run through `TRANSCODE_GATE` via `ProxyWorker(QThread)`, cached under `data/proxies/`.

**Test:** Open a real 4K/high-bitrate clip, confirm a 720p proxy generates and is cached, confirm a second open reuses the cache instead of regenerating.

### Step 4.3 — Player panel

**Build:** `vldash/ui/player_panel.py`: `QVideoWidget`, defaults to 720p on open, quality `QComboBox` for 720p/1080p/4K.

**Test:** Real clip defaults to 720p and scrubs smoothly. Switching to 4K plays the original file directly with no transcode. Switching to 1080p generates and plays that proxy.

### Step 4.4 — Real thumbnails in the Media Bin

**Build:** Wire `media.py::grab_thumbnail()` into the Phase 3 Media Bin grid, replacing the file-type placeholder graphic with a real ffmpeg frame grab, cached alongside proxies.

**Test:** Media Bin grid cells for real clips show actual frame thumbnails instead of placeholders. A clip without a cached thumbnail yet shows the placeholder briefly, then updates once the grab completes, without blocking the UI.

**STOP after Phase 4.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 5: Transport controls and timeline

**Goal:** JKL shuttle, frame stepping, fullscreen, spacebar, and the marker timeline strip.

### Step 5.1 — JKL shuttle and frame step

**Build:** L/J/K per the 1x/2x/4x wrap-around spec, `QTimer`-driven reverse-step emulation, left/right arrow frame-accurate stepping when paused, spacebar play/pause (forward only, active only when focus is in the timeline/player area).

**Test:** Against a real clip: speed cycling wraps correctly both directions, arrow-key stepping moves exactly one frame, spacebar does nothing while typing in chat or a marker note.

### Step 5.2 — Fullscreen and timeline strip

**Build:** Plain `F` toggles fullscreen. `vldash/ui/timeline_strip.py` paints marker ticks (colored by tag) along the scrub bar, sized as a slim strip directly under the Player, not a peer-sized dock.

**Test:** `F` toggles fullscreen cleanly in and out. Timeline renders correctly once markers exist (verified again in Phase 6).

**STOP after Phase 5.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 6: Markers and metadata documents

**Goal:** Timestamp/tag markers with autosuggest, and the per-clip Markdown metadata document.

### Step 6.1 — Quick-tag and M-marker

**Build:** Digit keys 1-9 for instant quick-tag markers. `M` captures the current timestamp, auto-pauses, opens `vldash/ui/marker_popup.py`'s inline note editor.

**Test:** Digit-key markers appear instantly with correct tag/color. `M` pauses playback and opens the note popup at the correct timestamp whether triggered while playing or after scrubbing.

### Step 6.2 — Autosuggest

**Build:** `vldash/suggest.py`: curated starter vocabulary blended with `note_phrases` frequency learning. Ghost-text prefix match in the popup, TAB commits, any other key is untouched normal typing.

**Test:** Typing a prefix that matches a curated or learned phrase shows ghost-text. TAB commits it. A different key (e.g. space) does not commit and continues normal typing.

### Step 6.3 — Metadata document

**Build:** `vldash/metadata_doc.py`: Markdown + YAML frontmatter, one file per clip under `_metadata\`, created on first marker or first chat action, `## Markers` section appended on every marker save.

**Test:** First marker on a clip creates `_metadata\<stem>.md` with correct frontmatter and marker line. Second marker appends, does not overwrite. Markers and doc both survive an app restart.

**STOP after Phase 6.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 7: Copy, verify, and discard

**Goal:** The organize pipeline: copy, hash-verify, never delete, with a working error/retry path.

### Step 7.1 — Chunked copy and streaming hash

**Build:** `vldash/hashing.py`: chunked copy (thread-safe for large files), streaming sha256 of source and destination.

**Test:** Copy a real 500MB+ clip, confirm byte-identical hash match, confirm progress reporting during the operation.

### Step 7.2 — OrganizeWorker and Discard folder

**Build:** `vldash/workers.py::OrganizeWorker(QThread)` running the copy/verify job through `GATE`, auto-created `Discard` folder under `dest`, Shift+X one-key discard, `]`/`[` next/previous-unreviewed navigation.

**Test:** Organizing to a real folder and discarding to `Discard` both go through the identical flow and both leave the source file provably untouched (still present, unchanged mtime) afterward. Shift+X auto-advances to the next unreviewed clip.

### Step 7.3 — Error and retry path

**Build:** `clips.status = 'error'` on a failed copy/verify, with a visible Retry action. Specific handling for disk-full, permission-denied, locked-file, and unreachable-drive cases.

**Test:** Force a failure (e.g. lock the destination file open in another program), confirm the clip lands in `error` with a working Retry, not a silent false-success or a stuck `organizing` state.

**STOP after Phase 7.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 8: Chat and agent core

**Goal:** The single chat panel, action-triggering, Ollama default with an optional model dropdown and an OpenClaw placeholder.

### Step 8.1 — Prompt construction and Ollama call

**Build:** `vldash/agent_core.py`: system prompt, per-turn context (clip, markers, dest folder listing), `ChatWorker(QThread)` calling `ollama_generate` through `GATE`.

**Test:** A throwaway script (no UI) sends a known clip + message, confirms a real Ollama response comes back through the gate.

### Step 8.2 — Action parsing and confirm/cancel

**Build:** `parse_action()` for the JSON-envelope action schema (`organize`, `append_metadata_note`, `search_footage`, `create_folder`, `rename_folder`, `delete_folder`). `vldash/ui/chat_panel.py` renders confirm/cancel cards for mutating actions, applies `append_metadata_note`/`search_footage` immediately.

**Test:** "File this in Animal clips" produces a `pending_action`, nothing touches disk until confirmed. "Delete this clip" is refused in plain text and offers Discard instead. Confirming an organize action calls the same `OrganizeWorker` path the manual UI button uses.

### Step 8.3 — Model selection and OpenClaw placeholder

**Build:** Ollama model dropdown (locally installed models, `hermes3:8b` default). OpenClaw/Grok option in the backend selector, shipped as a clearly-labeled "not yet connected" placeholder unless the real OpenClaw invocation mechanism has been confirmed with Jeremy by this point.

**Test:** Switching the model dropdown changes which model actually answers. Selecting OpenClaw (if still unconfirmed) shows the placeholder state, does not silently no-op or crash. Stopping Ollama and sending a message shows an "unavailable" state, not a hang.

**STOP after Phase 8.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 9: Folder registry

**Goal:** Let the user register additional folders beyond the 3 defaults.

### Step 9.1 — Add Folder dialog and dynamic roots

**Build:** `vldash/ui/add_folder_dialog.py`: native folder picker, prompts every time for a label and a kind (`readonly`/`dest`). `paths.py` resolves against the live `roots` table including user-added rows. `media_bin_panel.py` renders one section per registered root.

**Test:** Add a throwaway test folder, confirm it's browsable. Confirm a `readonly`-kind added folder is rejected as an organize/copy target. Unregister it and confirm the app forgets it without touching the folder on disk.

**STOP after Phase 9.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 10: Canvas page

**Goal:** The editor-planning corkboard, cards, regions, multiple boards, filling the Canvas page already reachable from the Phase 1 page-bar.

### Step 10.1 — Board switcher and cards

**Build:** `vldash/ui/canvas_panel.py`, `canvas_card.py`: replace the Phase 1 placeholder Canvas page content with the real toolbar (board switcher, card/region count) and surface; multiple named boards, drag-a-clip-to-create-a-card, `media.py::grab_thumbnail()` for card previews, viewport caching for smooth pan/zoom.

**Test:** Switch to the Canvas page, create a board, drag 3-4 real clips onto it, confirm smooth pan/zoom with the cards placed. Double-click a card, confirm it switches back to the Sort page with that clip loaded in the Player.

### Step 10.2 — Regions and persistence

**Build:** `canvas_region.py`: resizable/colored/named grouping boxes, region membership on drop.

**Test:** Create a named region, drag cards into and out of it, restart the app, confirm card positions and region membership both persisted.

**STOP after Phase 10.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 11: Local AI, auto-tagging, transcription, search

**Goal:** VLM auto-tagging on open, user-triggered transcription, FTS5 search surfaced through chat.

### Step 11.1 — VLM auto-tagging

**Build:** `vldash/vlm_tagging.py`: 3-frame grab, base64 POST to a local vision model with `images`, result stored in `ai_analysis`, shown as a dismissible "AI suggested tags" chip row.

**Test:** Opening a real clip auto-populates the chip row within a reasonable delay, clearly labeled as AI-generated and editable.

### Step 11.2 — Transcription

**Build:** `vldash/transcribe.py`: ffmpeg audio extraction, `faster-whisper` (CPU, int8) through `WHISPER_GATE`, segments stored in `transcripts` and appended to the metadata doc.

**Test:** Manually triggering "Transcribe audio" on a clip with real dialogue produces a correct timestamped transcript in the metadata doc.

### Step 11.3 — Search index and chat action

**Build:** `vldash/search_index.py` FTS5 table over filenames/tags/transcripts/marker notes, `search_footage` chat action wired to it.

**Test:** Chat "which clips mention <a word actually present in test footage>" returns the correct clip via the FTS5 query, not a hallucinated match.

**STOP after Phase 11.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 12: Rough-cut export

**Goal:** Keeper CSV and FCPXML export for DaVinci Resolve.

### Step 12.1 — Keeper CSV

**Build:** `vldash/export_edl.py`: CSV export of tagged markers across selected clips.

**Test:** Export opens cleanly in a spreadsheet with correct filename/timestamp/tag/note columns.

### Step 12.2 — FCPXML rough assembly

**Build:** FCPXML export sequencing organized clips (board order or organize-timestamp order), Keeper marker ranges as subclip in/out points.

**Test:** Export a small test board, import into DaVinci Resolve, confirm it lands as a timeline with the expected clips/markers (spot-check, not full parity).

**STOP after Phase 12.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 13: End-to-end pass and README

**Goal:** Full manual walkthrough and a real README.

### Step 13.1 — End-to-end walkthrough

**Build/Test:** Run the full walkthrough described in the plan's End-to-end verification section: browse, play, shuttle, mark, organize, discard, chat actions, folder registry, canvas, AI tagging, transcription, search, export, and the deliberate error/UX pass (Ollama down, root unreachable, forced organize failure, every Help menu item, resource monitor, model dropdown, spacebar, and every button's keyboard-equivalent parity).

### Step 13.2 — README

**Build:** `README.md`: how to run (`python -m vldash.main` or equivalent), the 3 default roots, default model, known limitations.

**Test:** Following the README from a clean checkout (fresh `.venv`, `pip install -r requirements.txt`, run command) actually launches the app.

**STOP after Phase 13.** Report a phase summary.

---

## Phase completion report (template)

When stopping at the end of a phase, report:

1. Phase number and title
2. Steps completed (IDs)
3. Commits / push SHAs (verified via `git fetch` + log)
4. Devlog file path(s) updated
5. Known follow-ups
6. Explicit: waiting for Jeremy's go-ahead before Phase N+1

---

_Mycelia Interactive LLC — Keep At It, Always._
