# Canonical check-in typed operational-evidence inputs

Date: 2026-08-23

Timestamp: 2026-08-23T11:20:38.5755231+10:00 (Australia/Brisbane)

## Lay summary

Raisa now has the next small piece needed to reason safely about whether an
ordinary check-in environment is genuinely ready. The system can hold a
strictly shaped reading for the database role, the custody/rotation evidence
for three credential slots, and the break-glass state. It cannot turn those
readings into permission, and it cannot replace evidence with a convenient
`yes` box.

This tranche deliberately does not claim that any real environment, role,
credential or verifier exists. It gives the later evaluator a reliable form to
read. All 201 focused and surrounding checks passed.

DeepSeek was not run this time. The accepted native-Harness runner is specialized
for one earlier one-edit exercise and does not fit this package unchanged. In
line with the pragmatic policy, we continued the real work instead of creating
another Harness-interoperability project. Native Harness remains available for
a future task whose shape already matches accepted machinery.

## Technical summary

- Reviewed source: `9011d83d769f45bb717c039a126a890d43922dce`.
- New pure module:
  `app/services/appointment_check_in_operational_evidence.py`.
- Exact aggregate: one role attestation, three ordered rotation/custody rows,
  one deny-only break-glass record.
- Boolean evidence claims, secret/resolution fields, abbreviated Git objects,
  malformed times and open shapes deny deterministically.
- Role mismatch, cross-binding mismatch, self-verifier references, future
  staleness and engaged/retired break glass remain typed inputs for the next
  evaluator; this module does not decide them.
- Verification: 57 focused and 201 focused/surrounding tests, Ruff, compile,
  source review and diff hygiene passed.
- DeepSeek/Gemini/native-subagent lanes were declined with recorded rationales;
  provider calls were zero.
- No route, database, secret, product runtime, deployment, Pages or protected
  ref changed.

Next: implement the pure environment evidence-gate evaluator with an explicit
evaluation time. The admission seam and every external operational fact remain
closed.
