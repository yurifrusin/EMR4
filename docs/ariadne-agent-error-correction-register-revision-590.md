# Ariadne agent error and correction register — revision 590

<!-- ariadne-agent-error-register-reading
revision: 590
incident_count: 795
new_incident_ids: AER-0792,AER-0793,AER-0794,AER-0795
open_incident_count: 0
-->

This revision note binds four corrected or contained observations to the clockwork-projected register. The canonical JSON register and pattern report remain clockwork-owned.

## AER-0792

The new source-repair validator initially imported its sibling `scripts` module before bootstrapping the repository root for direct invocation. Module-imported tests passed, but the direct evidence-generation command failed before writing evidence. The script now uses the repository's established root insertion before sibling imports, and direct invocation passes.

## AER-0793

The first post-repair surrounding packet included two tests frozen to the consumed pre-repair controller digest and one test frozen to the consumed attempt-004 latch. Their three expected failures did not invalidate the successor repair. An exact historical-test selection now preserves those assertions unchanged, excludes the real-Node fixture required to remain closed and passes every applicable selector.

## AER-0794

The register-closeout intent initially treated the next revision reading as if it were ordinary pre-existing evidence. Three clockwork dry runs rejected that assumption at the decision-source, incident-evidence and revision-reading surfaces without changing canonical state. The corrected typed shape binds decisions and incidents to existing evidence, pre-authors this exact revision reading and leaves canonical JSON/pattern projection to clockwork.

## AER-0795

A follow-up closeout-intent patch omitted one comma between JSON properties. The next clockwork check stopped during parsing before transaction preparation or canonical state change. The comma is restored, and the closeout now requires JSON parsing after every intent patch rather than only after initial authoring.
