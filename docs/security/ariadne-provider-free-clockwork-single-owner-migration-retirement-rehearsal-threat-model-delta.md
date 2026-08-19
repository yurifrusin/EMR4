# Threat-model delta — clockwork single-owner migration and retirement rehearsal

**Date:** 2026-08-19
**Operation:** `ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal`

## Scope

This delta covers one provider-free canonical-mirror migration from read-only legacy oracle state to exclusive clockwork ownership. It does not authorize canonical repository mutation, provider work, product data or runtime use.

## Protected assets

- exact canonical graph, Compass, latch, error register, pattern report and Current Baton readings;
- full 40-character task source and four protected-ref readings;
- single-writer ownership, lease sequence and immutable generation digests;
- byte-complete prior generation and rollback availability;
- preserved accepted evidence, untracked files and protected refs;
- honest construction/steady-state efficacy measurements.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Dual writers during or after cutover | Exact ownership map; cutover is rejected unless every surface has one owner and all legacy writers are `retired_in_mirror`. |
| Stale or replayed writer | Exclusive lease binds operation, source, previous generation, sequence and ownership digest; stale token or generation fails before staging. |
| Abbreviated or caller-authored Git source | Resolver obtains `HEAD`; schema forbids source fields in intent; exact `^[0-9a-f]{40}$` validation and ancestry checks. |
| Protected-ref drift | All four refs are read immediately before reduction and promotion and must equal `2e34bdad732fdab32fbf778280b3d3c70d66d602`. |
| Partial or mixed generation | Validate all bytes/digests before one atomic pointer replacement; precommit staging is unreachable and removed on failure, while a post-replacement exception is explicitly classified committed and exposes only the complete new generation. |
| Pointer changed without complete generation | Pointer schema binds generation ID, bundle digest, ownership digest and lease sequence; target generation is fully re-read before replacement. |
| Corrupt or unavailable rollback | Generation zero is immutable, complete and digest-bound; rollback revalidates every byte before pointer change. |
| Clean closeout invents an incident | Event-kind contract makes `clean_closeout` preserve register and pattern bytes exactly; any revision/count drift rejects the bundle. |
| Human copies counts/revisions/paths | Exact intent schema contains no such fields and rejects unknown keys; reducer derives all values. |
| Current Baton prose exceeds latch limits or drifts from Compass | Typed baton reading is generated from bounded intent plus derived readings; latch text length and Compass current-position are validated in the same transaction. |
| Mutable-current fixture contaminates historical replay | Generation zero captures immutable bytes and digest before comparison; later live latch state is only an admission guard. |
| Manual exact-test or aggregate fixture drift | Command manifest selects whole named suites and generated aggregates; no manually copied pytest node or count is accepted. |
| Runner returns before final process status | Each command result requires explicit exit status; missing/ongoing session state is terminal failure, never success. |
| Path escape or canonical-file targeting | All output paths are engine-owned relative names under the exact isolated mirror root; resolved containment is checked before every write. |
| Rehearsal mutates current controls | Publisher rejects repository canonical paths and tests byte-snapshot them before and after every successful/failing run. |
| Efficiency claim hides build cost | Construction reruns and projected steady-state reruns are separate immutable evidence fields; no amortised pass condition. |
| Rehearsal evidence duplicates canonical files | Full generations exist only in disposable storage; the retained receipt contains exact file digests, pointer state, ownership and rollback results rather than copied canonical bytes. |

## Security acceptance

Acceptance requires zero path escapes, zero partial generations, zero dual-owned surfaces, zero stale/legacy writer success, byte-exact rollback, unchanged canonical inputs and protected refs, and complete prevention or prepublication rejection of AER-0643 through AER-0651. Any ambiguity is `revision_required`.
