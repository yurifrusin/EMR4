# Ariadne agent-error register revision 167

Date: 2026-08-10

Revision 167 adds AER-0193. The r149 Gemini 3.6 Flash/high reviewer returned a
schema-constrained `pass` even though its own receipt named the actual parent
`c8ab7602e16e24453dbf909597b4f702a2388416` while the reviewed contract and
packet contained a different nonexistent forty-character value. It also
claimed the resulting invalid range diff check passed.

Sol rejects that pass in
`raisa-context-fabric-durability-parse-characterization-review-sol-rejection.json`.
The receipt remains immutable evidence, but grants no acceptance. The corrected
candidate must pass deterministic verification and a fresh exact-HEAD review
whose challenge resolves and compares both full Git object IDs before any
disposable PostgreSQL run.
