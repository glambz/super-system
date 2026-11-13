# Flow: build

A new feature or a new project. Runs the whole backbone. The `change` flow reuses these steps with the differences listed in `change.md`.

1. **Understand.** Ask one question at a time until you know who it is for, what success looks like, goals and non-goals, constraints, and the existing stack (if any). Scouts may read the codebase meanwhile. With the `ui` track and brand screens in scope, also settle brand tone and audience.
2. **Explore options.** Follow "Explore options" in each active track file. UI options are per screen, backend options per component. Name the main screens/components.
3. **Gate 1.** The user picks one option per screen/component, or asks for changes (back to step 2).
4. **Spec.** Write the chosen options to each track's "Spec artifact" (UI: project DESIGN.md + library copy; backend: `docs/design/`).
5. **Plan.** Break the work into tasks. Each task names its files, the interface it produces or consumes, the test that proves it, and whether it is mechanical. Also name shared runtime resources that could collide if tasks run concurrently (a dev-server port, a test database); tasks that share one run one at a time unless the user says otherwise. For each feature touching both tracks, decide whether to split contract-first or run backend-first then frontend (don't split when the UI part is tiny or the API can't be known up front):
   - **Contract:** written by the orchestrator before Gate 2 approval at `docs/design/api/<feature>.md` (routes, request/response, status codes, error shapes, shared type names + file), frozen at Gate 2.
   - **Backend task:** owns backend files and shared type definitions assigned by the contract.
   - **Frontend task:** owns UI files; codes against the contract and mocks the API. (Both run concurrently when file sets don't overlap.)
6. **Gate 2.** Approve the task breakdown, frozen contracts, split choices, and concurrency mode.
7. **Implement + review.** Dispatch implementers on their slot. Send each output (or each batch, in economy) to a reviewer, as defined in `references/modes.md`, applying the track's "Quality lenses". Run tasks concurrently only if chosen at Gate 2. For split features, after both tracks merge, run an **integration check**: a reviewer with a browser tests the real UI against the real API plus end-to-end tests; mismatches go back as fix rounds.
8. **Verify.** Each active track's "Verify" section, at the scope the workflow mode sets.
9. **Final audit & retrospective.** You, personally, against the Definition of done in SKILL.md, at the scope the workflow mode sets. Refresh the library copy (UI). Then run the Retrospective in SKILL.md.
10. **Report.** The end-of-run report from SKILL.md.
