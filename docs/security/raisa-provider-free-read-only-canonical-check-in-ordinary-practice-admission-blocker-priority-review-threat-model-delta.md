# Canonical check-in admission blocker-priority review — threat-model delta

Date: 2026-08-23

Status: `frozen`

## Scope

This provider-free review reads five accepted repository artifacts and emits a
dependency ranking. It adds no product or operational capability.

## Threats and controls

| Threat | Control |
|---|---|
| A synthetic or documentary artifact is promoted to a live fact | Retain all six external facts as `absent`; only independently observed target-bound evidence can change them. |
| More repository work is invented after the last prerequisite passed | Require `repository_prerequisites_remaining = 0` and admit only a non-actuating decision brief. |
| A downstream provisioning choice bypasses target selection | Enforce the exact five-rank dependency order and reject inversions. |
| Evidence acquisition silently authorizes ordinary activation | Keep activation as rank 5, separately confirmed after all evidence gates. |
| A model selects a target, custody owner or lasting scope | Preserve all five human choices as `unselected` and pause after the root-decision brief. |
| Old 6/3/3 evidence is mistaken for the current state | Bind both the original and latest accepted readings and reconcile them explicitly to 11/0/1. |
| A short or copied Git abbreviation binds the review | Machine-check only full 40-character commit objects and ancestry. |
| Review opens a provider, data or protected surface | Use only the five allowlisted text inputs; prohibit all external and product-runtime capabilities. |

## Residual risk

The review cannot prove operational readiness. It can only identify the root
decision and prevent repository ceremony from masquerading as the six absent
external facts. A real target, custody regime, provisioning authority,
independent readback and later activation confirmation remain outside this
tranche.
