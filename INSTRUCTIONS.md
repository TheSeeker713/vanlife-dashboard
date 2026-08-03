# vanlife-dashboard — Build Instructions

Companion to [AGENTS.md](AGENTS.md). This file is the executable build spec: protocol, devlog rules, and phased steps with tests.

Workspace: `D:\_Dev\AI-Setup\SEEKERS_GHOSTS\_test_project\vanlife-dashboard`
Public repo: `github.com/TheSeeker713/vanlife-dashboard`
Default branch: `main`

---

## PHASE_STEP_PROTOCOL

Within a phase, execute all steps in sequence without waiting for human input between steps.

Every step is: build the step's deliverable, test it, verify the test actually passed (check real output/state, don't assume a clean exit code means success), and only if the test passes: commit, push to `main`, and write a devlog entry (see Devlog spec below). A failed or unverified test means the step is not complete. Do not move to the next step until the failure is resolved and the test passes.

After the LAST step in a phase is committed and pushed, stop. Do not start the next phase. Report a phase summary and wait for Jeremy's explicit go-ahead before continuing.

---

## Devlog spec

- **Location:** `docs/devlog/{YYYY-MM-DD}devlog.md`
- One file per calendar day. Create it on the first entry of that day. Append for every subsequent step completed that day.
- Devlogs are tracked in git. Never gitignore them.
- Every commit and push at the end of a step is paired with a devlog entry for that step, timestamped with date and time.
- Written in first person as Jeremy Robards, CTO and CAIO of Mycelia Interactive LLC. Not written as an AI. Not written as a status report. Written like a real person narrating their own work: "I started on...", "Got stuck for a while on...", "That was frustrating.", "Didn't expect that to work but it did." Natural reactions mixed with real technical detail. Professional grade writing with genuine personal humor woven in, not corporate voice, not robotic changelog format.
- Each entry must be detailed and explicit about what was actually built or debugged in that step, not vague. It should read like someone who understands the system explaining their own work.
- Never use em dashes anywhere in devlog text. Use commas or colons instead.
- Never reach for "it's not X, it's Y" contrast framing repeatedly. Never write fragmented pseudo-profound sentences ("Short. Isolated. Trying to feel reflective."). Both are documented AI writing tics; write in real sentences instead.
- Write from the four components of authentic self-expression: self-awareness (say what actually happened, including the parts that didn't work), unbiased processing (don't spin a rough step into a clean win it wasn't), behavioral consistency (the same voice across entries), relational transparency (write like explaining it to someone you trust, not performing for an audience).

**Entry shape (guidance, not a rigid template):**

```markdown
### HH:MM - Phase N Step M: <short title>

I ...
```

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

**Build:** Create the project folder structure (`app/`, `app/ui/`, `data/`, `data/proxies/`, `docs/devlog/`) and a dedicated venv at the project root (`python -m venv .venv`).

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

**Build:** `app/ui/palette.py` (shared hex constants: warm amber/terracotta accent, semantic tag colors, both light and dark surface tokens). `app/ui/dark_theme.qss` (default) and `app/ui/light_theme.qss`, both built together from the same palette, not "dark now, light later."

**Test:** Launching a minimal `QApplication` with `dark_theme.qss` applied shows a consistent dark theme, no unstyled default-grey widgets mixed in. Swapping in `light_theme.qss` at runtime shows a consistent light theme with the same layout.

### Step 1.2 — MainWindow shell: page-bar, Sort page, Canvas page placeholder

**Build:** `app/ui/main_window.py`: `QMainWindow` with a top page-bar (`Sort` / `Canvas` tabs, plus a theme toggle) driving a page stack. Sort page: Media Bin (left, placeholder content), Player (center, placeholder), Timeline strip (slim, directly under Player), Chat drawer and Metadata drawer stacked on the right (independent, not tabbed together). Canvas page: placeholder full-page content, reachable via its page-bar tab. Menu bar scaffolded with the full roster (File, Edit, View, Clip, Canvas, Tools, Help), items present even if disabled until their feature phase lands.

**Test:** App launches dark-themed to the shell. Page-bar switches between Sort and Canvas correctly. Every panel and every menu item from the roster is present (even if inert). No crash on launch.

### Step 1.3 — Drawer component, layout persistence, shortcut cheat sheet

**Build:** `app/ui/drawer.py`: reusable collapsible-panel component with docked/collapsed states (Media Bin additionally gets a maximized state), used by Media Bin, Chat, and Metadata rather than three hand-rolled implementations. `QSettings`-backed `saveState()`/`restoreState()` for layout, including which drawers are collapsed and Media Bin's current state. `Help > Shortcuts` (and `?`/F1) opens a cheat sheet overlay listing the shortcut roster (populated as later phases add real shortcuts).

**Test:** Media Bin's collapse (`⟨`/`⟩`) and maximize (`⤢`) both work and can be combined with the other panels correctly (maximizing Media Bin hides Chat/Metadata/Timeline as expected). Chat and Metadata collapse independently of each other. Resize/collapse a panel, switch to Canvas and back, close and relaunch the app, confirm the arrangement (including drawer/maximize states) persisted. Cheat sheet opens and closes cleanly.

**STOP after Phase 1.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 2: Backend and data foundation

**Goal:** The database, the path allow-list, the sys.path wiring to SEEKERS_GHOSTS, and startup health checks.

### Step 2.1 — sys.path wiring and gates

**Build:** `app/config.py`: sentinel-checked `sys.path.insert` to the SEEKERS_GHOSTS root, import `GATE` from `app.concurrency`, define `TRANSCODE_GATE` and `WHISPER_GATE` as independent `SingleJobGate` instances.

**Test:** A throwaway script imports `config` and confirms all three gates exist and are distinct instances. Confirm whether this project's own `app/` package name collides with the sibling's `app` package in practice; if it does, rename this project's package to `vldash/` before continuing and re-run this test.

### Step 2.2 — Database schema

**Build:** `app/db.py`: full schema (`clips`, `markers`, `chat_messages`, `organize_events`, `note_phrases`, `roots`, `canvas_boards`, `canvas_regions`, `canvas_cards`, `ai_analysis`, `transcripts`, `footage_search` FTS5), `init_db()`, default `roots` seed (source, dest, project).

**Test:** Fresh `init_db()` creates every table. `roots` has exactly 3 rows with `is_default=1`. Re-running `init_db()` does not duplicate the seed.

### Step 2.3 — Path allow-list

**Build:** `app/paths.py::resolve_safe_path(root_key, relative)`, resolving against the live `roots` table, raising `PathViolation` on any traversal outside the resolved root.

**Test:** Real entries list correctly under all 3 default roots. A `..`-style relative path raises `PathViolation`, not a silent escape.

### Step 2.4 — Logging and startup health checks

**Build:** Rotating `data/app.log`. Startup checks: each default root reachable, `ffmpeg`/`ffprobe` on `PATH`, Ollama connectivity (non-blocking status badge).

**Test:** Healthy case: app launches clean, all checks pass. Unhealthy case: temporarily rename a root folder, confirm a clear in-app error, not a crash or silent empty tree; restore the folder afterward.

**STOP after Phase 2.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 3: Media Bin panel

**Goal:** Real, working directory browsing for the 3 default roots, presented as a Resolve-style Media Pool rather than a bare file tree, wired into the Phase 1 Sort page.

### Step 3.1 — Grid/Filmstrip/List views for the 3 default roots

**Build:** `app/ui/media_bin_panel.py`: Grid (default)/Filmstrip/List view toggle for Source (read-only), Destination (browse + create/rename/delete), Project (read-only), all routed through `resolve_safe_path`. `media.py`/ffmpeg don't exist yet, so grid cells use a file-type placeholder graphic, not a blank box and not a real thumbnail yet, that lands in Phase 4.

**Test:** Real directory entries render for all 3 roots against the actual `J:` and `D:` paths, in all 3 view modes. Dest-side create/rename works. Deleting a non-empty dest folder is refused with a clear error, not a recursive wipe.

**STOP after Phase 3.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 4: Video playback and proxies

**Goal:** Smooth playback of real high-bitrate footage via lazily generated proxies.

### Step 4.1 — ffprobe wrapper

**Build:** `app/media.py::probe(path)`, capturing `duration_seconds`/`fps` into the `clips` row on first open.

**Test:** Run against a real `.MOV` from `Clips\`, confirm correct duration/fps captured.

### Step 4.2 — Proxy generation

**Build:** `ensure_proxy(clip, quality)` for `720p`/`1080p`/`4k`, NVENC hardware encode with `libx264` CPU fallback, run through `TRANSCODE_GATE` via `ProxyWorker(QThread)`, cached under `data/proxies/`.

**Test:** Open a real 4K/high-bitrate clip, confirm a 720p proxy generates and is cached, confirm a second open reuses the cache instead of regenerating.

### Step 4.3 — Player panel

**Build:** `app/ui/player_panel.py`: `QVideoWidget`, defaults to 720p on open, quality `QComboBox` for 720p/1080p/4K.

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

**Build:** Plain `F` toggles fullscreen. `app/ui/timeline_strip.py` paints marker ticks (colored by tag) along the scrub bar, sized as a slim strip directly under the Player, not a peer-sized dock.

**Test:** `F` toggles fullscreen cleanly in and out. Timeline renders correctly once markers exist (verified again in Phase 6).

**STOP after Phase 5.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 6: Markers and metadata documents

**Goal:** Timestamp/tag markers with autosuggest, and the per-clip Markdown metadata document.

### Step 6.1 — Quick-tag and M-marker

**Build:** Digit keys 1-9 for instant quick-tag markers. `M` captures the current timestamp, auto-pauses, opens `app/ui/marker_popup.py`'s inline note editor.

**Test:** Digit-key markers appear instantly with correct tag/color. `M` pauses playback and opens the note popup at the correct timestamp whether triggered while playing or after scrubbing.

### Step 6.2 — Autosuggest

**Build:** `app/suggest.py`: curated starter vocabulary blended with `note_phrases` frequency learning. Ghost-text prefix match in the popup, TAB commits, any other key is untouched normal typing.

**Test:** Typing a prefix that matches a curated or learned phrase shows ghost-text. TAB commits it. A different key (e.g. space) does not commit and continues normal typing.

### Step 6.3 — Metadata document

**Build:** `app/metadata_doc.py`: Markdown + YAML frontmatter, one file per clip under `_metadata\`, created on first marker or first chat action, `## Markers` section appended on every marker save.

**Test:** First marker on a clip creates `_metadata\<stem>.md` with correct frontmatter and marker line. Second marker appends, does not overwrite. Markers and doc both survive an app restart.

**STOP after Phase 6.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 7: Copy, verify, and discard

**Goal:** The organize pipeline: copy, hash-verify, never delete, with a working error/retry path.

### Step 7.1 — Chunked copy and streaming hash

**Build:** `app/hashing.py`: chunked copy (thread-safe for large files), streaming sha256 of source and destination.

**Test:** Copy a real 500MB+ clip, confirm byte-identical hash match, confirm progress reporting during the operation.

### Step 7.2 — OrganizeWorker and Discard folder

**Build:** `app/workers.py::OrganizeWorker(QThread)` running the copy/verify job through `GATE`, auto-created `Discard` folder under `dest`, Shift+X one-key discard, `]`/`[` next/previous-unreviewed navigation.

**Test:** Organizing to a real folder and discarding to `Discard` both go through the identical flow and both leave the source file provably untouched (still present, unchanged mtime) afterward. Shift+X auto-advances to the next unreviewed clip.

### Step 7.3 — Error and retry path

**Build:** `clips.status = 'error'` on a failed copy/verify, with a visible Retry action. Specific handling for disk-full, permission-denied, locked-file, and unreachable-drive cases.

**Test:** Force a failure (e.g. lock the destination file open in another program), confirm the clip lands in `error` with a working Retry, not a silent false-success or a stuck `organizing` state.

**STOP after Phase 7.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 8: Chat and agent core

**Goal:** The single chat panel, action-triggering, Ollama default with an optional model dropdown and an OpenClaw placeholder.

### Step 8.1 — Prompt construction and Ollama call

**Build:** `app/agent_core.py`: system prompt, per-turn context (clip, markers, dest folder listing), `ChatWorker(QThread)` calling `ollama_generate` through `GATE`.

**Test:** A throwaway script (no UI) sends a known clip + message, confirms a real Ollama response comes back through the gate.

### Step 8.2 — Action parsing and confirm/cancel

**Build:** `parse_action()` for the JSON-envelope action schema (`organize`, `append_metadata_note`, `search_footage`, `create_folder`, `rename_folder`, `delete_folder`). `app/ui/chat_panel.py` renders confirm/cancel cards for mutating actions, applies `append_metadata_note`/`search_footage` immediately.

**Test:** "File this in Animal clips" produces a `pending_action`, nothing touches disk until confirmed. "Delete this clip" is refused in plain text and offers Discard instead. Confirming an organize action calls the same `OrganizeWorker` path the manual UI button uses.

### Step 8.3 — Model selection and OpenClaw placeholder

**Build:** Ollama model dropdown (locally installed models, `hermes3:8b` default). OpenClaw/Grok option in the backend selector, shipped as a clearly-labeled "not yet connected" placeholder unless the real OpenClaw invocation mechanism has been confirmed with Jeremy by this point.

**Test:** Switching the model dropdown changes which model actually answers. Selecting OpenClaw (if still unconfirmed) shows the placeholder state, does not silently no-op or crash. Stopping Ollama and sending a message shows an "unavailable" state, not a hang.

**STOP after Phase 8.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 9: Folder registry

**Goal:** Let the user register additional folders beyond the 3 defaults.

### Step 9.1 — Add Folder dialog and dynamic roots

**Build:** `app/ui/add_folder_dialog.py`: native folder picker, prompts every time for a label and a kind (`readonly`/`dest`). `paths.py` resolves against the live `roots` table including user-added rows. `media_bin_panel.py` renders one section per registered root.

**Test:** Add a throwaway test folder, confirm it's browsable. Confirm a `readonly`-kind added folder is rejected as an organize/copy target. Unregister it and confirm the app forgets it without touching the folder on disk.

**STOP after Phase 9.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 10: Canvas page

**Goal:** The editor-planning corkboard, cards, regions, multiple boards, filling the Canvas page already reachable from the Phase 1 page-bar.

### Step 10.1 — Board switcher and cards

**Build:** `app/ui/canvas_panel.py`, `canvas_card.py`: replace the Phase 1 placeholder Canvas page content with the real toolbar (board switcher, card/region count) and surface; multiple named boards, drag-a-clip-to-create-a-card, `media.py::grab_thumbnail()` for card previews, viewport caching for smooth pan/zoom.

**Test:** Switch to the Canvas page, create a board, drag 3-4 real clips onto it, confirm smooth pan/zoom with the cards placed. Double-click a card, confirm it switches back to the Sort page with that clip loaded in the Player.

### Step 10.2 — Regions and persistence

**Build:** `canvas_region.py`: resizable/colored/named grouping boxes, region membership on drop.

**Test:** Create a named region, drag cards into and out of it, restart the app, confirm card positions and region membership both persisted.

**STOP after Phase 10.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 11: Local AI, auto-tagging, transcription, search

**Goal:** VLM auto-tagging on open, user-triggered transcription, FTS5 search surfaced through chat.

### Step 11.1 — VLM auto-tagging

**Build:** `app/vlm_tagging.py`: 3-frame grab, base64 POST to a local vision model with `images`, result stored in `ai_analysis`, shown as a dismissible "AI suggested tags" chip row.

**Test:** Opening a real clip auto-populates the chip row within a reasonable delay, clearly labeled as AI-generated and editable.

### Step 11.2 — Transcription

**Build:** `app/transcribe.py`: ffmpeg audio extraction, `faster-whisper` (CPU, int8) through `WHISPER_GATE`, segments stored in `transcripts` and appended to the metadata doc.

**Test:** Manually triggering "Transcribe audio" on a clip with real dialogue produces a correct timestamped transcript in the metadata doc.

### Step 11.3 — Search index and chat action

**Build:** `app/search_index.py` FTS5 table over filenames/tags/transcripts/marker notes, `search_footage` chat action wired to it.

**Test:** Chat "which clips mention <a word actually present in test footage>" returns the correct clip via the FTS5 query, not a hallucinated match.

**STOP after Phase 11.** Report a phase summary. Wait for Jeremy's go-ahead.

---

## PHASE 12: Rough-cut export

**Goal:** Keeper CSV and FCPXML export for DaVinci Resolve.

### Step 12.1 — Keeper CSV

**Build:** `app/export_edl.py`: CSV export of tagged markers across selected clips.

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

**Build:** `README.md`: how to run (`python -m app.main` or equivalent), the 3 default roots, default model, known limitations.

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
