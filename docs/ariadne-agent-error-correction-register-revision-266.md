# Ariadne agent error and correction register — revision 266

Date: 2026-08-14

Timestamp: 2026-08-14T09:12:10+10:00 (Australia/Brisbane)

Revision 266 records AER-0304. The register now contains 304 bounded known
incidents, all corrected.

AER-0304 records an Antigravity adapter-observation vocabulary error in the
first pre-verifier runtime state. It used `antigravity_cli_observation`; the
harness admits `agy_cli_observation`. Deterministic preflight returned
`revision_required`, so no Antigravity project or Gemini review started.

The corrected state copies the exact admitted method from a current passing
veto-predispatch state and must produce a distinct passing receipt before the
external verifier can launch.

No protected output, prompt, secret, credential, patient, clinical, document or
product-derived value is retained in this revision or its sanitized receipt.
