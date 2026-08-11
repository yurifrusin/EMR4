# Ariadne agent error and correction register — revision 226

Date: 2026-08-11

Revision 226 adds and closes AER-0260. The register now contains 260 bounded
known incidents.

## AER-0260 — AES-C4 pre-dispatch profile mismatch

The first AES-C4 verifier pre-dispatch state used an unconfigured Antigravity
adapter observation method, added a Gemini worker-slot inventory not present in
the accepted runtime profile and declared a workspace receipt without a
matching configured inventory. The orchestrator receipt returned
`revision_required` with all three exact reasons. No verifier, provider or
external mutation started and candidate HEAD `743c6354eadd3661d668bb0d567e0693d4b32e9c`
remained unchanged.

Sol preserved the invalid runtime state and receipt, recovered the exact
current Antigravity observation shape from a passing repository example and
repeated the complete receipt with `agy_cli_observation`, the required
DeepSeek-slot inventory, no invented workspace receipt and no assigned agent
ID. Only the corrected passing receipt may authorize dispatch.
