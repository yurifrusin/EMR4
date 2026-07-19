# Bernie Conversational Diary North Star — Extra High Sol Review

Date: 2026-07-19

Reasoning level: `Sol Extra High`

Decision: `strategic_direction_pass_stage3_not_authorized`

## Decision

The user-authorized strategic synthesis passes. EMR4 should pursue the death of
the Diary as an interaction burden, not the death of the Diary as authoritative
software. *bernie* becomes the conversation-first twin of current Diary truth;
the grid becomes optional overview, verification, exception-handling, and
fallback.

This is a product-direction decision only. It does not authorize Stage 3
participants or execution, voice capture, ambient listening, providers, PII,
production, deployment, release, a new appointment action, GraphQL mutation,
or autonomous confirmation.

## Accepted artifacts

| Artifact | SHA-256 | Disposition |
|---|---|---|
| `docs/bernie-conversational-diary-north-star.md` | `b240a07e776300df960b6b99560d808b53fc005883281931fd5f890c096d1ea9` | Product north star |
| `docs/bernie-stage3-conversational-diary-decision.md` | `7c5dd96d949e789f777a55be60099efe11b8d10a1dbdb1af23ab2fef8fbaccab` | Reshaped decision, not authorization |
| `docs/bernie-stage2-technical-workflow-retrospective.md` | `51022d8d045326e1a33385e89349875caf385ad4e78c958b72a98ef58e97dfd3` | Tooling/workflow recommendations only |

The fresh rehydration and pre-plan receipts both pass with SHA-256
`e1863f6c84cf52a186e24127dd7e9151c8c5c43dcd9140eae9467a96ebcb57e9`.
The verifier-acceptance receipt passes with SHA-256
`12c736eae8d10fb174933ae717527ff372cb88ed291d65a6c79e318db1f76f82`.
The integration and pre-commit receipts pass with SHA-256 values
`9b589c638bcabe034603df62972da9ea015b17a2e650453510b62d7727a95be8`
and `451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`.
Every receipt names all five required rehydration sources.

Before this branch, `HEAD`, `master`, `handoff/current`, `origin/master`, and
`origin/handoff/current` were clean and aligned at
`ea5299cc7ecdd8abf764f12a42f17f91b13f17b1`.

## API Spine disposition

- Boundary classification: receptionist read/context product strategy plus the
  existing appointment-create confirmation command.
- Accepted pattern: practice-scoped read frames for questions; typed REST
  commands for auditable effects; events for committed change; PostgreSQL for
  authority.
- Required safety: explicit staff confirmation, current backend revalidation,
  idempotency, audit, receipts, tenant isolation, and answer/proposal/committed
  labels.
- Gates avoided: GraphQL mutation, provider invocation, model-to-database
  writes, broad Diary/context exposure, PII, ambient audio, production, and new
  action families.

## Reshaped Stage 3 decision

Stage 3 should test grid-free conversational work, not merely comprehension of
the existing booking form. The recommended study is local, synthetic,
provider-disabled, supervised, typed-first, and evidence-first. Yuri must still
decide participants, task/comparison protocol, thresholds, modality,
observation retention, and correction authority before execution.

Post-Stage-3 work is conditional on observed evidence: deepen read frames,
authorize one valuable missing command, address one measured language gap,
test explicit voice activation, design event-driven awareness, or stop.

## Technical decisions

1. **Auto-merge:** recommend enabling repository auto-merge as opt-in only
   after acceptance. Keep strict current-head checks, conversation resolution,
   enforced admins, linear history, and no force/delete unchanged. No setting
   changed here.
2. **Ruff:** recommend a separate bounded tooling tranche with a pinned dev
   dependency, `pyproject.toml` configuration, local/CI parity, and a clean
   initial baseline. Do not install it ad hoc or add it to production runtime
   dependencies. No package changed here.
3. **Sol Extra High:** Stage 2's single-thread ownership was deliberate and
   efficient because its database, migration, transaction, runtime, acceptance,
   and integration lifecycle was tightly coupled. Use this Sol-first adaptive
   pattern for similar work; delegate only when separability or independent
   review creates more value than briefing and reconciliation cost.

Additional maintenance candidates are the historical empty-database migration
chain, one canonical verification entry point, deterministic receipt line
endings, risk-proportional test-wrapper timeouts, and a future production
database-role/GUC design.

## Verification and handoff

The handover and API Spine artifact population passes `36/36`, `AGENTS.md`
remains below its compactness limit at 437 lines, and `git diff --check` passes.
No protected evidence, historical Diary content, external corpus, provider,
cloud, PII, production, deployment, release, or product runtime was used.

The engine remains paused. The next product work is a new Yuri decision on the
six Stage 3 protocol points; the tooling recommendations may instead be opened
as a separate maintenance tranche without authorizing Stage 3.
