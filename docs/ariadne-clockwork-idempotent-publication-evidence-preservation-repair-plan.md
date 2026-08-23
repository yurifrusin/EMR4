# Governance clockwork idempotent publication evidence preservation repair — plan

Date: 2026-08-23

Timestamp: 2026-08-23T18:58:39.0105413+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`ariadne-provider-free-governance-clockwork-idempotent-publication-evidence-preservation-repair`

## Purpose

Keep the first successful publication evidence/report pair byte-exact when an
operator repeats `--publish` for an already-published intent, while retaining a
single generated machine-readable record of the idempotent readback.

This is the first ranked repair from the matched efficacy review. It changes
only the existing clockwork CLI output branch and its tests. It adds no new
operator-authored document, approval, gate, ledger, writer or control layer.

## Exact source and owned files

The starting task HEAD is
`53483bffefb762fcb79a28597b06169669dd3c3d`.

Implementation ownership is limited to:

- `scripts/ariadne_governance_clockwork_tick.py`; and
- `tests/test_ariadne_governance_clockwork_tick.py`.

The occupied proof may generate exactly one machine evidence file beside the
already accepted parent closeout:

- `clockwork-tick-idempotent-readback.json`.

No canonical clockwork, product or provider source may be changed by the
occupied readback itself.

## Frozen behavior

For an exact already-published intent and `--publish`:

1. validate the live canonical state through the existing validator;
2. derive the existing idempotent transaction facts, including zero command
   execution, zero publication and zero lease movement;
3. require the existing publication evidence JSON and Markdown report;
4. validate that the JSON is a passing `publication_committed` result for the
   same operation, generation and source, and that the report binds the same
   operation, generation, source and publication disposition;
5. leave both publication files byte-exact;
6. atomically write only
   `<prefix>-idempotent-readback.json` with the idempotent result; and
7. print the same idempotent result to stdout.

`<prefix>` remains `clockwork-tick` for ordinary/blocked/user-decision ticks
and `clockwork-checkpoint-tick` for checkpoint ticks.

Missing, unreadable, schema-invalid or mismatched publication evidence rejects
before the readback file is written. It must not cause verification command
execution, canonical mutation, pointer movement, lease movement or alteration
of either publication file.

## Verification

Deterministic verification must prove:

1. a valid publication pair remains byte-identical after readback recording;
2. the readback JSON contains `idempotent_readback`, zero executed commands,
   zero published generations and zero committed lease advance;
3. missing or mismatched publication evidence rejects without any output or
   canonical mutation;
4. ordinary and checkpoint prefixes derive their exact readback names;
5. Ruff passes on the two owned files;
6. the focused clockwork suite passes; and
7. all four provider-free governance files pass together.

After the candidate is committed, one occupied idempotent `--publish` may run
against the accepted matched-review intent. Before and after SHA-256 readings
must prove its publication evidence/report pair unchanged. The generated
readback must bind lease 215 and the accepted generation, while production
live-state validation proves zero drift and no canonical movement.

Do not use a second occupied readback merely to prove readback idempotence; the
unit test owns that behavior.

## Acceptance

The repair passes only if:

- the original publication pair is byte-exact before and after the occupied
  readback;
- exactly one generated readback JSON is added;
- canonical generation, transaction, pointer, latch and lease are unchanged;
- no semantic verification command is reexecuted;
- the failure cases are fail-closed;
- the existing first-publication output path is unchanged;
- no new operator field, document, gate, ledger or control layer is required;
  and
- the focused and full governance suites pass.

## Parallelism assessment

- **DeepSeek:** declined. The native occupied profile remains paused, Claude
  Code is not an authorised fallback, and the repair is one tightly coupled
  CLI/output/test slice.
- **Gemini:** declined. Byte identity, JSON binding, command counts and live
  canonical state are deterministic; no provider veto is authorised.
- **Native subagents:** declined under developer policy and because the output
  branch, tests and occupied proof are serial.
- **Owner:** GPT Sol.

Reassess only if the repair requires canonical schema/transaction changes, the
publication pair cannot be authenticated locally, or the occupied proof moves
canonical state.

## Next tranche

On acceptance, proceed under standing authority with a typed serial
continuation-state projection inside the existing orchestrator preflight,
measured against the observed 14-file / 2,334-line burden. It must replace
repeated runtime-state form filling rather than add another layer.

## Claim boundary

Passing evidence will prove only that a repeated publish preserves one valid
publication pair and records one local idempotent reading. It will not prove
all historical overwritten evidence recoverable, arbitrary output prefixes,
reduced test cadence, native-Harness reliability, provider suitability,
product correctness, production readiness or protected integration safety.
