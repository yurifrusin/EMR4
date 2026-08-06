# Sol admission rejection — observation-to-temporal-signal candidate

Date: 2026-08-06

Decision: `revision_required`

Rejected worker HEAD:
`594715bfd3487515d8cf6f5ace08182c1d74ae64`

Implementation commit:
`b7e8ecc9bfe65c547435bff1b100c7ff1600fc4e`

## Finding

The canonical packet and same-packet proofreader were strict, but the public
admission seam did not enforce every frozen exact field in its sealed trusted
policy, binding, alias-registry, impact-policy and activation inputs. A caller
could coordinate new seals and related digests around an authority-widened
registry or impact policy, including `command_authority: true`, and still reach
`ADMIT_SIGNAL`. Several schema, id, version, closed-list and authority fields
had the same direct-validator gap. The source validator could also expose a
plain `TypeError` for a non-string raw event id, and the public mapping seam
needed an equivalent cross-link audit.

This contradicts the frozen exact-contract and zero-authority boundaries even
though the final canonical proofreader would block a modified release packet.
No candidate was integrated, accepted, pushed or released.

## Required correction

The existing bounded worker lane must enforce exact closed trusted-contract
semantics while preserving the intended expired, revoked and continuity
decisions; reject malformed source/prior types through the contract exception;
close any equivalent mapping-seam substitution; add direct adversarial tests;
regenerate only owned deterministic artifacts; and rerun the complete focused
and inherited serial verification packet. A fresh independent veto remains
mandatory after Sol admits the corrected implementation.

## Boundary reconciliation

No database, source, feed, watcher, listener, persistence, product read,
patient/product/protected data, provider, command execution, API/app route,
deployment, production, release, Pages or protected-ref surface was opened.
The worker worktree remained isolated and the main task worktree remained
tracked-clean apart from this preservation record and pre-existing allowed
continuity artifacts.
