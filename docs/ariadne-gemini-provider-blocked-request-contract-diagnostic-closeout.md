# Ariadne Gemini Provider-Blocked Request-Contract Diagnostic Closeout

Date: 2026-07-24
Owner: GPT Sol
Final result:
`ariadne_gemini_provider_blocked_request_contract_diagnostic_pass`

## Outcome

The no-call diagnostic found one concrete Gemini 3.x request-contract defect:
attempt 003 sent `generationConfig.candidateCount: 1` to
`gemini-3.5-flash`. Google's current Gemini 3.5 migration contract says
`candidate_count` is not supported in Gemini 3.x and must be removed.

That unsupported field is capable of producing the observed HTTP 400
`INVALID_ARGUMENT`, and it is now absent. Because the deliberately minimised
attempt-003 audit did not retain the provider's error message, this closeout
does not claim the field is proven to have been the provider's exact historical
rejection reason. Schema complexity and other provider-side checks are not
retroactively excluded.

## Request-contract repair

The exact Gemini request constructor now lives in the pure provider-contract
module and is used by the one-use broker. Local diagnostics therefore inspect
the same constructor that any separately authorised future broker run would
use.

The repaired request:

- omits `candidateCount`;
- preserves the unchanged provider schema hash
  `sha256:39a0f6da352a8da5f8291291a8f87abaa6aa9daa6b7359a8221341ebb756f1e2`;
- retains the supported JSON response MIME type and JSON schema;
- retains `MEDIUM` thinking with thought return disabled;
- retains the 2,048-token ceiling and no-store setting; and
- is built and inspected only with authored-synthetic sentinel text.

## Terra audit-export defect

The durable exporter no longer selects recognised keys and silently drops the
rest. It now copies every allowlisted event field losslessly and fails with
`audit-event-export-field-not-allowlisted` if any field has not been reviewed.

A synthetic broker-ready event containing `allowed_path`, `upstream_host`,
`upstream_path` and `maximum_provider_calls` survives export exactly and its
hash chain revalidates. A synthetic future field is rejected before export.
This repairs future behaviour only. The original attempt-003 durable evidence
remains immutable and `revision_required`.

## Boundary result

No Gemini, Terra or other provider/model request was made. No credential or
provider environment value was read or forwarded. No prompt or schema was
transmitted. No container, network, PostgreSQL, product API, event feed,
mailbox or command surface was opened. Both attempt-003 ledgers remain
consumed and unchanged.

## Verification

- provider-blocked structural diagnostic: passed;
- focused request-contract and audit population: 39 passed;
- focused Continuity/Compass population: 63 passed;
- fixed eleven-file repository-only population: 262 passed;
- static provider-free validation: passed;
- Python compile, Node syntax, Ruff, JSON parsing, Continuity/Compass schema,
  whitespace and Bandit medium-or-higher gates: passed.

The fixed verifier disabled repository conftest and plugin autoload and
forwarded no provider or database environment.

## Continuing gate

This result accepts the local request-contract diagnosis and future
audit-export repair only. It does not prove a Gemini candidate, a two-model
comparison or provider acceptance of a repaired request.

Any occupied Gemini attempt, credential mount, prompt transmission, provider
call or container lifecycle requires a new exact decision from Yuri.
