@AGENTS.md

Claude Code auto-loads `CLAUDE.md` at session start, not `AGENTS.md`
directly (the two are separate conventions from different tools). This
file exists purely so the import line above actually pulls `AGENTS.md`
in automatically, rather than depending on a session remembering to
read it manually. `AGENTS.md` in turn points to `INSTRUCTIONS.md` and
`.claude/rules/`, so everything this project needs an agent to know
chains from this one file.
