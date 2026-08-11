# AES-C5 product-runtime admission — paired closeout for Yuri

Date: 2026-08-11

Attention required now: `yes_for_any_further_aes_or_product_runtime_direction`

## Lay summary

The final planned Agent Execution Surface rehearsal passed.

Raisa made one real authenticated read through the existing practitioner-list
backend into a disposable local PostgreSQL schema filled only with newly
invented test staff. It correctly kept the inactive and wrong-practice records
out. A separate external broker reduced that result to the smallest useful
booking-choice packet and sent it through the Sydney Vertex Bernie lane exactly
once. The model selected the requested invented practitioner, and an
independent deterministic check admitted only a harmless, non-command result.

The important gain is architectural: the database read and model call did not
share one broad permission. Each received its own one-use, one-destination
authority generation, and both were exhausted and revoked. The database was
unchanged, the disposable schema was removed, the call ledger is consumed,
and no reusable broker, credential, process, listener, tool or command path was
left behind.

Nothing involving a real practitioner, patient, appointment or clinical fact
was used. This does not open live practice data, more calls, writes, tools,
deployment or production.

## Technical summary

- reviewed/occupied source: `4e5d96ada19c51432fa4db46c76e23c952147c52`;
- route: authenticated
  `GET /api/v1/practice/practitioners?activeOnly=true&limit=4&offset=0`;
- source proof: one route call, three active same-practice rows, three measured
  read/control SQL statements, unchanged practitioner/appointment/audit counts;
- composition: one immutable `authoritative_read` generation followed only
  after minimization by one immutable `provider_inference` generation;
- provider: Vertex `gemini-2.5-flash`, `bernie-emr4-dev`, impersonated keyless
  Bernie ADC, `australia-southeast1`, one call, no retry/fallback/tool;
- result: HTTP 200/`STOP`, 2,713 ms, 451 prompt, 105 candidate, 391 reasoning,
  947 total tokens, approximately USD 0.00138 at rechecked Standard rates;
- release: exact four-field digest-bound practitioner match with
  `command_authority: false`;
- cleanup: both ledgers consumed, both generations exhausted/revoked, schema
  absent, no residual lease/alias/token/listener/process/capability/temp root;
  and
- independent gate: fresh Gemini 3.6 Flash/high passed 71 focused tests, Ruff,
  compilation and clean exact-head Git checks with zero external operations;
  and
- final gates: 75 AES-C5 focused/continuity tests, the wider serial governance
  packet, 190 canonical-fast tests and 184 CI-static tests passed with Ruff,
  target-3.11 source compilation, Diary JavaScript, leakage lint and whitespace.

The CI-only literal Python 3.11 runtime assertion could not execute because
this workstation has Python 3.14 only; its exact lint/static commands were run
separately and passed, so this is an environment note rather than an omitted
test or an authority expansion.

## Issues and deliberately closed surfaces

The first worker candidate incorrectly tried to use two destinations in one
AES-C0 generation and assumed narrower route shapes than the application owns.
Sol recovered it into two independently immutable generations, corrected exact
nullability and nested-key validation, removed broker metadata from the model
request and prevented a trivial one-answer output schema. The repaired source
then passed the fresh veto. The separate CLI credential-store check also needed
one wrapper correction because PowerShell treated gcloud's normal
impersonation warning as an error; no token was exposed and no inference or
state change occurred.

Still closed: real-person, patient, clinical, appointment and operational
practice data; continuing database/source/provider access; watcher or reusable
runtime; filesystem or provider tool; generic network; credential/IAM change;
command/write; production identity/RLS claims; deployment; production;
release; Pages; and protected-ref movement.

## Place in Raisa and next work

AES-C0 through AES-C5 are now complete. Together they move the Practice
Context Fabric from a closed authority grammar through admission, custody,
hostile containment, one authored-synthetic provider crossing and finally one
authored-synthetic real application-route/database crossing—without turning
the Bureau into a command plane.

There is no planned or authorized AES-C6. The sprint engine therefore pauses
at a genuine programme-choice boundary. Any next step involving a real
practice population, another product-data class, a reusable runtime, a tool or
command, deployment or production needs Yuri to choose and authorize that new
direction.
