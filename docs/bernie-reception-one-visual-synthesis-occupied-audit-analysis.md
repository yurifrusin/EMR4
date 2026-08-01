# Reception One visual synthesis occupied-call audit analysis

## Disposition

`revision_required`

The single primary occupied design-synthesis call reached the exact authorised
Sydney Vertex endpoint and returned HTTP 200. The deterministic proofreader
then rejected the candidate with `priority_order_invalid`. The broker released
no candidate field and the occupied cell exited fail-closed.

## Deterministic findings

- The call used `gemini-2.5-flash`, project `bernie-emr4-dev`, the exact Bernie
  service account, keyless impersonated ADC and
  `australia-southeast1-aiplatform.googleapis.com`.
- API-key authentication and provider or regional fallback were not used.
- The provider reported 693 prompt tokens, 493 candidate tokens and 1,186 total
  tokens with 2,986 ms latency.
- The eight-event external audit chain verifies through
  `sha256:eabdababc968d39032e8265a26f92a5c89413be6876d0341c1134022898e8963`.
- Mechanical sorting of evidence and risk identifiers was safe-repairable, but
  the priority-order finding was not.
- The single-use ledger is consumed after exactly one reserved provider call.
- Cleanup records no task container, relay, network, image, broker process,
  temporary token or temporary build context.

## Retry decision

No retry is permitted. The frozen conditional second call applies only to a
deterministic request-construction defect. This call returned a candidate under
HTTP 200 and failed the semantic output contract, so changing or relaxing the
proofreader, retaining the rejected candidate, or spending the repair ledger
would exceed the admitted boundary.

## What this proves

The evidence proves that one authored-synthetic request traversed the exact
configured Australian Vertex locational endpoint through the accepted
keyless-impersonation and isolation boundary, and that the egress gate rejected
an invalid typed draft without releasing it.

It does not prove that Vertex supplied an admissible Reception One design,
physical or sovereign Australian processing, production readiness, clinical or
scheduling correctness, representative-staff usability, or authority for a
model to inhabit or operate the Reception One UI.
