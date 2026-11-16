# super-system: polish briefs name the pattern; test scripts print UTF-8

Source: the retrospective of the v3.2 follow-up run (`~/.super-system/runs/super-system-20261115-034232/retro.md`), proposals 1 and 2. The user approved both on 2026-11-16. One task, **P**.

Files allowed: `skills/super-system/references/modes.md`, `README.md`, `tests/check_skill.py`, `tests/check_scripts.py`.

## Hard constraints

- `skills/super-system/SKILL.md` is not changed (8179 bytes; `tests/check_skill.py` caps it at 8192).
- Each rule is stated once; no broken references; model names only in `references/platforms.md`; no personal paths or IDs in skill files.
- Never write an instruction telling an agent to load or run this skill itself.
- Keep every existing rule. No pre-existing sentence changes. House style: short sentences, plain words.
- Python 3 standard library only. Nothing outside the files allowed changes.

## Item A: polish briefs name the pattern (`references/modes.md`, "Minor triage")

Evidence: a review listed the same harmless extra line in two places. The polish brief named those two places and the implementer fixed exactly those. The next review found the same line in a third place in the same file; the one polish round was already used.

Add one sentence to the "Minor triage" bullet, after the sentence about polish groups starting early. Its meaning is fixed; wording may be tightened to house style:

> When a minor is one case of a repeated pattern, the polish brief states the pattern and asks the implementer to check every similar place in its files allowed, not only the cited lines.

Test: a required phrase for this sentence in `tests/check_skill.py`, added and run before the documentation edit (keep the failing output).

## Item B: the test scripts print UTF-8 (`tests/check_skill.py`, `tests/check_scripts.py`)

Evidence: both scripts report a failed check with `print(f"FAIL: {f}")`. On Windows, Python that writes to a pipe uses the console code page (cp1252). Some checks build their failure message from a file name that holds an emoji and CJK text. When such a check fails, the script crashes with `UnicodeEncodeError` instead of printing the `FAIL:` line. A reviewer reproduced this with `tests/check_scripts.py`.

What must hold, for both scripts:

1. A failed check's message always prints, whatever the console code page or locale, also under `PYTHONIOENCODING=ascii`: a message that holds an emoji or CJK text prints as a `FAIL:` line and the script exits non-zero, with no traceback.
2. Output for a passing run is unchanged (`check_skill: OK`, `check_scripts: OK`), and so are the exit codes.
3. The change is the smallest that holds (for example setting the output encoding once at the start of `main()`).

No permanent test is required for item B: the scripts are the test harness itself. Red evidence instead: in your scratch folder, make a copy of each script in which one check returns a failure message holding `🎉 中`, run it with `PYTHONIOENCODING=ascii` before and after your change, and record the crash (before) in `red_evidence` and the clean `FAIL:` line (after) in `summary`. Never leave such a copy in the project folder.

## README

Add one line to the existing "What's new in v3.2" list, after the last line, in the same style, covering both items. No existing line changes.

## Not in scope

Every other file, and every other behaviour of the two test scripts.
