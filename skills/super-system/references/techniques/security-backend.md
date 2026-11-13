# Technique: Backend Security

Source: security-and-hardening; run lessons 2026-11-13 (constant-time byte compares, shared auth helper, no broad except)

Apply to every backend task and review:

1. **Unified authorization:** enforce authorization on every changed route, handler, and tool through one shared helper so REST and any MCP/CLI/job layer apply the exact same rule.
2. **Membership, role, and default deny:** verify both tenant/resource membership and actor role/ownership; deny by default.
3. **Trust-boundary validation:** validate all external input (types, schemas, lengths, ranges) at the entry boundary; never concatenate user input into SQL, shell commands, or queries (use parameterized queries).
4. **Secrets and compares:** read secrets from env or a secret store only — never hardcode secrets or fallback defaults in code. Perform constant-time compares on `bytes` (encode strings to UTF-8 first so non-ASCII never raises).
5. **Transport and error hygiene:** accept tokens/keys in headers, never query strings. Never use broad `except` blocks that mask real bugs or turn internal errors into auth/404 responses.
6. **SSRF and LLM boundaries:** allowlist scheme, host, and non-private resolved IPs for server-side URL fetches; treat LLM output as untrusted input.
7. **Logging and responses:** never log secrets, tokens, or personal data; strip sensitive fields from API responses.
8. **Auth tests:** include tests proving both a denied actor (401/403) and an allowed actor.
