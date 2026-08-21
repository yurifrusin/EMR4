# Ariadne agent error and correction register — revision 588

Date: 2026-08-21
Timestamp: 2026-08-21T14:04:01.2651862+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 588
incident_count: 780
new_incident_ids: AER-0777,AER-0778,AER-0779,AER-0780
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

All four incidents are corrected or contained and none remains open. The two
receipt failures demonstrate the clockwork gate acting before runtime; the
bootstrap recurrence demonstrates that a remembered prose rule was
insufficient until converted into a regression test.
