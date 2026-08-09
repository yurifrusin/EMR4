# Ariadne agent error and correction register revision 132

Date: 2026-08-09

Status: bounded register correction candidate

Revision 132 adds AER-0157 and brings the register to 157 bounded incidents
with zero open incidents.

## AER-0157 — invalid Antigravity observation method in verifier acceptance

The first post-veto acceptance state correctly described the one fresh clean
Gemini 3.6 Flash/high pass but used descriptive method
`verifier_runtime_receipt` for `antigravity_cli_print`. That value is not in
the adapter's closed method allowlist. The deterministic Ariadne preflight
therefore returned `revision_required` with
`adapter_probe_method_invalid:antigravity_cli_print` before Sol accepted the
review or started behavior attempt 024.

The failed state and receipt remain immutable. The distinct corrected state
uses the admitted `agy_cli_observation` method while retaining the same five
sources, exact clean candidate, terminal verifier receipt and closed behavior
runtime boundary. This is related to AER-0154's adapter-pair mistake; the
prevention control now requires copying the complete adapter ID/method pair
from `orchestration/harness_settings/transport_adapters.yaml` before drafting
descriptive evidence.
