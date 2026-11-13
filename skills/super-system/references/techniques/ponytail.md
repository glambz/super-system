# Technique: Ponytail (minimum working diff)

Source: ponytail

- **Climb the ladder** (stop at the first rung that holds):
  1. Does this need to exist at all? Skip speculative work (YAGNI).
  2. Already in this codebase? Reuse existing helpers, types, and patterns.
  3. Standard library does it? Use it.
  4. Native platform feature covers it? Prefer it over custom JS or libraries.
  5. Already-installed dependency solves it? Use it; add no new dependencies.
  6. Can it be one line? Make it one line.
  7. Only then: ship the minimal code that works.
- **No bloat or unrequested changes:** no single-implementation interfaces, no factories for one type, no speculative config, no unrequested refactors, freezes, or behavior changes.
- **Root cause once:** fix bugs where all callers route through; never widen a shared helper for unrelated callers or patch only one path.
- **Fewest files, delete over add:** prefer deleting code over adding layers; remove any import, variable, or helper you added that ends up unused.
- **Protect existing tests:** never edit or weaken an existing test to make it pass or hide a bug; leave known-failing tests untouched.
- **Never simplify away:** input validation at trust boundaries, error handling that prevents data loss, security checks, or accessibility.
- **Reviewer:** reject bloat, unused additions, unrequested changes, and weakened tests as findings.
