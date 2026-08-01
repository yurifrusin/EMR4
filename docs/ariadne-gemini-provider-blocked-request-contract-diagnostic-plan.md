# Ariadne Gemini Provider-Blocked Request-Contract Diagnostic

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's explicit authorisation of a provider-blocked Gemini
request-contract diagnostic and repair of the defect revealed by the Terra run
Status: active

## Purpose

Diagnose the Gemini attempt-003 HTTP 400 by comparing the exact
repository request constructor with the current public Gemini 3.5
GenerateContent contract, without contacting a provider. At the same time,
replace the audit exporter's silent field filtering with a fail-closed,
lossless allowlist boundary so a future broker field cannot be omitted without
failing the rehearsal.

## Authorised scope

- repository-local source inspection and implementation;
- current public Gemini request-contract documentation;
- authored-synthetic request sentinels and provider-error fixtures only;
- extraction of the exact Gemini request constructor into a pure, locally
  inspectable function used by both the broker and diagnostic;
- correction of demonstrably unsupported request fields or combinations;
- request-shape assertions that record keys, types and schema hashes but no
  prompt or schema content;
- a fail-closed external-audit event exporter;
- deterministic focused and repository-only regression verification;
- sanitised diagnostic evidence, closeout and continuity records.

## Closed scope

This tranche must not:

- make a Gemini, Terra or other provider/model request;
- read, inspect, validate, print, hash or mount a provider credential;
- transmit a prompt, schema, request body or authored task outside the
  repository;
- retry or mutate either consumed attempt-003 ledger;
- start a real container, broker, work cell, network, database, event feed,
  product API, mailbox, scheduler or command adapter;
- rewrite attempt-003 evidence or claim that a later static diagnosis proves
  the exact provider-side rejection when the raw 400 message was not retained;
- access PII, protected holdouts or historical Diary material;
- commit, push, integrate, deploy, release or grant product/runtime authority.

## Diagnostic method

1. Compare the attempt-003 request constructor with the current official
   Gemini 3.5 GenerateContent and migration contracts.
2. Treat any mismatch as a supported static finding, not as retroactive proof
   of the exact unretained provider error.
3. Move the corrected request constructor into the provider-contract module so
   the broker and local diagnostic cannot drift.
4. Build only an authored-synthetic sentinel request and assert its exact
   structural keys, bounded scalar settings and provider-schema hash.
5. Record no prompt, system instruction or schema values.

## Audit-export repair

The trusted orchestrator may export a broker audit event only when every event
field is present in the explicit public-event allowlist. Known events must be
copied losslessly. Any unknown field must raise
`audit-event-export-field-not-allowlisted`; silent omission is forbidden.

The repair is verified with:

- a complete synthetic broker-ready event containing the four fields omitted
  from the original attempt-003 durable copy;
- hash-chain verification before and after export;
- exact exported-field equality; and
- a synthetic unknown field that must be rejected.

Historical attempt-003 evidence remains immutable and
`revision_required`.

## Acceptance

Pass:
`ariadne_gemini_provider_blocked_request_contract_diagnostic_pass`.

Any provider call, credential access, prompt transmission, container/network
start, database access, historical evidence mutation, silent audit-field loss,
request-shape failure or repository regression:
`ariadne_gemini_provider_blocked_request_contract_diagnostic_revision_required`.

Passing this tranche authorises no live Gemini retry.
