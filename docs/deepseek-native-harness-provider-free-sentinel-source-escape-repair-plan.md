# DeepSeek native Harness provider-free sentinel source escape repair plan

Date: 2026-08-21
Timestamp: 2026-08-21T15:37:35.2971612+10:00 (Australia/Brisbane)

## Decision and scope

This tranche repairs exactly one diagnosed Python-to-JavaScript escape coordinate in `sentinel_source()`. The accepted predecessor proved that an ordinary Python bytes literal translates JavaScript `\r` and `\n` spellings into raw line terminators before the generated sentinel module is written. The admitted repair changes only that return literal from ordinary bytes to raw bytes.

The tranche is provider-free and static. It may add only this plan, its threat delta, a frozen contract and schemas, a deterministic repair validator, focused tests, bounded evidence, continuation receipts and closeout records. It may modify only `scripts/raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py`, and within that file only the single `b` to `br` literal-prefix transformation in `sentinel_source()`.

## Exact inputs and transformation

- Accepted diagnosis source: `1609d7fa2c505fbd3f4f28a1a7f1f823356059d3`.
- Planning source: `eca807562c32c232034c63268b3e5f149e267592`.
- Repair target preimage SHA-256: `83d7b7ed0a438993f32b60d98f1dda567875eb67e6fcba5087d9b6796d23deeb`.
- Exact source transformation: one occurrence of `return b'''import {` becomes `return br'''import {`.
- Expected repaired source SHA-256: `e64b6c7f6b13bae69dd910963620e03e292b5262c5b05029305d6097f3e6191b`.
- Expected generated sentinel SHA-256: `8b53bc7fb781d29d87310ee2d3425ca159a62fed4893a3e4db94069d63cd60bd` over exactly 1,157 bytes.

Every other byte of the repair target, including its request, profile, tool, guard, lifecycle and provider boundaries, must remain identical to the planning-source preimage.

## Fail-closed proof

1. Resolve every Git source mechanically and require full 40-character object IDs with the diagnosis and planning sources ancestral to `HEAD`.
2. Read the repair-target preimage directly from the planning Git object and require its frozen digest.
3. Require the worktree target to equal the preimage plus exactly one inserted ASCII `r` at the frozen literal prefix. Any second source change fails closed.
4. Parse the candidate as Python AST without importing or executing it. Require exactly one zero-argument `sentinel_source()` with exactly one returned bytes literal.
5. Evaluate only the static returned literal. Require the exact repaired module digest and length, literal spellings for `split(/\r?\n/)` and `+ "\n",`, and zero raw CR/LF bytes inside JavaScript regex or quoted literals.
6. Compare every tracked file below the three frozen consumed-evidence roots with the planning Git object and require byte identity.
7. Exercise hostile mutations for the ordinary-literal regression, any additional source edit, malformed/multiple return shapes, raw line terminators, digest drift and consumed-evidence drift.
8. Record zero Node, Harness, broker, worker, model, provider, network and raw-stream-reconstruction activity.

## Acceptance

- The exact one-byte source transformation is present and no other pre-existing source byte changed.
- The repaired generated module has the frozen digest and length, preserves the intended JavaScript escape sequences and has zero lexical line-terminator violations.
- The request/profile boundaries remain byte-identical through exact whole-file delta proof.
- Every tracked file under the consumed bounded-worker attempts, repaired-sentinel boot proof and accepted preactivation diagnosis roots remains byte-identical to the planning Git object.
- Focused tests, predecessor static-diagnosis tests, Ruff, bytecode compilation, deterministic pre-verifier receipt and required governance checks pass.
- All executable Harness/provider activity counters remain zero.

## Parallelism assessment

- DeepSeek lane: declined with negative leverage. Any worker, Harness or provider activity breaches the source-only latch.
- Gemini lane: declined with negative leverage. Provider review is outside the latch; exact-delta, AST, lexical and hostile-mutation proofs are the independent controls.
- Native-subagent lane: declined with negative leverage. Current developer policy prohibits proactive delegation, and the one-byte repair is serially coupled to one source owner.

## Boundaries and successor

This tranche authorises no Node, Harness, broker, worker, model, provider or network process/request; no retry or reinterpretation of a consumed attempt; no raw-stream reconstruction; and no product, configuration, route, database, feature-flag, allowlist, grammar, client, waiting-area, patient, appointment, clinical, runtime, deployment, release, Pages or protected-ref change.

If accepted, a separately frozen provider-free repaired-sentinel boot proof may use a fresh attempt identity to test activation. This source repair does not authorise that process.
