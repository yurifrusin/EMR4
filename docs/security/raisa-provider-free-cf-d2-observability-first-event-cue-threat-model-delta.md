# Threat-model delta — CF-D2 observability-first event and cue architecture

Date: 2026-08-13

Timestamp: 2026-08-13T16:04:58+10:00 (Australia/Brisbane)

Status: `provider_free_unmounted_architecture_only`

## Assets protected

- authoritative Diary truth and command authority;
- practice isolation;
- contiguous source/checkpoint meaning;
- durable cue obligation identity and coverage;
- operator evidence integrity; and
- the privacy boundary between payload-free cues and patient/product data.

## New trust boundary

The proposed future boundary is between a source-owned committed event
position, one fenced logical observer, a durable payload-free cue obligation
and a Reception One consumer that performs a fresh authorised read. This
tranche models that boundary only; it starts none of those components.

## Threats and controls

| Threat | Control |
|---|---|
| Event or cue treated as current truth or write grant | Exact authority-plane denial; fresh authorised read and command-time recheck remain mandatory |
| Missed position hidden as success | Checkpoint cannot cross a gap or absent terminal receipt |
| Required cue lost while checkpoint advances | Receipt and required obligation must be atomically bound before checkpoint eligibility |
| Duplicate or out-of-order delivery causes repeated effect | Stable observation and obligation identities; idempotent reuse; contiguous checkpoint |
| Poison or unsupported event blocks invisibly | Immutable `rejected_unsupported` receipt with allowlisted reason and operator attention |
| Two observers advance the same partition | External lease generation and fencing; stale generation rejects checkpoint write |
| Lag is understated after missing observation or epoch change | Typed `unknown` and `epoch_mismatch`; neither may serialize as zero |
| Cue leaks appointment or patient content | Closed minimal fields; no resource/person identifier, status, time, free text or payload |
| Delivery acknowledgement is mistaken for durable freshness | Reconciliation records one fresh-read attempt only and confers no ongoing freshness |
| Diagnostic repeats CF-D2 ambiguity | One-to-one stage evidence; correction ineligible until remaining hypotheses have distinct outcomes |
| Architecture artifact silently opens runtime | Explicit false runtime/database/source/network/provider/command/deployment flags and hostile mutation tests |

## Residual risk

The contract has not been represented in PostgreSQL or exercised across a
process restart. Its future source epoch, lease, retention and integration-
principal mechanisms remain design choices requiring separate evidence. A
practice-wide payload-free cue may refresh more UI than strictly necessary;
that is an accepted privacy-favouring first tradeoff, not an authority change.

## Closed surfaces

No protected evidence, historical Diary/PHI, product/patient/clinical data,
watcher, database/source, persistence, operational retention, provider/ADC,
credential/IAM/network, executable tool, command/write, route, deployment,
production, release, Pages or protected-ref authority is opened.
