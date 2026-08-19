# Threat-model delta — clockwork live canonical adoption and retirement

Date: 2026-08-19
Timestamp: 2026-08-19T12:41:00.9132105+10:00 (Australia/Brisbane)

**Operation:** `ariadne-provider-free-clockwork-live-canonical-adoption-retirement`

## Scope

This delta covers one provider-free task-branch adoption of the clockwork as the sole repository-governance closeout publisher. It covers the canonical authority files, writer retirement guard, generation pointer, pre-pointer recovery and disposable rollback. It grants no product, provider, deployment, release, Pages or protected-ref authority.

## Protected assets

- the exact seven canonical authority-file bytes and their semantic relation;
- the full 40-character task source and four protected-ref readings;
- the immutable pre-adoption Git generation and rollback availability;
- one-writer ownership, lease sequence, generation digest and pointer;
- accepted historical scripts and evidence retained without publication authority;
- all untracked files, especially `docs/branding/`;
- honest live-adoption and first-closeout efficacy readings.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Two accepted writers during cutover | One exclusive lease; staged full generation; ownership pointer installed last; direct legacy updater guard becomes active with the pointer. |
| Partial canonical materialization | Private byte backup; fault-injected replacement; every pre-pointer failure restores and rereads all seven previous bytes before lease release. |
| Pointer selects incomplete or mismatched files | Pointer binds all ten file digests; active-state validation rereads every canonical and metadata surface before success. |
| Post-pointer exception reported as failure | Classify committed only when full active generation rereads; otherwise terminal corruption and no acceptance. |
| Stale or replayed writer | Lease binds operation, full source, previous generation and sequence; stale token/source/generation fails before staging. |
| Abbreviated or caller-authored Git source | Git resolver obtains `HEAD`; schema excludes source fields from intent; full `^[0-9a-f]{40}$` validation and ancestry checks. |
| Protected-ref drift | All four refs are read before preparation and immediately before pointer commit and must equal `2e34bdad732fdab32fbf778280b3d3c70d66d602`. |
| Rollback bytes unavailable | Previous generation binds the full reviewed implementation-candidate Git source and per-file hashes; disposable rollback uses `git show <full-object>:<exact-path>` and rereads every byte. |
| Destructive retirement erases evidence | Historical updaters remain committed; retirement removes publication authority through a central direct-execution guard and ownership gate only. |
| One of 145 updaters bypasses the guard | Frozen inventory classifies all files; 137 share the Compass entry guard and eight old entry points receive the same guard; coverage test fails on any unclassified updater. |
| Manual baton/latch/register edit bypasses writer guard | Canonical-state validator compares each file to the selected generation manifest; any drift blocks acceptance, commit and push. |
| Caller copies counts, revisions or paths | Strict intent contains no derived fields; graph/Compass/register/Git readings, output paths and digests are engine-derived. |
| Clean closeout invents register activity | Clean-closeout mode preserves register and pattern bytes exactly; any count/revision or byte drift rejects publication. |
| AGENTS and Compass disagree | Typed Current Baton rows and full Compass are generated from the same prospective transaction; consistency tests run before pointer installation. |
| Mutable current fixture contaminates rollback | Previous bytes come from the exact full reviewed implementation-candidate Git object, which must descend from initial source `a6129d9a0c391314691cb73b28a5f21f1e834654`, not from a later mutable worktree reading. |
| Provider or product scope leaks through the adoption | Contract allowlists only repository-governance paths and provider-free commands; all product/data/runtime/deployment/protected surfaces remain in the latch's closed boundary. |
| Untracked evidence is overwritten | Exact path allowlist excludes `docs/branding/` and every untracked path; pre/post inventory verifies preservation. |
| Efficiency claim hides adoption cost | Construction reruns, closeout reruns, guard trips and future three-closeout readings are separate evidence; no amortised acceptance shortcut. |

## Security acceptance

Acceptance requires one active owner for ten surfaces, four retired legacy classes, complete 145-file guard coverage, zero unclassified publisher, zero path escape, zero protected-ref drift, exact pre-pointer restoration at every injected fault, byte-exact disposable rollback, successful full-state reread after activation, unchanged untracked files and a fresh exact-candidate veto. Any ambiguity is `revision_required`.
