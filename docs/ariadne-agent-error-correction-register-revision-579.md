# Ariadne agent error and correction register — revision 579

Date: 2026-08-21

Timestamp: 2026-08-21T08:24:15.9013739+10:00 (Australia/Brisbane)

Status: `prospective_clockwork_reading`

<!-- ariadne-agent-error-register-reading
revision: 579
incident_count: 738
new_incident_ids: AER-0733,AER-0734,AER-0735,AER-0736,AER-0737,AER-0738
open_incident_count: 0
-->

This revision adds six corrected low-severity observations from the structured
diagnostic seam recovery to revision 578's 732 incidents. The exclusive
clockwork derives the canonical register; this reading must match 738 total
incidents, latest `AER-0738`, and zero open incidents.

## AER-0733 — the first seam draft crossed an accepted source boundary

The first implementation draft added v2 behavior directly to the accepted v1
terminal and consumed native controller. The compatibility gate reported that
the predecessor's source-bound recovery evidence was no longer current before
the draft was staged.

Correction: the v2 terminal and future controller envelope moved wholly into
the new seam component, and both accepted files were restored byte-for-byte.

## AER-0734 — the first seam suite repeated a historical equality selection

The first compatibility command selected two immutable predecessor equality
tests already known to compare the evolved attempt-003 controller against its
pre-attempt-003 digest. They correctly returned `evidence_not_current` and no
runtime or provider activity occurred.

Correction: the current descendant suite tests the immutable attempt terminal,
the accepted current controller and the new isolated seam without asking an
historical report to regenerate at a descendant source.

## AER-0735 — the first clockwork intent used invalid schema vocabulary

The read-only clockwork check rejected the non-admitted node kind
`architecture` and three string-valued `contract_evidence` entries before any
canonical mutation.

Correction: the node uses the admitted `tooling` kind and an empty typed
contract-evidence collection. The contract artifacts remain bound through
ordinary evidence and the baton acceptance list.

## AER-0736 — the restored receipt repeated machine-owned Git evidence

The first post-compaction runtime state repeated two full Git object IDs inside
descriptive source evidence. The orchestrator preflight correctly rejected the
receipt because its machine snapshot alone owns exact Git-ref evidence.

Correction: the descriptions retain the required source meaning without Git
objects, and a distinct corrected five-source receipt passes with zero manually
supplied object IDs.

## AER-0737 — two closeout observations used freehand stage labels

The next read-only clockwork validation rejected two descriptive incident-stage
labels that were not members of the fixed stage vocabulary. It stopped before
manifest command execution or canonical mutation.

Correction: both observations use the admitted `closeout` stage, and the
clockwork validator remains the vocabulary owner before transaction prepare.

## AER-0738 — the first publication omitted an explicit closed boundary

The first canonical publication derived a next-operation latch without the
explicit no ordinary-practice enablement, feature-flag, allowlist or command-
mounting token. The post-publication baton test rejected that generation.

Correction: the clockwork rolled the generation back byte-exactly, the only
input now restores the omitted boundary, and the same post-publication test
remains mandatory before commit.

All six observations were contained before closeout. None changes attempt 003,
authorises a runtime/provider action, or expands product, data, deployment,
Pages or protected-ref authority.
