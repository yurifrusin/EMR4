# Function-and-trigger-body architecture exact veto

Date: 2026-08-07

Candidate source HEAD:
`f51f5b65dd77d9282e5325a5e4f17edd872d14df`

Review worktree:
`C:\Users\sarashera\EMR4-worktrees\r33`

Review branch:
`codex/review-durability-function-trigger-body-f51f5b65`

Decision: `revision_required`

## Review envelope

The fresh read-only reviewer inspected the exact twenty-four-path packet,
including the active plan and three normative recoveries before the generated
contract, schema, builder, all nine entry-point programs, all thirteen trigger
programs, validator, tests and API Spine evidence. Exact HEAD/status preflight
and postflight were clean and unchanged. The prescribed focused pytest packet,
Ruff and `git diff --check` passed. No file or ref was changed in the review
worktree.

## Material findings

1. **Coordinator transition semantics were incomplete.** The candidate
   distinguished only receipt-present and primary-present cases, collapsed
   other states to `MISSING_ADMISSION`, and did not explicitly prove or enact
   the frozen conflict, predecessor, gap, epoch, key, watermark, frame,
   obligation and dependent-row rules.
2. **Retention eligibility was not an exact database-derived proof.** The
   generation census selected only `ACTIVE`, rather than every state except
   `CONSUMED`; related checkpoint, anchor, key and pin populations were not
   consistently bound to that census; count/non-empty checks did not establish
   policy grace or interval overlap; and three result constants were outside
   the exact REC19 vocabulary.
3. **The non-temporal appointment fence included historical effects.** Alias
   and outbox absence checks were scoped to the practice/stream but not to the
   current top-level transaction and current command relationship. Valid
   historical projection rows could therefore reject an otherwise valid
   non-temporal update.
4. **Normative and privilege closure was not independently enforced.** The
   semantic validator did not validate the exact recovery values, signature
   owner/security-definer/public-execute envelope, effective role privileges or
   enum membership. The generated structural schema deliberately omitted
   critical scalar meaning, while the adversarial packet ultimately relied on
   equality with the baseline it had just generated.

## Independently reproduced resealed attacks

After candidate and schema digests were refreshed, both semantic and
structural validation incorrectly admitted:

- direct owner `DELETE` privilege on the outbox;
- widening of the REC19 retention-reason enum;
- a producer security-definer owner swap; and
- removal of the producer's central event-membership assertion.

These are P1 defects. No P0 issue was found. The API Spine boundary and narrow
claim ceiling remain correctly closed, but this exact candidate cannot be
accepted as the machine-readable body architecture.

## Boundary outcome

The candidate remains preserved as rejected evidence. No SQL or DDL was
rendered or executed; no migration, database, source, feed, watcher, listener,
provider, product or patient data, runtime, application/API/Diary change,
deployment, release, Pages rebuild or protected-ref movement occurred.

DECISION: revision_required
