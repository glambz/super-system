# Flow: review

A read-only audit. No edits, no gates.

1. **Scope.** A diff, branch or commit range; a set of paths; or the whole project. Ask if the user didn't say.
2. **Read.** Scouts read in parallel, split by area. Coverage by workflow mode: full = every file in scope; normal = changed files plus code that calls or is called by them; economy = changed files only.
3. **Assess.** Apply each active track's "Quality lenses". If an approved plan or spec exists, also check the code against it and flag anything outside its scope.
4. **Verify findings.** After each area's scout, dispatch a fresh verifier (`scout` role) to re-read every cited line, reproduce cheaply where possible, apply the severity rubric (`references/severity.md`), and mark duplicates in the findings register (drop what can't be supported). The orchestrator samples (all `critical` findings + at least 1 in 5 of the rest) instead of re-reading everything.
5. **Retrospective.** Run the Retrospective in SKILL.md.
6. **Report.** Findings sorted critical → important → minor, each with `file:line`, what is wrong, the concrete failure it causes, and a suggested fix. List what was not reviewed. Offer to run `fix` or `change` on the findings the user picks.

## Findings register

| ID | Severity | Location | Summary | Evidence | Duplicates of |
|---|---|---|---|---|---|
| F-1 | critical \| important \| minor | `file:line` | What is wrong | Verified code or reproduction output | `—` or `F-N` |
