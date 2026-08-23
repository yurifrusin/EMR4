# Sol acceptance — canonical check-in typed operational-evidence inputs

Date: 2026-08-23

Timestamp: 2026-08-23T11:20:38.5755231+10:00 (Australia/Brisbane)

Decision: `accepted_pending_clockwork_publication`

Reviewed source: `9011d83d769f45bb717c039a126a890d43922dce`

I accept the pure unmounted typed-input module and focused tests. The model is
closed, immutable and capability-free. It contains no Boolean evidence claim,
secret or resolution result, current-time source, manifest comparison,
evaluator outcome, admission result or effect method.

Acceptance is supported by 57 passing focused tests, 201 passing focused and
surrounding tests, Ruff, compilation, `git diff --check` and direct source
review. Structurally valid hostile observations remain representable for the
next evaluator, including wrong bindings, self-verifier references, stale-at-
future-evaluation evidence and non-inactive break glass.

DeepSeek native Harness was correctly declined because no already accepted
runner fits this package unchanged; no new Harness engineering or silent
transport fallback occurred. Gemini was not required for this low-risk
unmounted type with no API/runtime semantic change.

This acceptance grants no external-fact, operational, admission, runtime,
deployment or protected authority.
