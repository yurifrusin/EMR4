# Ariadne agent error and correction register — revision 619

Date: 2026-08-22

Timestamp: 2026-08-22T17:06:02.0539735+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 619
incident_count: 964
new_incident_ids: AER-0964
open_incident_count: 0
-->

This revision adds one bounded, corrected input-binding observation from the
provider-free edit-coordinate future-runner integration rehearsal. It occurred
before the Node fixture, changed no accepted predecessor and invoked no worker,
model, provider, broker or network path.

## AER-0964 — runner binding conflated accepted source ancestry with file ownership

The first implementation preflight required the accepted logical source commit
to contain the later derived `future-runner.mjs` evidence path. The predecessor
contract instead binds two different facts: the exact current runner bytes and
the accepted source commit from which the runner was derived. The unnecessary
file-at-source assertion therefore returned `input_binding_rejected` before any
fixture execution.

The failure terminal is preserved. The correction keeps exact current bytes and
SHA-256 binding, independently proves the accepted source is a full Git commit
and ancestor of current HEAD, and no longer invents file ownership absent from
the predecessor contract. The corrected preflight, real-tool replay and hostile
tests pass with zero retry, resume or fallback.

## Register reading

This was one narrow correction to a newly introduced invariant, not a repeat of
the earlier abbreviated-object or manual-Git-prose lapses. The durable control
is to preserve the typed distinction between artifact identity, derivation
source and Git ancestry instead of collapsing them into one overloaded check.
