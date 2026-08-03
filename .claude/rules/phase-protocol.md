# Phase-close protocol (vanlife-dashboard)

Self-contained restatement of the build cadence so it's followed even
without re-reading `INSTRUCTIONS.md` first. `INSTRUCTIONS.md` remains the
authoritative source for per-phase Build/Test detail; this file is the
process shape.

## Inside a phase

Execute steps (N.1, N.2, N.3...) in sequence without waiting for human
input between them. Each step: build the deliverable, test it, verify
the test actually passed (real output/state, not an assumed clean exit
code). A failed or unverified test means the step isn't done, fix it
before moving to the next step. Steps do not each get their own commit,
the phase commits once, after the close-out sequence below.

## Phase close-out sequence

Run in order, once every step in the phase is built and individually
tested:

1. **Cross-Check & Full Project Audit.** Grep for stale references to
   anything renamed or removed this phase. Confirm `AGENTS.md`,
   `INSTRUCTIONS.md`, and the plan doc still agree with what was
   actually built. Confirm no stray test/debug artifacts are staged.
   Review the full diff about to be committed, not just the newest file.
2. **Re-run tests.** The phase's own automated tests, plus a quick
   regression pass against prior phases' tests, not only the newest
   step's test.
3. **Commit and push.** One commit for the phase (a couple more only if
   the audit surfaced real fixes), pushed to `main`.
4. **Devlog entry.** Written per `.claude/rules/devlog-voice.md`,
   immediately after the push, same date/time-stamp discipline as
   before (`docs/devlog/{YYYY-MM-DD}devlog.md`, one file per calendar
   day, `### HH:MM - Phase N: <short title>` heading).
5. **UI/UX checklist**, phases with a user-facing surface only. Produce
   a concrete, phase-specific checklist (each item: an action plus an
   expected result, short enough to run in a few minutes, derived from
   that phase's actual Build/Test descriptions, not written in advance
   for phases not yet built). Present it to Jeremy directly. The phase
   is not closed and the next phase does not start until Jeremy has
   run it himself and confirmed, not merely accepted the agent's own
   report. Phases with no user-facing surface (pure backend/governance)
   get a lighter functional-verification note instead, stated
   explicitly rather than silently skipped.

Stop after step 5. Do not start the next phase until Jeremy gives
explicit go-ahead.
