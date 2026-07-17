# Bernie T3R1 Synthetic Shadow Refresh

Date: 2026-07-18

Decision: `provider_free_shadow_refresh_pass`

## Outcome

T3 now projects the exact 192 admitted synthetic Silver v2 receptionist
dialogues into its provider-neutral shadow-evaluation contract. The projection
preserves all six actions, eight dialogue forms, and both noise levels without
copying, relabelling, or promoting the v2 evidence.

This is an offline evaluation-readiness result. It is not a live-model score,
provider approval, product-runtime activation, clinical validation, or diary
write authority.

## Contract refresh

The earlier T3 contract scored intent, entities, date/time, clarification, and
one read-only tool choice. T3R1 retains those five dimensions and adds an
optional sixth dimension for explicit whole-action withdrawal. Existing T3
cases remain five-dimensional; every v2 projection case opts into the sixth
dimension.

The v2 projection exposes only these non-executing shadow labels:

- `propose_create`, `propose_move`, `propose_resize`, `propose_cancel`, and
  `propose_status_change`;
- `explain_schedule`;
- `request_clarification`; and
- `no_action`.

No product mutation tool is exposed. A model response may describe a proposal,
but the shadow runner cannot execute it. The existing safety checks still reject
write-authority claims, completed-action claims, and tools outside the safe
case allowlist.

## Exact evidence

- v2 anchor binding:
  `sha256:8609cdd7cab00281c7c2061cf24291be91ca225c5e26c41f8aa5411729f47b23`;
- v2 candidate binding:
  `sha256:1dd79a3209f87e46dbdb2a375c2f2c82a654e9208105f6ee28b4cb5ce4b4d46e`;
- v2 admission binding:
  `sha256:a3f2ba35e5526d5b4529d37a77214b7034cb11f29517b4a5a3f1df044c5346e0`;
- accepted selection:
  `sha256:0f3802e175e41eac387918165a090519a8b67af479d09c3851601acc4c6ed1e6`;
- T3R1 projection:
  `sha256:c39cc71a988a425886d96ccb75ccf07a3937f5e1363899b08366319f4dd7b4bd`;
- T3R1 report:
  `sha256:1c08d7bce492cdc94be5fa032498356cd1cb1283e2d5d387df86d1565f2de5a4`.

The offline expected-decision echo ran every case twice. It returned 384/384
perfect and safe samples, 2,304/2,304 scored dimensions, and zero variance.
This proves projection, runner, scorer, safety, and aggregation plumbing only;
the report explicitly records `establishes_model_quality=false` and
`provider_calls_performed=false`.

## Verification

The focused T3 plus v2 preservation gate passed 127/127; the final combined
gate including handover and closeout guards passed 139/139. Exact report
regeneration, Python compilation, `git diff --check`, the T3 live-replay gate,
the interpretation readiness gate, and the provider-boundary report also
passed. The three readiness checks continue to report blocked or false for live
calls, runtime/provider wiring, database access, route changes, historical
material, memory/RAG, and writes.

## Authority and next decision

Sol owned this tightly coupled contract refresh. No external worker or model
received the v2 projection, and no external prompt was sent.

Protected holdouts v1-v10 remain sealed. T3.5 adapters, external prompts, live
provider calls, provider tools, raw-response persistence, product/runtime
wiring, API/database/UI changes, confirmation, deployment, release, and every
write surface remain closed.

The next useful experiment is a capped, synthetic-only, no-write comparison of
candidate LLMs against this projection. It requires a separate Yuri approval
covering providers, exact models, prompt/response retention, cost cap, kill
switch, and evidence rules before any call is made.
