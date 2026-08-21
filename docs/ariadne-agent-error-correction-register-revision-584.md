# Ariadne agent error and correction register — revision 584

Date: 2026-08-21
Timestamp: 2026-08-21T11:59:13.0977106+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 584
incident_count: 759
new_incident_ids: AER-0756,AER-0757,AER-0758,AER-0759
open_incident_count: 0
-->

## AER-0756 — preplanning prose supplied a manual Git object

The first attempt-004 preplanning receipt correctly returned
`revision_required` because the `git_refs_and_worktree` prose contained a
manually supplied full protected-ref object. The receipt boundary requires its
Git snapshot to be machine-owned. The rejected receipt is preserved; the prose
now names only the configured expected commit and the corrected receipt reports
zero manual object IDs. No planning, process, provider or publication action
preceded the rejection.

## AER-0757 — preceding closeout documents omitted required timestamps

Fresh successor rehydration found that several newly authored documents in the
preceding accepted historical-validator repair contained `Date:` but omitted
the required ISO 8601 Australia/Brisbane `Timestamp:`. Their accepted evidence
bytes remain immutable. This tranche adds a focused document guard requiring
both fields and the explicit `+10:00` offset for its plan, threat delta,
closeout, Sol acceptance and Yuri summary. The requirement is now a mechanical
reading instead of an orchestrator memory obligation.

## AER-0758 — closeout draft guessed a full pre-verifier object ID

The first closeout draft copied the correct eight-character abbreviation but
manually guessed the remaining characters of the pre-verifier commit. A direct
`git rev-parse` comparison caught the incorrect 40-character value before
staging. The draft was corrected to the machine-resolved full object and a
focused test now resolves both candidate and pre-verifier objects from Git and
requires those exact values in closeout and acceptance. No candidate, provider,
runtime or protected effect occurred.

## AER-0759 — closeout node used an unadmitted kind

The first read-only clockwork closeout check labelled the readiness graph node
as `rehearsal`, which is descriptive prose rather than an admitted Compass node
kind. Clockwork rejected the prospective projection with `node_kind_invalid`
before transaction preparation, command execution or publication. The node now
uses the admitted `tooling` kind. The mandatory read-only projection check
remains the prevention control for closed graph vocabulary.

All four incidents are corrected or contained and none remains open.
