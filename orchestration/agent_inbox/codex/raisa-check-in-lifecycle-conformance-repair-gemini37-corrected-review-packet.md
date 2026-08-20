# Corrected Gemini 3.7 Flash/high veto — check-in lifecycle conformance repair

Date: 2026-08-20

This is the one permitted fresh corrected veto after the initial immutable
Gemini receipt at
`orchestration/agent_inbox/antigravity/raisa-check-in-lifecycle-conformance-repair-gemini37-review-receipt.json`
found that the retained Harness root was doubled inside isolated worktrees.
Review only; GPT Sol remains decision owner.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\check-in-lifecycle-gemini-bcd3f594`
- Branch: `codex/review-check-in-lifecycle-bcd3f594`
- HEAD: `7d39641c3170fc0fec76fadce5cd45309bdffdb2`
- Correction base: `0fd047447605d91fbda35c59b0fef711826699ad`
- Correction source: `a425055b3ed2b691e969b4454d33124ba092f016`
- Corrected clockwork checkpoint: `7d39641c3170fc0fec76fadce5cd45309bdffdb2`
- Required model/effort: `gemini-3.7-flash-high` / `high`

First read `AGENTS.md` completely and perform its five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Validate the active latch. Restore DeepSeek as
declined, Gemini as the one selected corrected veto, and native subagents as
declined. Review only.

## Review question

Return `pass` only if the corrected candidate fixes the initial P1 in both the
primary checkout and an isolated worker worktree, all nine exact commands pass,
the immutable failed native terminal is unchanged, and no authority or claim is
widened. A pass accepts the bounded repair and honest negative evidence; it does
not accept native Harness lifecycle success.

## Exact allowlist

Read only `AGENTS.md`, the initial review receipt, these paths, and the exact
`0fd047447605d91fbda35c59b0fef711826699ad..7d39641c3170fc0fec76fadce5cd45309bdffdb2`
diff. Do not enumerate the repository or inspect branding or unrelated paths.

- `orchestration/agent_inbox/antigravity/raisa-check-in-lifecycle-conformance-repair-gemini37-review-receipt.json`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/native-probe-consumed.json`
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/native-probe-terminal.json`
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/repair-evidence.json`
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/repair-report.md`
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/efficacy-reading.json`
- `scripts/raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py`
- `tests/test_raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py`

## Required challenges

1. Verify exact root, branch, full HEAD and clean pre/post state.
2. Confirm `_worker_root()` maps both `C:/Users/sarashera/emr4` and any direct
   child of `C:/Users/sarashera/EMR4-worktrees` to exactly
   `C:/Users/sarashera/EMR4-worktrees`, without a doubled segment.
3. Confirm `NATIVE_INSTALLATION_ROOT` remains that root plus only the exact
   retained installation ID, while the existing exact-root, symlink, lockfile,
   package-version, source-hash and method-shape gates remain unchanged.
4. Confirm the new regression covers primary and isolated worktree shapes and
   C03/C04 now both return zero in the isolated worktree.
5. Confirm the initial Gemini receipt is immutable and no finding is silently
   reclassified or omitted.
6. Confirm consumed/native terminal, evidence and report bytes are unchanged;
   there is no retry, native process, provider call, Docker or database action.
7. Confirm the report still states that the process failed before
   `agents.create` and mount and does not overclaim success.
8. Confirm the corrected clockwork uses machine-resolved full Git IDs and has
   zero canonical drift.
9. Execute exactly the bound nine commands; every exit code must be zero and
   the worktree must remain clean.
10. Confirm no product/API/config/client/flag/allowlist/grammar/waiting-area,
    data, production, deployment, release, Pages or protected-ref change.

## Forbidden actions and decision

Do not edit, format, commit, push, install, launch Harness, retry the consumed
process, call DeepSeek, invoke Docker/database, inspect `docs/branding/`, access
product or protected data, deploy or accept output. Return one schema-constrained
`pass` only if no material P0-P2 finding or command failure remains; otherwise
return `revision_required` with exact allowlisted evidence. Do not emit a second
decision.
