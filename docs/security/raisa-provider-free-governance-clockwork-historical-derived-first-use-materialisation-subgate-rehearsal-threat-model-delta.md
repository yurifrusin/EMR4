# Raisa provider-free governance clockwork historical-derived first-use materialisation subgate rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T10:38:41.3497625+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed`

## Change under review

The clockwork gains one exact boundary set that can represent a future local-
only, digest-bound first-use fixture write. This tranche changes governance
admission only. It neither reads private material nor performs the represented
write.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A partial set is mistaken for authority | Exact set equality is required; any omitted member rejects as `historical_subgate_incomplete`. |
| Measurement authority silently becomes materialisation authority | The measured-probe and materialisation sets are distinct; any cross-set mixture rejects as a mode conflict. |
| Denial and allowance coexist ambiguously | Legacy denial or typed historical denial mixed with either allowance mode rejects. |
| A descriptive or altered token widens scope | Historical and `allow_...` tokens are drawn from closed constants; unknown values reject. |
| The boundary drifts from its accepted contract | The exact successor-contract bytes are SHA-256-bound and its critical fields are asserted in tests. |
| A different gate or abbreviated Git ID is substituted | The only materialisation set embeds full source `abcd4206a363b0c565c070e0f2cb9c54d627b3b3`. |
| A blocked candidate still creates a fixture | The boundary requires an exact digest-bound gate receipt and states that blocked or revision-required results write nothing. |
| A writer changes the admitted candidate | Written bytes must match the admitted candidate digest; authority remains non-transitive. |
| This subgate itself touches private data or writes | Tests use authored-synthetic boundary lists only; the validator is pure and no archive reader or fixture writer is added. |
| Product/provider scope is inferred | The mandatory product-data floor and the byte-bound contract keep provider, model, product, database, client, runtime and ordinary-practice authority false. |

## Residual boundary

Passing proves only that the governance clockwork can represent the exact
future mode without ambiguity. It does not prove candidate quality, archive
access, de-identification, fixture writing, downstream scenario usefulness or
product safety. Those remain closed for the separately latched successor.
