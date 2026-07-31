# Threat-model delta: Reception One extended proposal runtime

Date: 2026-07-30

Scope: default-off authored-synthetic development proposal runtime

| Threat | Required control |
|---|---|
| A UI-supplied appointment UUID escapes practice scope | Resolve it only after authentication and exact practice filtering; replace it with a request-scoped HMAC handle before planner admission. |
| A selected appointment smuggles patient or clinical content | Frame allowlist is limited to opaque patient/practitioner/appointment refs, date, local time, duration and scheduling status. Exclude reasons, notes, contact details and all clinical fields. |
| A model converts a proposal into a command | Closed catalogue, `proposal_only` effect ceiling, deterministic review, no confirmation operators and no signed evidence in the model/typesetter envelope. |
| Move/resize bypasses conflict checks | Reuse the existing backend update-proposal service against fresh database truth after plan admission. |
| Cancellation becomes an irreversible delete | Reuse delete-proposal only; release warning/freshness findings without calling confirm or delete. |
| Squeeze-in silently overbooks or moves another patient | Policy fixes `allow_overbook=false`, `allow_move_existing=false`, `requires_human_review=true`; no mutation operation ID exists. |
| Stale selected context is replayed | Bind handle, request, correlation, practice, expiry and context revision; re-read the appointment before adapter output. |
| Raw identifiers or signed evidence leak to the Bureau/provider | Exact output schema carries opaque handles and allowlisted findings only; sanitize durable audit and browser evidence. |
| Live provider receives product context or credentials | Occupied frame is separately authored-synthetic; the cell has no ADC/API keys; the one-use broker alone holds the existing keyless impersonated ADC. |
| Endpoint, identity or cost drifts | Pre-call exact project/SA/model/region/hostname/IAM/audit gates, no fallback, one primary plus at most one contract repair and USD 1 total ceiling. |

Residual risk: this proves only authored-synthetic development behavior. It
does not establish privacy, residency, retention, usability or safety for real
patients or production operations.
