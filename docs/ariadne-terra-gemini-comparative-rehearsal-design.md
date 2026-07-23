# Ariadne Terra/Gemini Comparative Rehearsal Design

Date: 2026-07-24
Status: frozen candidate design

## The work cell and its proofreader

The model is an untrusted cognitive worker behind a locked form. It receives
only the shared synthetic task and two schemas. Its only possible output is a
five-draft JSON envelope. A deterministic host gate first checks the full
schema and then runs the accepted Ariadne proofreader. The model has no route
to an EMR command or human-facing edge.

The provider-facing schema is deliberately the intersection of the strict
schema subsets accepted by both APIs. It constrains shape, authority classes,
known identifiers, and byte/count bounds. The existing full schema remains
authoritative for port order, port-specific payloads, exact constants, and
provenance. Provider-schema success alone never releases an edge.

## Isolation topology

Each lane is built and destroyed separately:

```text
sealed task + schemas
        |
        v
read-only work cell -- private internal network --> one-use broker --> exact provider endpoint
        |
        v
bounded stdout envelope --> full schema --> deterministic proofreader --> sanitised evidence
```

The work cell:

- runs as a non-root user with a read-only root filesystem, dropped
  capabilities, `no-new-privileges`, resource limits, no published port, no
  host/repository mount, and only a private Docker network;
- contains no provider SDK, CLI, API key, general shell task, tool definition,
  or provider identity;
- computes the common system prompt and task prompt from sealed files;
- authenticates once to the internal broker and accepts one bounded,
  normalised response.

The broker:

- is the only component with provider egress and the lane credential;
- accepts one authenticated `POST /infer`, verifies the exact prompt, task,
  and schema hashes, and rejects a second request;
- constructs a provider-specific raw HTTPS request in memory;
- fixes the model, host, path, token cap, structured-output mode, storage
  policy, tool absence, and candidate count;
- follows no redirect and records metadata only;
- returns only parsed draft JSON and numeric usage to the work cell.

## Identical-input rule

The cognition projection removes the historical `model_contract` from the
accepted attempt fixture and replaces provider-labelled schema identifiers and
titles with neutral metadata. It changes no evidence value or validation
constraint. Provider identity, endpoint, reasoning setting, pricing,
credentials, and lane history are outside the model prompt. Both lanes must
report the same:

- shared-task SHA-256;
- full-schema SHA-256;
- common-provider-schema SHA-256;
- system-prompt SHA-256;
- task-prompt SHA-256 and byte count.

Gemini cannot receive Terra output or verdict. Comparison occurs only after
both cleanups and uses hashes, numeric usage, and deterministic verdict codes.
There is no model vote.

## Failure and cleanup

All provider, parsing, size, schema, proofreader, isolation, and cleanup
failures are fail-closed. Provider responses and prompts remain memory-only.
The ledger is consumed before the work cell starts and is not rolled back.
Cleanup is exact-name, lane-local, and verified by read-only inspection.

Gemini is suppressed only after a Terra boundary failure, secret exposure,
shared-contract compromise, or cleanup failure. This stop rule is deterministic
and recorded without sending Terra content to Gemini.
