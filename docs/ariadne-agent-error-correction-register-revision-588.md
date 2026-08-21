# Ariadne agent error and correction register — revision 588

Date: 2026-08-21
Timestamp: 2026-08-21T14:22:57.0516264+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 588
incident_count: 786
new_incident_ids: AER-0777,AER-0778,AER-0779,AER-0780,AER-0781,AER-0782,AER-0783,AER-0784,AER-0785,AER-0786
open_incident_count: 0
-->

## AER-0777 — incomplete declared-adapter inventory

The first preplanning state omitted two declared but unused transport adapters.
Preflight rejected it before dispatch or native activity. The rejected pair is
preserved and the passing v3 state includes all six declarations.

## AER-0778 — compact state dropped latch keys and authored Git evidence

The second state over-compressed the exact latch and wrote a full protected
commit into the narrative Git-evidence field. Preflight rejected both errors,
prohibited dispatch and performed no native work. The passing v3 restores the
exact latch and leaves all Git object readings to the machine snapshot.

## AER-0779 — direct-script import-bootstrap recurrence

The first boot-controller CLI check repeated AER-0773's missing repository-root
bootstrap. It failed before contract, evidence or Node activity. The bootstrap
is restored and a dedicated direct-subprocess test now makes the requirement
executable.

## AER-0780 — zero-Node test blocked required Git subprocesses

The initial zero-Node guard replaced every `Popen`, including the Git ancestry
checks that deterministic admission requires. The guard now rejects only
`node`/`node.exe` and permits non-Node subprocesses. Focused and widened suites
pass.

## AER-0781 — repaired sentinel exited before activation

The sole pinned rc.7 process exited 1 after 7,310 ms and emitted no HMR event.
The attempt is consumed without retry. Provider, model, broker, worker and
network counts stayed zero; process and disposable-root cleanup passed. The
boot proof is rejected and the result is contained into a static diagnosis.

## AER-0782 — failed terminal used success-affirmative claim wording

The immutable failed terminal's generic claim sentence says it proves sentinel
loading and HMR readiness, contradicting its controlling structured fields:
`failed_closed`, zero events and readiness false. The terminal remains
immutable; the closeout makes the structured interpretation authoritative and
future output-contract tests must branch claim wording on result.

## AER-0783 — register append used a non-unique patch anchor

The first postterminal append matched the first generic corrected-status row,
placed two new incidents after AER-0001 and left the historical register as
trailing JSON. JSON parsing and focused register tests rejected it before
staging or publication. The typed clockwork reducer now owns the append.

## AER-0784 — error-register projection bypassed clockwork ownership

The candidate commit directly changed the canonical error register and pattern
report instead of supplying incident observations to the single-owner tick.
Live-state validation exposed the drift. Both files were restored byte-exactly
to the selected generation before this typed publication.

## AER-0785 — active-latch projection bypassed clockwork ownership

The checkpoint commit directly changed the clockwork-owned active latch.
Live-state validation treated that otherwise plausible checkpoint as canonical
drift. The latch was restored byte-exactly and this tick alone now advances it.

## AER-0786 — v2 tick intent omitted required observations

The first closeout intent selected the incident-bearing v2 schema but supplied
an empty observation list. Validation rejected it before projection or
publication. The corrected intent supplies the complete ordered observation
set and lets the clockwork allocate identifiers and derived counts.

All ten incidents are corrected or contained and none remains open. The
receipt failures and canonical-drift checks demonstrate the clockwork gate
acting before runtime or publication; the direct-bootstrap recurrence and the
manual canonical writes show why prose memory is being replaced by executable
ownership and regression controls.
