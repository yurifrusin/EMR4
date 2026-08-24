# Raisa provider-free governance clockwork historical-derived minimised scenario consumption subgate rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T12:43:17.1361806+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed`

## Change under review

The clockwork gains one exact boundary set representing a future single local
test read of one digest-bound minimised historical-derived fixture. This
tranche changes governance admission only. It reads neither the archive nor
the fixture and performs no represented consumption.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A partial set is mistaken for authority | Exact set equality is required; any omitted member rejects as `historical_subgate_incomplete`. |
| Probe or materialisation authority silently becomes consumption authority | All three allowance sets are distinct; any cross-set mixture rejects as a mode conflict. |
| Denial and allowance coexist ambiguously | Legacy denial or typed historical denial mixed with any allowance mode rejects. |
| A descriptive or altered token widens scope | Historical and `allow_...` tokens are drawn from closed constants; unknown values reject. |
| The boundary drifts from the accepted successor contract | The exact contract bytes are SHA-256-bound and its critical fields are asserted in tests. |
| An abbreviation or different first-use source is substituted | The only consumption set embeds full source `4740813d53ebbc4872fe8c0c08ce2578b1982770`. |
| A different local fixture is consumed | The only set embeds exact fixture SHA-256 `2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe`. |
| A later consumer repeatedly or broadly reads local data | The form permits at most one ignored-fixture read and explicitly denies every archive read. |
| Derived structure is treated as operational or provider data | Consumption is limited to local provider-free authored-synthetic test context; product, database, route, client, runtime, configuration and ordinary practice remain denied. |
| This subgate itself accesses private data | The validator and tests use committed strings and contract fields only; no archive or ignored fixture path is opened. |
| Passing becomes reusable authority | The final member declares authority non-transitive, and the successor must freeze a new exact consumer envelope. |

## Residual boundary

Passing proves only that the governance clockwork can represent one exact
future local-test consumption mode without ambiguity. It does not consume or
validate the fixture, prove adapter behavior, authorize archive access, expose
real data, or open product/provider/runtime/ordinary-practice authority. Those
remain closed for the separately latched successor.
