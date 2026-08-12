# Provider-free ordinary/fallback Diary client proposal-confirm parity design

Date: 2026-08-12

Parent: `docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-plan.md`

## Client flow

```text
staff gesture
  -> proposal request + per-gesture Idempotency-Key
  -> block/warning review against the fresh proposal
  -> require allowlisted confirm endpoint + signed payload
  -> signed confirm + confirm Idempotency-Key
  -> accept only confirmed_write appointment result
```

There is no arrow from missing evidence or a rejected confirm to a raw
compatibility write.

## Booking-modal warning state

The Save button owns a proposal-attempt key and the exact warning-code set last
shown to the user. A second click re-runs the proposal. Blocks always win. A
different warning-code set replaces the displayed warning state and requires a
new click. Only an identical fresh warning set may proceed as confirmed.

Changing any booking input uses the existing reset hook, which clears the
proposal key, confirm key and warning-code state.

## Follow-up status step

Create and update confirmation do not accept status in their command contract.
The client therefore preserves the current sequential behavior:

```text
confirmed create/update
  -> status proposal for returned/target appointment
  -> optional warning/terminal dialogue
  -> signed status confirm
```

The base write and status write are distinct committed commands. The design
does not claim atomicity across them. A failure after the base confirmation is
reported as a partial outcome so staff can refresh against current truth.

## Compatibility boundary

The native client no longer selects the raw routes. The FastAPI route
decorators, handlers, raw-compat evidence tags, default audit signal and route
tests remain intact. This is client parity evidence only; unknown external
consumers and retirement prerequisites remain unresolved.
