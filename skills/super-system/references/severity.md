# Severity rubric

Use this rubric when classifying findings in `review` and task reviews:

- **critical:** exploitable without auth, across tenants/organisations, account takeover, or money figures wrong.
- **important:** a real bug or weakness with a narrower blast radius. Latent issues (unreachable today) are at most `important`.
- **minor:** correctness nits, dead code, performance, observability, or missing tests.
