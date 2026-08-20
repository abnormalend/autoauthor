#!/usr/bin/env bash
# autoauthor_run.sh — drive a seeded project from foundation to export,
# one fresh headless Claude Code session per phase invocation.
#
# Usage (from anywhere):
#   autoauthor_run.sh <project-dir>
#   autoauthor_run.sh <project-dir> --stop-after draft
#   autoauthor_run.sh <project-dir> --max-runs 40
#   autoauthor_run.sh <project-dir> --dry-run
#
# Why a driver script and not a meta skill. Every phase skill is resumable
# from cold — state.json holds the phase, git holds the history — so the
# memory between phases is the repository, not the conversation. Running
# the phases inside one session means running the later ones in the
# degraded context the skills themselves warn against; each `claude -p`
# invocation here gets a virgin context and the repo tells it where it is.
#
# The driver starts AFTER seed, deliberately: seeding is where the premise
# gets iterated and tuned with a human in the loop, and no guard below can
# tell a good premise from a cheap one. No state.json means no seed —
# the driver refuses and says so.
#
# Containers: a collection or series project is a shell around works/ —
# the driver runs each work, in the declared running order, to the end of
# its own pipeline, then stops and names the cross-work pass. The
# cross-work pass and export are container decisions (running order,
# accepted convergence findings) and stay supervised.
#
# Stopping is a feature. A phase skill that hits a real question STOPs,
# which headless just ends the invocation — so the driver treats "the
# session ran and HEAD did not move" as "a human is needed", prints the
# log path, and exits 1 rather than re-asking the same question forever.
# A dirty tree after a run means the same thing (every skill commits what
# it keeps).
#
# Notifications: the phase skills do not send any — reporting to a phone
# is the driver's job, because only the driver knows a phase ended. Set
#   AUTOAUTHOR_NOTIFY_CMD=/path/to/notify.sh
# to any command taking two arguments (title, message) — a Pushover
# script, ntfy, mail. It is called on every phase transition and whenever
# the driver stops, best-effort: a failing notifier never stops a run.
#
# Permissions: the default flags are `--permission-mode acceptEdits`,
# which still denies anything outside the allowlist in headless mode. A
# genuinely unattended run needs either a permission allowlist in the
# project's .claude/settings.json or
#   AUTOAUTHOR_CLAUDE_FLAGS="--dangerously-skip-permissions"
# — the latter only somewhere you would let an agent run unattended.

set -euo pipefail

MAX_RUNS=30
STOP_AFTER=""
DRY_RUN=0
CLAUDE_BIN="${AUTOAUTHOR_CLAUDE:-claude}"
CLAUDE_FLAGS="${AUTOAUTHOR_CLAUDE_FLAGS:---permission-mode acceptEdits}"
NOTIFY_CMD="${AUTOAUTHOR_NOTIFY_CMD:-}"

# Pipeline order, phase (state.json) -> skill. Seed is absent on purpose.
PHASES=(foundation drafting revision review)
SKILLS=(foundation draft revise review)

usage() {
  sed -n '2,41p' "$0" | sed 's/^# \{0,1\}//'
}

die() { echo "autoauthor_run: $1" >&2; exit "${2:-1}"; }

notify() { # notify <title> <message> — best-effort, never fatal
  [ -n "$NOTIFY_CMD" ] || return 0
  $NOTIFY_CMD "$1" "$2" >/dev/null 2>&1 || true
}

stop() { # stop <message> — a human is needed: notify, then die
  notify "autoauthor: stopped" "$1"
  die "$1"
}

json_get() { # json_get <file> <key> -> value or "null"
  python3 - "$1" "$2" <<'EOF'
import json, sys
try:
    v = json.load(open(sys.argv[1])).get(sys.argv[2])
except Exception as e:
    sys.exit(f"unreadable {sys.argv[1]}: {e}")
print("null" if v is None else v)
EOF
}

json_list() { # json_list <file> <key> -> one element per line
  python3 - "$1" "$2" <<'EOF'
import json, sys
for v in (json.load(open(sys.argv[1])).get(sys.argv[2]) or []):
    print(v)
EOF
}

skill_for_phase() { # -> skill name, or "" for export/done, dies on unknown
  local phase=$1 i
  [ "$phase" = "export" ] && { echo ""; return; }
  for i in "${!PHASES[@]}"; do
    if [ "${PHASES[$i]}" = "$phase" ]; then echo "${SKILLS[$i]}"; return; fi
  done
  die "unknown phase '$phase' in state.json — the driver knows ${PHASES[*]} and export" 2
}

skill_rank() { # position in the pipeline, for --stop-after
  local skill=$1 i
  for i in "${!SKILLS[@]}"; do
    if [ "${SKILLS[$i]}" = "$skill" ]; then echo "$i"; return; fi
  done
  die "--stop-after wants one of: ${SKILLS[*]}" 2
}

run_one() { # run_one <project-dir> — one work (or standalone) to completion
  local dir=$1 phase skill before after log n new_phase

  for ((n = 1; n <= MAX_RUNS; n++)); do
    phase=$(json_get "$dir/state.json" phase)
    skill=$(skill_for_phase "$phase")
    if [ -z "$skill" ]; then
      echo "== $dir: phase is export — this work's pipeline is done"
      return 0
    fi
    if [ -n "$STOP_AFTER" ] && [ "$(skill_rank "$skill")" -gt "$(skill_rank "$STOP_AFTER")" ]; then
      echo "== $dir: next phase would be $skill, past --stop-after $STOP_AFTER — stopping as asked"
      return 0
    fi

    if [ "$DRY_RUN" = 1 ]; then
      echo "DRY RUN: (cd $dir && $CLAUDE_BIN -p \"/autoauthor:$skill\" $CLAUDE_FLAGS)"
      return 0
    fi

    [ -n "$(git -C "$dir" status --porcelain)" ] && \
      stop "$dir has a dirty tree — a skill stopped mid-step and a human should look before anything else runs"

    mkdir -p "$dir/edit_logs/auto"
    before=$(git -C "$dir" rev-parse HEAD)
    log="$dir/edit_logs/auto/run-$(date -u +%Y%m%d_%H%M%S)-$skill.log"
    echo "== $dir: run $n/$MAX_RUNS — /autoauthor:$skill (log: $log)"
    # The invocation may end non-zero on a skill STOP; the progress check
    # below is the verdict, not the exit code. </dev/null because claude -p
    # reads piped stdin as prompt input — inside the container loop, stdin
    # is the works list, and the first invocation ate every later work.
    (cd "$dir" && "$CLAUDE_BIN" -p "/autoauthor:$skill" $CLAUDE_FLAGS </dev/null) 2>&1 | tee "$log" || true

    [ -n "$(git -C "$dir" status --porcelain)" ] && \
      stop "$dir: tree left dirty by /autoauthor:$skill — read $log; a human is needed"
    after=$(git -C "$dir" rev-parse HEAD)
    if [ "$after" = "$before" ]; then
      stop "$dir: /autoauthor:$skill made no commit — it likely STOPped on a question. Read $log, answer it interactively, then re-run"
    fi
    new_phase=$(json_get "$dir/state.json" phase)
    if [ "$new_phase" != "$phase" ]; then
      notify "autoauthor: $(basename "$dir")" "phase $phase done → $new_phase"
    fi
  done
  stop "$dir: reached --max-runs $MAX_RUNS without finishing — raise it if progress is real, read the last log if it is not"
}

main() {
  local dir="" structure works w all_done
  while [ $# -gt 0 ]; do
    case "$1" in
      --stop-after) [ $# -ge 2 ] || die "--stop-after needs a skill name" 2
                    STOP_AFTER=$2; skill_rank "$STOP_AFTER" >/dev/null; shift 2 ;;
      --max-runs)   [ $# -ge 2 ] || die "--max-runs needs a number" 2
                    case "$2" in (*[!0-9]*|"") die "--max-runs wants an integer, got '$2'" 2 ;; esac
                    MAX_RUNS=$2; shift 2 ;;
      --dry-run)    DRY_RUN=1; shift ;;
      -h|--help)    usage; exit 0 ;;
      -*)           die "unknown flag $1 (see --help)" 2 ;;
      *)            dir=$1; shift ;;
    esac
  done
  [ -n "$dir" ] || die "usage: autoauthor_run.sh <project-dir> [--stop-after <skill>] [--max-runs N] [--dry-run] (see --help)" 2
  [ -f "$dir/state.json" ] || \
    die "$dir has no state.json — the driver starts AFTER seeding. Run /autoauthor:seed interactively first; the premise deserves the iteration" 2
  if [ "$DRY_RUN" != 1 ]; then
    command -v "$CLAUDE_BIN" >/dev/null || die "'$CLAUDE_BIN' not found on PATH (set AUTOAUTHOR_CLAUDE)" 2
    git -C "$dir" rev-parse HEAD >/dev/null 2>&1 || die "$dir is not a git repository with a commit — seed initialises one" 2
  fi

  structure=$(json_get "$dir/state.json" structure)
  if [ "$structure" = "collection" ] || [ "$structure" = "series" ]; then
    echo "== container ($structure): running each work in the declared order"
    [ -n "$(json_list "$dir/state.json" works)" ] || \
      die "container declares no works — seed creates the first and adds it to state.json's works array" 2
    all_done=1
    while IFS= read -r w; do
      [ -f "$dir/works/$w/state.json" ] || die "container names work '$w' but works/$w/state.json is missing" 2
      run_one "$dir/works/$w"
      [ "$(json_get "$dir/works/$w/state.json" phase)" = "export" ] || all_done=0
    done < <(json_list "$dir/state.json" works)
    if [ "$DRY_RUN" != 1 ] && [ "$all_done" = 1 ]; then
      notify "autoauthor: $(basename "$dir")" "every work is done — cross-work pass and export are yours"
      echo "== every work is done. The cross-work pass and export are container decisions — run"
      echo "   /autoauthor:$( [ "$structure" = collection ] && echo collection || echo series ) and then /autoauthor:export from $dir yourself"
    fi
  else
    run_one "$dir"
    if [ "$DRY_RUN" != 1 ] && [ -z "$STOP_AFTER" ]; then
      notify "autoauthor: $(basename "$dir")" "pipeline done — ready for /autoauthor:export"
      echo "== phase is export — run /autoauthor:export from $dir (typesetting choices are worth supervising)"
    fi
  fi
}

main "$@"
