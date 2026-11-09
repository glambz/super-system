# Flow: build

A new feature or a new project. Runs the whole backbone. The `change` flow reuses these steps with the differences listed in `change.md`.

1. **Understand.** Ask one question at a time until you know who it is for, what success looks like, goals and non-goals, constraints, and the existing stack (if any). Scouts may read the codebase meanwhile. With the `ui` track and brand screens in scope, also settle brand tone and audience.
2. **Explore options.** Follow "Explore options" in each active track file. UI options are per screen, backend options per component. Name the main screens/components.
3. **Gate 1.** The user picks one option per screen/component, or asks for changes (back to step 2).
4. **Spec.** Write the chosen options to each track's "Spec artifact" (UI: project DESIGN.md + library copy; backend: `docs/design/`).
5. **Plan.** Break the work into tasks. Each task names its files, the interface it produces or consumes, the test that proves it, and whether it is mechanical. Also name shared runtime resources that could collide if tasks run concurrently (a dev-server port, a test database); tasks that share one run one at a time unless the user says otherwise.
6. **Gate 2.**
7. **Implement + review.** Dispatch implementers on their slot. Send each output (or each batch, in economy) to a reviewer, as defined in `references/modes.md`, applying the track's "Quality lenses". Run tasks concurrently only if chosen at Gate 2.
8. **Verify.** Each active track's "Verify" section, at the scope the workflow mode sets.
9. **Final audit.** You, personally, against the Definition of done in SKILL.md, at the scope the workflow mode sets. Refresh the library copy (UI).
10. **Report.** The end-of-run report from SKILL.md.
