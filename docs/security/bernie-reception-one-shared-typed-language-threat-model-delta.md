# Reception One Shared Typed Language Threat-Model Delta

## Added assets and boundaries

This descendant adds one provider-emittable `PlanProgram` schema and one
audit-only `operator_note`. The typed program crosses the isolated-cell egress
boundary into a deterministic proofreader. The note crosses a separate
deterministic note gate before any text can enter the audit.

The trusted compiler is not a planner. It may only decode frozen integer tables,
generate deterministic step identifiers and attach trusted request metadata.

## Principal threats and controls

| Threat | Control |
|---|---|
| Natural language becomes a covert command channel | The note is never parsed, executed, released to product or consulted by program compilation. |
| Note leaks credentials or identifiers | Byte, character, secret-pattern, URL, email, identifier and frame-name scans; rejected text is discarded and only hash/reason codes survive. |
| Note stores hidden reasoning | The prompt requests a concise operational account, not rationale; reasoning markers and multi-line/markup output fail closed. |
| Note falsely claims an appointment was changed | The note must preserve proposal/review status and explicitly say no booking was changed; contrary command-shaped claims fail closed. |
| Typed output exploits free-form identifiers | Goal, operator and source references are bounded integers; names and step IDs are trusted frozen-table expansions. |
| Forward/cyclic references | Step-output codes may reference only an earlier step and a real output index. |
| Type confusion | The proofreader compares every source semantic type with the exact operator input signature before compilation. |
| Omitted required input | `-1` is valid only for an input marked optional in the frozen catalogue. |
| Provider schema passes a semantically invalid plan | Existing PlanDraft proofreader runs after the direct PlanProgram gate and before execution/release. |
| Safe repair invents meaning | PlanProgram accepts no semantic repair. A retry may change only a deterministic provider request-contract defect. |
| Raw response becomes an audit log | The broker parses in memory and retains only hashes, token/latency metadata, admitted note text and typed proofreader/release manifests. |
| Historical failures are rewritten | The work is a new graph descendant; consumed ledgers and prior conclusions remain unchanged. |

## Unchanged stops

No real/product/patient/health/clinical/historical data, appointment
confirmation/write, API-key/static-key/user credential, global endpoint,
cross-region fallback, provider substitution, product delivery, Word/voice,
production, deployment or release is opened by this delta.
