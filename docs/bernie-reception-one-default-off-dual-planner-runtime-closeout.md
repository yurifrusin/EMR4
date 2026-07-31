# Reception One Default-off Dual-planner Runtime Closeout

**Date:** 2026-07-30
**Result:** `reception_one_default_off_dual_planner_occupied_model_and_recovered_route_pass`

## Outcome

The default-off dual-planner runtime has reached its bounded live Vertex
denouement.

The existing authenticated, development-only, authored-synthetic Reception One
proposal route now supports:

- `deterministic`, still the default with zero provider calls; and
- `isolated_vertex`, separately default-off and bound to the exact Bernie
  keyless impersonated-ADC Sydney lane.

Both terminate at the same deterministic proofreader and existing proposal-only
API Spine adapter. Neither can confirm or write an appointment.

## Occupied result

Exactly one provider call was made:

- provider/model: Google Vertex AI `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- impersonated service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- location/hostname: `australia-southeast1` /
  `australia-southeast1-aiplatform.googleapis.com`;
- HTTP status: 200;
- latency: 5,183 ms;
- token usage: 4,820 prompt, 901 thinking, 239 candidate and 5,960 total;
- proofreader: `admit`, no violations and no safe repair;
- release: one 45-minute `resize` proposal through
  `proposeAppointmentUpdate`, requiring human confirmation;
- write and confirmation performed: false.

The single-use ledger consumed exactly one provider call and the dialogue
stopped after admission. No retry or fallback followed.

## Cleanup-race recovery

After the occupied dialogue had passed, Windows briefly retained the closed
backend log handle and the first outer harness failed while deleting its
post-response runtime directory. This did not affect the provider, cell,
proofreader or ledger result; their audit already proved complete cleanup.

The cleanup loop was repaired with a bounded `PermissionError` retry and a
focused regression test. No second provider call was made. Instead, an
authenticated deterministic replay exercised the same HTTP route and
proposal-only update adapter:

- HTTP 200;
- zero provider calls;
- exact 45-minute resize;
- fresh and safe update-proposal adapter;
- no write or confirmation;
- database counts and hashes unchanged.

The disposable database, backend process, runtime directory, cell and relay
containers, images, network and temporary token are all absent. The raw request
frame was removed and replaced by a hash-only manifest.

## Verification

- Focused dual-planner tests: 10 passed.
- Inherited route, proofreader and context tests: 23 passed.
- Relevant API Spine tests: 25 passed.
- Compass tests: 10 passed.
- Python compilation, YAML/JSON validation and real isolation: passed.
- Continuity and Compass validation: passed before the occupied call.
- External audit chain: 11 events, valid terminal hash.
- Provider calls across occupied attempt and recovery: exactly 1.

## Candid conclusion

This is a positive composed runtime result: the occupied model/proofreader lane
passed, and the authenticated route/adapter was re-proved without another
provider call after the outer cleanup exception. The first outer HTTP response
was not durably retained, so the evidence is not represented as a second,
independently persisted end-to-end occupied HTTP response.

It proves the configured and observed Sydney locational request path, not
Australian physical or sovereign processing. It does not authorise or prove
real/product-derived, patient, health, clinical or historical data use,
appointment writes, production, deployment or release.
