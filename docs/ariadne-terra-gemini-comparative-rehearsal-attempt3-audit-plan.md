# Ariadne Terra/Gemini Comparative Rehearsal — Attempt 003 Audit Run

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's instruction to run both models again and check the audit
Status: closed
`ariadne_terra_gemini_comparative_rehearsal_attempt3_revision_required`

## Purpose

Run one fresh, bounded comparative rehearsal against the unchanged
authored-synthetic work-cell task and inspect whether the trusted external
audit track provides a sufficient account of provider contact, typed output
observation, deterministic verification, proofreader disposition and cleanup.

Attempts 001 and 002 remain immutable. Their ledgers and evidence are not
reset, reused or overwritten.

## Exact live authority

After a fresh five-source receipt, provider-free repository verification,
credential-presence gates and real-isolation preflight pass:

1. consume the new Terra attempt-003 ledger immediately before starting its
   work cell;
2. make at most one `gpt-5.6-terra` Responses API generating request;
3. verify exact Terra container and network teardown;
4. consume the new Gemini attempt-003 ledger immediately before starting its
   work cell;
5. make at most one `gemini-3.5-flash` `generateContent` request; and
6. verify exact Gemini container and network teardown.

There is no retry, fallback, model substitution, cross-model input, vote,
tool use, self-acceptance or downstream delivery. A Terra boundary failure
suppresses Gemini without consuming its ledger.

## Audit contract

The trusted broker emits a monotonically sequenced, SHA-256-linked event
record outside the work-cell sandbox. The host independently verifies that
chain and records:

- provider-call start and completion counts;
- provider status and allowlisted error metadata;
- request and response byte counts and hashes;
- the provider schema-profile hash;
- a typed-output manifest containing field names, output ports and hashes,
  but no draft values;
- full-schema and deterministic proofreader outcomes;
- final route disposition and cleanup.

The audit must never record credentials, raw prompts, raw provider responses,
draft payload values, hidden reasoning or free-form chain of thought. Bounded
decision rationale is permitted only through the typed output contract and is
checked against cited evidence and rules by the deterministic proofreader.

## Closed surfaces

The attempt may not access PostgreSQL or another database, the existing event
feed, product APIs, product data, PII, protected or historical evidence, live
mailboxes, EMR commands, deployment, production or release surfaces. The
broker is the only component that receives a provider credential. The work
cell receives only its one-use broker token and the sealed authored-synthetic
task.

## Result rule

Pass:
`ariadne_terra_gemini_comparative_rehearsal_attempt3_pass`.

Any occupied-process failure:
`ariadne_terra_gemini_comparative_rehearsal_attempt3_revision_required`.

A gate failure before a new lane ledger is consumed leaves that process
authority available. No failed occupied process may be retried under this
plan.
