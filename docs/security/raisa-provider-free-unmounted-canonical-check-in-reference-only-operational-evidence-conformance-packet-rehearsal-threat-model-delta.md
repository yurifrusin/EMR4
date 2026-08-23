# Threat-model delta — canonical check-in reference-only operational-evidence conformance packet

Date: 2026-08-23

Timestamp: 2026-08-23T14:40:30.0790284+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_delta`

## New seam

One repository fixture traverses four independently accepted pure components
for the first time. A satisfied evidence reading must remain distinct from an
ordinary-practice admission, and authored-synthetic references must never be
misrepresented as operational facts.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| The coordinator reimplements component semantics | Call the five accepted public functions directly; record their existing reason codes and add no alternate admission rule. |
| Synthetic references are promoted to live facts | Fix the packet class to `authored_synthetic_opaque_reference_only` and every result's external-fact status to `not_established`. |
| A secret enters evidence | Use only opaque references and identifiers; schema and recursive forbidden-field tests reject value/password/token/private-key/connection fields. |
| A satisfied gate admits ordinary practice | Require the exact ordinary terminal to remain `ordinary_activation_closed`; any admitted decision fails the rehearsal. |
| Snapshot substitution bypasses binding | Mutate both generation and digest and require `ordinary_evidence_missing`. |
| Ambiguous or stale manifest selection falls back | Provide no selection fallback; require `manifest_ambiguous` and `manifest_stale`. |
| Self-verification or duplicate evidence passes | Exercise explicit self-verifier, duplicate reference and duplicate artifact attacks under existing evaluator precedence. |
| Break glass becomes an allow path | Only inactive deny-only posture satisfies; `engaged_deny` remains a denial. |
| New test harness gains ambient capability | Permit repository fixture reads only; forbid environment, credential, network, database, subprocess, product route and filesystem writes in the rehearsal source. |
| Generic Harness work resumes accidentally | Make no worker/provider call and add no native-Harness diagnostic or adapter change. |
| Completion is confused with operational readiness | Retain six absent facts, five unselected human decisions and the 11/0/1 not-ready verdict. |

## Residual boundary

Passing completes only the last repository prerequisite. The next possible
work requires human-owned selection of a real target and operating policy.
Nothing in this packet authorizes those selections, lasting provisioning or
ordinary activation.
