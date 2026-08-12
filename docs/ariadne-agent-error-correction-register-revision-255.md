# Ariadne agent error and correction register — revision 255

Date: 2026-08-12

Revision 255 records and corrects AER-0287 and AER-0288. The register now
contains 288 bounded known incidents with none open.

AER-0287 preserves the first final-review predispatch state. It used the
unconfigured method `command_preflight` for the Antigravity adapter and omitted
the configured inactive DeepSeek worker-slot inventory. Orchestrator preflight
returned `revision_required`; no reviewer was dispatched. A distinct v2 state
uses configured `agy_cli_observation`, includes the mandatory slot inventory and
passes without changing the candidate.

AER-0288 preserves the subsequent provider-schema admission failure. The new
command-results schema used tuple-only `prefixItems`; Antigravity reached the
configured Gemini lane, but the provider returned HTTP 400 because its tool
schema requires an explicit array `items` field. No model review, command,
candidate mutation or review receipt resulted. The repair presents a uniform,
provider-admissible item schema. Exact command IDs, argv arrays, ordering and
zero exit codes remain enforced deterministically by the local admission gate,
where that stronger invariant belongs.
