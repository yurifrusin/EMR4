# Independent veto packet: Rayleen source-adapter result-closure repair

Date: 2026-08-06

Review only the exact immutable repair candidate below. Do not edit any file or
implement a repair.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r2`.
- Branch: `codex/review-context-fabric-rayleen-source-adapter-1663d6d1`.
- Required HEAD: `1663d6d1cc79ebc8f2cb15446d6fa61196bd4fe8`.
- Frozen planning source: `1f008abf806c27c7e37251384f846a4a513dbad5`.
- Rejected candidate: `3edbe828fa1f261e59b8478db79d80e4c291cbbc`.
- The worktree must remain tracked-clean and unchanged.

## Prior veto to reproduce

The first independent fallback veto returned `revision_required`: the file
named `adapter-result.schema.json` actually described only acceptance evidence.
A resealed unknown source-envelope property crossed into the unchanged parent
assembler and the final projector merely discarded it. A narrow grant also
left ungranted optional waiting fields in the pre-projection envelope.

## Review objective

Determine whether `3edbe828..1663d6d1` closes that exact defect without
broadening the frozen pure/unmounted/authored-synthetic boundary. Review the
complete repair and especially:

- the distinct recursively closed `adapter-result.schema.json` and
  `acceptance-evidence.schema.json`;
- `validate_waiting_room_source_adapter_result` and
  `extract_waiting_room_source_envelope`;
- seal verification and cross-link, count, time, TTL, uniqueness and closed
  wait/threshold/exception checks;
- effective-grant minimization in `_build_entries`;
- the acceptance generator's use of the extractor rather than direct nested
  result access;
- adversarial resealed outer/nested/boolean-as-integer tests;
- 15/15 regenerated evidence and exact on-disk fixture hash; and
- AER-0039/AER-0040 containment without treating the ordinary candidate defect
  as an agent incident.

Adversarially attempt unknown properties at every result/envelope/payload/
entry/trace layer, missing/extra required fields, Python booleans in integer
positions, mismatched but individually resealed nested digests/ids/counts/time,
duplicate appointment references, inconsistent derived values and a narrow
field grant. Any mutated result must fail before an envelope is supplied to the
parent assembler.

Verify that the accepted Current-weave module/evidence remain byte-identical,
that the positive extractor-built source alone replaces the hand-authored
waiting source and parent proofreading returns `RELEASE`, and that no `app/**`,
Diary UI, GraphQL/REST route, database, watcher, provider, event transport,
command, deployment, Pages or protected-ref surface was added.

Using `C:\Users\sarashera\emr4\.venv\Scripts\python.exe`, you may run
provider-free tests only. At minimum collect and execute serially:

- the 18-test focused source-adapter file;
- the seven-file inherited A4/Context Fabric packet, expected 177 tests; and
- the 43-test Ariadne agent-error register file.

Run only non-regenerative tests and static checks. Do not execute the acceptance
generator in the review worktree because it rewrites timestamped evidence.

Do not access ADC/cloud, call a provider, inspect patient/product/protected data
or `docs/branding/`, deploy, release, rebuild Pages or move refs. Report exact
HEAD/status before and after, commands/counts, findings by severity, claims not
established, and exactly one terminal decision: `pass` or `revision_required`.
