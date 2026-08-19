# Relay-free check-in unknown-response transport redesign closeout

Date: 2026-08-19

Status: **accepted pending the generic clockwork closeout publication**

## Outcome

The redesign passes. EMR4 now has a provider-free, no-database proof that a
future one-shot PostgreSQL caller can receive its ephemeral credential through
attached stdin while its outcome is classified independently from exact
terminal OCI state. The prior Windows host TCP relay and
`multiprocessing.Queue` are absent from the new path.

This is transport evidence only. It does not prove a database connection,
transaction, rollback, commit-uncertainty readback, exact-one effect or product
readiness.

## Exact sources

- User-decision clockwork source:
  `44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4`
- Frozen plan source:
  `dcb5093a61f0365aeb2651e3bcfd87a36fe0c438`
- Implemented static candidate:
  `ce869a5936b0fdeefbcf0595f1616641fd688d07`
- One-shot execution source:
  `cd40c5c3cfdc57eb72e99ccc9bc88bf593b36e76`
- Proof-artifact commit:
  `31cbebc4462d2795b9d6bca84a48186901515a6a`
- Exact independently reviewed candidate:
  `4f0f54c2b0861828f9994444201b8da1bd54be00`
- Protected local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

## Technical result

- The exact cached `postgres:16-bookworm` image was used with no pull,
  `--network none`, logging driver `none`, read-only rootfs, no port, bind,
  volume or external network, and one bounded tmpfs.
- A random 32-byte token was supplied only through attached stdin after exact
  no-secret configuration inspection. It was absent from released evidence,
  Docker configuration, argv, labels and logs.
- Attachment status, output and return code were excluded from outcome
  evidence. Exact captured identity plus stopped OCI state supplied the result.
- Only exit 42 with no OOM, empty state error and zero restart count admitted
  the simulated incomplete-response classification. No success or retry was
  released.
- All 256 hostile contract mutations and all 96 hostile OCI states were
  rejected with zero escapes.
- No database process, connection, transaction, SQL statement, product row,
  provider call or ordinary admission release occurred.
- The attachment and captured container were absent and zero matching labelled
  resources remained. The occupied proof ran exactly once with zero retries.

Gemini 3.7 Flash/high independently returned `pass` at exact unchanged HEAD
`4f0f54c2b0861828f9994444201b8da1bd54be00`; all ten bound commands exited
zero and the review worktree stayed clean.

## Clockwork efficacy reading

The mechanism did useful work, but the construction record is not spotless.
The durable reading records one occupied proof, zero occupied retries, one
Gemini review, zero Gemini corrections, zero manual canonical edits and zero
canonical drift.

Twelve prepublication corrective cycles remain attributable to caller-authored
planning, receipt or gear construction:

1. one invalid parallel-leverage vocabulary draft;
2. one attempt-002 SHA-256 transcription correction;
3. one mutable-current source-binding correction;
4. one immutable historical test-fixture correction;
5. one guessed full-HEAD receipt correction;
6. one checkpoint command-manifest admission correction;
7. one same-operation checkpoint idempotency repair;
8. one module-import correction;
9. one paired report-write placement correction; and
10. one local yielded-session result recapture through a correctly retained
    session identifier; and
11. one post-review audit correction recording that two optional packet paths
    used descriptive `clockwork-decision` labels while the retained files use
    the generic `clockwork-tick` names; and
12. one closeout-intent rejection because its graph node supplied two lineage
    relationships where the admitted clockwork schema requires exactly one.

The eleventh defect did not affect the exact candidate, contract, proof,
manifest, command results or current latch, so the original packet and passing
receipt remain immutable and no ceremonial second review was launched. None of
the twelve corrections caused a second occupied proof or verifier call. The generic checkpoint
CLI now requires exact intent-digest equality for replay and recreates its JSON
evidence and Markdown report as a pair. The remaining efficiency target is to
derive more runtime-state/source-evidence fields instead of asking Sol to
transcribe them.

## Boundaries retained

No app, API Spine, OpenAPI, GraphQL, configuration, migration, product test,
client, feature flag, allowlist, generic-status `Arrived`, action grammar or
waiting-area behavior changed. No ordinary practice was enabled. No product,
patient, appointment, clinical or protected data was used. No production,
deployment, release, Pages or protected-ref authority opened. `docs/branding/`
and all unrelated untracked files remain preserved.

## Next operation

The next dependency-satisfied tranche is
`raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal`.
It may first freeze a new plan that uses this exact relay-free transport with a
uniquely named disposable authored-synthetic PostgreSQL instance. It may not
execute until deterministic admission and a fresh five-source preexecution
receipt pass. It must retain no-retry semantics, authoritative restricted-role
readback, forced-RLS isolation, exact cleanup and zero ordinary release.

Pushover closeout: `pending_after_clockwork_publication`.
