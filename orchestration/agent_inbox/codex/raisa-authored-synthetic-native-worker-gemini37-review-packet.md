# Gemini 3.7 Flash/high semantic veto — bounded native DeepSeek worker

Date: 2026-08-20

Review only. GPT Sol owns implementation, deterministic execution, recovery,
acceptance, clockwork and Git. The deterministic command ledger owns command
results. This call owns semantic and containment judgment only and must not
launch the native Harness or DeepSeek.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\gemini37-synthetic-native-worker-veto-001`
- Branch: `codex/review-synthetic-native-worker-0c93f7a2`
- Candidate HEAD: `0c93f7a24e0e12fe518b3927bd67db6c28b83d27`
- Frozen plan source: `5df7f2f494b6253e66ab91742495373a6c149aa5`
- Model/effort: `gemini-3.7-flash-high` / `high`

Read `AGENTS.md` completely, restore the five named sources, validate the active
latch and protected boundaries, then inspect only the exact allowlist. DeepSeek
is reserved for a later independently checkpointed one-edit run. Native
subagents are declined under developer policy. No native process, agent
session, worker turn, model request or DeepSeek provider request is admitted
during this review.

## Review question

Return `pass` only if the candidate safely admits exactly one later
authored-synthetic non-product worker edit through the accepted rc.7 preset and
exact `edit`, `glob`, `read` projection, while mechanically enforcing one
provider request, one native process, zero automatic retries, zero fallbacks,
zero auxiliary model calls and immutable terminal/cleanup evidence. Challenge:

- whether the complete baseline prompt plus successful exact-path `edit`
  `concludesTurn` hook really stops the upstream agent loop without a second
  provider request;
- whether the broker rejects a second completion before upstream transit;
- whether pre- and post-tool controls fail closed for multiple, nested,
  off-path, replace-all, errored or unaccepted calls;
- whether the exact expected source bytes and public plus holdback cases prevent
  a plausible-but-wrong patch from passing;
- whether the worker receives no provider credential and has no shell, test,
  Git, database, product, data or fallback surface;
- whether review, fresh disposable-root preparation and a separate committed
  checkpoint all precede the only occupied process;
- whether preparation remains bound to the full exact reviewed Git commit even
  after the review receipt becomes a descendant commit;
- whether request/tool/terminal evidence is sufficient to distinguish success,
  refusal, timeout, crash, over-call and boundary violation without retaining
  raw prompt, response, reasoning or credentials; and
- whether exact root cleanup preserves every user-owned or unrelated path.

Return `revision_required` with exact allowlisted evidence for any P0-P2 issue.
Do not rely on test names or documentation claims where the implementation can
be inspected.

## Exact allowlist

- `AGENTS.md`
- `docs/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal-plan.md`
- `docs/security/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal-threat-model-delta.md`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/contract.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/contract.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/deterministic-evidence.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/deterministic-evidence.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/deterministic-report.md`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/occupied-terminal.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal/candidate-command-validation-receipt-v3.json`
- `scripts/raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py`
- `scripts/ariadne_deepseek_native_harness_broker.mjs`
- `scripts/raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal.py`
- `scripts/deepseek_native_harness_provider_free_effective_tool_composition_guard.mjs`
- `tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py`
- `tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal_plan.py`
- `tests/test_ariadne_deepseek_native_harness_broker.py`
- Exact Git diff `5df7f2f494b6253e66ab91742495373a6c149aa5..0c93f7a24e0e12fe518b3927bd67db6c28b83d27`

Do not inspect branding or unrelated files. Do not edit, format, commit, push,
install, prepare the attempt, create the checkpoint, execute `--native`, launch
Harness, call DeepSeek, invoke Docker or a database, access product/protected
data, deploy, release, rebuild Pages or move any protected ref.
