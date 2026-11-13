# Technique: Contract-First Split

Source: contract-first split specification (docs/design/api/<feature>.md)

Apply whenever a feature is split across backend and UI tasks:

1. **Read the frozen contract:** read `docs/design/api/<feature>.md` before editing any code. It defines routes, methods, request/response bodies, status codes, error shapes, and shared type names with their owning file.
2. **Backend task:** own backend files and the shared type definitions assigned by the contract. Satisfy every route, field name, status value, status code, and error shape verbatim.
3. **Frontend task:** own UI files only. Code strictly against the contract shapes and shared type names; mock the API locally until the post-merge integration check.
4. **No unilateral drift:** never rename a field, alter a status vocabulary, or change an error shape on one side. If the contract is ambiguous or needs a change, stop and return `status: "blocked"` (or escalate) so the orchestrator updates the contract for both sides.
5. **Reviewer:** verify every implemented route, payload, status code, error shape, and UI API call or mock matches `docs/design/api/<feature>.md` exactly.
