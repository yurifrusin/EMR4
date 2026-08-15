# Provider-free unmounted delete-confirm physical-design architecture closeout

Date: 2026-08-15

Timestamp: 2026-08-15T16:35:48+10:00 (Australia/Brisbane)

Result: `raisa_provider_free_unmounted_delete_confirm_physical_design_architecture_pass`

Reviewed source: `3fd22ba69f96c0378538ea27c6bea444fcb81936`

Implementation authority: `false`

Reasoning level: material authority / transaction architecture / Extra High

## Accepted result

The five additive cancellation domains identified by the physical
representability review now have one exact fail-closed design:

- the product `users` row is the lockable authority fence, with a
  PostgreSQL-owned positive monotonic authority generation;
- exact normalized grants admit only `appointment.cancel.confirm` and the
  separately required `appointment.read`; row absence denies and no user is
  automatically granted either capability;
- dedicated cancellation reuses appointment version `n -> n + 1`, status
  `Cancelled`, an exact ten-code reason vocabulary and separately nullable
  500-character cancellation text;
- the private family-qualified receipt gains only `authority_generation` and
  binds actor, role, session digest, operation, route, target, request and
  pre/post state before replay;
- initial response and replay use one integrity-checked stored canonical
  six-field UTF-8 JSON byte buffer;
- delete audit preserves attributable state/version/reason transitions while
  keeping human warning acknowledgements distinct from internal evidence; and
- one `READ COMMITTED` transaction locks authority fence, appointment and
  idempotency row in that order, repeats the full authority check while all
  locks are held and spends one cumulative 2000 ms lock-wait budget without an
  effect retry.

Fresh readback occurs after commit in a new transaction, requires exact current
`appointment.read`, and is reconciliation only. It never proves or reverses
the command outcome.

The current full delete-confirm response is not silently relabelled as the
accepted minimized receipt. Any response/route compatibility transition
remains a later explicit gate. GraphQL remains read-only and events remain
non-authoritative acceleration hints.

## Verification

- all twenty exact source hashes pass;
- contract, schema, validator and authored-synthetic evidence agree at
  fingerprint `sha256:5d0512a64ecf9c907962b9a86a0cc56023c75363786ba52be9702b63c7018fa5`;
- all 166 hostile mutations fail closed;
- the exact review manifest passed the architecture validator, 63 focused
  architecture/allocation tests, 36 API Spine tests, Ruff and whitespace;
- the canonical fast profile independently passed Ruff, 209 maintained-source
  compilations, 196 API Spine/handover/receipt/maintenance tests, Diary syntax
  and whitespace; and
- the first ordinary Gemini 3.7 Flash/high Antigravity veto returned one
  schema-constrained `pass` at unchanged clean source.

“Provider-free” labels the product/architecture evidence: no product provider,
ADC or product runtime was invoked. The separately authorised independent
review did use Gemini 3.7 Flash/high and received only the exact non-protected
authored-synthetic repository packet.

## Issues exposed and resolved

The direct 3.7 allocation change initially left two live verifier resource
references on the old 3.6 id; focused tests caught both and they were corrected
before dispatch. The new allocation now spans the launcher, worker pool,
transport, sprint, security-review, operating-model and verifier policies.
Gemini 3.6 remains explicit historical compatibility only, never a silent
fallback.

AER-0329 preserves a recurrent Sol source-binding error: an uncommitted
runtime-state draft initially expanded an abbreviated commit display instead
of copying literal `git rev-parse HEAD`. The draft was rejected, the exact
object was captured and substituted before receipt admission or any model
call, and the candidate remained unchanged.

## Claim and authority boundary

This proves a coherent unmounted physical design. It does not prove or
authorise an ORM model, migration, service helper, executable DDL/SQL,
PostgreSQL trigger/lock behaviour, mounted route, capability provisioning,
product command or readback runtime.

No patient, clinical, product or protected evidence was used. No product
provider/ADC, database, real transaction, source watcher, credential/IAM,
deployment, production, release, Pages or protected-ref authority was opened.
`docs/branding/` and every unrelated untracked file were preserved and
excluded.

## Next direction and requested pause

The next dependency-satisfied product tranche remains the provider-free
unmounted delete-confirm physical schema-and-transaction scaffold. It may lower
only this exact design into a separately frozen model, inert migration and
unmounted helper/static-test surface; database execution, route mounting and
all broader surfaces remain closed.

Per Yuri's explicit instruction, product development pauses at this completed
boundary. No scaffold tranche is opened. The immediate activity after closeout
is a read-only primary-source assessment of PrimeIntellect `prime-agent` for
concrete, evidence-backed Ariadne harness ideas; it grants no implementation or
programme-direction authority.
