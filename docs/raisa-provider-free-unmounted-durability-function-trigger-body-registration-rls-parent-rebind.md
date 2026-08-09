# Function/trigger body registration-RLS parent rebind

Date: 2026-08-08

Status: deterministic parent-only rebind; executable runtime remains closed

The typed function/trigger body contract is rebound to corrected structural
source commit `9fb107ab598fba418b42be6d233c4960a6f29840` and canonical structural
contract SHA-256
`sha256:d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`.

No support-function, entry-point or trigger body program, signature, derived
effect summary, failure registry, trigger declaration, role grant, transaction
fence or renderer order changes. The only body-contract value change is its
exact parent binding; the resulting canonical body-contract SHA-256 is
`sha256:422b7cd5203893ecd2269c9b2dbf4018ed359661d5ebe962de55afffb03c340c`.

The next dependency is inert-artifact regeneration from these two exact
parents, followed by exact parse/catalogue and behavior descendant rebinding.
No database execution, application migration or wiring, operational source,
patient/product data, provider/model call, command/write, deployment,
production, release, Pages or protected-ref authority is opened.

## 2026-08-09 stream-head lock-visibility rebind

The bounded behavior failure-023 recovery changes only
`pol_cf_01_update USING` in the structural parent so the lifecycle entry point
can retain its existing `SELECT ... FOR UPDATE` lock. `WITH CHECK` remains
producer-only and lifecycle retains zero direct table DML/SELECT.

The corrected structural source is commit
`338c30ddb01561ce97a4b9837317e771b555c221` with canonical contract SHA-256
`sha256:a79be2598a3e3c5a8636ab8a1c16c06523ce9716d2387764cfecc1004ff5d14e`.
The body contract is rebound mechanically to that parent and resealed as
`sha256:6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b`.

All 22 typed body programs, signatures, effects, failure registry, trigger
declarations, role grants, transaction fences and renderer order remain
byte-equivalent after excluding the parent and contract seals. The prior
parent-rebind record above remains historical provenance rather than current
authority.
