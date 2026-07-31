# Ariadne Terra/Gemini Provider-Contract Diagnostic Hardening Closeout

Date: 2026-07-24
Owner: GPT Sol
Final result:
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_revision_required`

## Outcome

The repository-local implementation is complete and its focused deterministic
gates pass. Provider-facing contracts now have explicit enum types and separate
Terra and Gemini profiles. Gemini receives no boolean enum; the full local
schema and deterministic proofreader retain the exact-value obligation.

Provider failures are reduced to allowlisted bounded metadata. Error messages,
response bodies and arbitrary headers are discarded.

The rehearsal also has a future external observer track. The trusted broker
seals ordered events into a hash chain, and the orchestrator verifies it. The
sandbox has no append, rewrite or delete authority. The record describes typed
field and output-port mechanics, hashes and proofreader disposition without
retaining raw prompts, responses, sensitive values or hidden reasoning.

This is not a provider-run result, does not retrofit attempt 002, and is not a
durable product audit store.

## Why the result is revision required

The implementation gates are green, but the tranche did not preserve its
no-PostgreSQL verification boundary.

An initial concurrent pytest invocation omitted `--noconftest`. The repository
autouse session fixture connected to the configured local PostgreSQL test
database and failed during fixture setup with duplicate enum `userrole` before
the scoped test bodies ran. Fixture setup may nevertheless have performed test
database DDL before the collision. No database inspection or cleanup was
attempted without authority.

All subsequent verification disabled the repository fixture, but a clean rerun
cannot erase the earlier boundary deviation. The acceptance result therefore
remains `revision_required`.

## Verification

- focused comparative population: 28 passed;
- API Spine artifact population: 36 passed;
- broader selected Ariadne/API population: 226 of 227 passed;
- the single broader failure is an untouched historical DeepSeek evidence-hash
  drift against current committed DeepSeek runtime sources;
- static provider-free validation passed and reported no provider call or
  prompt transmission;
- Python compile, Node syntax, Ruff, JSON parse, whitespace and Bandit
  medium-or-higher gates passed.

The corrected pytest populations all used `--noconftest`.

## Raw-reasoning decision

Raw reasoning is not an audit-quality record. It can contain secrets or
sensitive data copied from context, unresolved hypotheses, prompt-injection
material, provider or system instructions and statements that appear decisive
after their uncertainty is lost. It is also difficult to minimise, retain and
disclose proportionately.

The audit substitute is a bounded typed rationale: decision code, evidence
frame identifiers, applicable rule identifiers, rejected or selected typed
alternative, confidence or uncertainty where useful, and the deterministic
proofreader disposition. This is reviewable without collecting private
scratch-work or chain-of-thought.

## Authority and next gate

No provider request, retry, credential read, container start, product API,
event feed or prompt transmission occurred in this hardening work. The consumed
attempt-002 ledgers remain consumed.

A fresh, separately accepted repository-only closeout could re-establish a
clean verification boundary. It would not itself authorise a provider retry or
model call. A durable practice-scoped audit sink, any protected values and any
product/runtime connection remain separately closed.
