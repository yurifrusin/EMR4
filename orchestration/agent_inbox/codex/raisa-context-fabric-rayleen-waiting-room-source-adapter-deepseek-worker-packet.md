# DeepSeek worker packet: Rayleen waiting-room Context Fabric source adapter

Decision format: implementation candidate only; never acceptance.

## Exact lease

- Worker: DeepSeek V4 Flash/high through Claude Code `--bare`.
- Worktree: `C:\Users\sarashera\EMR4-worktrees\context-fabric-rayleen-source-adapter-worker`.
- Branch: `codex/context-fabric-rayleen-source-adapter-worker`.
- Exact source HEAD: `1f008abf806c27c7e37251384f846a4a513dbad5`.
- Rehydrate completely from `AGENTS.md`, the frozen plan, design, threat delta,
  accepted Current-weave design/module/tests, and A4 serialized-frame schema
  before editing.

## Objective

Implement the frozen plan exactly. Build one pure provider-free unmounted
adapter from a closed serialized authored-synthetic
`emr4.waiting_room_context_frame.v1` plus the already accepted sealed Current
binding/grant and a sealed backend-authored complete alias manifest to one
sealed `current_waiting_room_projection` source envelope. Replace only the
hand-authored waiting source in the accepted four-source synthetic packet and
prove the existing assembler and same-packet proofreader still release.

## Owned files

You may create or modify only:

- `scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py`;
- `scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter_acceptance.py`;
- `scripts/raisa_provider_free_practice_context_fabric_current_operational_weave.py` only for the smallest optional-derived-field compatibility change described by the plan;
- `tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py`;
- `tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py` only if a focused regression is necessary for that compatibility change;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/adapter-result.schema.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/authored-synthetic-waiting-room-frame.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter/provider-free-acceptance-evidence.json`;
- `orchestration/agent_inbox/deepseek/raisa-context-fabric-rayleen-waiting-room-source-adapter-worker-receipt.json`.

Do not edit the frozen plan, design, threat delta, AGENTS, implementation plan,
other documentation, other evidence, API routes, app code or harness settings.

## Required implementation properties

1. Reuse canonical `seal`, `verify_seal`, hashing and the accepted Current
   binding/grant/source constants. Do not weaken or fork parent authority.
2. Validate the A4 input against the exact accepted recursive JSON Schema using
   the repository dependency; reject all extra/invalid nested fields.
3. Admit exact Rayleen/current-operational/waiting-source scope, Receptionist
   role, current binding/grant/session and all-false authority before reading
   source payload values.
4. Define and verify a recursively closed sealed alias manifest. It must bind
   the exact canonical source-frame digest plus binding/grant/session digests,
   exact source practice/location, Fabric practice/location refs, expiry and
   complete one-to-one appointment/practitioner aliases. Reject missing,
   duplicate, unrelated or raw-UUID aliases.
5. Verify frame/fact/signal coordinates, A4 TTL <=120 seconds, unique facts,
   unique signal kinds, no orphans, exact nested labels and closed values.
6. Recompute elapsed minutes, threshold bands, missing-arrival/overdue
   exceptions and longest-wait ranks; require the complete supplied signal set
   to match exact recomputation. Do not invent missing elapsed/threshold data.
7. Output no patient display token, raw UUID, source label id, scheduled/arrival
   timestamp or excluded field class. Canonically scan the released envelope
   and trace for every raw source identifier/token and fail if found.
8. Preserve observation and source revision. Expiry is the minimum of source,
   binding, grant and manifest; never extend. Enforce frozen cardinality and
   canonical-byte limits.
9. The output source envelope must use the existing Current weave exact source
   triple/evidence/data labels and be accepted when substituted into the
   canonical four-source packet. Modify `_project_waiting` only as needed to
   omit unavailable optional derived fields rather than index them.
10. The pure adapter path performs zero provider/network/database/filesystem
    write/subprocess/API/command/deployment/protected actions. The acceptance
    generator alone writes its two owned canonical artifacts atomically.

## Tests

Use the exact root interpreter:
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe`.

At minimum run serially:

- the new focused test file;
- `tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py`;
- `tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py`;
- `tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py`;
- `tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py`;
- API Spine regression tests relevant to no new GraphQL/REST command surface;
- Ruff/compile and `git diff --check`.

The acceptance evidence must record exact hashes, test counts, zero-call/action
posture, source/output digests, parent proofreader `RELEASE`, and the strict
claim boundary. It must validate against the new closed schema.

## Forbidden surfaces

No patient/clinical/product-derived/financial/protected/historical-PHI data; no
real DB/session/feed/watcher; no provider or network; no product route/runtime;
no command/write; no app or Diary UI change; no deployment/production/release/
Pages; no protected evidence or protected-ref movement; no reading or staging
`docs/branding/` or unrelated untracked files. Do not use `git add .` or
`git add -A`.

## Handoff

Run the required tests, stage only the explicit owned paths, commit on the
worker branch with message `Implement Rayleen Context Fabric source adapter`,
and leave the worktree tracked-clean. The receipt must state exact source and
candidate HEADs, changed paths, commands/counts, evidence hash, any limitation,
and `decision: candidate_for_sol_review`.
