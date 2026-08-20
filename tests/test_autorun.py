"""The unattended driver: one fresh headless session per phase invocation.

The driver's contract is narrow on purpose: it starts AFTER seed (a premise
needs a human iterating on it), maps state.json phases to skills, treats
"ran but HEAD did not move" as "a human is needed", and on a container runs
each work in the declared order rather than the container itself. These
tests cover the parts that need no `claude` binary: the refusals, the
phase map, and the dry-run routing — and then the real loop, driven by a
shim `claude` on AUTOAUTHOR_CLAUDE that commits, stalls, or dirties the
tree the way a live session can. The shim reads piped stdin the way
`claude -p` does, because that is how the container loop's first
invocation once ate every later work off the works list.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent / "plugin/autoauthor"
SCRIPT = ROOT / "shared/scripts/autoauthor_run.sh"

# Mirrors the PHASES/SKILLS arrays in the script; the test below keeps the
# two in step with the skills that actually ship.
PHASE_TO_SKILL = {
    "foundation": "foundation",
    "drafting": "draft",
    "revision": "revise",
    "review": "review",
}


def run(args, cwd):
    return subprocess.run(["bash", str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=cwd)


def project(tmp_path, phase, structure=None, works=None, name=""):
    d = tmp_path / name if name else tmp_path
    d.mkdir(parents=True, exist_ok=True)
    state = {"phase": phase, "structure": structure}
    if works is not None:
        state["works"] = works
    (d / "state.json").write_text(json.dumps(state))
    return d


def test_script_is_executable_and_help_exits_zero(tmp_path):
    assert SCRIPT.stat().st_mode & 0o111, "autoauthor_run.sh must be executable"
    r = run(["--help"], tmp_path)
    assert r.returncode == 0, r.stderr
    assert "foundation" in r.stdout


def test_every_mapped_skill_ships():
    for phase, skill in PHASE_TO_SKILL.items():
        assert (ROOT / "skills" / skill / "SKILL.md").exists(), (phase, skill)
    assert "seed" not in PHASE_TO_SKILL.values(), "the driver starts after seed"


def test_refuses_a_project_that_was_never_seeded(tmp_path):
    r = run([str(tmp_path)], tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "seed" in r.stderr.lower()


def test_dry_run_maps_the_phase_to_its_skill(tmp_path):
    d = project(tmp_path, "drafting")
    r = run([str(d), "--dry-run"], tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "/autoauthor:draft" in r.stdout


def test_unknown_phase_is_refused_by_name(tmp_path):
    d = project(tmp_path, "composting")
    r = run([str(d), "--dry-run"], tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "composting" in r.stderr


def test_stop_after_refuses_an_unknown_skill(tmp_path):
    d = project(tmp_path, "drafting")
    r = run([str(d), "--dry-run", "--stop-after", "polish"], tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr


def test_stop_after_stops_before_a_later_phase(tmp_path):
    d = project(tmp_path, "revision")
    r = run([str(d), "--dry-run", "--stop-after", "draft"], tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "/autoauthor:" not in r.stdout.replace("stop-after", "")
    assert "stopping as asked" in r.stdout


def test_container_dry_run_routes_to_each_unfinished_work(tmp_path):
    c = project(tmp_path, "export", structure="collection",
                works=["01-alpha", "02-beta"], name="coll")
    project(c, "export", name="works/01-alpha")
    project(c, "foundation", name="works/02-beta")
    r = run([str(c), "--dry-run"], tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "01-alpha" in r.stdout and "pipeline is done" in r.stdout
    assert "02-beta" in r.stdout and "/autoauthor:foundation" in r.stdout


def test_container_with_a_missing_work_dir_is_refused(tmp_path):
    c = project(tmp_path, "export", structure="collection",
                works=["01-alpha"], name="coll")
    r = run([str(c), "--dry-run"], tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "01-alpha" in r.stderr


# --- the real loop, against a shim claude ---------------------------------

GIT_ID = ["git", "-c", "user.email=shim@test", "-c", "user.name=shim"]

# Advances state.json one phase and commits, the shape of a phase run that
# finished. `cat` first: `claude -p` reads piped stdin as prompt input, and
# a shim that skipped that read would hide the works-list-on-stdin bug.
ADVANCE = """#!/bin/bash
[ -t 0 ] || cat >/dev/null
python3 - <<'PY'
import json
order = ["foundation", "drafting", "revision", "review", "export"]
s = json.load(open("state.json"))
s["phase"] = order[order.index(s["phase"]) + 1]
json.dump(s, open("state.json", "w"))
PY
git add state.json && git -c user.email=shim@test -c user.name=shim commit -qm "shim: advance"
"""

STALL = "#!/bin/bash\n[ -t 0 ] || cat >/dev/null\necho 'stopped on a question'\n"
DIRTY = "#!/bin/bash\n[ -t 0 ] || cat >/dev/null\necho x > leftover.txt\n"
CHURN = ("#!/bin/bash\n[ -t 0 ] || cat >/dev/null\ndate >> churn.txt\n"
         "git add churn.txt && "
         "git -c user.email=shim@test -c user.name=shim commit -qm 'shim: churn'\n")


def seeded(d, phase):
    """A committed git repo with a state.json — what seed leaves behind."""
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitignore").write_text("edit_logs/\neval_logs/\nbriefs/\n")
    (d / "state.json").write_text(json.dumps({"phase": phase}))
    for cmd in (["git", "init", "-q"], [*GIT_ID, "add", "-A"],
                [*GIT_ID, "commit", "-qm", "seed"]):
        subprocess.run(cmd, cwd=d, check=True, capture_output=True)
    return d


def drive(tmp_path, args, shim_body):
    shim = tmp_path / "claude-shim"
    shim.write_text(shim_body)
    shim.chmod(0o755)
    return subprocess.run(
        ["bash", str(SCRIPT), *args], capture_output=True, text=True,
        cwd=tmp_path, stdin=subprocess.DEVNULL,
        env={**os.environ, "AUTOAUTHOR_CLAUDE": str(shim)})


def phase_of(d):
    return json.loads((d / "state.json").read_text())["phase"]


def test_loop_walks_a_standalone_to_export(tmp_path):
    d = seeded(tmp_path / "p", "foundation")
    r = drive(tmp_path, [str(d)], ADVANCE)
    assert r.returncode == 0, r.stdout + r.stderr
    assert phase_of(d) == "export"
    assert "run /autoauthor:export" in r.stdout


def test_a_run_with_no_commit_exits_1_and_names_the_log(tmp_path):
    d = seeded(tmp_path / "p", "drafting")
    r = drive(tmp_path, [str(d)], STALL)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "no commit" in r.stderr
    named = [t for t in r.stderr.split() if "edit_logs/auto/" in t]
    assert named and Path(named[0].rstrip(",")).exists(), r.stderr
    assert phase_of(d) == "drafting", "a stalled phase must not advance"


def test_a_run_that_leaves_the_tree_dirty_exits_1(tmp_path):
    d = seeded(tmp_path / "p", "drafting")
    r = drive(tmp_path, [str(d)], DIRTY)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "dirty" in r.stderr


def test_a_dirty_tree_is_refused_before_anything_runs(tmp_path):
    d = seeded(tmp_path / "p", "drafting")
    (d / "junk.txt").write_text("uncommitted")
    r = drive(tmp_path, [str(d)], ADVANCE)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "dirty" in r.stderr
    assert phase_of(d) == "drafting", "nothing may run over a dirty tree"


def test_commits_without_progress_hit_max_runs(tmp_path):
    d = seeded(tmp_path / "p", "drafting")
    r = drive(tmp_path, [str(d), "--max-runs", "3"], CHURN)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "max-runs" in r.stderr


def test_container_loop_runs_every_work_not_just_the_first(tmp_path):
    """`claude -p` eats piped stdin; inside the works loop stdin was the
    works list, so the first invocation consumed every later work and the
    driver announced a finished collection with works untouched."""
    c = seeded(tmp_path / "coll", "export")
    works = ["01-a", "02-b", "03-c"]
    (c / "state.json").write_text(json.dumps(
        {"phase": "export", "structure": "collection", "works": works}))
    for w in works:
        seeded(c / "works" / w, "review")
    subprocess.run([*GIT_ID, "commit", "-aqm", "container"], cwd=c,
                   check=True, capture_output=True)
    r = drive(tmp_path, [str(c)], ADVANCE)
    assert r.returncode == 0, r.stdout + r.stderr
    for w in works:
        assert phase_of(c / "works" / w) == "export", f"{w} never ran"
    assert "every work is done" in r.stdout
