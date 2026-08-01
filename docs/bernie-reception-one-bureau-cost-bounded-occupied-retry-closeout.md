# Reception One Bureau cost-bounded occupied retry closeout

Status: failed closed before provider transport
Recorded: 2026-07-31

The attempt did not call Vertex. The inner v6.8 pre-call gate rejected the new
outer authority manifest because it lacked the legacy compatibility fields
`decision=authorised_by_yuri` and `requested_exact_boundary`. That gate runs
before provider-ledger creation, broker or container start, token refresh or
provider transport. The artifact directory accordingly contains only the
two-event parent dialogue audit and sanitized frame manifest.

The outer UI harness then attempted to validate a runtime audit reference on
the HTTP 502 error object and reported the less useful
`runtime_audit_ref_invalid`. The independently reproduced inner code is
`occupied_authority_missing`.

No prompt or payload reached Vertex. No provider ledger, external audit,
provider response, token usage, credential material, fallback, confirmation
or write exists. The exact disposable database, runtime processes and
temporary runtime directory were removed, and the independent container,
image, network, database and port residue check passes.

The cumulative ledger remains terminal and conservatively charges the full
USD 0.02 reservation. No refund or credit is claimed. A successor may proceed
only with a distinct authority manifest, identifiers, ledgers and output
directory, a focused inner-gate regression, complete regating, and cumulative
accounting beginning at USD 0.0238049.

This result proves a repository-local authority-contract mismatch and safe
cleanup. It proves no model behavior, Vertex request or Australian processing.
