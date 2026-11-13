# Technique: Test-Driven Development (TDD)

Source: superpowers/test-driven-development

Follow Red → Green → Refactor for every code change (skip only when the brief states a docs/config task needs no test):

1. **Red — write a failing test first:**
   - Test one real behavior with a clear name; avoid mock-only assertions that test mocks instead of production code.
   - Run the new test on the unchanged base code using the exact test command and interpreter from the brief.
   - Save the failing command and output excerpt (≤ 2,000 chars) in `red_evidence`.
   - Confirm the failure is for the stated missing feature or bug — never an import, syntax, or fixture error.
   - A test that already passes on the base code proves nothing; rewrite it until it fails for the stated cause.
2. **Green — minimal fix:**
   - Write the simplest code that makes the failing test pass.
   - Re-run the exact same test command and the project suite; confirm all targeted tests pass and note any pre-existing failures.
3. **Refactor — after green only:**
   - Clean up duplication or unclear names while keeping all tests green; add no new behavior.
4. **Reviewer:**
   - Verify red on the base (run the new test against a scratch copy of the base files, without modifying project files) and green now.
   - Reject any new or regression test that already passes on the base code.
