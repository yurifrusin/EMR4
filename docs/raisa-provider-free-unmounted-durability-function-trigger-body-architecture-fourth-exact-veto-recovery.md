# Durability function-and-trigger-body fourth exact-veto recovery

Date: 2026-08-08

Status: replacement built with 339-test deterministic acceptance complete;
fresh clean exact-HEAD independent veto pending

Rejected candidate HEAD:
`0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d`

Rejected candidate contract:
`sha256:c8d27c85def134056598be7ef12cda3ae7b509b3d06b16a536459baea51bc24b`

Independent veto:
`orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-final-independent-veto.md`

Immutable parent contract:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

Replacement candidate contract:
`sha256:f71287f266a3252d2a0736e511287600939a40bc70397710600c12581e24d4f3`

## Recovery classification

The sixth body candidate remains rejected despite Sol's complete 305-test pass
and the survival of R6A–R6D under independent challenge. Fresh exact-HEAD
review found one P1: the key-rotation producer locked the right anchor row but
did not reverify its contents before using its digest to author the next
lifecycle revision.

The fourth recovery adds only the missing parent-bound rotation fence. It does
not weaken any earlier recovery and changes no API Spine, provider, data,
runtime, database, DDL, command, deployment or protected boundary.

## R7A — exact rotation-entry anchor fence

On the new-effect branch of `rotate_observation_key_v1`, immediately after
locking the one current anchor and before locking the prior key or performing
any effect, one `F_ANCHOR` assertion must independently prove:

- anchor `checkpoint_state` equals the locked checkpoint state;
- anchor `last_contiguous_position` equals the locked checkpoint position;
- anchor `last_observation_digest` equals the locked checkpoint observation
  digest;
- anchor `checkpoint_integrity_digest` equals the locked checkpoint integrity
  digest; and
- every anchor controlling digest—policy, principal, binding, source,
  registry, impact and key schedule—equals the corresponding locked generation
  digest.

The anchor locator already fixes exact practice/source/stream/epoch,
observer/generation and checkpoint lifecycle revision. Locator equality or the
stored `anchor_digest` alone is insufficient. Only after the field-complete
assertion may the body lock the prior key, validate the future interval and use
the verified anchor digest in `key_rotation_digest_v1`.

Exact replay of an already stored identical key interval remains inert and is
not a new rotation; it must not acquire the new-effect anchor/key locks or
rewrite lifecycle state.

## Hostile acceptance

Focused candidate-independent tests must enumerate the exact rotation branch
and reject, after resealing, removal or substitution of each checkpoint field
and each of the seven controlling-digest equalities. They must also reject a
wrong relation, row symbol, comparison operator, assertion failure class,
assertion moved after the first effect, or digest use before the assertion.

The replacement must pass every inherited body, API Spine, AER and standing
continuation test; builder `--check`; Ruff; `git diff --check`; explicit-path
worktree guards; and a fresh clean exact-HEAD independent veto. Candidate
`0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d` is immutable rejection evidence
and cannot become accepted source.

## Closed boundary

This remains pure, provider-free, unmounted and repository-local. It renders or
executes no SQL/DDL; creates no migration, database object or operational
state; opens no database/source/feed/watcher/listener, product/patient read,
provider, command, runtime, credential, deployment, production, release, Pages
or protected-ref authority.
