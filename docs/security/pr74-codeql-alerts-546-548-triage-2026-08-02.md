# PR 74 CodeQL alerts 546–548 triage

Date: 2026-08-02

Branch source revision: `1f950bfa9dbccd7858841b76fad08ce1e7cdb533`

Pull request: `yurifrusin/EMR4#74`

## Normalized inputs

| Triage item | Alert | Rule | Location | Native severity |
|---|---:|---|---|---|
| `triage-001` | 546 | `py/ineffectual-statement` | `app/services/application_identity_federation.py:190` | note |
| `triage-002` | 547 | `py/ineffectual-statement` | `app/services/application_identity_federation.py:199` | note |
| `triage-003` | 548 | `py/ineffectual-statement` | `app/services/application_identity_federation.py:203` | note |

## Static security triage

Verdict for each instance: `not_actionable`, high confidence, no exploitability
stack rank.

The cited expressions are ellipsis bodies on three structural `Protocol`
methods. There is no attacker-controlled source, transformation, dangerous
sink or protected operation in any statement. The module is a default-off,
route-free authored-synthetic policy component; repository search finds no
FastAPI or GraphQL router importing it. The applicable `SECURITY.md` keeps the
backend authoritative for identity and audit, but these inert stub expressions
neither grant authority nor affect a runtime decision. No supported product
security boundary is crossed.

Counterevidence to a security finding is complete: the statements are type
contracts, their concrete in-memory and PostgreSQL implementations own the
actual behavior, and the scanner rule is tagged maintainability/quality/useless
code rather than a security-severity query. There is no material static proof
gap.

## Quality disposition and repair

The findings are valid quality defects even though they are not security
vulnerabilities. Each ellipsis is replaced with an explicit
`NotImplementedError`, preserving the structural protocol contract while
making accidental direct invocation fail visibly. No authentication decision,
binding behavior, session state, database path or product boundary changes.

The three native alerts remain undismissed. Fresh CodeQL workflow run
`30718544607` and wrapper check `91418376728` passed at fixed task-branch HEAD
`eeb39df38f6d7ccda76b0d28a92047ed98816717`. Exact GitHub REST readback reports
alerts 546, 547 and 548 `fixed`, with no dismissal and no native alert mutation.
The durable readback is
`orchestration/continuity/raisa-real-identity-microsoft-federation-boundary/codeql-pr74-alerts-readback.json`.

The final security disposition remains `not_actionable`: none of the three
quality instances survives as a product security finding. The source repair is
verified and their repaired review conversations may now be resolved before
PR 74 integration.
