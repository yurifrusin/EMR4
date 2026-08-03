# Davida Practice-Administration Architecture — DeepSeek Worker Packet

Source head: `bb8a6f554b417df019727345ba91a7d555b0bd41`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-practice-administration-architecture`

Branch: `codex/davida-practice-administration-architecture`

Model/transport: DeepSeek V4 Flash/high through Claude Code `--bare` only.
DeepSeek Pro and every fallback are forbidden.

## Mandatory rehydration

Before editing, read `AGENTS.md` completely and produce a fresh five-source
rehydration statement naming exactly:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

Read the complete EMR4 API Steward skill and its review checklist. Verify this
exact branch, clean worktree, source head and protected-ref boundary. A compacted
or inherited summary is not authoritative.

## Task

Design the first bounded Davida lane descendant: an architecture-only,
provider-free, non-executing practice-administration boundary. Davida is the
custodian interface for relatively stable institutional knowledge, never the
owner of database truth or an autonomous database actor.

Specify separate Davida and Bernie work-cell/container identities with a shared
mechanical kernel and separate immutable policies. Davida may interpret
natural-language intent in a future sandbox, but only typed candidates may
cross into deterministic validation and existing backend-owned command paths.

## Permitted reads

Read only these task inputs and the exact adjacent sources named here:

- `AGENTS.md`;
- `docs/bernie-davida-parallel-seam-plan.md`;
- `docs/bernie-davida-shared-agent-boundary.md`;
- `docs/security/bernie-davida-parallel-seam-threat-model-delta.md`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json`;
- `docs/ariadne-bounded-cognitive-work-cell-proofreader-gate-plan.md`;
- `docs/api-spine/manifests/agent-capability-charters.yaml`, limited to the
  existing declarative agent-boundary patterns;
- `docs/api-spine/manifests/application-auth-policies.yaml`, limited to
  practice-scoped read/proposal/confirmation separation patterns;
- `docs/api-spine/graphql/schema.graphql`, limited to current practitioner,
  location, room and waiting-list read surfaces;
- current room and waiting-list GET router implementations, limited to proving
  whether they normalize or commit during reads;
- the current active-practitioner read router/service used by the accepted
  practitioner directory bridge;
- `tests/test_bernie_davida_parallel_seam.py`; and
- this packet.

Do not perform broad repository discovery or inspect protected/historical
evidence.

## Owned files

- `docs/davida-practice-administration-boundary-plan.md`
- `docs/davida-practice-administration-boundary-design.md`
- `docs/security/davida-practice-administration-boundary-threat-model-delta.md`
- `orchestration/continuity/davida-practice-administration-boundary/capability-contract.json`
- `orchestration/continuity/davida-practice-administration-boundary/capability-contract.schema.json`
- `tests/test_davida_practice_administration_boundary.py`

Do not edit any other file. In particular, do not edit `AGENTS.md`,
`docs/branding/`, application/runtime code, routers, models, migrations,
`app/main.py`, API Spine artifacts, shared auth, existing agent charters,
workflows, harness settings, protected evidence, or other agents' files.

## Required contract

- Separate authoritative truth, advisory interpretation, session/context state
  and declarative manifest policy. Database truth remains authoritative.
- Define Davida as a separate cell/container/agent identity from Bernie. Share
  only a provider-neutral mechanical kernel, typed envelopes, deterministic
  proofreader primitives and audit vocabulary; policies, scopes, memory and
  credentials do not cross.
- Davida receives no database credential, ORM session, generic database client,
  GraphQL mutation, REST command credential or event actuator.
- Define an exact read/context-desk pattern. Current active-practitioner data is
  eligible only through the existing pure practice-scoped read. A future active
  location source must be a pure projection before admission.
- Explicitly block the current room and waiting-list GET paths from Davida when
  inspection proves they normalize or commit during a nominal read.
- Provide a closed operation enum for the first safe administrative domain.
  Unknown operations fail closed.
- Davida may emit typed advisory drafts and proposal candidates only. It never
  emits human confirmation, a signed command, `writes_authorized=true`, or a
  release envelope that can mutate state.
- Describe future backend-owned REST proposal and confirmation envelopes with
  practice binding, actor/session binding, candidate hash, expiry,
  idempotency, optimistic concurrency/precondition, least-privilege
  authorization and audit fields. The backend constructs command authority only
  after explicit human confirmation.
- Events are hints that can request a fresh authorized read; their payloads are
  never truth or commands.
- Name a conservative four-tranche sequence after this architecture: pure read
  projections, provider-free typed interpretation/proofreading, one bounded
  proposal path, then one separately authorised confirmed write vertical.
- Keep providers, real identity, patient/clinical data, autonomous writes,
  deployment, production and release closed. Make no runtime claim.
- Conform to the API Spine: GraphQL remains scoped read-only, REST/OpenAPI owns
  any future writes, events never carry commands, manifests remain declarative
  and context frames remain minimal/non-authoritative.

## Verification and commit

Do not run pytest: the root conductor will serialize all pytest runs because
the repository test bootstrap shares PostgreSQL state. You may run Ruff on the
owned test, `py_compile`, JSON/schema parsing and read-only git diff checks.

Commit only the six owned files. Stage every path explicitly, then verify
`git diff --cached --name-only` contains exactly those paths and no
`docs/branding/` path. Never use `git add -A` or `git add .`. Do not fetch,
merge, rebase, switch branches or push.

Return the five-source statement, changed files, candidate commit hash, static
check results, unresolved blockers, and finish with exactly `DECISION: pass` or
`DECISION: revision_required`.
