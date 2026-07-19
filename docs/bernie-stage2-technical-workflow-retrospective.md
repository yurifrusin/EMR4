# Bernie Stage 2 Technical and Workflow Retrospective

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision: `recommendations_approved_and_implemented_pending_protected_integration`

Execution record:
`docs/bernie-stage2-technical-maintenance-closeout.md` and
`orchestration/agent_inbox/codex/stage2-technical-maintenance-sol-acceptance.md`.
The production database-role/GUC and field-encryption recommendation remains
deferred to a future production-planning decision.

## Outcome

Stage 2's product result remains final `stage2_pass`. This retrospective records
technical/process improvements exposed by the tranche without reopening it or
silently changing repository settings, dependencies, authority, or Stage 3.

## 1. GitHub auto-merge

### Observed state

- repository `allow_auto_merge` is `false`;
- `master` requires four strict current-head checks;
- conversation resolution and linear history are required;
- branch protection is enforced for administrators; and
- force-push and deletion are disabled.

PR 38 had green checks but could neither merge immediately nor queue because
auto-merge was disabled. Its three Advanced Security conversations correctly
blocked merge until bounded fixes landed and GitHub resolved the threads.

### Recommendation

Enable repository auto-merge, but keep it opt-in per PR and use squash merge for
accepted tranches. Sol should request auto-merge only after acceptance, exact
scope review, and a passed pre-push receipt. Existing strict checks and required
conversation resolution must remain unchanged.

This would remove idle orchestration time without weakening a gate: PR 38 would
still have waited for its review fixes and fresh CodeQL pass. Do not use admin
bypass as a substitute.

Changing the repository setting is a small external policy mutation and should
be executed only after Yuri explicitly accepts this recommendation.

## 2. Ruff and reproducible developer tooling

### Observed state

- Ruff is absent from the project `.venv`;
- it is not declared in `requirements.txt` or `pyproject.toml`;
- no `requirements-dev.txt`, `.pre-commit-config.yaml`, or `uv.lock` exists; and
- the Python Security workflow installs `pip-audit` and Bandit, but no Python
  correctness/style linter.

The missing Ruff tool did not invalidate Stage 2. CodeQL caught one unused test
import, while two empty-except observations required explanatory comments.
Default Ruff rules would have caught the unused import; CodeQL remains necessary
for the exception-flow review.

### Recommendation

Add Ruff in a bounded tooling tranche, not as an unrecorded local `pip install`:

1. introduce a pinned development-tool dependency source;
2. configure a deliberately small clean initial rule set in `pyproject.toml`,
   beginning with syntax/error and unused-import rules;
3. run the same command locally and in CI;
4. establish a clean baseline before making the lint context required; and
5. expand rules only through reviewed, non-mechanical churn.

Do not add Ruff to production `requirements.txt` merely to make it available to
developers. The exact version and dependency format should be frozen when the
tooling tranche begins.

## 3. Sol Extra High ownership

Stage 2's Sol-only execution was deliberate, not an accidental failure to
delegate. The tranche combined one mutable PostgreSQL lifecycle, Alembic
upgrade/downgrade evidence, ORM constraints, RLS, runtime transaction ordering,
failure injection, API contracts, security acceptance, GitHub review recovery,
and protected integration. These were tightly coupled and serial. Preparing and
reconciling worker packets would probably have cost more than direct execution.

The result supports a **Sol-first adaptive single-thread** default for similarly
coupled tranches:

- use Extra High for architecture, acceptance meaning, security/privacy,
  authority, migration, and contradictory-evidence decisions;
- spend less deliberation on frozen mechanical edits and deterministic reruns
  while retaining one coherent context and owner;
- use checkpoints, receipts, durable closeouts, and fresh acceptance contexts
  to control context growth;
- delegate only genuinely separable mechanical artifacts whose briefing and
  review cost is lower than direct work; and
- retain independent machine or human/model vetoes where independence adds
  safety value.

Lower-cost workers remain useful for stable fixture generation, contained test
authoring, or independent reproduction. They should not be dispatched merely
to create parallel activity, and they do not receive acceptance or integration
authority.

## 4. Additional bounded maintenance candidates

These are recommendations, not current authority:

1. **Repair the historical empty-database Alembic chain.** A truly empty
   database stops in pre-Stage-2 migration `d4787...`; current-head
   upgrade/downgrade evidence still passed. Repair would improve onboarding and
   ephemeral CI database creation.
2. **Create one canonical verification entry point.** Encode focused pytest,
   API Spine, handover, Bandit, leakage, compile, and syntax commands so local
   and CI evidence cannot drift.
3. **Make receipt line endings deterministic.** Generated JSON produced CRLF/LF
   normalization warnings; write canonical LF bytes so recorded hashes match
   Git content consistently across Windows and CI.
4. **Standardize outer test timeouts.** The 100-node Stage 2 suite completed in
   49.7 seconds but first hit a 60-second wrapper limit. Use risk-proportional
   timeout margins and preserve actual pytest failure separately from launcher
   timeout.
5. **Design the production database role before production.** Stage 2 proved
   RLS with a restricted role but did not provision a production runtime role
   or prevent arbitrary tenant-GUC selection by compromised SQL.

Recommended order if Yuri opens a maintenance tranche:

1. Ruff/developer-tool parity;
2. auto-merge repository setting;
3. canonical verification and receipt normalization;
4. historical empty-database migration repair; and
5. production database-role design only when production planning is authorized.
