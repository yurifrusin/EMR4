# Sol acceptance — canonical check-in pure environment evidence-gate evaluator

Date: 2026-08-23

Timestamp: 2026-08-23T12:01:25.0104668+10:00 (Australia/Brisbane)

Decision: `accepted_pending_clockwork_publication`

Reviewed source: `89640f1bb6ad992f68d5c20fd578b4062eeb193d`

I accept the pure unmounted evaluator and focused conformance. It deterministically
returns every accepted closed reason, denies absent or ambiguous manifest
populations without selection, reads no ambient clock, and treats a satisfied
reading as data with no admission or command capability.

Acceptance is supported by 57 passing focused tests, 258 passing focused and
surrounding tests, Ruff, compilation, `git diff --check` and direct source
review. The public boundary also fails closed for a caller-controlled timezone
object that raises during offset evaluation.

DeepSeek native Harness was correctly declined because no accepted runner is
compatible with this package unchanged. No new Harness engineering, generic
test, provider call or fallback occurred. Gemini and native subagents added no
proportionate leverage.

This acceptance grants no external-fact, admission, runtime, deployment or
protected authority.
