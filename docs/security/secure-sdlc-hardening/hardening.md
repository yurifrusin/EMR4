# Security Hardening Review: EMR4 delivery control plane

## Evidence Basis

I inspected the API Spine/security contracts, the repository's security
workflows, and point-in-time GitHub security state recorded in
`evidence-manifest.json`. The evidence shows strong detection and authority
design, but a gap between documented protected integration and the controls
GitHub technically enforces. CodeQL candidates are treated as unvalidated
signals, not confirmed vulnerabilities.

## Constraints

The recommended change must preserve Sol's protected integration authority,
avoid opening any Bernie holdout/provider/write gate, retain economical CI,
and permit emergency recovery. Changing GitHub repository protection affects
an external system and therefore remains a user decision.

## Opportunity Portfolio

| Opportunity | Evidence | Options | Recommendation | Proposal |
| --- | --- | --- | --- | --- |
| Enforce the delivery security boundary | Unprotected `master`, push protection off, untriaged high CodeQL candidates, existing strong scanners (E001-E005) | Keep advisory controls; enforce protected integration and response gates | Enforce gates after alert triage and an emergency-path rehearsal | [Delivery control plane](proposals/secure-delivery-control-plane.md) |

## Recommendation Summary

I recommend the enforced-gates option under current constraints. The scanners
already generate useful evidence; the missing control is preventing a change
from bypassing that evidence and ensuring alerts acquire owners and decisions.
We should first triage the ten high CodeQL candidates so that required checks
are based on understood signal, then enable branch and secret push protection
with a tested break-glass route.

## Next Decisions

- Authorize a bounded CodeQL high-alert validation sprint.
- Approve or decline GitHub `master` branch protection and secret-scanning
  push protection after the proposed required-check set is confirmed.
- Select vulnerability-response SLAs and the break-glass approver/recording
  rule.
