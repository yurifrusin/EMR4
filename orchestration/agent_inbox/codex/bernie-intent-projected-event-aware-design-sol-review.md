# Bernie Intent-Projected and Event-Aware Diary Design — Sol Review

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision: `design_integration_pass_runtime_not_authorized`

## Decision reviewed

Yuri completed review of the living product notepad and explicitly directed
that all entries be integrated into the overall design. Yuri additionally
decided that low-interruption committed-event awareness is invaluable and must
be foundational to Bernie's Diary twin from the outset.

The accepted unified direction is:

1. the fixed grid becomes an intent-projected family of precise, reversible
   views;
2. the complete fluid UX meta-grid receives a dedicated future visual-design
   tranche, with Claude Fable the current preferred resource only after an
   explicit subscription, cost, synthetic-context, and transmission decision;
   and
3. Bernie is designed with a carefully filtered nervous system connected only
   to committed typed Diary events.

This review accepts product and non-runtime API design only. It does not accept
Stage 3 execution or any event, provider, Fable, PII, production, deployment,
release, or write runtime.

## Canonical artifacts

| Artifact | SHA-256 |
|---|---|
| `docs/bernie-intent-projected-event-aware-diary-design.md` | `da9f2284a452fe6c89d44e1e067d4563131496df36b03ad5570d4a690fca0929` |
| `docs/bernie-conversational-diary-north-star.md` | `c20b33224eab9dbf5b510041a3903557fe437659eda98ef68c66c9010b7a66d6` |
| `docs/bernie-stage3-conversational-diary-decision.md` | `0e7c4fd734a070abef681790d35876d39e38eefd156a53c54cfa95600afef8df` |
| `docs/bernie-product-ideas-notepad.md` | `8e03532a1635f8b7b515c9086e20818409e4a91c718dc2a5b0e8bb3c5325ba85` |
| `implementation_plan.md` | `29d21b5b7d3c0d4048368062fba2a932e650fafdde959308c740fb6c0b9c1cc0` |
| `docs/api-spine/async/integration-events.yaml` | `3fe9b651c52634b4acc97410d07c9e143699fad9ccf404d6e2b116988a0e415e` |
| `docs/api-spine/manifests/agent-capability-charters.yaml` | `fb90edc8582364892a6b3ffff3e4d9354bb34adaa231257f5c9cbc07cbf288aa` |
| `tests/test_api_spine_artifacts.py` | `44a81cd299343b313de198b742a67972549794050602e3b882a5c45b49315fe4` |

## API Spine disposition

Boundary classification:

- intent projection is authorised read context plus reversible local
  presentation state;
- committed Diary events are async observations of completed backend change;
- an event is a signal for a fresh authorised read, not a portable record or
  command grant;
- GraphQL remains a read/context graph with no mutation root;
- all state change remains an explicit REST/OpenAPI command; and
- every follow-up appointment mutation still requires staff confirmation,
  backend revalidation, idempotency, audit, and receipt.

The non-runtime prototypes now require publish-after-commit, transactional
outbox or equivalent, stable event identity, aggregate revision, user-visible
deduplication, fresh scoped reads, deterministic low-interruption filtering,
role/practice/resource rechecks, user attention controls, and no automatic
spoken PHI. They prohibit direct identifiers/free text in the event payload and
mechanically deny event-as-command authority.

## Stage 3 disposition

Stage 3 no longer asks whether intent projection or event awareness is valuable.
It measures safe interaction shape, interruption burden, view correctness, and
implementation order using authored synthetic scenarios.

The six user decisions remain required. Protocol and threshold decisions now
also cover:

- practitioner/date/time and patient-centred projections;
- view refinement and return-to-context;
- relevant committed-event notices;
- suppression of unrelated, foreign, uncommitted, and rolled-back signals;
- replay deduplication and stale/out-of-order reconciliation; and
- dismiss, snooze, mute, explain-why, and show-context behaviour.

The exact relationship between Stage 3 and the deferred fluid UX design tranche
remains part of the protocol decision. Stage 3 execution remains paused.

## Verification

- fresh five-source rehydration receipt: `passed`, SHA-256
  `e1863f6c84cf52a186e24127dd7e9151c8c5c43dcd9140eae9467a96ebcb57e9`;
- fresh five-source pre-acceptance receipt: `passed`, SHA-256
  `ee226aba19816c04c2e70eac5a2751eab6ca24057c767b3d224465c6f44c82a3`;
- fresh five-source pre-commit receipt: `passed`, SHA-256
  `451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`;
- handover plus API Spine artifact population: `41 passed`;
- deterministic committed-event awareness invariants: `5 passed` within that
  population;
- `AGENTS.md`: 437 lines, below the `<500` compactness gate; and
- `git diff --check`: passed.

No protected fixture, holdout, historical Diary material, provider, external
prompt, participant, audio, PII, production system, deployment, release, or
new mutation was accessed or opened.

## Worker and reasoning disposition

Sol Extra High owned the product, attention, security, API, Stage 3, and
authority synthesis because they are tightly coupled and materially revise
user-visible behaviour and architecture. No external worker, provider, or
native subagent was used.

## Next bounded work

After protected integration of this design, execute Yuri's separately approved
non-production maintenance tranche:

1. opt-in GitHub auto-merge under unchanged strict protections;
2. pinned Ruff developer and CI parity;
3. canonical verification plus LF receipt normalization;
4. the historical empty-database Alembic repair; and
5. standardized risk-proportional test-wrapper timeouts.

Production database-role/GUC and field-encryption design remains deferred
because its original recommendation was expressly conditional on production
planning authority.
