# Default-off runtime instrumentation - lay and technical closeout

Date: 2026-08-12

Result: `passed`

## Lay summary

We have found a safe place for the proposed diagnostic shadow without yet
installing it. The key discovery is that a database write can be finished before
the web framework has actually built and sent the final response. So the design
does not run the diagnostic from the appointment route itself.

Instead, the route would place one tiny, non-identifying note in a private
single-use slot after the database work succeeds. Only after the ordinary HTTP
response has been sent would a separate outer layer try once to hand that note
to a diagnostic observer. If anything is missing, disabled, full or broken, the
note is simply lost. The patient's action, response, audit and database result
cannot be changed by the shadow.

The design is off everywhere by default. It also refuses to invent identity:
unless the server can provide a safe authenticated session reference and its
own correlation reference, nothing is staged.

## Technical summary

- accepted source: `ed52950f451af88892a8f469157ecf8c8567da81`;
- exact source hashes and AST facts bind four raw appointment handlers and their
  audit/commit-owning helpers;
- phase 1 is post-helper-success single-assignment staging only;
- phase 2 is post-final-send atomic take-and-clear plus one non-awaiting
  `offer_nowait` call with no result channel;
- configuration is immutable, globally disabled, practice/route allowlists are
  empty, and the external latch is disable-only;
- the existing raw-compat audit/header setting has no shadow authority;
- missing server-owned context denies; bearer-token hashing and caller-owned
  correlation are forbidden;
- projection/record shapes remain exactly 24/15 fields with no free text,
  response content, credential or raw retention;
- 60/60 hostile mutations, 15 tranche tests, 152 focused tests and the canonical
  repository profile pass; and
- Continuity 251 / Compass 233 is current.

## Deliberately closed

No route or middleware has been changed or executed. No runtime observer,
feature flag, queue, sink, persistence, database/source/watcher/event access,
provider call, product/patient data, kernel, command/write, deployment, release,
Pages or protected ref has opened. Existing untracked files, including
`docs/branding/`, remain preserved and excluded.

## Place in the Raisa direction and next tranche

This converts the pure shadow experiment into an implementable but still
fail-closed mounting design. The next tranche is the globally-disabled typed
scaffold: build the generation/context/projection/cell/post-send interfaces,
leave every enablement empty and attach no observer or sink, then prove the
disabled path and all four authored-synthetic route results remain equivalent.

Yuri's attention is not required; the next scaffold is dependency-satisfied and
continues under standing authority.
