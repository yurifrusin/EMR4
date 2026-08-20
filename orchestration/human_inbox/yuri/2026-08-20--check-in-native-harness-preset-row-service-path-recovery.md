# Native Harness preset-row service-path recovery — paired closeout

Date: 2026-08-20

Timestamp: 2026-08-20T18:41:10.4055454+10:00 (Australia/Brisbane)

## Lay summary

We found and fixed the reason the DeepSeek Harness could not see the EMR4 worker
preset. The Harness was replacing the configured preset roots with its own
built-in root, and our diagnostic profile had also disabled the separate user
root where the EMR4 preset actually lived. Re-enabling that derived user root—
without changing the installed Harness—made the native preset service find and
verify the exact EMR4 row.

The single admitted Harness process passed on its first run and cleaned up in
718 ms. It did not create an agent or contact DeepSeek. So this is a successful
Harness service-layer repair, not yet a DeepSeek worker-development result.

The review workflow also taught us something important about the “vocabulary
lapse” problem. Two reviews failed because Gemini was required to copy a long,
exact command/result ledger back into JSON. Once deterministic clockwork kept
that ledger and Gemini was asked only for technical judgment, the same review
passed cleanly. That division is the practical fix: let models reason; let the
gears carry exact hashes, command names and counts.

No attention is required. The first closeout draft tried to return to the
default-off route-adapter tranche, but the clockwork correctly refused because
that product operation is already accepted. The useful next step is instead a
provider-free proof that the now-visible EMR4 preset can mount and project its
exact three-tool view before any DeepSeek request.

## Technical summary

- semantic candidate: `da52514548ef1c1253e379f983165545482592a6`;
- split-veto executor candidate:
  `a6b3fc9ea582677419b5053952336792fd088d0c`;
- preexecution source: `e295441de4272135f70f712e964293e623fec43f`;
- terminal/repair source: `3369c92e315e65b64243204dd225265987246a12`;
- native terminal: `PRESET_DIGEST_BOUND_PASSED`, all eight markers;
- process/retry: `1/0`, 718 ms, exit 0;
- agent, turn, broker, model, provider, network, Docker and database: all `0`;
- cleanup: process and disposable root absent;
- deterministic executor gate: 12/12 exact commands passed;
- independent semantic gate: Gemini 3.7 Flash/high clean `pass`;
- verification: 56 focused tests, 449 register tests, Ruff and compile pass;
- register: revision 574, six corrected incidents, none open; and
- protected refs: all remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Deliberately closed: DeepSeek/model work, agent or preset mount, retry of the
consumed process, attempt 006, database/product/API/client/ordinary-practice
change, production, deployment, release, Pages and protected-ref movement.

Next tranche:
`raisa-provider-free-check-in-native-harness-preset-mount-effective-tool-projection-rehearsal`.
It remains provider-free and initially deterministic. Any native process must
be separately checkpointed, one-shot and terminal before an agent session,
turn, broker, model or provider request.

The first non-PHI continuing Pushover request
`d65c2006-6c3e-4ce1-81f1-0e20ccfa3fc5` is preserved. The corrected successor
notification succeeded with request `432db1da-c8ac-4744-9633-e578612f8072`.
