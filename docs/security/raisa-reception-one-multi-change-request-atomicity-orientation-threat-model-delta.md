# Reception One multi-change request atomicity orientation threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T19:45:27+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted selected-action-console composition at reviewed
source `1d9e58fd2624f87b8b3def538297054999e7bef3` and closeout commit
`f362f0de378fdddb610a04ae61182aaae2c105c0`

## Changed surface

No runtime changes. The orientation classifies how several requested appointment
changes and future channel-originated interpretations may be represented before
any proposal or confirmation.

## Threats and required controls

| Threat | Required control |
|---|---|
| The provider model is treated as physically clicking a trusted UI control | Buttons are human presentation affordances; a provider or adapter may emit only a typed inert candidate that passes deterministic admission. |
| Siri, email, SMS or another channel inherits the recipient's application authority | Channel possession, identity, authenticated principal, confirmer and command authority remain separate facts; no adapter runtime is opened. |
| Several same-family changes become several partial writes | Compose admitted time, duration and practitioner values into one existing update-family proposal and one explicit confirmation; forbid automatic single-field sequencing. |
| A status-plus-update request is falsely described as atomic | Classify it `cross_family`, disclose that no current all-or-nothing command exists and keep the review plan non-executable. |
| Separate confirmations imply rollback or success of the remaining action | Re-propose each later action against fresh truth and state explicitly that each confirmed command is independently committed. |
| A failed second action leaves a hidden partial outcome | Surface the first committed result as truth and the later block as a separate outcome; never collapse them into one success/failure label. |
| Contradictory values are resolved by model confidence or list order | Deterministically require clarification for more than one value per field or an ambiguous target. |
| Requested values contaminate current truth | Keep candidates and proposals labelled provisional; only fresh source readback supplies committed display values. |
| A complex button becomes a generic tool or command dispatcher | Treat complex affordances as typed presentation macros over allowlisted action meaning; grant no route, tool or write capability. |
| Model-generated field names broaden the update schema | Admit only the exact closed action and field vocabulary; unknown or unsupported fields fail closed. |
| Status authority leaks into the update family | Preserve the distinct status proposal/confirm family and its vocabulary; do not place status inside an update patch by convention. |
| An event or Context Frame is mistaken for command evidence | Treat events as acceleration hints and frames as expiring evidence; confirmation rechecks current authority and authoritative source truth. |
| Voice ambiguity or spoken PHI creates unsafe confirmation | Voice remains future-closed; any later design must add confidence, privacy, replay, liveness and secure confirmation gates without changing this command boundary. |
| Read-only orientation is mistaken for implemented adapter safety | Label all evidence `repository_static_authored_synthetic` and make no runtime, usability or production claim. |

## Residual boundary

The current update contract is structurally multi-field, but this tranche must
report exactly which combined-field and transactional properties are already
tested. It cannot infer a new UI, a status-plus-update transaction, an adapter
authentication design or real-world safety from source shape alone.

A future adapter may open or populate an editor only after a separate typed
admission and identity design. A future all-or-nothing cross-family action
requires its own kernel command, conflict/freshness domain, idempotency, audit,
rollback and database proof.
