# Disposable PostgreSQL behavior function-name-form recovery

Date: 2026-08-08

Status: bounded parser candidate; runtime closed pending fresh veto

## Evidence

Attempt 014 is preserved byte-for-byte as
`provider-free-behavior-transaction-failure-evidence-014.json`. It repeated
the fixed `BTR-E01` / `22P02` boundary with no admitted scenario and verified
exact owned-container cleanup, but the reviewed coordinate parser released no
function coordinate.

The absence does not prove that PostgreSQL supplied no PL/pgSQL context. The
first parser admitted only a schema-qualified context spelling, whereas
PostgreSQL's standard function-context display may omit the schema from the
function name even when the call itself is schema-qualified.

## Closed correction

The parser now admits exactly two spellings and no others:

- `emr4_context_fabric.<allowlisted_function>(...)`; or
- `<allowlisted_function>(...)`.

Both forms must still be unique, use the fixed scenario's closed function-name
allowlist and carry one bounded internal line. Trusted code normalizes either
form to the same schema-qualified evidence identifier. Any other schema,
function, malformed line, missing coordinate or ambiguity releases nothing.
Raw SQL, values, messages, signatures and unrestricted identifiers remain
sealed.

## Next gate

No parent SQL or scenario changes. Focused hostile tests and one fresh exact-
HEAD Gemini 3.6 Flash/high veto must pass before another newly owned contained
diagnostic attempt. If no coordinate is released again, the failure remains
evidence for a distinct bounded diagnostic rather than authority for
speculative SQL changes.
