# Ariadne agent error and correction register — revision 258

Date: 2026-08-12

Revision 258 records and corrects AER-0291. The register now contains 291
bounded known incidents with none open.

During status-confirm adapter discovery, Sol searched the broad `tests` tree
instead of an exact non-protected file allowlist. One matching line from a
protected fixture was printed in truncated tool output. The search stopped
immediately. Its content is discarded and prohibited from planning,
implementation, tests and acceptance. No repository file, runtime, database,
provider, product data, command or ref was mutated by the search.

This recurs the protected-scope pattern recorded by AER-0054 and AER-0092:
`orchestrator.overbroad_repository_content_search`. The strengthened control is
literal: every later content search must name exact already-known
non-protected files. Directory-root searches over `tests`, `docs` or the
repository root are prohibited even when the pattern itself appears narrow.

The incident and control are registered before any adapter plan, preplanning
receipt, implementation or acceptance. Subsequent adapter evidence may use
only the appointment router, appointment schemas, appointment-command OpenAPI
contract and exact selected status-confirm/API test files.
