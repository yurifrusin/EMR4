# Ariadne agent error and correction register — revision 620

Date: 2026-08-22

Timestamp: 2026-08-22T17:43:07.7749502+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 620
incident_count: 966
new_incident_ids: AER-0965,AER-0966
open_incident_count: 0
-->

This revision adds two bounded, corrected clockwork-input observations from the
integrated-runner stock-headless closeout. The check rejected before generation
construction or publication, so every canonical surface and accepted source
remained unchanged.

## AER-0965 — descriptive successor boundary omitted the exact typed floor value

The first closeout intent described the ordinary-practice closure as
`no_ordinary_practice_enablement_or_live_product_runtime`. That meaning was
narrowly appropriate but it did not also carry the clockwork's exact required
closed-vocabulary value
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
The validator therefore returned `tick_next_boundaries_floor` before preparing
a generation.

The correction restores the exact required value and retains the useful
successor-specific constraints separately. Future intents must start their
boundary list from the deterministic `REQUIRED_NEXT_BOUNDARIES` typed floor and
only then append narrower tranche-specific values.

## AER-0966 — incident stage was reconstructed as an unregistered description

The second closeout check described AER-0965's stage as
`governance_validation`. The meaning was clear but the incident schema permits
only its closed set of stages, including `closeout`. The validator therefore
returned `tick_incident_stage` before prospective register projection or any
generation write.

The correction selects the exact `closeout` value. Future incident records must
take this field directly from `INCIDENT_STAGES`; a model should never be asked
to reproduce this vocabulary freely.

## Register reading

These failures are evidence for the user's concern about form-filling lapses. The
right response is not another instruction to remember a phrase: the clockwork
already denied both near-synonyms, and the new durable rules make both finite
sets construction inputs rather than prose reconstructed from memory.
