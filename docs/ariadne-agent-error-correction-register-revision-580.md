# Ariadne agent error and correction register — revision 580

Date: 2026-08-21

Timestamp: 2026-08-21T09:19:00.3227540+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 580
incident_count: 743
new_incident_ids: AER-0739,AER-0740,AER-0741,AER-0742,AER-0743
open_incident_count: 0
-->

## AER-0739 — masked staged-whitespace gate

The plan commit did not stop on the staged whitespace warning because later
commands masked the gate exit. A mechanical descendant removed the whitespace,
and later critical gates use immediate exit checks.

## AER-0740 — default-wrapper byte perturbation

The first opt-in serializer draft changed default wrapper bytes by one blank
line. The historical equality test rejected it before staging, and the
conditional template now preserves default output.

## AER-0741 — insertion-order JSON under real Node

Attempt 001 proved that semantically safe insertion-order JSON does not meet
the canonical reader contract. The plan-admitted recursive key-order serializer
and fresh attempt 002 pass.

## AER-0742 — delayed pre-commit receipt exit check

One combined command did not guard the receipt invocation immediately. A
separate fail-closed readback proved the preserved receipt passed before
staging; subsequent preflight commands use immediate guards.

## AER-0743 — missing prospective register reading

The first clockwork closeout check referenced this revision before its required
human reading artifact existed. Transaction preparation rejected before
canonical mutation; this exact reading was then authored before the corrected
check.

All five incidents are corrected or contained. None remains open, and none
opened DSH/Harness, provider, product, data, deployment, protected evidence or
protected-ref authority.
