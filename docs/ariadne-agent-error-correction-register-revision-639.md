# Ariadne Agent Error and Correction Register — Revision 639

Date: 2026-08-23

Timestamp: 2026-08-23T10:30:23.9779889+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 639
incident_count: 1082
new_incident_ids: AER-1060,AER-1061,AER-1062,AER-1063,AER-1064,AER-1065,AER-1066,AER-1067,AER-1068,AER-1069,AER-1070,AER-1071,AER-1072,AER-1073,AER-1074,AER-1075,AER-1076,AER-1077,AER-1078,AER-1079,AER-1080,AER-1081,AER-1082
open_incident_count: 0
-->

## AER-1060 — Preplanning receipt used manual Git bindings and a premature disposition

The first preplanning receipt supplied manually typed Git bindings and marked
the not-yet-dispatched worker lane `selected`. Validation failed closed. A
machine-resolved snapshot and the admitted `planned` disposition passed before
dispatch.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1061 — Windows-invalid wildcard used in dependency search

A read-only ripgrep search supplied a wildcard in a Windows path. Ripgrep
rejected it; explicit literal paths supplied the required dependency reading.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1062 — Package script invoked outside module context

The orchestrator invoked a package-backed script directly and received
`ModuleNotFoundError`. Re-running it through `python -m` restored the repository
module path without changing evidence.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1063 — Scaffold carried non-canonical terminal blank lines

The initial scaffold ended with extra blank lines outside the frozen exact-byte
form. A deterministic EOF check detected them and the files were normalized
before worker dispatch.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1064 — Windows wildcard search form recurred

The invalid wildcard-path form recurred once while locating native-Harness
provider-free scripts. The search failed without mutation and was replaced by
an explicit directory-root search.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1065 — Preset-source helper called with the wrong argument shape

The first coordinator preparation call supplied the wrong argument to
`build_preset_source` and raised `TypeError` before dispatch. Reading the exact
signature and rebinding the call corrected the coordinator.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1066 — Command-manifest identifier exceeded its closed bound

The first coordinator preparation used a command ID longer than the admitted
manifest schema permits. Validation rejected it before provider or worker
activity; the concise ID `PF_MANIFEST_NORMALIZER` passed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1067 — External native Harness was incorrectly required to own an Ariadne workspace receipt

The first pre-dispatch receipt treated the externally controlled native Harness
as an Ariadne assigned worker slot and failed `workspace_receipt_missing`.
Removing that false ownership claim preserved the Harness as external evidence.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1068 — External native Harness was incorrectly required to sit at the handoff ref

The next pre-dispatch receipt retained the same incorrect assigned-slot model
and failed `workspace_not_at_handoff`. The final receipt represented only real
Ariadne slots and passed before the occupied session.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1069 — PowerShell regex quoting changed a source-inspection token into a command

A read-only source inspection used the wrong PowerShell quoting, so `read` was
interpreted as a cmdlet. A single-quoted literal pattern produced the intended
inspection without changing state.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1070 — Recursive cleanup command was rejected before execution

The first disposable-root cleanup request used a recursive command shape that
the tool policy rejected. No deletion occurred. Cleanup proceeded only after
an exact parent/name assertion.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1071 — Existing cleanup helper did not match the task-specific attempt root

The accepted general cleanup helper did not own this coordinator's exact root
layout and refused it. An exact asserted deletion removed only the named
disposable root and subsequent readback proved its absence.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1072 — Coordinator omitted the broker's textual rejection reason

The coordinator retained terminal status and request counts but not the
broker-rejection reason event. The exact seven-tool request header was read
structurally before cleanup and pinned package/broker source confirmed the
mismatch. The trace is attributable but is not scored complete.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1073 — Stock headless tool suite exceeded the exact broker allowlist

The occupied request declared seven tools while the broker permitted exactly
three, producing one fail-closed HTTP 400 rejection before provider I/O. The
native lane ended under the pragmatic stop rule and Sol recovered the real
source task; no new runner or broader broker was introduced.

Origin: harness. Severity: moderate. Status: corrected and contained.

## AER-1074 — Oversized Pytest parameter became an unsafe test identity

A 32-KiB bytes parameter was embedded directly into a parameterized test ID,
causing two repository test-setup errors before assertions. Compact explicit
IDs retained the same size-boundary cases and passed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1075 — Ambient-capability guard matched a harmless substring

The first static guard searched for `environ`, which also appears in the word
`environment`, and rejected the safe module. Restricting the check to actual
ambient-access spellings such as `os.environ` removed the false positive.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1076 — Historical no-app-change tripwire contradicted its authorized descendant

The accepted gap-decomposition test permanently denied every later `app/**`
change, including the exact unmounted normalizer it had identified as future
work. The test and plan now permit only that named service file while retaining
all route, API Spine, Diary, sidebar and environment-file denials.

Origin: repository. Severity: moderate. Status: corrected and contained.

## AER-1077 — Unhashable enum-shaped YAML could escape typed denial

Source review found that a list or mapping supplied for two closed string enums
could raise during set membership. Explicit string checks and adversarial tests
now convert both forms to `manifest_shape_invalid` without exception.

Origin: repository. Severity: moderate. Status: corrected and contained.

## AER-1078 — Serial Pytest wrapper omitted its remainder separator

The first final-suite invocation omitted `--` before Pytest arguments, so the
wrapper rejected `-q` without running tests. The corrected invocation acquired
the serial lock and passed all 149 tests.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1079 — Paired incident observations reused one attempt key

The first clockwork dry-run rejected two paired incident groups because each
group reused an `attempt_key`; the v2 intent requires observation keys to be
unique even when higher-level incidents are related. Unique keys were assigned
and the rejected intent hash was retained. No canonical surface changed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1080 — Ad hoc contract-evidence row lacked the graph evidence identifier

The second clockwork dry-run rejected an ad hoc path/status row in
`contract_evidence`, whose graph schema requires typed evidence identifiers.
The contract was already bound through ordinary node evidence, so the graph
field was restored to the accepted empty form. No canonical surface changed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1081 — Invalid Windows wildcard recurred during closeout diagnosis

A read-only diagnostic search again passed a wildcard as a Windows path and
ripgrep rejected it. The corrected search used the Continuity directory with a
filename glob filter and located the required examples without mutation.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1082 — Current-node Markdown omitted required Brisbane Timestamp headers

The first live publication passed the clockwork transaction but the
postpublication baton-consistency test found that the current closeout, Sol
acceptance and Yuri summary lacked their required top-level Brisbane
`Timestamp:` headers. The clockwork rolled back byte-exactly, the three headers
were added, and the corrected source was prepared for a fresh dry-run and
publication.

Origin: operator. Severity: moderate. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,082 corrected or contained incidents and
zero open incidents after clockwork publication. The native Harness terminal
was a deterministic pre-provider tool-contract rejection rather than an
untraceable model failure. The remaining rows are bounded preparation,
inspection, cleanup and deterministic-verification corrections; none opened a
secret, provider payload, database, product route, ordinary-practice admission,
deployment, Pages action or protected ref. The matched reading supports lean
monitored native-Harness use, not another generic qualification programme.
