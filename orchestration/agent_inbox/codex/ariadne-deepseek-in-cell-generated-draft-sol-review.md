# Ariadne DeepSeek In-Cell Generated-Draft Rehearsal - Sol Review

Date: 2026-07-23

Decision: `revision_required`

Result:
`ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required`

Reviewer: GPT Sol High

## Finding

I do not accept a generated-draft or proofreader result because none occurred.
The single occupied model-process attempt was correctly consumed, and the
broker correctly failed closed on a method/path outside its one-route
allowlist before any DeepSeek request.

## Evidence accepted

I accept the narrower runtime evidence:

- exact five-source and pre-attempt receipts passed;
- the five-file image build and recorded provenance passed;
- the model process started in the declared read-only, non-root, capability-
  free, mount-free internal-network cell;
- the provider key remained in the broker and never entered the cell;
- one broker request was rejected and zero requests were forwarded;
- no usage, generation, schema candidate or proofreader input existed;
- the single-use ledger prevents retry; and
- all runtime resources and local image tags were removed.

## Failure meaning

The result identifies an incomplete Claude Code gateway contract, not a
DeepSeek model failure and not a proofreader failure. Official gateway
documentation names Messages and token-counting endpoints and permits a model
catalogue query; the frozen broker exposed only Messages. Because the rejected
method/path was deliberately not retained, the exact preliminary endpoint
remains unproved.

## Authority finding

The attempt authority is consumed. The provider-call count was zero, but the
model-process attempt still counts exactly as frozen. A diagnostic or retry is
a fresh Yuri decision.

PII, protected/historical evidence, product APIs, databases, events, mailboxes,
human actions, commands, production, deployment, release and autonomous action
remain closed.
