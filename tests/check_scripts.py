#!/usr/bin/env python3
"""Verify helper scripts under skills/super-system/scripts/.

Run from repo root:
    python tests/check_scripts.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "skills" / "super-system" / "scripts"

EXPECTED_SCRIPTS = [
    "_lib.sh",
    "run-agy.sh",
    "run-codex.sh",
    "review-wrap.sh",
    "queue.sh",
    "wait-done.sh",
    "removed-checks.py",
    "worktree-setup.sh",
    "worktree-cleanup.sh",
]

PERSONAL_PATHS = re.compile(
    r"(C:\\Users\\[^\\\"']+|C:/Users/[^/\"']+|/Users/[^/\"']+|/home/[^/\"']+)",
    re.I,
)
MODEL_NAMES = re.compile(
    r"\b(Opus|Sonnet|Haiku|Argon|Flash|gpt-[0-9]|claude-[0-9]|gemini-[0-9])\b", re.I
)


def find_bash():
    bash = shutil.which("bash")
    if sys.platform == "win32":
        candidates = [
            Path("C:/Program Files/Git/usr/bin/bash.exe"),
            Path("C:/Program Files/Git/bin/bash.exe"),
        ]
        if bash and "system32" in bash.lower():
            bash = None
        if not bash:
            for c in candidates:
                if c.is_file():
                    return str(c)
    return bash


def check_exists_and_headers():
    fails = []
    for name in EXPECTED_SCRIPTS:
        p = SCRIPTS_DIR / name
        if not p.is_file():
            fails.append(f"{name}: missing")
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        head = "\n".join(lines[:35]).lower()
        if "usage:" not in head:
            fails.append(f"{name}: missing Usage: comment in header")
        if "copy" not in head or "run folder" not in head or "never edit" not in head:
            fails.append(f"{name}: missing copy-to-run-folder / never-edit header rule")
    return fails


def check_syntax():
    fails = []
    bash = find_bash()
    for name in EXPECTED_SCRIPTS:
        p = SCRIPTS_DIR / name
        if not p.is_file():
            continue
        if name.endswith(".sh"):
            if not bash:
                fails.append(f"{name}: bash not found for syntax check")
                continue
            r = subprocess.run([bash, "-n", str(p)], capture_output=True, text=True)
            if r.returncode != 0:
                fails.append(f"{name}: bash -n failed: {r.stderr.strip()}")
        elif name.endswith(".py"):
            try:
                compile(p.read_text(encoding="utf-8"), str(p), "exec")
            except SyntaxError as exc:
                fails.append(f"{name}: syntax check failed: {exc}")
    return fails


def check_clean_content():
    fails = []
    for name in EXPECTED_SCRIPTS:
        p = SCRIPTS_DIR / name
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m_path = PERSONAL_PATHS.search(text)
        if m_path:
            fails.append(f"{name}: contains personal path {m_path.group(0)!r}")
        m_model = MODEL_NAMES.search(text)
        if m_model:
            fails.append(f"{name}: contains model name {m_model.group(0)!r}")
    return fails


def _git(repo, *args):
    env = os.environ.copy()
    env["MSYS_NO_PATHCONV"] = "1"
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def _init_temp_repo(base_dir):
    repo = Path(base_dir) / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    return repo


def check_removed_checks_functional():
    script = SCRIPTS_DIR / "removed-checks.py"
    if not script.is_file():
        return ["removed-checks.py: missing for functional test"]
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _init_temp_repo(tmp)
        target = repo / "app.py"
        target.write_text(
            "def handler(user):\n"
            "    if not user:\n"
            "        raise HTTPException(status_code=403, detail='forbidden')\n"
            "    x = 1 + 1\n"
            "    return x\n",
            encoding="utf-8",
        )
        _git(repo, "add", "app.py")
        _git(repo, "commit", "-m", "base")

        # Remove both the security check and an unrelated line.
        target.write_text(
            "def handler(user):\n"
            "    return 2\n",
            encoding="utf-8",
        )
        r = subprocess.run(
            [sys.executable, str(script), str(repo), "HEAD", "app.py"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            return [f"removed-checks.py exited {r.returncode}: {r.stderr.strip()}"]
        out = r.stdout
        if "app.py:3:" not in out or "raise HTTPException" not in out:
            fails.append(f"removed-checks.py: did not report 'app.py:3:' with 'raise HTTPException'; got: {out!r}")
        if "x = 1 + 1" in out:
            fails.append(f"removed-checks.py: reported unrelated removed line 'x = 1 + 1'; got: {out!r}")

        # git quotes non-ASCII names and tab-terminates names with spaces in diff headers.
        odd = repo / "café x.py"
        odd.write_text("def f(u):\n    if not u:\n        raise HTTPException(403)\n", encoding="utf-8")
        _git(repo, "add", "café x.py")
        _git(repo, "commit", "-m", "odd name")
        odd.write_text("def f(u):\n    return u\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(script), str(repo), "HEAD", "café x.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if "café x.py:3:" not in r.stdout:
            fails.append(f"removed-checks.py: did not name the non-ASCII/space path 'café x.py:3:'; got: {r.stdout!r} {r.stderr!r}")

        # Deny branches (rules 1 & 2) and '--' handling (rule 3).
        deny = repo / "deny.py"
        deny.write_text(
            "def check(user, org_ids, flag):\n"
            "    if user.org_id not in org_ids:\n"
            "        return False\n"
            "    if flag == 1:\n"
            "        return {'error': 'denied'}\n"
            "    if flag == 2:\n"
            '        return  {  "error": "bad"}\n'
            "    if flag == 3: return None\n"
            "    if flag == 4: return\n"
            "    if flag == 5:\n"
            "        return None\n"
            "    elif flag == 6:\n"
            "        return\n"
            "    val = 42\n"
            "    return None\n",
            encoding="utf-8",
            newline="\n",
        )
        _git(repo, "add", "deny.py")
        _git(repo, "commit", "-m", "deny branches")
        deny.write_text("def check(user, org_ids, flag):\n    return 0\n", encoding="utf-8", newline="\n")

        r_deny = subprocess.run(
            [sys.executable, str(script), str(repo), "HEAD", "deny.py"],
            capture_output=True,
            text=True,
        )
        if r_deny.returncode != 0:
            fails.append(f"removed-checks.py (deny.py) exited {r_deny.returncode}: {r_deny.stderr.strip()}")
        else:
            out_deny = r_deny.stdout
            expected_deny = (
                "deny.py:2:     if user.org_id not in org_ids:\n"
                "deny.py:3:         return False\n"
                "deny.py:5:         return {'error': 'denied'}\n"
                'deny.py:7:         return  {  "error": "bad"}\n'
                "deny.py:8:     if flag == 3: return None\n"
                "deny.py:9:     if flag == 4: return\n"
                "deny.py:11:         return None\n"
                "deny.py:13:         return\n"
            )
            deny_lines = out_deny.splitlines()
            if not deny_lines or any("deny.py:15:" in ln for ln in deny_lines):
                fails.append(f"removed-checks.py: expected non-empty deny listing without deny.py:15, got: {out_deny!r}")
            if out_deny != expected_deny:
                fails.append(f"removed-checks.py (deny.py) mismatch:\ngot:      {out_deny!r}\nexpected: {expected_deny!r}")

            r_deny_dash = subprocess.run(
                [sys.executable, str(script), str(repo), "HEAD", "--", "deny.py"],
                capture_output=True,
                text=True,
            )
            if r_deny_dash.returncode != 0 or r_deny_dash.stdout != expected_deny:
                fails.append(
                    f"removed-checks.py: '--' before file mismatch: rc={r_deny_dash.returncode} "
                    f"got={r_deny_dash.stdout!r} expected={expected_deny!r}"
                )

            r_usage = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            if r_usage.returncode != 2 or "[--]" not in r_usage.stderr:
                fails.append(f"removed-checks.py: usage stderr missing '[--]': rc={r_usage.returncode} err={r_usage.stderr!r}")

            r_all = subprocess.run(
                [sys.executable, str(script), str(repo), "HEAD"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            r_all_dash = subprocess.run(
                [sys.executable, str(script), str(repo), "HEAD", "--"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if r_all_dash.returncode != 0 or r_all_dash.stdout != r_all.stdout:
                fails.append(
                    f"removed-checks.py: bare '--' changed output: rc={r_all_dash.returncode} "
                    f"got={r_all_dash.stdout!r} expected={r_all.stdout!r}"
                )

            uni = repo / "uni.py"
            uni.write_text(
                'def check():\n    raise ValueError("denied 😀 中")\n',
                encoding="utf-8",
                newline="\n",
            )
            _git(repo, "add", "uni.py")
            _git(repo, "commit", "-m", "unicode check")
            uni.write_text("def check():\n    return 0\n", encoding="utf-8", newline="\n")
            r_uni = subprocess.run(
                [sys.executable, str(script), str(repo), "HEAD", "uni.py"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "ascii"},
            )
            if r_uni.returncode != 0 or 'uni.py:2:     raise ValueError("denied 😀 中")' not in r_uni.stdout:
                fails.append(
                    f"removed-checks.py (unicode): rc={r_uni.returncode} out={r_uni.stdout!r} err={r_uni.stderr!r}"
                )
    return fails


def check_shell_helpers_functional():
    bash = find_bash()
    if not bash:
        return ["bash not found for shell functional tests"]
    for name in (
        "review-wrap.sh",
        "queue.sh",
        "wait-done.sh",
        "worktree-setup.sh",
        "worktree-cleanup.sh",
        "run-agy.sh",
        "run-codex.sh",
    ):
        if not (SCRIPTS_DIR / name).is_file():
            return [f"{name}: missing for functional test"]

    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # 1. review-wrap.sh
        repo = _init_temp_repo(tmp_path)
        (repo / "a.txt").write_text("base\n", encoding="utf-8")
        _git(repo, "add", "a.txt")
        _git(repo, "commit", "-m", "init")
        (repo / "a.txt").write_text("changed\n", encoding="utf-8")

        rw = (SCRIPTS_DIR / "review-wrap.sh").as_posix()
        r_ok = subprocess.run(
            [bash, rw, repo.as_posix(), "HEAD", "true"],
            capture_output=True,
            text=True,
        )
        if r_ok.returncode != 0:
            fails.append(f"review-wrap.sh failed on unchanged review: {r_ok.stdout} {r_ok.stderr}")

        r_dirty = subprocess.run(
            [bash, rw, repo.as_posix(), "HEAD", bash, "-c", f"echo hack >> '{(repo / 'a.txt').as_posix()}'"],
            capture_output=True,
            text=True,
        )
        if r_dirty.returncode == 0:
            fails.append("review-wrap.sh returned 0 even though reviewer modified a file")

        # 1b. review-wrap.sh with non-ASCII filenames/content under PYTHONIOENCODING=ascii
        rw_uni_base = tmp_path / "rw_uni"
        rw_uni_base.mkdir()
        rw_repo = _init_temp_repo(rw_uni_base)
        uni_file = rw_repo / "note_🎉_中.txt"
        uni_file.write_bytes(b"base \xf0\x9f\x8e\x89 \xe4\xb8\xad \xff\xfe\n")
        _git(rw_repo, "add", "note_🎉_中.txt")
        _git(rw_repo, "commit", "-m", "init unicode")
        ascii_env = {**os.environ, "PYTHONIOENCODING": "ascii"}

        for qp in ("true", "false"):
            _git(rw_repo, "config", "core.quotePath", qp)
            r_rw_uni = subprocess.run(
                [bash, rw, rw_repo.as_posix(), "HEAD", bash, "-c", f"printf 'x' >> '{uni_file.as_posix()}'"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=ascii_env,
            )
            if r_rw_uni.returncode == 0 or r_rw_uni.stdout.splitlines() != ["changed: note_🎉_中.txt", "review-wrap: CHANGED"]:
                fails.append(
                    f"review-wrap.sh (quotePath={qp}, ascii) failed to report only the changed unicode file: "
                    f"rc={r_rw_uni.returncode} out={r_rw_uni.stdout!r} err={r_rw_uni.stderr!r}"
                )

        # 2. worktree-setup.sh & worktree-cleanup.sh (including nested link inside deps)
        (repo / ".env").write_text("SECRET=1\n", encoding="utf-8")
        dep_dir = repo / "deps"
        dep_dir.mkdir()
        (dep_dir / "keep.txt").write_text("important\n", encoding="utf-8")
        inner_target = tmp_path / "inner_target"
        inner_target.mkdir()
        (inner_target / "nested.txt").write_text("nested\n", encoding="utf-8")
        inner_link = dep_dir / "inner_link"
        if sys.platform == "win32":
            subprocess.run(
                [bash, "-c", 'MSYS_NO_PATHCONV=1 cmd /c mklink /J "$1" "$2" > /dev/null', "_", str(inner_link), str(inner_target)],
                check=True,
            )
        else:
            os.symlink(str(inner_target), str(inner_link))

        wt = tmp_path / "wt1"
        ws = (SCRIPTS_DIR / "worktree-setup.sh").as_posix()
        wc = (SCRIPTS_DIR / "worktree-cleanup.sh").as_posix()
        r_ws = subprocess.run(
            [bash, ws, repo.as_posix(), wt.as_posix(), "feat-1", "HEAD", "--env", ".env", "--link", "deps"],
            capture_output=True,
            text=True,
        )
        if r_ws.returncode != 0:
            fails.append(f"worktree-setup.sh failed: {r_ws.stdout} {r_ws.stderr}")
        else:
            if not (wt / ".env").is_file():
                fails.append("worktree-setup.sh did not copy .env")
            if not (wt / "deps" / "keep.txt").is_file():
                fails.append("worktree-setup.sh did not link deps/")
            if not (wt / ".worktree-links").is_file():
                fails.append("worktree-setup.sh did not write .worktree-links manifest")
            r_wc = subprocess.run(
                [bash, wc, repo.as_posix(), wt.as_posix()],
                capture_output=True,
                text=True,
            )
            if r_wc.returncode != 0:
                fails.append(f"worktree-cleanup.sh failed: {r_wc.stdout} {r_wc.stderr}")
            if wt.exists():
                fails.append("worktree-cleanup.sh did not remove worktree directory")
            if not (dep_dir / "keep.txt").is_file():
                fails.append("worktree-cleanup.sh followed link and deleted source deps/keep.txt!")
            if not inner_link.exists() or not (inner_link / "nested.txt").is_file():
                fails.append("worktree-cleanup.sh descended into junction/symlink and broke deps/inner_link!")

        # 2d. Extra junction/symlink inside worktree NOT in manifest (repro3.sh)
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        (outside_dir / "precious.txt").write_text("keep-me\n", encoding="utf-8")
        wt_extra = tmp_path / "wt_extra"
        r_ws_e = subprocess.run(
            [bash, ws, repo.as_posix(), wt_extra.as_posix(), "feat-extra", "HEAD", "--env", ".env", "--link", "deps"],
            capture_output=True,
            text=True,
        )
        if r_ws_e.returncode != 0:
            fails.append(f"worktree-setup.sh (extra link test) failed: {r_ws_e.stdout} {r_ws_e.stderr}")
        else:
            extra_link = wt_extra / "extra_link"
            if sys.platform == "win32":
                subprocess.run(
                    [bash, "-c", 'MSYS_NO_PATHCONV=1 cmd /c mklink /J "$1" "$2" > /dev/null', "_", str(extra_link), str(outside_dir)],
                    check=True,
                )
            else:
                os.symlink(str(outside_dir), str(extra_link))
            r_wc_e = subprocess.run(
                [bash, wc, repo.as_posix(), wt_extra.as_posix()],
                capture_output=True,
                text=True,
            )
            if r_wc_e.returncode != 0:
                fails.append(f"worktree-cleanup.sh (extra link) failed: {r_wc_e.stdout} {r_wc_e.stderr}")
            if wt_extra.exists():
                fails.append("worktree-cleanup.sh (extra link) did not remove worktree")
            if not (outside_dir / "precious.txt").is_file():
                fails.append("worktree-cleanup.sh followed unlisted extra junction and deleted outside/precious.txt!")

        # 2e. Pre-validation in worktree-setup.sh leaves no half-created worktree on error
        wt_bad = tmp_path / "wt_bad"
        r_bad_env = subprocess.run(
            [bash, ws, repo.as_posix(), wt_bad.as_posix(), "feat-bad-env", "HEAD", "--env", "missing.env"],
            capture_output=True,
            text=True,
        )
        if r_bad_env.returncode == 0 or wt_bad.exists() or "missing.env" not in (r_bad_env.stdout + r_bad_env.stderr):
            fails.append(f"worktree-setup.sh did not reject missing --env cleanly: rc={r_bad_env.returncode} exists={wt_bad.exists()} err={r_bad_env.stderr!r}")

        tracked_dir = repo / "tracked_dir"
        tracked_dir.mkdir()
        (tracked_dir / "file.txt").write_text("tracked\n", encoding="utf-8")
        _git(repo, "add", "tracked_dir/file.txt")
        _git(repo, "commit", "-m", "add tracked_dir")
        r_bad_link = subprocess.run(
            [bash, ws, repo.as_posix(), wt_bad.as_posix(), "feat-bad-link", "HEAD", "--link", "tracked_dir"],
            capture_output=True,
            text=True,
        )
        if r_bad_link.returncode == 0 or wt_bad.exists() or "tracked_dir" not in (r_bad_link.stdout + r_bad_link.stderr):
            fails.append(f"worktree-setup.sh did not reject tracked --link cleanly: rc={r_bad_link.returncode} exists={wt_bad.exists()} err={r_bad_link.stderr!r}")

        # 2c. worktree-cleanup.sh refuses when manifest and --links are both missing
        wt_untracked = tmp_path / "wt_no_manifest"
        r_ws_u = subprocess.run(
            [bash, ws, repo.as_posix(), wt_untracked.as_posix(), "feat-nomani", "HEAD"],
            capture_output=True,
            text=True,
        )
        if r_ws_u.returncode == 0 and (wt_untracked / ".worktree-links").is_file():
            (wt_untracked / ".worktree-links").unlink()
            r_wc_refuse = subprocess.run(
                [bash, wc, repo.as_posix(), wt_untracked.as_posix()],
                capture_output=True,
                text=True,
            )
            if r_wc_refuse.returncode == 0:
                fails.append("worktree-cleanup.sh should refuse when .worktree-links and --links are both missing")
            # Explicit --links allows cleanup when manifest is missing
            r_wc_explicit = subprocess.run(
                [bash, wc, repo.as_posix(), wt_untracked.as_posix(), "--links", "none"],
                capture_output=True,
                text=True,
            )
            if r_wc_explicit.returncode != 0 or wt_untracked.exists():
                fails.append(f"worktree-cleanup.sh --links none failed: {r_wc_explicit.stdout} {r_wc_explicit.stderr}")

        # 2b. worktree-setup.sh & worktree-cleanup.sh with POSIX-form paths (Git Bash /c/...)
        wt_posix_win = tmp_path / "wt_posix"
        if sys.platform == "win32":
            repo_posix = subprocess.check_output(
                [bash, "-c", 'cygpath -u "$1"', "_", str(repo)], text=True
            ).strip()
            wt_posix = subprocess.check_output(
                [bash, "-c", 'cygpath -u "$1"', "_", str(wt_posix_win)], text=True
            ).strip()
        else:
            repo_posix = repo.as_posix()
            wt_posix = wt_posix_win.as_posix()
        r_ws_p = subprocess.run(
            [bash, ws, repo_posix, wt_posix, "feat-posix", "HEAD", "--env", ".env", "--link", "deps"],
            capture_output=True,
            text=True,
        )
        if r_ws_p.returncode != 0:
            fails.append(f"worktree-setup.sh failed with POSIX paths: rc={r_ws_p.returncode} {r_ws_p.stdout} {r_ws_p.stderr}")
        else:
            if not (wt_posix_win / ".env").is_file():
                fails.append("worktree-setup.sh (POSIX paths) did not copy .env")
            if not (wt_posix_win / "deps" / "keep.txt").is_file():
                fails.append("worktree-setup.sh (POSIX paths) did not link deps/")
            r_wc_p = subprocess.run(
                [bash, wc, repo_posix, wt_posix],
                capture_output=True,
                text=True,
            )
            if r_wc_p.returncode != 0:
                fails.append(f"worktree-cleanup.sh failed with POSIX paths: rc={r_wc_p.returncode} {r_wc_p.stdout} {r_wc_p.stderr}")
            if wt_posix_win.exists():
                fails.append("worktree-cleanup.sh (POSIX paths) did not remove worktree directory")
            if not (dep_dir / "keep.txt").is_file():
                fails.append("worktree-cleanup.sh (POSIX paths) deleted source deps/keep.txt!")

        # 3. queue.sh
        cmds_file = tmp_path / "cmds.txt"
        q_out = tmp_path / "q.txt"
        cmds_file.write_text(
            f"echo one >> '{q_out.as_posix()}'\necho two >> '{q_out.as_posix()}'\n",
            encoding="utf-8",
        )
        r_q = subprocess.run(
            [bash, (SCRIPTS_DIR / "queue.sh").as_posix(), "2", "0", cmds_file.as_posix()],
            capture_output=True,
            text=True,
        )
        if r_q.returncode != 0 or sorted(q_out.read_text(encoding="utf-8").splitlines()) != ["one", "two"]:
            fails.append(f"queue.sh failed: rc={r_q.returncode} out={r_q.stdout} err={r_q.stderr}")

        # 4. wait-done.sh (including pattern starting with '-')
        wd_file = tmp_path / "wait.log"
        wd_file.write_text("starting\nREADY_NOW\n-DASH_OK\n", encoding="utf-8")
        r_wd = subprocess.run(
            [bash, (SCRIPTS_DIR / "wait-done.sh").as_posix(), wd_file.as_posix(), "READY_NOW", "1", "1"],
            capture_output=True,
            text=True,
        )
        if r_wd.returncode != 0 or "done" not in r_wd.stdout.lower():
            fails.append(f"wait-done.sh failed: rc={r_wd.returncode} out={r_wd.stdout} err={r_wd.stderr}")
        r_wd_dash = subprocess.run(
            [bash, (SCRIPTS_DIR / "wait-done.sh").as_posix(), wd_file.as_posix(), "-DASH_OK", "0", "1"],
            capture_output=True,
            text=True,
        )
        if r_wd_dash.returncode != 0 or "done" not in r_wd_dash.stdout.lower():
            fails.append(f"wait-done.sh failed on '-' pattern: rc={r_wd_dash.returncode} out={r_wd_dash.stdout} err={r_wd_dash.stderr}")

        # 5. run-agy.sh and run-codex.sh with stubbed CLI binaries (no real CLI!)
        stub_bin = tmp_path / "bin"
        stub_bin.mkdir()
        run_dir = tmp_path / "run"
        for sub in ("briefs", "logs", "results", "scratch"):
            (run_dir / sub).mkdir(parents=True)
        (run_dir / "briefs" / "T-implementer-r1.md").write_text("brief\n", encoding="utf-8")
        schema = tmp_path / "schema.json"
        schema.write_text("{}", encoding="utf-8")

        agy_stub = stub_bin / "agy"
        agy_stub.write_text(
            "#!/usr/bin/env bash\n"
            "cat <<'JSON'\n"
            '{"event":"init","init":{"conversation_id":"conv-123"}}\n'
            '{"event":"result","result":{"status":"SUCCESS","conversation_id":"conv-123","structured_output":{"status":"done","summary":"ok","files_changed":[],"tests_run":null,"blocker":null,"red_evidence":[],"no_test_reason":"test"}}}\n'
            "JSON\n",
            encoding="utf-8",
        )
        codex_cwd_log = tmp_path / "codex_cwd.txt"
        codex_stub = stub_bin / "codex"
        codex_stub.write_text(
            "#!/usr/bin/env bash\n"
            f"printf '%s|%s\\n' \"$PWD\" \"$*\" >> '{codex_cwd_log.as_posix()}'\n"
            "out=''\n"
            "while [[ $# -gt 0 ]]; do\n"
            "  if [[ \"$1\" == \"-o\" ]]; then out=\"$2\"; shift 2; else shift; fi\n"
            "done\n"
            "printf '{\"status\":\"done\"}' > \"$out\"\n"
            "echo '{\"type\":\"thread.started\",\"thread_id\":\"th-1\"}'\n"
            "echo '{\"type\":\"turn.completed\"}'\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PATH"] = str(stub_bin) + os.pathsep + env.get("PATH", "")

        r_agy = subprocess.run(
            [
                bash,
                (SCRIPTS_DIR / "run-agy.sh").as_posix(),
                "T-implementer",
                repo.as_posix(),
                run_dir.as_posix(),
                "1",
                schema.as_posix(),
                "test-model",
                "low",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        agy_res = run_dir / "results" / "T-implementer-r1.json"
        agy_meta = run_dir / "results" / "T-implementer-r1.meta"
        if r_agy.returncode != 0 or not agy_res.is_file() or not agy_meta.is_file():
            fails.append(f"run-agy.sh failed: rc={r_agy.returncode} err={r_agy.stderr}")
        else:
            parsed = json.loads(agy_res.read_text(encoding="utf-8"))
            if parsed.get("status") != "done":
                fails.append(f"run-agy.sh result mismatch: {parsed}")
            meta_txt = agy_meta.read_text(encoding="utf-8")
            if "conv-123" not in meta_txt or "SUCCESS" not in meta_txt:
                fails.append(f"run-agy.sh meta missing fields: {meta_txt!r}")

        (run_dir / "briefs" / "T-implementer-r2.md").write_text("brief2\n", encoding="utf-8")
        r_codex = subprocess.run(
            [
                bash,
                (SCRIPTS_DIR / "run-codex.sh").as_posix(),
                "T-implementer",
                repo.as_posix(),
                run_dir.as_posix(),
                "2",
                schema.as_posix(),
                "test-model",
                "low",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        codex_res = run_dir / "results" / "T-implementer-r2.json"
        if r_codex.returncode != 0 or not codex_res.is_file():
            fails.append(f"run-codex.sh failed: rc={r_codex.returncode} out={r_codex.stdout} err={r_codex.stderr}")
        else:
            parsed = json.loads(codex_res.read_text(encoding="utf-8"))
            if parsed.get("status") != "done":
                fails.append(f"run-codex.sh result mismatch: {parsed}")

        # Verify run-codex.sh resume runs with cwd == project_dir
        (run_dir / "briefs" / "T-implementer-r3.md").write_text("brief3\n", encoding="utf-8")
        r_codex_res = subprocess.run(
            [
                bash,
                (SCRIPTS_DIR / "run-codex.sh").as_posix(),
                "T-implementer",
                repo.as_posix(),
                run_dir.as_posix(),
                "3",
                schema.as_posix(),
                "test-model",
                "low",
                "th-1",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        if r_codex_res.returncode != 0:
            fails.append(f"run-codex.sh resume failed: rc={r_codex_res.returncode} err={r_codex_res.stderr}")
        else:
            repo_posix_real = subprocess.check_output(
                [bash, "-c", 'cd "$1" && pwd', "_", repo.as_posix()], text=True
            ).strip()
            last_line = codex_cwd_log.read_text(encoding="utf-8").splitlines()[-1]
            got_cwd, got_args = last_line.split("|", 1)
            if got_cwd != repo_posix_real or "exec resume th-1" not in got_args:
                fails.append(f"run-codex.sh resume cwd/args mismatch: cwd={got_cwd!r} (expected {repo_posix_real!r}) args={got_args!r}")

        # Verify role-key enforcement (reviewer requires 'verdict')
        (run_dir / "briefs" / "T-reviewer-r1.md").write_text("review\n", encoding="utf-8")
        r_bad_key = subprocess.run(
            [
                bash,
                (SCRIPTS_DIR / "run-codex.sh").as_posix(),
                "T-reviewer",
                repo.as_posix(),
                run_dir.as_posix(),
                "1",
                schema.as_posix(),
                "test-model",
                "low",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        if r_bad_key.returncode == 0:
            fails.append("run-codex.sh succeeded for reviewer without 'verdict' key")

        # Verify <task>-<role> validation fails clearly when role suffix is missing
        (run_dir / "briefs" / "plain-r1.md").write_text("brief\n", encoding="utf-8")
        for runner in ("run-agy.sh", "run-codex.sh"):
            r_no_role = subprocess.run(
                [
                    bash,
                    (SCRIPTS_DIR / runner).as_posix(),
                    "plain",
                    repo.as_posix(),
                    run_dir.as_posix(),
                    "1",
                    schema.as_posix(),
                    "test-model",
                    "low",
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            if r_no_role.returncode == 0 or "role" not in r_no_role.stderr.lower():
                fails.append(f"{runner} did not fail clearly on missing role suffix: rc={r_no_role.returncode} err={r_no_role.stderr!r}")

        # Verify run-codex.sh rate-limit retry scoping and meta-file-first behavior
        stub_bin_rl = tmp_path / "bin_rl"
        stub_bin_rl.mkdir()
        (stub_bin_rl / "codex").write_text(
            "#!/usr/bin/env bash\n"
            "printf 'call\\n' >> \"$CODEX_CALL_LOG\"\n"
            "calls=$(wc -l < \"$CODEX_CALL_LOG\" | tr -d ' ')\n"
            "out=''\n"
            "while [[ $# -gt 0 ]]; do\n"
            "  if [[ \"$1\" == \"-o\" ]]; then out=\"$2\"; shift 2; else shift; fi\n"
            "done\n"
            "case \"$CODEX_TEST_MODE\" in\n"
            "  false_retry)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-fr\"}'\n"
            "    echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"HTTP 429 rate limit exceeded, quota\"}}'\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  event_limit)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-ev\"}'\n"
            "    if [[ \"$calls\" -eq 1 ]]; then\n"
            "      echo '{\"type\":\"error\",\"message\":\"high demand\"}'\n"
            "      exit 1\n"
            "    fi\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  stderr_limit)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-err\"}'\n"
            "    if [[ \"$calls\" -eq 1 ]]; then\n"
            "      echo 'usage limit' >&2\n"
            "      exit 1\n"
            "    fi\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  bad_json)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-bad\"}'\n"
            "    printf 'not json' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  error_spaced)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-sp\"}'\n"
            "    if [[ \"$calls\" -eq 1 ]]; then\n"
            "      echo '{\"type\": \"error\", \"message\": \"high demand\"}'\n"
            "      exit 1\n"
            "    fi\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  error_reordered)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-ro\"}'\n"
            "    if [[ \"$calls\" -eq 1 ]]; then\n"
            "      echo '{\"id\":\"1\",\"type\":\"error\",\"message\":\"high demand\"}'\n"
            "      exit 1\n"
            "    fi\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  item_nested_error)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-in\"}'\n"
            "    echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"error\",\"message\":\"429 rate limit, quota\"}}'\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "  error_unicode)\n"
            "    echo '{\"type\":\"thread.started\",\"thread_id\":\"th-uni\"}'\n"
            "    if [[ \"$calls\" -eq 1 ]]; then\n"
            "      echo '{\"type\":\"error\",\"message\":\"high demand 😀 中\"}'\n"
            "      exit 1\n"
            "    fi\n"
            "    printf '{\"status\":\"done\"}' > \"$out\"\n"
            "    echo '{\"type\":\"turn.completed\"}'\n"
            "    ;;\n"
            "esac\n",
            encoding="utf-8",
            newline="\n",
        )

        def _run_codex_rl(case_name, mode, extra_env=None):
            call_log = tmp_path / f"calls_{case_name}.txt"
            call_log.write_text("", encoding="utf-8")
            (run_dir / "briefs" / f"{case_name}-implementer-r1.md").write_text("brief\n", encoding="utf-8")
            rl_env = os.environ.copy()
            rl_env["PATH"] = str(stub_bin_rl) + os.pathsep + rl_env.get("PATH", "")
            rl_env["RETRY_SLEEP"] = "0"
            rl_env["CODEX_TEST_MODE"] = mode
            rl_env["CODEX_CALL_LOG"] = call_log.as_posix()
            if extra_env:
                rl_env.update(extra_env)
            proc = subprocess.run(
                [
                    bash,
                    (SCRIPTS_DIR / "run-codex.sh").as_posix(),
                    f"{case_name}-implementer",
                    repo.as_posix(),
                    run_dir.as_posix(),
                    "1",
                    schema.as_posix(),
                    "test-model",
                    "low",
                ],
                capture_output=True,
                text=True,
                env=rl_env,
            )
            num_calls = len(call_log.read_text(encoding="utf-8").splitlines())
            meta = run_dir / "results" / f"{case_name}-implementer-r1.meta"
            return proc, num_calls, meta

        p_fr, c_fr, _ = _run_codex_rl("fr", "false_retry")
        if p_fr.returncode != 0 or c_fr != 1:
            fails.append(f"run-codex.sh false retry on item.completed: rc={p_fr.returncode} calls={c_fr} err={p_fr.stderr!r}")

        p_ev, c_ev, _ = _run_codex_rl("ev", "event_limit")
        if p_ev.returncode != 0 or c_ev != 2:
            fails.append(f"run-codex.sh did not retry real limit in error event: rc={p_ev.returncode} calls={c_ev} err={p_ev.stderr!r}")

        p_se, c_se, _ = _run_codex_rl("se", "stderr_limit")
        if p_se.returncode != 0 or c_se != 2:
            fails.append(f"run-codex.sh did not retry real limit in stderr: rc={p_se.returncode} calls={c_se} err={p_se.stderr!r}")

        p_bj, _, meta_bj = _run_codex_rl("bj", "bad_json")
        meta_txt = meta_bj.read_text(encoding="utf-8") if meta_bj.is_file() else ""
        if p_bj.returncode == 0 or not meta_bj.is_file() or "th-bad" not in meta_txt:
            fails.append(f"run-codex.sh unparsable answer failed meta check: rc={p_bj.returncode} meta_exists={meta_bj.is_file()} meta={meta_txt!r}")

        p_sp, c_sp, _ = _run_codex_rl("sp", "error_spaced")
        if p_sp.returncode != 0 or c_sp != 2:
            fails.append(f"run-codex.sh did not retry spaced error event: rc={p_sp.returncode} calls={c_sp} err={p_sp.stderr!r}")

        p_ro, c_ro, _ = _run_codex_rl("ro", "error_reordered")
        if p_ro.returncode != 0 or c_ro != 2:
            fails.append(f"run-codex.sh did not retry reordered error event: rc={p_ro.returncode} calls={c_ro} err={p_ro.stderr!r}")

        p_in, c_in, _ = _run_codex_rl("in", "item_nested_error")
        if p_in.returncode != 0 or c_in != 1:
            fails.append(f"run-codex.sh false retry on nested item error: rc={p_in.returncode} calls={c_in} err={p_in.stderr!r}")

        p_uni, c_uni, _ = _run_codex_rl("uni", "error_unicode", extra_env={"PYTHONIOENCODING": "ascii"})
        if p_uni.returncode != 0 or c_uni != 2:
            fails.append(f"run-codex.sh did not retry unicode error event: rc={p_uni.returncode} calls={c_uni} err={p_uni.stderr!r}")

    return fails


def check_contrast_check_functional():
    script = SCRIPTS_DIR / "contrast-check.py"
    if not script.is_file():
        return ["contrast-check.py: missing for functional test"]
    fails = []
    r = subprocess.run(
        [sys.executable, str(script), "😀中", "#FFFFFF"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
    )
    if r.returncode != 2 or "error:" not in r.stdout or "😀中" not in r.stdout or "Traceback" in r.stderr:
        fails.append(
            f"contrast-check.py (unicode arg, ascii): rc={r.returncode} out={r.stdout!r} err={r.stderr!r}"
        )
    return fails


def main():
    fails = []
    for check in (
        check_exists_and_headers,
        check_syntax,
        check_clean_content,
        check_removed_checks_functional,
        check_contrast_check_functional,
        check_shell_helpers_functional,
    ):
        fails += check()
    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        return 1
    print("check_scripts: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
