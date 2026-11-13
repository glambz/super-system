# Flow: fix

Find the root cause of a bug and fix it there. No options step and no Gate 1.

1. **Reproduce.** Get a reliable reproduction: a command, a failing test, or exact browser steps. If you can't, gather what evidence exists and ask the user.
2. **Root-cause investigation.** Use the systematic-debugging technique: trace the bad value or behavior back to where it originates, form one hypothesis at a time and test it. Find every caller of the code you expect to change. Scouts may gather logs and code. No fix is proposed until the cause is stated with evidence.
3. **Fix plan.** The cause and its evidence; where the fix goes (the place all affected callers route through, not just the path in the report); the regression test; the files touched. If the fix touches both tracks, include the Gate 2 contract-first split decision (frozen `docs/design/api/<feature>.md` + integration check, or backend-first then frontend). Include a `## Decisions during the run` section and append every orchestrator decision made after Gate 2 (date, decision, reason).
4. **Gate 2.**
5. **Regression test first.** Write a test that fails on the current code for the stated cause. Run it and watch it fail (`red_evidence`).
6. **Implement + review.** The minimal fix. The reviewer confirms the test fails without the fix and passes with it (recorded in `regression_checks`), and checks the sibling callers.
7. **Verify.** Each active track's "Verify" section, plus the full test suite.
8. **Final audit, retrospective and report.** As in `build.md`; the report states the root cause.

If the investigation shows the fix needs a design change (a new API, a schema change, a redesigned screen), stop and propose switching to the `change` flow.
