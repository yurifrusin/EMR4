# Threat-model delta — read-only status-confirm runtime-gap admission review

Date: 2026-08-12

This tranche adds no runtime attack surface. Its primary risks are accidental
runtime authorisation from documentation, incomplete source selection,
protected-scope discovery recurrence, softening a blocking mismatch into a
readiness claim, and treating historical/elapsed tests as current proof.

Controls are an exact hash-bound non-protected allowlist, nine closed review
dimensions, citation-required findings, deterministic blocker precedence,
hostile mutation rejection, no application import, and an explicit
`implementation_authorized: false` invariant for every verdict. A missing
source, hash mismatch or uncertain material fact stops the review. AER-0291
forbids broad search and its exposed content contributes no evidence.

No route, database, product data, provider, network, command, deployment,
release, Pages or protected-ref capability is opened.
