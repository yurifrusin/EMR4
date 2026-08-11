# Ariadne agent error and correction register — revision 225

Date: 2026-08-11

Revision 225 adds and closes AER-0259. The register now contains 259 bounded
known incidents.

## AER-0259 — invalid AES-C4 continuation-event vocabulary

The first AES-C4 preplanning receipt attempt used inferred event label
`pre_plan` instead of the configured `pre_sprint_planning` value. The
orchestrator preflight returned `revision_required`; no evidence from that
attempt was admitted and no dispatch, provider call or external mutation
followed it.

Sol preserved the observation, repeated the full receipt attempt using the
exact configured vocabulary and admitted only the resulting passing receipt.
The prevention control requires every future event to be copied from the
configured schema or a current passing repository example rather than inferred
from prose.
