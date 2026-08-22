# Ariadne agent error and correction register — revision 617

Date: 2026-08-22

Timestamp: 2026-08-22T15:33:39.2497985+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 617
incident_count: 960
new_incident_ids: AER-0957,AER-0958,AER-0959,AER-0960
open_incident_count: 0
-->

This revision adds two bounded, corrected preexecution observations, one post-
compaction receipt-vocabulary observation and one closeout-intent vocabulary
observation from the native-Harness useful-worker coordinate recovery. All
failed outside occupied authority. None is an occupied retry.

## AER-0957 — contract generated before bound schema bytes were final

The first control candidate removed trailing blank lines from copied schemas
after generating the deterministic contract. Exact contract equality and the
provider-free check rejected the stale candidate. The corrected descendant
regenerated the contract from the final bytes before preparation.

## AER-0958 — clockwork-owned canonical surfaces were updated directly

While recording AER-0957, the orchestrator directly edited the AGENTS and
agent-error-register surfaces that belong exclusively to the governance
clockwork. The checkpoint dry-run rejected `canonical_drift`. The exact surfaces
were restored to the last accepted generation, the first preparation identity
was closed and cleaned, and only the transactional clockwork advanced the live
checkpoint and this register.

## AER-0959 — post-compaction leverage values escaped the configured enum

The first post-compaction runtime state described the DeepSeek result as
`mixed` leverage and the unused Gemini lane as `none`. Both were reasonable
prose but invalid typed values. The orchestrator preflight rejected the receipt
before commit or clockwork publication. The corrected state uses configured
values `positive` and `neutral`, retaining the qualifications only in each
lane's rationale, and the fresh receipt passes.

## AER-0960 — closeout incident stage used descriptive rather than typed form

The first clockwork closeout intent labelled AER-0959's stage `verification`
instead of configured `deterministic_verification`. The clockwork rejected
`tick_incident_stage` before preparing or publishing any canonical surface. The
corrected descendant uses the configured value and requires intent-schema
validation before a closeout candidate commit, rather than discovering a form
error only after publication of that candidate.

## Register reading

The incidents show why a clockwork reading is preferable to remembered
procedure: a stale binding and an ownership violation stopped before they could
consume the one paid request, and a vocabulary lapse stopped before canonical
publication. A second vocabulary lapse then stopped at the first closeout
dry-run with zero canonical mutation. The process was not free, but it prevented
more ambiguous occupied reruns or invalid state and preserved exact corrective
evidence.
