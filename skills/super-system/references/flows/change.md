# Flow: change

Redesign or refactor existing code. Same steps as `build.md`, with these differences:

- **Understand** starts with an audit of what exists: framework and build pipeline, routing, styling or module architecture, component/module tree, and concrete pain points (with file:line or screenshots as evidence). Ask the user which pain points matter most.
- **Explore options:** each option names the existing weaknesses it fixes and what it leaves untouched.
- **Plan:** aim for the smallest working diff; prefer deleting and reusing over adding. Keep every behavior outside the approved scope exactly as it was, and say how that is tested.
- **Existing decisions win:** the project's stack and the user's earlier choices override generic defaults from this skill or its dependencies.
- **Verify** includes the routes/endpoints next to the change, to catch regressions in what was supposed to stay the same.
