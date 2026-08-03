# Diary Application-Session Architecture — DeepSeek Worker Packet

Source head: `bb8a6f554b417df019727345ba91a7d555b0bd41`

Worktree: `C:\Users\sarashera\EMR4-worktrees\diary-application-session-architecture`

Branch: `codex/diary-application-session-architecture`

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

Design the first bounded Diary lane descendant: an architecture-only,
provider-free, non-executing contract for default-off native-Diary composition
of the already accepted application-session practitioner read.

The contract must preserve the current native Diary behaviour when the feature
is off. It is not a new directory API and is not a general GraphQL migration.
It shares only the lower application-session/product-read authorization bridge
with Office consumers. It must not depend on Bernie, Davida, a probabilistic
work cell, a proofreader, or the Office one-use terminal reload/logout lifecycle.

## Permitted reads

Read only these task inputs and the exact adjacent sources named here:

- `AGENTS.md`;
- `docs/bernie-davida-parallel-seam-plan.md`;
- `docs/bernie-davida-shared-agent-boundary.md`;
- `docs/security/bernie-davida-parallel-seam-threat-model-delta.md`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`;
- `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json`;
- `docs/raisa-provider-free-session-practitioner-directory-read-bridge-plan.md`;
- `docs/raisa-provider-free-office-practitioner-directory-consumer-plan.md`;
- `docs/diary/diary.js`, limited to the existing practitioner read, auth and
  fallback functions needed to bind the static contract;
- `docs/api-spine/graphql/schema.graphql`, limited to
  `Query.practice.practitioners` and the returned display-safe types;
- `docs/api-spine/manifests/application-auth-policies.yaml`, limited to the
  accepted native-Diary application-session/product-read policy identifiers;
- `tests/test_raisa_provider_free_session_practitioner_directory_read_bridge.py`;
- `tests/test_raisa_provider_free_office_practitioner_directory_consumer.py`;
- `tests/test_bernie_davida_parallel_seam.py`; and
- this packet.

Do not perform broad repository discovery or inspect protected/historical
evidence.

## Owned files

- `docs/raisa-provider-free-native-diary-application-session-practitioner-composition-plan.md`
- `docs/raisa-provider-free-native-diary-application-session-practitioner-composition-design.md`
- `docs/security/raisa-provider-free-native-diary-application-session-practitioner-composition-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition/composition-contract.json`
- `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition/composition-contract.schema.json`
- `tests/test_raisa_provider_free_native_diary_application_session_practitioner_composition.py`

Do not edit any other file. In particular, do not edit `AGENTS.md`,
`docs/branding/`, application/runtime code, Diary HTML/JS/CSS, shared auth,
models, migrations, routes, `app/main.py`, API Spine artifacts, manifests,
workflows, harness settings, protected evidence, or other agents' files.

## Required contract

- Bind exactly `Surface.NATIVE_DIARY` and the accepted application-session
  action, policy and resource identifiers from the existing auth bridge.
- Bind the existing read to
  `Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)` and
  only the display-safe shape
  `{id, displayName, roleLabel, active, defaultLocation {id, name}}`.
- Make composition unmounted and default-off. When off, the current bearer-auth
  GraphQL read and its existing REST fallback remain byte-for-byte unmodified
  and behaviourally unchanged.
- Permit only an authenticated, practice-scoped fresh read. Session artifacts,
  authority envelopes and raw identifiers are not UI data.
- Keep Office terminal session consumption/logout/reload behaviour out of the
  native Diary contract.
- Keep providers, probabilistic interpretation, proofreader gates, writes,
  real identity, Microsoft federation, deployment, production and release
  closed.
- Define fail-closed mismatch, stale/superseded response and privacy behaviour,
  deterministic acceptance cases, residual risks and a safe implementation
  handoff. Make no runtime or usability claim.
- Conform to the API Spine: GraphQL remains scoped read-only; no mutation,
  command tunnel, new REST surface or event actuator is introduced.

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
