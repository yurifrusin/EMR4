# Reception One Pre-printed Form v5 Threat-model Delta

Status: active
Parent: Reception One Proofreader Dialogue v4

## New boundary

The model no longer echoes the system-owned PlanProgram version. It returns only
`operator_note`, `goal_code`, and `steps`; the one-use broker injects the frozen
`version_code: 3` before exact local validation.

## Threats and controls

| Threat | Control |
|---|---|
| Model overrides a system-owned field | Provider response schema excludes it; exact model-body schema rejects additional properties. |
| Broker silently repairs model judgement | Injection is limited to the single constant field; hashes cover the model body, pre-printed field manifest and assembled program; no other mutation is allowed. |
| Pre-printing hides an invalid body | The body is validated first, then the assembled object is validated against unchanged PlanProgram v3 before compilation. |
| Prompt examples mask baseline capability | The v5 baseline forbids examples, demonstrations, prompt search and fine-tuning. |
| Proofreader becomes a planner | Correction tickets retain closed violation codes and coordinates only; no answer or patch is selected. |
| Partial correction smuggles stale fields | Turn 2 must replace the complete model-authored body and is terminal. |
| Extra retry evades the budget | One correction or request-contract repair consumes the only second call; no third call. |
| Natural-language note becomes an authority channel | The note is separately bounded and proofread, audit-only, excluded from compilation and product delivery, and discarded on rejection. |
| Credentials reach the work cell | Only the one-use broker holds existing impersonated ADC; the cell is credential-free and has only broker reachability. |
| Provider or regional fallback | Exact hostname, project, service account, model and region are checked and no fallback path exists. |
| Provider evidence leaks prompts or responses | Evidence retains hashes, closed findings, typed admitted fields and provider metadata only. |
| Rehearsal changes product truth | No API route, database, product mount, confirmation path or command authority is present. |

## Residual limits

Structured output support can increase syntactic success without establishing
semantic reliability. One or two authored-synthetic observations cannot justify
training, production use or claims about real receptionist language. The
configured Sydney locational endpoint and observed request path do not establish
Australian physical or sovereign processing.
