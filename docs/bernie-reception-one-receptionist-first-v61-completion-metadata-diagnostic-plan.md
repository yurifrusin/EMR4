# Reception One v6.1 Completion-metadata Diagnostic

Status: authorised after repeated pre-schema no-release
Recorded: 2026-07-30

The frozen cohort and its first same-contract continuation both received HTTP
200 with non-JSON text for `b-move-shift`. Neither response produced a typed
candidate, proofreader input or release. Raw provider text remains discarded.

The broker may now retain only:

- allowlisted Vertex `finishReason` enums;
- bounded candidate and part counts; and
- the four existing non-negative usage-token integers.

It must not retain or inspect response text, finish messages, hidden reasoning
or any new provider-controlled string. This audit-only instrumentation changes
no request, prompt, schema, proofreader, model, project, identity, ADC,
endpoint, data, isolation or release contract.

One diagnostic primary plus at most one ordinary proofreader-ticket correction
is permitted with distinct ledgers and USD 1 ceiling. If the call again fails
before JSON admission, the allowlisted finish metadata determines whether a
bounded request repair is supported. A schema-admitted exact result closes the
sequence. No fallback, product/database access, write, confirmation, delivery,
deployment or release is permitted.
