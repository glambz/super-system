# Backend track

Read alongside the flow file whenever the `backend` track is active. Rules already in SKILL.md (gates, modes, roles, safeguards) are not repeated here.

## Before exploring

Read the existing architecture, data model, API conventions, test setup and how the project is deployed. Follow established patterns unless Gate 1 approves a change to them.

## Explore options

- How many options: the workflow-mode table in SKILL.md.
- Each option states: what it is (API shape, schema, or architecture), how it fits the existing code, its tradeoffs (complexity, migration risk, performance, operability), and what it rules out later.
- End with a recommendation and the reason for it.

## Spec artifact

Source of truth lives in the project under `docs/design/`, in whichever form fits:
- **API contract:** the project's existing format (e.g. OpenAPI); create one only if the change adds or alters an API.
- **Schema doc:** tables or collections touched, migrations, and backfill plan.
- **ADR:** `docs/design/adr/NNNN-<title>.md` with context, decision, consequences, for decisions a future reader would otherwise have to reverse-engineer.

Code follows the spec; when the code must diverge, update the spec in the same task. Backend specs are not copied to the design library.

## Implementation defaults

- Validate input at every trust boundary; parameterized queries only.
- Authorization on every new or changed endpoint.
- Secrets come from the environment or a secret store, never code or logs.
- Handle errors wherever data could be lost or left half-written.
- Log failure paths with enough context to diagnose, without secrets or personal data.
- Migrations are reversible, or the plan says why not.

## Verify

- Run the test suite (scope per the workflow-mode table in SKILL.md).
- Contract and integration tests against real dependencies where the project already has them (containers, test database).
- Run migrations against a copy (local or test database), never prod; run down migrations too when they exist.

## Quality lenses

1. **Correctness:** behavior matches the spec, including edge inputs.
2. **Error handling:** failures at boundaries are caught, reported and leave data consistent.
3. **Security:** input validation, authorization, secrets handling, injection.
4. **Performance:** no N+1 queries, unbounded queries or loops; new queries have the indexes they need; large lists paginate.
5. **Observability:** failures are visible in logs or metrics with enough context to act on.
