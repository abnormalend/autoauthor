---
name: auto
description: Use when the user wants the pipeline run unattended — "run the whole book", "take it from foundation to the end", "automate the remaining phases" — on a project that has already been seeded.
model: sonnet
---

# Autoauthor Auto — the unattended driver

Runs `shared/scripts/autoauthor_run.sh`, which drives a seeded project
from its current phase to the end of its pipeline: one fresh headless
`claude -p "/autoauthor:<skill>"` session per invocation, so every phase
starts with a virgin context and reads its position from state.json and
git. This skill is a supervisor around that script, not a pipeline of its
own — do NOT run the phase skills inline here; the whole point of the
driver is that they run in contexts this session does not share.

## Before launching

1. Verify the target is a seeded project: `state.json` exists in the
   directory the user named (or the CWD). If not, STOP — seeding is
   interactive on purpose; the premise needs a human iterating on it.
   Point the user at `/autoauthor:seed`.
2. If `state.json` has `"structure": "collection"` or `"series"`, say
   what will happen: the driver runs each work in `works/`, in the
   declared order, to the end of its own pipeline, then stops — the
   cross-work pass and export stay supervised.
3. **Permissions are the one thing to settle with the user.** The
   driver's default (`--permission-mode acceptEdits`) will stall
   headless the first time a phase needs a Bash command outside the
   allowlist. Ask which the user wants:
   - a project `.claude/settings.json` allowlist (safest; the
     fewer-permission-prompts skill can build one), or
   - `AUTOAUTHOR_CLAUDE_FLAGS="--dangerously-skip-permissions"` —
     only on a machine where they would let an agent run unattended.
   Do not choose for them.
4. Ask (or infer from the request) whether to run to the end or
   `--stop-after <foundation|draft|revise|review>` for a supervised
   checkpoint.

## Launch

Run in the background — the pipeline takes hours, not minutes:

```bash
"${CLAUDE_PLUGIN_ROOT}/shared/scripts/autoauthor_run.sh" <project-dir> [--stop-after <skill>] [--max-runs N]
```

Use the Bash tool's background mode; report the log directory
(`<project>/edit_logs/auto/`) to the user immediately. If the user has a
notification command (a script that takes a title and a message —
Pushover, ntfy, whatever), set `AUTOAUTHOR_NOTIFY_CMD` to it when
launching: the driver calls it on every phase transition and whenever it
stops, so the phone is the progress feed. Ask once; do not assume one
exists.

If the nested `claude` invocation fails inside this session's shell
(environment conflicts are possible when Claude Code launches Claude
Code), do not debug it here: give the user the exact command to run from
a plain terminal — the script is self-contained and that is its primary
documented path.

## While it runs / when it stops

- Check progress by reading the newest file in `edit_logs/auto/` and
  `git -C <project> log --oneline -5` — never by re-running phases.
- Exit 0 with "phase is export": report done and name
  `/autoauthor:export` (or the cross-work pass for a container).
- Exit 1: the driver found a stopped skill (no commit, or a dirty
  tree). Read the log it names, tell the user WHAT question the phase
  stopped on, and offer to resolve it interactively in this session —
  that is the human moment the driver exists to surface, not an error
  to retry. Resolving the stopped question interactively (which may mean
  running that one phase skill here, with the user watching) is the one
  sanctioned exception to "never run phases inline" — the prohibition is
  on making unattended progress in this context, not on answering a
  question in it.
- Never restart the driver over a dirty tree.
