# Provider-free durability registration RLS recovery

Date: 2026-08-08

Status: deterministic architecture correction; runtime closed pending exact
descendant rebinding and fresh independent veto

Behavior attempt 018 admitted the reviewed corrected artifact, reached
`BTR-E01`, and stopped with SQLSTATE `42501` before any scenario was admitted.
The exact owned container was removed and absence was verified. Its immutable
failure evidence has SHA-256
`sha256:aeb88e2f404adb62300c0c0574b114c4254ccceb047140e75dd55eac6de61bc7`.

Static effect-to-policy reconciliation identified one closed structural
contract defect. `register_observer_generation_v1` runs for an exactly bound
`LIFECYCLE` session and must create or reload the initial stream head, then
create the generation's two initial frame rows and two initial invalidation
watermarks. All affected relations use forced row-level security. The accepted
policies admitted only `PRODUCER` for stream-head select/insert and only
`COORDINATOR` for frame/watermark select/insert, so the security-definer owner
still failed the policy check because each predicate deliberately re-derives
authority from `session_user`.

The correction adds `LIFECYCLE` to exactly six predicates:

- stream-head `SELECT` and `INSERT`;
- frame-generation `SELECT` and `INSERT`; and
- invalidation-watermark `SELECT` and `INSERT`.

It does not add `LIFECYCLE` to any update policy. No runtime login receives a
direct Fabric-table grant, role membership, inheritance, `BYPASSRLS`, owner
authority, trigger execution or another entry point. Producer and coordinator
behavior remains unchanged. The registration function body and the frozen
twenty behavior scenarios remain unchanged.

The corrected structural contract is canonically sealed as
`sha256:d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`.
Its body parent, inert artifact, render manifest, parse/catalogue contract and
evidence, and behavior contract must now be rebound in order. No new behavior
attempt is eligible until the complete corrected chain passes deterministic
checks and one fresh exact-HEAD Gemini 3.6 Flash/high veto.
