# Governance clockwork prospective evidence and transaction-fact repair

Date: 2026-08-23

Timestamp: 2026-08-23T16:43:10.7836980+10:00 (Australia/Brisbane)

Result: `complete_prospective_error_set_and_command_local_transaction_facts_pass`

## Lay result

The clockwork now reads the whole relevant form before it moves. If a proposed
current node has several missing or malformed Date/Timestamp headers, unsafe or
duplicate paths, or absent plan/closeout/acceptance evidence, one typed response
lists all detectable problems together. Nothing is published and the pointer
does not move.

The clock also takes its own transaction reading. Dry preparation,
prepublication rejection, clean publication, harmless idempotent readback and
byte-exact rollback each report their actual command-local attempts, lease
movement and generation identities. An operator no longer has to author these
facts. The mechanism deliberately does not invent a historical total from a
current pointer that cannot contain that history.

## Technical result

- the existing tick validates all prospective `plans`, `closeouts` and
  `acceptances` before transaction projection or any canonical write;
- one hostile helper fixture returns ten ordered errors in one reading;
- a two-file build fixture asserts four distinct header defects in one
  rejection and proves every canonical, metadata and pointer byte unchanged;
- the CLI turns that rejection into typed `revision_required` JSON rather than
  a traceback-only correction loop;
- the current-Baton consistency test consumes the production timestamp
  validator, so the timestamp rule is no longer reconstructed twice;
- five exact transaction dispositions emit output-owned facts with no new
  intent field;
- an actual idempotent readback reported zero preparations, publications,
  rollbacks and lease movement at lease 212 with zero canonical drift; and
- Ruff, byte compilation and all 108 focused governance tests pass.

The first full run exposed six historical replay-fixture compatibility defects:
the new human-evidence fixtures used an ordinary Markdown path where the graph
requires a canonical Codex acceptance-reference path. Test-only fixtures were
corrected to preserve that existing graph invariant; all six targeted tests and
the full suite then passed. One attempted diagnostic used pytest node selectors
with the whole-file provider-free runner, whose contract intentionally rejects
them. Direct serial pytest was used for the six-node diagnosis, followed by the
canonical whole-file suite. Neither issue caused product, provider or canonical
state to rerun.

## Matched efficacy

The preceding packet had three postpublication rollback shapes: two missing
human-evidence timestamps and one manually authored publication count. The two
timestamp shapes are now prospective typed rejections; the counter shape is now
an output-owned fact. This removes the measured failure shapes without adding
an operator field, approval, gate, ledger, required closeout document or second
control layer.

This does not mean every future closeout will be mistake-free. It means these
three known classes are now handled at the clock face instead of by manual
reconstruction after the mechanism has moved.

## Harness relation and boundaries

The useful lesson from the DeepSeek gear work remains the three coarse readings:
`prepared`, `terminal`, and `accepted_or_recovered`. This repair improves the
governance clock independently of a worker transport. The native occupied
profile remains paused, Claude Code is not a silent fallback, and no Harness or
provider was invoked.

No product source, check-in choice, patient or clinical data, runtime,
deployment, release, Pages, protected evidence or protected ref changed.
