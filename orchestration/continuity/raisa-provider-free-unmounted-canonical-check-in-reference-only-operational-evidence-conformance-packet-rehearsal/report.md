# Canonical check-in reference-only conformance packet report

Date: 2026-08-23

Timestamp: 2026-08-23T15:13:47.3927515+10:00 (Australia/Brisbane)

Result: `raisa_provider_free_unmounted_canonical_check_in_reference_only_operational_evidence_conformance_packet_rehearsal_pass`

The authored-synthetic packet normalized and satisfied the evidence gate,
then remained denied at `ordinary_activation_closed`. It established no
operational fact and released no ordinary-practice admission.

| Hostile case | Evidence-gate reason | Admission reason |
|---|---|---|
| `manifest_absent` | `manifest_absent` | `ordinary_evidence_missing` |
| `manifest_ambiguous` | `manifest_ambiguous` | `ordinary_evidence_missing` |
| `manifest_secret_material` | `manifest_invalid` | `ordinary_evidence_missing` |
| `evidence_boolean_claim` | `role_evidence_invalid` | `ordinary_evidence_missing` |
| `manifest_stale` | `manifest_stale` | `ordinary_evidence_missing` |
| `wrong_environment` | `environment_mismatch` | `ordinary_evidence_missing` |
| `wrong_role` | `role_binding_missing` | `ordinary_evidence_missing` |
| `self_verified_role` | `role_evidence_invalid` | `ordinary_evidence_missing` |
| `duplicate_evidence_reference` | `rotation_evidence_invalid` | `ordinary_evidence_missing` |
| `rotation_key_mismatch` | `secret_reference_invalid` | `ordinary_evidence_missing` |
| `break_glass_engaged` | `break_glass_not_inactive` | `ordinary_evidence_missing` |
| `snapshot_binding_mismatch` | `evidence_gate_satisfied` | `ordinary_evidence_missing` |

Readiness remains exactly 11 satisfied / 0 blocking / 1 operational
evidence gap. Six external facts remain absent and five human choices
remain unselected. No API, route, product, provider, runtime, deployment
or protected-ref surface changed.
