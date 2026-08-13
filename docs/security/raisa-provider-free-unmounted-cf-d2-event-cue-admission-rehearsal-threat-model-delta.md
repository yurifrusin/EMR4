# Threat-model delta — unmounted CF-D2 event and cue admission rehearsal

Date: 2026-08-13

Timestamp: 2026-08-13T16:42:39+10:00 (Australia/Brisbane)

Status: `provider_free_unmounted_pure_state_only`

## Assets protected

- source-owned Diary truth and backend command authority;
- partition, epoch, position and lease-generation integrity;
- immutable terminal classification and cue-obligation identity;
- contiguous checkpoint meaning;
- payload-free operator evidence; and
- the separation between one fresh-read attempt and durable freshness.

## New exercised boundary

The rehearsal admits authored-synthetic transition candidates into an
ephemeral in-memory state object. The boundary ends before persistence,
transport, source observation or application wiring. The runner may serialize
only normalized rehearsal evidence; it may not serialize operational state.

## Threats and controls

| Threat | Control |
|---|---|
| Extra payload smuggles appointment or person truth into a cue | Closed candidate field set and explicit prohibited-field rejection before mutation |
| Duplicate creates a second receipt or obligation | Stable identity/fingerprint comparison and original-object reuse |
| Divergent content reuses an occupied position | `identity_conflict`; normalized state must remain byte-identical |
| Out-of-order event skips unseen work | Checkpoint walks only the next contiguous terminal position |
| Required cue is lost while checkpoint moves | Receipt and obligation are one admission transition; deliberate no-obligation candidate rejects atomically |
| Unsupported event creates a cue | Rejected terminal receipt carries no obligation |
| Coalescing erases coverage or joins unrelated work | Only adjacent pending same-reason obligations merge; endpoints remain explicit |
| Stale active/standby owner mutates state | Every transition compares an exact positive lease generation and rejects stale/equal competitors |
| Unknown or cross-epoch lag appears healthy | Non-numeric `unknown` and `epoch_mismatch` results; zero exists only as an exact same-epoch calculation |
| Cue changes display without current truth | Projection outcomes require authorised fresh scoped read; typed failures retain the prior display |
| Test harness is mistaken for persistence or restart evidence | Pure in-memory implementation, explicit effect flags and no database/process/source APIs |

## Residual risk

Python object behavior does not prove a PostgreSQL representation, transaction,
crash boundary, unknown-commit recovery, lease service, dispatch transport,
retention policy, latency or operations. A later representation must preserve
these exact transitions without importing authority from the rehearsal.

## Closed surfaces

No protected evidence, historical Diary/PHI, product/patient/clinical data,
watcher, database/source, persistence, operational retention, provider/ADC,
credential/IAM/network, executable tool, command/write, route, deployment,
production, release, Pages or protected-ref authority is opened.
