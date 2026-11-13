# Technique: Verification Before Completion

Source: superpowers/verification-before-completion

Applies to every role before returning an answer:

1. **Fresh command evidence:** run the exact verification command named in your brief right after your final edit, using the exact interpreter or toolchain path given (never a bare `python`, `node`, or global binary when a path is specified).
2. **Read the full output:** check exit code and failure counts. Never write "should pass", "probably", or "looks good".
3. **Exact `files_changed`:** compute `git diff --name-only <base>` plus new untracked files (`git ls-files -o --exclude-standard`) and report that exact list.
4. **Audit removed checks:** diff your changed files against `<base>` (`git diff <base> -- <files>`) and inspect every removed line. List every removed permission, validation, visibility, or error check with the reason removing it is safe. Never silently drop an existing check.
5. **No omissions:** report any test failure observed during verification by name, even if pre-existing.
6. **Reviewer / Scout:** trust only what you directly read, ran, or measured; report every gap in `not_checked`.
