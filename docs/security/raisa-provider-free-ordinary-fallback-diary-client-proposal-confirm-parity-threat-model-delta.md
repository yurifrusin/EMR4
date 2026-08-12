# Threat-model delta: ordinary/fallback Diary client proposal-confirm parity

Date: 2026-08-12

Parent:
`docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-plan.md`

## Changed surface

The native Diary stops selecting seven raw compatibility mutations and sends
proposal-attempt idempotency headers on every proposal family it uses. Backend
route behavior is unchanged.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A fresh block appears after staff confirmed an earlier warning | Blocks are evaluated on every proposal response, including the second Save click. |
| Warning drift is silently accepted | The exact warning-code set shown is stored and compared with the fresh set; changed warnings require renewed review. |
| Missing signed evidence downgrades to a raw mutation | Every client mutation helper rejects a missing endpoint/payload; raw fallbacks are absent. |
| A proposal request is rejected because its header is absent | Every native proposal request sends a non-empty per-gesture `Idempotency-Key`. |
| A failed signed confirm falls back to compatibility behavior | Confirm failures and non-`confirmed_write` results throw and perform no raw request. |
| A post-create/update status failure is mistaken for total rollback | The client explicitly reports that booking details were saved but status was not applied. |
| Client parity is mistaken for route retirement safety | Compatibility routes remain mounted and `audit` remains the default; declarations deny external-consumer and release readiness. |
| Delete endpoint absence becomes authority to raw-delete | The existing 404 branch may use only the signed status proposal/confirm family. |

## Residual gates

The two-step create/update-plus-status flow is not atomic. External raw-route
consumers are not inventoried, the four compatibility handlers do not yet share
one conditional-command kernel, and create serialization, route retirement,
header rollout, deployment and production remain unproved.
