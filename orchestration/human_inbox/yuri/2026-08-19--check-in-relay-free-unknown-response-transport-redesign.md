# Check-in relay-free unknown-response transport redesign

Date: 2026-08-19

## Plain-language summary

The replacement transport worked. We removed the unreliable Windows relay and
queue from the tested path and proved, without starting a database, that a
future caller can take a temporary password through one channel while Docker's
own final process state supplies the result through another. The one live
fixture and the one independent review both passed first time, and nothing was
left running.

This does not yet prove the PostgreSQL rollback/unknown-result behavior. The
next tranche will freeze that exact relay-free database rehearsal before it is
allowed to run.

## Technical summary

- Accepted reviewed source:
  `4f0f54c2b0861828f9994444201b8da1bd54be00`
- Occupied proof source:
  `cd40c5c3cfdc57eb72e99ccc9bc88bf593b36e76`
- Proof count/retries: 1 / 0
- Gemini 3.7 Flash/high reviews/corrections: 1 / 0
- Host relay, multiprocessing queue, network, Docker logs and database: absent
- Closed outcome: exact stopped OCI identity, exit 42, no OOM/error/restart
- Hostile gates: 256/256 contract and 96/96 state rejections
- Cleanup: attachment absent, container absent, matching resources 0
- Protected refs: all four remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

The efficiency picture is mixed but encouraging. Clockwork kept canonical
drift and manual canonical edits at zero and prevented all thirteen construction
and closeout corrections from becoming another occupied run or model review. Those thirteen
corrections are itemized in the technical closeout rather than folded into the
successful runtime count. The next tranche will measure the same four numbers:
occupied reruns, verifier corrections, prepublication correction cycles and
manual canonical edits.

No ordinary practice, product/API/config/client change, product/patient/
clinical data, provider, production, deployment, release, Pages or protected
ref was opened. `docs/branding/` and unrelated untracked files remain untouched.

Clockwork closeout is accepted at Continuity 335 / Compass 317, generation
`gen-26454678fc92fe38ebdfc4464b5a325f6f7c55a9cc1fbbaad7eb7ad2be178760`,
lease 9. The non-PHI continuing Pushover notification succeeded with request
`8b5600fb-f514-402f-b33c-697a739de320`.
