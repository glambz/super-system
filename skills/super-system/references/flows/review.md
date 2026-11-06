# Flow: review

A read-only audit. No edits, no gates.

1. **Scope.** A diff, branch or commit range; a set of paths; or the whole project. Ask if the user didn't say.
2. **Read.** Scouts read in parallel, split by area. Coverage by workflow mode: full = every file in scope; normal = changed files plus code that calls or is called by them; economy = changed files only.
3. **Assess.** Apply each active track's "Quality lenses". If an approved plan or spec exists, also check the code against it and flag anything outside its scope.
4. **Confirm every finding** before reporting it: re-read the code, and run a test or reproduction where that is cheap. Drop what you can't support.
5. **Report.** Findings sorted critical → important → minor, each with `file:line`, what is wrong, the concrete failure it causes, and a suggested fix. List what was not reviewed. Offer to run `fix` or `change` on the findings the user picks.
