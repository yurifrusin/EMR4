# Bernie Stage 3A — Final Yuri Formative Validation Closeout

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `stage3a_pass`

Claim scope: `yuri_only_local_authored_synthetic_formative_validation`

## Outcome

Stage 3A passes within its exact formative boundary. Yuri completed the full
fourteen-scenario study, the seven contaminated scenarios were corrected and
rerun, and the separately required real local confirmation check passed through
the visible Diary control, FastAPI, and an isolated PostgreSQL database.

This supports the conversational, intent-projected, committed-event-aware
Diary direction and the usefulness of its functional just-in-time views. It is
not representative-staff evidence, a language-model evaluation, a live event
runtime, production readiness, clinical validation, deployment or release
authority.

## Corrected functional evidence

The exact corrected export is:

- filename: `bernie-stage3a-stage3a-132a0a9c-c3f4-4019-b904-6f38eeefcefa.json`;
- SHA-256: `55146de6b7ad2743acf5ce9505230a39c5ff8a641f366d5018d2689282359ffb`;
- size: 7,775 bytes;
- schema: `bernie.stage3a.study-export.v2`;
- evidence mode: `authored_synthetic_fixture_browser`;
- participant scope: `yuri_only`;
- reference date: `2026-07-20`;
- prompt/transcript content: false; and
- observations: exactly S3A-03, S3A-04, S3A-06, S3A-11, S3A-12, S3A-13,
  and S3A-14.

All seven projections were rated useful. Six scenarios were recorded complete
and the fixture-only S3A-06 route safely blocked. No issue flag was selected.
The raw export remains outside the repository; only its hash and bounded
aggregate findings are retained.

The rerun proves:

- chronological practitioner and patient projections;
- clean scenario transitions and correct authored grid dates;
- both required routes for S3A-03, S3A-04, and S3A-11;
- all three authored dates inspected for Margaret's upcoming appointments;
- one relevant committed-change notice backed by a current projection;
- exact suppression of the unrelated, foreign-practice, and rolled-back
  population; and
- one visible relevant effect plus silent replay and stale/out-of-order
  suppression.

## S3A-06 facilitator clarification

The raw export records `suppressed_events` for S3A-06. Immediately after
exporting, Yuri independently corrected this choice to `Separate safety check —
not run here`; `suppressed_events` belongs to S3A-13.

The export was not rewritten. The self-correction is retained as facilitator
evidence and as a formative wording finding. It establishes the correct final
distinction: the fixture harness cannot confirm or commit, while S3A-06 is
verified separately through the authoritative Diary path. No unsafe action or
mistaken commitment occurred. The final comprehension gate therefore passes,
with the label worth simplifying before a representative-staff study.

## Separate authoritative confirmation check

Evidence label: `live_local_browser_backend_postgres`.

Environment:

- database: `gp_pms_stage3a_3af7c33c_20260720_s3a06`;
- PostgreSQL: loopback `127.0.0.1:5434`;
- UI/backend: loopback ports 3000 and 8001;
- practice, receptionist, practitioner, patient, roster, schedule, Diary
  column, room, waiting area, and appointment type: authored synthetic only;
- interpreter provider: `fake`;
- live provider: false;
- cloud credentials present: false; and
- API interception or mocked transport: none.

The real Diary accepted the frozen request, displayed a proposal for Margaret
Thompson with Dr Alex Shera at 14:00 on 20 July 2026, and exposed one distinct
visible confirmation control. Before confirmation, PostgreSQL contained zero
appointments, zero appointment audits, and zero command-idempotency rows.

Sol clicked the visible `Confirm booking` control. The ordinary REST
`confirm-bernie` command returned HTTP 200; the Diary displayed exactly one
`Booking Confirmation Receipt`; and the grid displayed exactly one 14:00–14:15
booked appointment. After a full page reload, the day summary and appointment
remained visible from authoritative readback. The browser recorded zero console
warnings or errors.

Post-confirm database readback is exactly:

| Record | Count | Correlation |
|---|---:|---|
| Appointment | 1 | booked, 14:00, 15 minutes |
| Appointment create audit | 1 | appointment and command links match |
| Command idempotency result | 1 | completed, HTTP 200, `confirmed_write`, target and audit links match |
| Stored typed receipt | 1 | `appointment.confirmation_receipt.v1`, outcome `appointment_created` |

The stored receipt records authenticated actor, practice scope, proposal
revalidation, conflict check, idempotency, audit and signed-evidence verification
as true. Optional session correlation is absent because this accepted Stage 1
Diary invocation did not supply a durable server-session identifier; the
confirmation outcome and receipt are stored in the completed command result.

Sanitized identity bindings are:

- appointment id SHA-256:
  `b0cdf477cb9732fe21792df1b91baae50ac7317b8af879e8331fb09a621cae23`;
- audit id SHA-256:
  `6aace67cc7a826f17ceb10eb88f6c0211f05c3efe381b168ce610e81b5381c23`;
- command id SHA-256:
  `38cf6417463ff741c7e873b95047bf26b97280371ee7b1f3aeca64a84974c390`.

The isolated synthetic database is preserved with that exact one-write state.
The browser tab was finalized, and the task-scoped backend/static processes
were stopped with ports 3000 and 8001 verified free. No credential, token, raw
header, prompt transcript, or screenshot containing non-synthetic data is
committed.

## Gate decision

| Gate | Result | Evidence |
|---|---|---|
| Correct practice scope | pass | authored single-practice fixtures; no cross-practice display |
| No write before confirmation | pass | zero appointment, audit and command rows after proposal |
| One confirmed write | pass | exactly one appointment, matching audit and completed command result |
| Typed outcome and receipt | pass | one stored v1 receipt with `appointment_created` outcome |
| Answer/proposal/commit distinction | pass | original study findings plus independently corrected S3A-06 classification and real confirmation plane |
| Event suppression | pass | full S3A-13 unrelated/foreign/uncommitted-or-rolled-back population silent |
| Replay/order safety | pass | S3A-14 surfaced once; replay and stale revision silent |
| No interruptive alert | pass | all event-fixture attention concise or silent |
| Fresh-read projection | pass | visible notices offer current synthetic projections, not event-payload truth |
| Identity ambiguity safety | pass | original S3A-07 clarification evidence remains intact |
| Evidence separation | pass | fixture and real local confirmation labels remain distinct |

No failed gate was overridden.

## Verification and bounded technical maintenance

The first final regression run exposed one stale historical source assertion:
it prohibited any `db.commit()` inside the supervised-booking route even though
accepted Stage 2 deliberately persists bounded server-owned session
transitions. The assertion was narrowed without changing runtime behaviour:
the route still cannot call a provider, confirm, create or audit an appointment,
and its one permitted commit remains guarded by a durable session snapshot. Its
docstring now states the same exact boundary. Ruff also exposed and removed one
unused test-only `Practitioner` import.

Verification then passed:

- stale assertion focused rerun: 1 passed;
- combined Stage 3A, durable confirmation/recovery, create-confirm,
  supervised-booking, signed-evidence, API Spine and accessible-confirmation
  population: 73 passed;
- final Stage 3A artifact, API Spine artifact, handover archive, and Ariadne
  population after the documentation update: 60 passed;
- JavaScript syntax checks for the Stage 3A and Diary assets: pass;
- focused Ruff checks: pass; and
- `git diff --check`: pass.

All pytest processes ran serially. No product behaviour, mutation family,
provider boundary, safety threshold or acceptance meaning was weakened.

## Product-direction refinement during closeout

Yuri removed the named-model dependency from the future meta-grid programme.
The conceptual interaction language will be designed in-house and remain
provider-neutral; high-fidelity styling may be fine-tuned later. Claude Fable,
Kimi, or any future design resource is optional and requires a fresh exact
cost/privacy/transmission decision before use. This refinement is durable in
the north star, detailed design, Stage 3 decision and product-ideas notepad. It
does not authorize the next tranche by itself.

## Authority disposition

Stage 3A is complete with `stage3a_pass`. Stage 3B, representative staff,
in-house meta-grid implementation, high-fidelity design, voice, event runtime,
provider calls, external prompt transmission, protected or historical evidence,
PII, production, deployment and release remain closed pending a fresh Yuri
decision.
