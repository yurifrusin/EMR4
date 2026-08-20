# Ariadne agent error and correction register — revision 576

Date: 2026-08-20

<!-- ariadne-agent-error-register-reading
revision: 576
incident_count: 715
new_incident_ids: AER-0707,AER-0708,AER-0709,AER-0710,AER-0711,AER-0712,AER-0713,AER-0714,AER-0715
open_incident_count: 0
-->

This revision records nine bounded control incidents exposed across the two
authored-synthetic native-worker attempts and their closeout. Neither attempt
contacted DeepSeek. The second attempt started one native Harness process and
failed before HMR; the remaining incidents are local controller, validation or
clockwork-contract errors. All are contained or routed to the provider-disabled
successor, and none remains open.

## AER-0707 — attempt 001 used two WorkOrder digest conventions

The controller hashed newline-terminated canonical JSON while the broker
hashed the parsed canonical object. The broker therefore rejected the first
attempt before readiness, Harness launch or provider I/O.

Correction: both sides now use the shared canonical-object digest and a real
provider-free controller-to-broker readiness regression exercises the seam.

## AER-0708 — attempt 001 cleanup masked its initiating failure

Windows read-only Git objects prevented first-pass removal and the terminal
reported only cleanup failure rather than retaining the preceding handshake
rejection.

Correction: bounded literal-root removal clears only owned read-only files and
terminal construction preserves the first failure alongside later cleanup
coordinates.

## AER-0709 — a post-compaction receipt repeated Git object IDs manually

Hand-authored Git-source prose duplicated exact object identities already
owned by the machine snapshot, and preflight rejected before dispatch.

Correction: narrative evidence now states that the machine snapshot alone owns
exact Git objects; object IDs are projected only from Git.

## AER-0710 — a broad process query matched its own diagnostic command

A PowerShell CommandLine substring search counted the diagnostic process that
contained the search text, despite the actual Harness/broker population being
zero.

Correction: owned-process absence uses executable-qualified `node.exe` and
exact Harness/broker predicates.

## AER-0711 — the validation runner flag was recalled incorrectly

The first post-terminal invocation used `--output`; argparse rejected before
running any command because the runner requires `--receipt`.

Correction: the schema-owned flag produced the accepted nine-command receipt;
future invocations are generated from the parser contract or wrapper.

## AER-0712 — attempt 002 lost its pre-HMR semantic startup cause

The sole native process exited 1 before the first HMR event. Its 7,314 stderr
bytes survived only as a size and digest under a generic terminal, with zero
provider requests, tools or file changes.

Correction: the attempt is consumed without retry and the next provider-free
tranche will terminalize a closed sanitized pre-HMR stage/cause before raw
startup streams are deleted.

## AER-0713 — the first clockwork intent used an unadmitted causal enum

Two incident rows supplied `verified_cause`, while the clockwork incident
schema admits only `observation_only`. The check rejected before mutation.

Correction: every incident row uses the schema-owned coordinate; verified
technical conclusions remain in supporting evidence and narrative summaries.

## AER-0714 — the second clockwork intent used lifecycle prose as stages

The intent supplied `cleanup`, `rehydration` and `preparation` rather than the
clockwork's closed seven-stage vocabulary. The check rejected before mutation.

Correction: those details map to `closeout`, `acceptance` and `dispatch`, with
the finer coordinate retained in each incident narrative.

## AER-0715 — the prospective register revision source was not written first

The third clockwork check referenced revision 576 during transaction
projection before its exact human-readable nine-incident reading existed.

Correction: the revision, total count and new incident IDs are derived from the
current register plus admitted observations and written before the idempotent
transaction check.
