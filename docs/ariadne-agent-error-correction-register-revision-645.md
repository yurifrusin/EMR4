# Ariadne agent error and correction register — revision 645

<!-- ariadne-agent-error-register-reading
revision: 645
incident_count: 1126
new_incident_ids: AER-1116,AER-1117,AER-1118,AER-1119,AER-1120,AER-1121,AER-1122,AER-1123,AER-1124,AER-1125,AER-1126
open_incident_count: 0
-->

## AER-1116

One direct-path latch invocation failed because the repository module must be
run with `python -m`. The module form was used on the fresh attempt and passed.

## AER-1117

One post-restart receipt draft repeated a protected Git object in prose. The
preflight rejected it before acceptance; the corrected receipt uses only the
machine-owned Git snapshot.

## AER-1118

One packet draft copied the wrong admission schema vocabulary. The canonical
call returned `snapshot_invalid`; the exact product vocabulary was read from
source, corrected and all focused and surrounding tests passed.

## AER-1119

One surrounding-suite command guessed a nonexistent test filename. Repository
search resolved the exact existing test path and the complete suite passed.

## AER-1120

One closeout intent used the descriptive Continuity node kind `rehearsal`,
which is outside the graph's closed vocabulary. The first clockwork check
failed before publication or pointer movement; the corrected intent selects
the admitted `integration` kind.

## AER-1121

The corrected `integration` kind was syntactically admitted but activated two
unrelated inherited appointment-availability contracts. The second dry check
failed before mutation; the conformance packet was reclassified as `tooling`,
matching its provider-free verification role without asserting irrelevant
product-contract evidence.

## AER-1122

One postpublication verification command supplied an unsupported `--check`
flag to the agent-error-register reporter. Argparse rejected it without
mutation; the canonical register is instead verified by the governance suite.

## AER-1123

The first publication revealed that the new Yuri summary lacked the exactly
one top-level Brisbane `Timestamp:` line required once it became current-node
evidence. Postpublication consistency verification rejected the generation and
the clockwork restored the previous generation byte-exactly at lease 206. The
summary now carries the required timestamp before a fresh publication attempt.

## AER-1124

The first rollback invocation incorrectly supplied `--intent`, which rollback
does not accept. Argparse rejected it without movement; the argument-free
rollback then restored the previous generation byte-exactly.

## AER-1125

The second publication found the same top-level Brisbane timestamp invariant
missing from the Sol acceptance. The clockwork again restored the previous
generation byte-exactly, this time at lease 208. The Sol acceptance now carries
the required timestamp, and every prospective plan, closeout and acceptance
Markdown path was scanned together before a fresh publication attempt.

## AER-1126

The first all-path timestamp scan reconstructed the repository parser with an
incorrect string slice and rejected a valid offset timestamp locally. It made
no mutation. The corrected scan uses the exact prefix, suffix, offset and date
logic from the current-Baton consistency test.
