# Ariadne Terra/Gemini Provider-Contract Diagnostic Hardening

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's instruction to implement the provider-free diagnostic repair
Status: closed
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_revision_required`;
fresh repository-only closeout follows under a separate acceptance record

## Purpose

Repair the local diagnostic gaps exposed by comparative rehearsal attempt 002
without making another provider request. The tranche makes provider request
profiles inspectable, validates the common output contract against explicit
Terra and Gemini subsets, and preserves only allowlisted non-content provider
error metadata.

## Authorised scope

- repository-local implementation and deterministic tests;
- authored-synthetic provider success and error fixtures only;
- explicit provider-schema profile compilation;
- OpenAI Responses and Gemini GenerateContent request-shape linting;
- typed enum normalisation for provider-facing schemas;
- bounded schema simplification where a provider subset requires it;
- allowlisted provider error status, type, code, parameter and request
  identifier extraction;
- sanitised dry-run evidence and closeout documentation.

## Closed scope

This tranche must not:

- make a provider or model request;
- read, validate, print, hash or mount a provider credential;
- start a container, broker, work cell, product API, database, event feed,
  mailbox or command;
- retry either consumed attempt-002 lane;
- retain provider error messages, response bodies, arbitrary headers, prompts,
  model output, PII, protected evidence or historical Diary material;
- grant product, scheduling, clinical, database, Git integration, deployment or
  autonomous-action authority.

## Contract repair

1. Compile a shared full contract into explicit provider-facing schemas.
2. Require a concrete JSON type on every provider-facing enum.
3. For Gemini, prohibit boolean enums and enforce boolean truth in the existing
   deterministic proofreader/full-schema gate.
4. Enforce provider-specific keyword, depth, property and union rules locally.
5. Keep the full deterministic schema authoritative after provider output.

## Diagnostic repair

The broker may retain only:

- HTTP status;
- response byte count and SHA-256 already retained;
- provider error status/type/code/parameter, if each value is a bounded scalar
  matching an explicit safe character allowlist;
- an allowlisted provider request identifier from a named header.

It must discard error messages, response bodies, unknown fields and all other
headers.

## External observer audit track

The cognition sandbox does not write, edit or delete its own audit record. The
trusted broker and orchestrator host create a sequenced, hash-chained trace
outside the sandbox. The trace records the observable typewriter mechanics:
sealed input and policy commitments, provider/schema commitments, typed draft
and output-port identifiers, emitted field names, content hashes, deterministic
proofreader rules and the final retry, human-gate, abort or release disposition.

It does not record hidden reasoning. Where an explanation is required, the work
cell must emit a bounded typed rationale that cites evidence frames and rule
identifiers. Raw prompts, provider responses, error messages, arbitrary headers,
secrets and unapproved sensitive values remain excluded.

## Verification

- focused comparative test population;
- authored-synthetic OpenAI and Gemini error fixtures;
- generic Draft 2020-12 validation plus provider-profile lint;
- deterministic proofreader regression;
- Python compile, Node syntax, JSON parse and whitespace checks;
- API Spine artifact regression;
- proof that no provider-call path was exercised.

## Result rule

Pass:
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_pass`.

Any failed local contract, sanitisation, boundary or regression gate:
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_revision_required`.

Passing this tranche grants no provider-call or retry authority.
