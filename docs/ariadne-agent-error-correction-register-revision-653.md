# Ariadne agent error and correction register — revision 653

Date: 2026-08-24

Timestamp: 2026-08-24T01:51:25.4005323+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 653
incident_count: 1140
new_incident_ids: AER-1139,AER-1140
open_incident_count: 0
-->

## AER-1139

The first privacy-gate closeout continuation intent included the paired Yuri
summary in `active_evidence_paths`. That schema admits documentation,
Continuity and agent-inbox roots, but not the human inbox. Preflight rejected
before runtime-state materialisation or mutation. The rejected intent is
preserved; the corrected receipt omits that path while the summary remains a
normal closeout artifact. This repeats the evidence-root classification family
recorded in AER-1138 and narrows its prevention control to a fixed admitted-root
lookup before every continuation intent.

## AER-1140

The first semantic clockwork check supplied an empty
`agent_error_observations` list. The next check recorded the observations but
exceeded the intent's 100-scalar-leaf budget with 109. The third used compact
descriptive boundary tokens rather than four exact mandatory floor tokens. The
fourth reached prospective evidence validation and found the Sol acceptance
had no exact `Timestamp:` line. The fifth then found that the semantically
equivalent preacceptance receipt did not exist at the convention-derived
`-pre-verifier-receipt.json` path, repeating the family observed in AER-1136.
All five checks were rejected before verifier execution, publication or pointer
movement. The corrected input uses exact boundaries and human-evidence shapes,
and materialises the exact conventional receipt. Future closeouts must take all
four deterministic interface readings before their first check.
