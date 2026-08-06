# Provider-free unmounted authored-synthetic observation-to-temporal-signal rehearsal design

Date: 2026-08-06

Status: frozen bounded implementation design

## Purpose

This rehearsal implements the pure membrane between source-shaped control
metadata and the accepted temporal classifier. It neither observes a source nor
owns context truth. Its only positive output is an existing sealed temporal
signal whose impact has been reconstructed from backend policy and registry
state.

## Trusted and untrusted values

The authored-synthetic source fixture is untrusted even though the repository
authors it. Trusted inputs are the exact sealed policy, observer binding,
backend alias registry, impact policy, synthetic-only activation, caller-
supplied backend clock and in-memory HMAC key. The proofreader reconstructs
those trusted objects from canonical builders; a supplied copy never becomes
authoritative merely because its seal is internally valid.

## Normalisation membrane

The source-shaped input is recursively closed before use. Its raw event id is a
non-semantic transport coordinate constrained by an exact ASCII grammar and
length ceiling. Trusted code derives a domain-separated keyed digest binding
source contract, observer generation and raw id, then drops the raw value. The
admitted observation contains no patient, person, appointment, practitioner,
location, time-slot, field, selector, correlation, reason, payload or callback
value.

Backend aliases are opaque handles with a closed grammar. Resolution requires
the exact registry digest and equality across practice binding, source system,
source contract and aggregate class. Registry entries—not source values—may
resolve the synthetic aggregate, location and practitioner references required
by the accepted temporal signal constructor.

## Impact ownership

The impact policy binds an exact event/schema/aggregate triple to a non-empty
minimum set of accepted temporal frame types. The signal's affected frame set
is the union of that floor and registry-derived impact. The source input has no
impact field, so omission cannot narrow classification. An absent route,
unresolvable alias or inconsistent registry returns bounded full invalidation
and cannot produce an ordinary signal or an `IRRELEVANT` result.

## Disabled policy and synthetic activation

Policy is and remains disabled. The test-only activation is a distinct sealed
coordinate accepted by only the pure rehearsal function, only with
`AUTHORED_SYNTHETIC` evidence, and only while all source/runtime/authority flags
are false. It changes no policy field and cannot be passed to a future live
observer. Without it, admission deterministically returns
`OBSERVER_DISABLED` before temporal construction.

## Admission and continuity

Admission compares exact prior observation coordinates supplied as inert
function input. Exact duplicate identity suppresses as duplicate; an older
position suppresses as replay. Missing baseline, predecessor mismatch,
position gap, revision gap, overflow or restart uncertainty returns
`FULL_INVALIDATION_REQUIRED` without advancing any cursor. No decision is
persisted in this rehearsal.

The emitted design-time continuity requirement states what a later runtime must
atomically persist, but every present effect flag is false. Observed coordinates
are not a durable checkpoint and success makes no no-loss or crash-recovery
claim.

## Temporal handoff

Only `ADMIT_SIGNAL` reaches the accepted public `make_signal` constructor. The
observation digest becomes signal identity; registry resolution supplies
aggregate and selector references; the policy floor supplies frame types; and
trusted clock values supply receipt/expiry. The sealed handoff trace binds the
complete provenance chain and is ineligible as a read grant.

The accepted `process_signals` function alone intersects the signal with a
session-bound manifest and watch lease. Its output may retire the immutable
frame set and emit an inert reassembly requirement, but this rehearsal never
calls a source adapter or admits new context.

## Proofreader

The proofreader rebuilds the canonical policy, binding, registry, impact,
activation, input normalisation, admission, signal, temporal result and traces
from authoritative synthetic inputs. It releases only exact equality while all
objects remain unexpired and every authority/effect ceiling is false. A
resealed substitution, widened impact, narrowed floor, leaked raw id/key or
different temporal result blocks the whole packet.

## Non-authority statement

The design adds no live source, database, event delivery, credential, durable
state, product read, patient data, provider, command, route, deployment or
production authority. It proves a deterministic contract only.
