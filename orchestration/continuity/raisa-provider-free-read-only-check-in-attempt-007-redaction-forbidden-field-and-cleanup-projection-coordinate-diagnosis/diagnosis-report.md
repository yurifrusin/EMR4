# Check-in attempt-007 redaction and cleanup-projection diagnosis report

Date: 2026-08-23

Timestamp: 2026-08-23T03:59:56.1228656+10:00 (Australia/Brisbane)

Status: `passed_read_only_diagnosis`

Evidence SHA-256:
`b6d473d20fa64757fc25fbd2eb4f1792d86ebc91e3f0a8bf5bb3c9bdcc62d8e4`

## Conclusion

Attempt 007 did not fail in the database lifecycle coordinate that stopped
attempt 006. It reached a later post-cleanup evidence-publication coordinate.
The exact parent result shape contains 67 statically bound key paths. Exactly
one conflicts with the source-owned forbidden-field predicate:

`closed_boundaries.live_secret_existing_hosted_or_product_database_used`

The predicate mechanically returns `redaction/forbidden_field` because the
leaf key contains the closed token `secret`. The predicate is working as
written; the prospective success projection was never tested against it during
static admission.

## Exact control flow

The base harness constructs the successful result inside its lifecycle
`try`, finalizes the cleanup projection in the corresponding `finally`, and
then calls final result redaction after that `try/finally` statement. Its
earlier `RehearsalFailure` handler does not cover that later call. The redaction
failure therefore escapes after cleanup has been calculated.

The attempt-007 wrapper catches the escaped typed failure, passes it to its
failure writer, and calls `_sanitized_failure`. That function supplies the
literal projection `{"status": "not_started"}` to the base failure-evidence
builder. A deterministic in-process fake reproduces the terminal stage, code
and cleanup value exactly. The wrapper is not reading or preserving the base
harness's finalized cleanup object.

## Smallest deterministic repair

The next repair should contain two inseparable gears:

1. `prospective_success_projection_static_gate` — build the complete final
   success-evidence structural projection during static admission and run it,
   including every contract-derived key, through the exact final redaction
   predicate before any occupied work. Safely rename or project the one
   conflicting closed-boundary field without weakening the predicate or
   changing its false/default-denial meaning.
2. `typed_post_finalization_terminal_bridge` — make the base harness convert
   post-cleanup redaction or schema failure into sanitised failure evidence
   carrying only its already-finalized cleanup projection. The wrapper must
   consume that typed projection and must not substitute an invented cleanup
   state.

Hostile tests must inject new exact-token, prefix and suffix conflicts and
prove rejection during static admission. They must also force a late
post-finalization failure and prove the exact finalized cleanup projection is
retained.

## Claim boundary

This read-only result proves the prospective forbidden-field collision, the
post-cleanup escape coordinate and the wrapper's deterministic cleanup
collapse. It does not prove rollback, unknown-response commit recovery,
transaction membership, role absence before teardown, internal cleanup
history or a successful attempt-007 result. The accepted predecessor's
independent zero-owned-Docker-resource observation remains separate evidence.

No Docker object, PostgreSQL process, SQL, database operation, worker,
provider, product path or protected evidence was used. Attempt 008 remains
closed. Dedicated check-in remains default-off, and no API, route, grammar,
client, waiting-area, production, deployment, release, Pages or protected-ref
authority changed.
