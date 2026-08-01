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

The three native alerts remain undismissed. Fresh CodeQL analysis must report
each instance fixed before its review conversation is resolved and PR 74 is
merged. Exact post-repair readback will be recorded without native alert
dismissal.
