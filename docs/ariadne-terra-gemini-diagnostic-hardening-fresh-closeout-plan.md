# Ariadne Terra/Gemini Diagnostic Hardening — Fresh Repository-Only Closeout

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's instruction to perform the necessary follow-up work
Status: active

## Purpose

Re-establish a clean acceptance boundary for the already implemented
provider-contract diagnostic hardening. The prior tranche and its PostgreSQL
fixture incident remain immutable. This is a new verification and closeout
record, not a relabelling of the earlier run.

## Authorised scope

- rehydrate the five required Ariadne sources;
- add a fail-closed repository-only verification entry point;
- run deterministic, authored-synthetic tests with repository
  `tests/conftest.py` explicitly disabled;
- diagnose the unrelated historical DeepSeek source-hash drift read-only;
- verify provider contracts, error redaction, audit-chain sealing, host
  verification, typed output manifests and proofreader regression;
- write superseding repository-only evidence and closeout documents.

## Closed scope

This follow-up must not:

- connect to PostgreSQL or any other database;
- read or inspect a database environment variable;
- make a provider/model request or read a provider credential;
- retry either consumed attempt-002 lane;
- start a container, broker, work cell, network, mailbox, product API, event
  feed, scheduler or command adapter;
- regenerate or rewrite historical DeepSeek execution evidence;
- access protected holdouts, PII or historical Diary material;
- commit, push, integrate, deploy or grant product/runtime authority.

## Fail-closed verification rule

The verification entry point must invoke pytest with `--noconftest` and a fixed
allowlist of repository-local test files. It must reject caller-supplied test
paths or arbitrary pytest arguments. It must perform static validation before
tests and must not inspect provider credentials.

## Acceptance

Pass:
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_fresh_closeout_pass`.

Any provider call, credential access, container start, database connection,
conftest load, in-scope failure, or unaccounted source change:
`ariadne_terra_gemini_provider_contract_diagnostic_hardening_fresh_closeout_revision_required`.

The earlier diagnostic-hardening `revision_required` record remains true
historical evidence regardless of this follow-up's result.
