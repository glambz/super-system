# Technique: Systematic Debugging

Source: superpowers/systematic-debugging

Used across scout, implementer, and reviewer in the `fix` flow:

1. **Reproduce first:** get a reliable failing command, test, or exact steps. Read full error messages, stack traces, line numbers, and recent diffs.
2. **One hypothesis at a time:** state `"X is the root cause because Y"` with evidence, and test minimally with one variable at a time. Never stack speculative fixes.
3. **Trace backward to the origin:** follow the bad value, wrong state, or missing check back through the call stack to where it first originates.
4. **Grep every caller and sibling path:** search all call sites and parallel entry points (REST routes, MCP/CLI tools, services, background jobs).
5. **Fix at the shared origin:** put one fix where all callers route through; never patch only the symptom path from the bug report.
6. **Three-fix rule:** if 3+ fixes fail or each fix exposes coupling elsewhere, stop and report an architectural problem as a blocker.
7. **Scout / Reviewer:** gather `file:line` evidence for every caller and sibling path, and verify the fix closes all of them.
