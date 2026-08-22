# Ariadne agent error and correction register — revision 630

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 630
incident_count: 1008
new_incident_ids: AER-1006,AER-1007,AER-1008
open_incident_count: 0
-->

## AER-1006 — Repair plan conflated normal signaling with teardown termination

Status: `closed_corrected`

The first frozen repair prose required zero normal and cleanup host signals,
but exact source inspection showed the accepted teardown already closes stdin
and calls `Popen.terminate()`, with bounded wait/kill fallback. Removing
Docker's invalid signal-proxy option therefore required distinguishing normal
control from intended teardown termination.

The plan and threat delta were corrected before the executable edit. The
repair attestation now proves zero normal-path terminate/kill and the unchanged
bounded teardown sequence separately. The prospective control is to render
lifecycle statements from exact AST call-role projections before plan commit.

## AER-1007 — Repair report test repeated line-wrap sensitivity

Status: `closed_corrected`

Despite AER-1005's newly stated normalized-document control, the first repair
postterminal test used two raw multiline substring assertions. The first clean
rerun exposed one wrapped sentence; after normalizing that assertion, the next
focused rerun exposed the second wrapped sentence.

Both assertions now use one normalized document representation and the full
current suite passes 94/94. No harness, attestation, Docker, database, provider
or canonical evidence was repeated. The durable next control is one shared
`normalized_markdown_contains` helper plus a test/lint prohibition on raw
multiline semantic substring assertions.

## AER-1008 — Closeout intent used a descriptive stage outside the typed vocabulary

Status: `closed_corrected`

The first clockwork dry run rejected the plan incident's `planning` stage.
Although the description was semantically intelligible, the register accepts
only its closed stage vocabulary and uses `dispatch` for this preimplementation
position.

The caller-authored intent was corrected to `dispatch` and the same dry run
then passed with zero live publications. No canonical ledger, executable,
test, Docker, database or provider action was repeated. The durable control is
to generate incident forms from the clockwork schema's enum-backed selector
rather than permitting a free-text stage field.
