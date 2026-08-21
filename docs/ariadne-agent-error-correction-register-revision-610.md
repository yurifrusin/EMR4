# Ariadne agent error and correction register — revision 610

Date: 2026-08-22

Status: **seven corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 610
incident_count: 918
new_incident_ids: AER-0912,AER-0913,AER-0914,AER-0915,AER-0916,AER-0917,AER-0918
open_incident_count: 0
-->

## AER-0912

The first post-clockwork verification command included a historical snapshot
test that intentionally hard-codes Continuity 324 and the former check-in
orientation. The two resulting failures did not contradict the live
Continuity 386 / Compass 368 state. The current-state suite was rerun without
that frozen equality node and passed; the historical test was not rewritten.

## AER-0913

A read-only PowerShell projection again attempted to pipe directly from an
inline `foreach` construct and stopped at parsing. No command, file or Git
state changed. The replacement used separate statement-form commands. This is
a recurrence of the command-form defect already registered at AER-0899.

## AER-0914

A PowerShell Git inspection left `^{commit}` unquoted. PowerShell split the
brace expression, so Git first resolved the parent form and then rejected the
encoded brace fragment. The quoted revisions returned the intended full
implementation and acceptance objects without changing repository state.

## AER-0915

The first correction controller counted three `selectedTools` tokens after its
signature rewrite had already consumed one. The direct source check rejected
the post-rewrite count before commit or evidence generation. The corrected
predicate requires the two body references remaining at that stage.

## AER-0916

The first raw-detail guard treated every internal `.message` read as a release.
It therefore rejected three accepted fixed-message equality or lookup checks
that publish no raw content. The corrected guard targets only actual detail,
stack, cause, environment, prompt, response or credential projections.

## AER-0917

The first controller CLI printed the closed rejected derivation but returned
exit code zero. The orchestrator detected the non-admitted result in its typed
output before commit or evidence generation. The CLI now returns nonzero for
every result except `root_service_forwarding_correction_admitted`, and the
accepted direct check exits zero only with no failed coordinate.

## AER-0918

The preliminary evidence resolved its candidate from current `HEAD`. That was
correct at generation time but made later deterministic recomputation select
the evidence-commit descendant instead of the implementation owner. The first
pre-verifier receipt was preserved as superseded. The corrected controller
asks Git for the commit that last changed its own path, passes that object
through the repository resolver and emits immutable v2 evidence. After the v2
evidence commit advanced `HEAD`, recomputation remained byte-equal and retained
the exact implementation source.

## Control reading

All seven incidents were detected without Node, native Harness, worker, model or
provider activity. Four were orchestration command or suite-selection costs;
three strengthened the prospective controller's own fail-closed semantics. Most
importantly, the tranche's Git plan and candidate identities were derived by
the repository resolver with zero caller-authored object IDs, so the original
clerical object-binding class did not recur inside the contract or evidence.
