# Ariadne agent-error register revision 9

Date: 2026-08-04

Status: A3/B3 terminal-accounting correction, evidence-only reconciliation and
deterministic acceptance complete; fresh independent acceptance pending

## AER-0017: terminal broker rejection split child and parent accounting

After the restored Bernie ADC passed every read-only control, Rayleen A3
transmitted one authored-synthetic request through the exact Sydney Vertex
boundary. The child ledger consumed one call and the hash-chained audit ended
at `provider_content_invalid` before candidate extraction or proofreading.
Nothing was released and Davida did not start.

The broker failure was correctly fail-closed, but the outer harness required a
`proofreader_completed` event on every path. It therefore reported the less
specific `audit_event_cardinality_invalid`, wrote no occupied attempt/tranche
evidence and left the parent ledger at zero consumed calls even though the
child ledger had consumed one. The immutable interruption evidence preserves
that exact split and its source hashes.

The correction treats a narrowly allowlisted provider-content shape rejection
as terminal before proofreading, never as `schema_invalid` correction
authority. Future broker responses preserve the exact reason and allowlisted
provider metadata, while the live harness writes no-release cleanup evidence,
reconciles parent consumption from the validated child attempt and closes the
tranche before any later lane. A separate evidence-only finalizer repairs the
already consumed attempt without touching credentials, sending another prompt
or starting Davida.

That finalizer has now closed the parent ledger at exactly one reserved and one
consumed call at USD 0.25, emitted terminal no-release attempt and tranche
evidence, and proved current exact runtime absence. The finalizer and acceptance
made zero provider calls; the acceptance evidence separately records the one
historical candidate-runtime provider call. AER-0017 remains open until the
fresh exact-HEAD independent veto passes.

No surviving evidence identifies the underlying provider-response subshape or
cause. In particular, a possible default-thinking/output-budget interaction is
an inference only. Changing `thinkingConfig`, the request hash or retry policy
would be a new material request-contract decision and is not authorised by
this correction.
