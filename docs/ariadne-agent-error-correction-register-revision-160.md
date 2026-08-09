# Ariadne agent error and correction register revision 160

Date: 2026-08-10

## Change

Revision 160 adds `AER-0186`, a repository-origin behavior-fixture defect found
by provider-free disposable PostgreSQL attempt 033. `BTR-E03` supplied the
outbox row's `source_contract_digest` where the accepted body required the
canonical `source_membership_digest_v1` over all eleven fields of that same
immutable row. The admission guard correctly returned `CF201`; the exact owned
container was removed and its absence verified, and zero scenarios were
admitted.

The correction derives the packet digest from the accepted typed body node and
renderer, requires the exact rendered expression in the bound inert artifact
and independently recomputes it for readback. It changes no database body,
scenario, SQLSTATE, principal, authority or runtime boundary.

## State

The register contains 186 incidents with none open after this correction. The
repair remains pending complete deterministic and fresh independent acceptance
before another database attempt.
