# Reception One Proofreader Dialogue v4 Threat-Model Delta

## Added boundary

V4 permits one schema-admitted, proofreader-rejected PlanProgram to generate a
closed correction ticket and one complete replacement opportunity. The
unchanged PlanProgram-v3 form, deterministic compiler, semantic proofreader,
proposal-only executor, human gate and backend command ownership remain
decisive.

## Threats and controls

| Threat | Control |
|---|---|
| A correction dialogue becomes an unbounded agent loop | The parent state machine permits at most two actual calls. Turn two is terminal. Request-contract repair and semantic correction compete for the same second call. |
| The proofreader becomes the planner | Tickets contain constraint findings, bounded coordinates and closed allowed-output sets only. They never select a replacement goal, operator, binding, dependency or proposal. |
| Rejected prose becomes a feedback or retention channel | `operator_note` is removed from `previous_typed_form`; rejected note text is discarded. Only its closed finding code and the complete-program hash may survive. |
| Raw provider output is replayed | Only the schema-admitted typed form is eligible for a ticket. Raw response bytes, rejected JSON text and hidden reasoning are never retained or returned. |
| A malformed response receives a privileged correction | No ticket is issued unless the response reduces to the exact local PlanProgram schema and the proofreader produces only correction-eligible findings. |
| Ticket fields are tampered with | The ticket has an exact local schema, program hash, target turn, one remaining attempt, closed field and violation enums, bounded coordinates and no additional properties. The broker reconstructs it from the first audit and compares exact bytes. |
| Allowed outputs disclose or invent the answer | Allowed output names are mechanically derived only from the already model-selected earlier operator. They describe its published type surface, not which output should be selected. |
| A second turn smuggles a patch | The provider must emit a complete replacement PlanProgram through the unchanged response schema. Partial programs and patches fail closed. |
| A correction bypasses freshness or supersession | Each turn reruns the exact frame boundary and proofreader. Stale context, scope, data-class, catalogue or authority failures are not correction-eligible. |
| A failed second turn is silently repaired | No semantic repair or third turn exists. The terminal result is proofreader admission, inert human gate or edge abortion. |
| Two ledgers are miscounted as one call | Every actual turn consumes a distinct one-call child ledger. The parent audit counts actual provider calls and rejects a third ledger or ordinal. |
| Provider/request defects consume an extra semantic budget | A deterministic request-contract repair consumes the only second-call slot; a semantic correction cannot follow it. |
| Model authority expands through dialogue | There is no product route, database access, confirmation or write actuator. Only admitted authored-synthetic in-memory proposal fields can be released. |
| Provider, credential or region fallback weakens assurance | Exact Gemini 2.5 Flash, Bernie project/service account, keyless ADC and Sydney hostname remain frozen and audited with no fallback. |
| Geography is overstated | Claims remain limited to published regional support and the configured/observed locational endpoint, not physical or sovereign processing. |

## Unchanged closed gates

Protected holdouts; historical Diary material; real, product-derived, patient,
health or clinical data; GraphQL mutations; REST writes; model-to-database
action; appointment confirmation; provider tools; explicit cache creation;
global or cross-region inference; API keys; Word; voice; production;
deployment and release remain closed.
