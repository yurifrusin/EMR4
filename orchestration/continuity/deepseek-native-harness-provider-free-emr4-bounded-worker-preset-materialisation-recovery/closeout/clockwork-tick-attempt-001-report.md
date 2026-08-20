# Governance clockwork tick — rejected attempt 001

Status: **rejected after postpublication observability audit**

Operation:
`deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery`

Source: `d54f8f55019c911277ad2ff6dd4e499ca10954f1`

Generation:
`gen-9c56d1fad99d61a4600bf37c7dcc1ada37be8a49c50b9ebfe2922f766ac077a7`

Lease sequence: 53

The canonical publication itself was deterministic and valid. The subsequent
verification chain yielded after partial pytest output, however, and the tool
caller emitted only stdout rather than the full execution envelope. The
returned unified-session identifier was therefore discarded. Process
inspection showed that the chain progressed to its final clockwork check and
completed, but its exact pytest exit was not recoverable as admissible evidence.

One fresh observed rerun, this time retaining and polling session `42419`,
passed to 100% with exit code zero. This is a recurrence of the existing
yielded-session-handle incidents rather than a candidate failure. The lease-53
generation is preserved here, canonical state is rolled back byte-exactly, and
the corrected incident-intake closeout must be published from a fresh source.
