# Ariadne Terra/Gemini Comparative Work-Cell Rehearsal Plan

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's bounded real-isolation comparative rehearsal authorization
Status: attempt 001 closed `revision_required`; fresh attempt 002 also closed
`revision_required` after one provider call per lane

## Purpose

Test two economical cloud cognition lanes against one byte-identical,
authored-synthetic Ariadne work-cell task:

1. `gpt-5.6-terra` through the OpenAI Responses API; then
2. `gemini-3.5-flash` through the Gemini Developer API `generateContent`
   method.

This is an admission experiment, not provider selection. Each model may fill
the same locked five-port draft form. The existing deterministic proofreader,
not either model, decides whether a draft can be released.

## Fixed scope

The shared cognition task is a projection of
`orchestration/continuity/ariadne-deepseek-in-cell/attempt.json` that excludes
its historical `model_contract` and neutralises provider-labelled
`schema_version`, schema `$id`, and schema `title` metadata. The accepted six
authored-synthetic context frames, selection rules, budgets, scope, output
constraints, and proofreader remain unchanged.

No patient data, PostgreSQL, event feed, product API, model tool, command,
container runtime socket, repository mount, live mailbox, external worker,
write authority, provider fallback, retry, or downstream delivery is in scope.

## Run order and authority consumption

- Both credential gates and all provider-free checks must pass before Terra
  authority can be consumed.
- Terra receives at most one provider-generating call. Its authority is
  consumed immediately before its work cell starts, irrespective of outcome.
- Terra's cell, broker, private network, output scratch, and lane-specific
  image tags must be removed and verified absent.
- Gemini may then receive at most one provider-generating call.
- A normal provider, schema, or proofreader failure in Terra does not bias or
  block independent Gemini execution. A boundary breach, secret exposure,
  shared-contract mismatch, or incomplete Terra cleanup does.
- Gemini authority is consumed immediately before its work cell starts,
  irrespective of outcome.
- Neither lane may retry, fall back, repair provider output, see the other
  lane's output, or invoke tools.

## Frozen provider contracts

### Terra

- Endpoint: `POST https://api.openai.com/v1/responses`
- Model: `gpt-5.6-terra`
- Reasoning effort: `medium`
- Structured output: strict JSON Schema
- `store: false`; no tools; one response; 2,048 maximum output tokens
- Published 2026-07-24 prices used only for a non-authoritative estimate:
  USD 2.50/M input tokens and USD 15.00/M output tokens

### Gemini

- Endpoint:
  `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent`
- Model: `gemini-3.5-flash`
- Thinking level: `MEDIUM`; thoughts not returned
- Structured output: `application/json` with the same common JSON Schema
- no tools; `store: false`; one candidate; 2,048 maximum output tokens
- Published 2026-07-24 prices used only for a non-authoritative estimate:
  USD 1.50/M input tokens and USD 9.00/M output tokens

No Vertex substitution is permitted because this tranche did not establish
that the exact Gemini model is available there.

## Acceptance

The tranche may pass only if both one-shot lanes execute, both cleanups pass,
the common prompt and schema hashes match, each provider call count is exactly
one, both full-schema gates pass, both deterministic proofreader verdicts pass,
and sanitised evidence contains no prompt, provider response, draft payload, or
secret.

Any other completed run is `revision_required`; it grants no retry. Missing
credentials before authority consumption are a closed credential gate, not a
failed model attempt.

## Required artifacts

- protocol design and security delta;
- inspectable comparison manifest and common provider schema;
- purpose-built broker and work-cell launcher sources;
- single-use per-lane ledgers;
- provider-free tests and real-isolation preflight evidence;
- sanitised per-lane and comparison evidence if calls execute;
- closeout, independent review, protected integration, and baton update.
