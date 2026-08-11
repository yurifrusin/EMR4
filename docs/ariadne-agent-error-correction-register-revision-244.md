# Ariadne agent error and correction register — revision 244

Date: 2026-08-11

Revision 244 records and closes AER-0277. The register now contains 277 bounded
known incidents.

## AER-0277 — CF-D2 pre-execution receipt event repaired

The first CF-D2 pre-execution runtime state used the descriptive event
`pre_execution`. That value is not present in the closed Ariadne continuation
event vocabulary. The deterministic preflight therefore returned
`revision_required` with `continuation_event_missing_or_unapproved`, admitted
no rehydration sources and prohibited dispatch.

The failure was detected before the runtime command. No Docker, PostgreSQL,
provider, product, network or other execution occurred, and immutable runtime
attempt 001 remains unconsumed. The failed state and receipt are preserved.

A distinct v2 state copies the admitted `pre_worker_dispatch` event directly
from `orchestration/harness_settings/orchestrator_requirements.yaml`, retains
the same five-source evidence and authority boundary, and must pass and be
committed before execution. Future receipts require a mechanical closed-enum
membership check before generation.
