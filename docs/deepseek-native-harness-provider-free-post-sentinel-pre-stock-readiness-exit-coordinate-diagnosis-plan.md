# DeepSeek native Harness provider-free post-sentinel pre-stock-readiness exit-coordinate diagnosis plan

Date: 2026-08-21

## Decision and scope

This tranche performs one process-free static diagnosis of the consumed
source-repaired sentinel boot. It may name one uniquely supported source-control
path between `sentinel_activated` and the observed exit-before-readiness, or it
must stop as `insufficient_static_evidence`.

The diagnosis is read-only with respect to the pinned `@deepseek-ai/dsh`
`0.1.0-rc.7` materialisation and the consumed native attempt. It may add only
this plan, threat delta, frozen contract and schemas, deterministic diagnosis,
tests, bounded evidence, review and closeout records, and clockwork inputs.

## Exact inputs

- Accepted failed terminal and closeout source:
  `f2de7108b0074501c66e2c82ad83b45294b402db`.
- Executed controller candidate:
  `84a9327d98812a9891af0ef5724045f7599eb3a5`.
- Accepted boot clockwork source:
  `2585cdae995ce90047d1f9099a36cb379de4f3b4`.
- Accepted sentinel-source repair candidate:
  `eb8913aacb19d823e251731f9393cc54fe71524c`.
- Sanitized terminal, consumed ledger, frozen boot contract, source-repaired
  controller, reusable boot controller, and static profile/sentinel author named
  and hash-bound in the contract.
- Pinned rc.7 launcher, profile-boot, headless bundle/startup, command-line
  adapter and Commander sources named and hash-bound in the contract.

The destroyed stderr stream must not be recreated, guessed, dictionary-matched,
or recovered from its retained digest. The static diagnosis does not use that
digest as an oracle.

## Fail-closed method

1. Bind every repository and pinned-package input by exact SHA-256 and every Git
   source by a full 40-character object ID.
2. Read source as inert bytes only. Do not import or execute the boot controller,
   profile author, Node, the Harness, a broker, a worker, a model or a provider.
3. Require the consumed terminal to retain exactly one
   `sentinel_activated` event, exit code `1`, no readiness, no retry, no raw
   streams and zero broker/worker/model/provider/network activity.
4. Require the frozen launch contract and terminal to agree that the inner
   headless argument snapshot was empty.
5. Require the rc.7 headless bundle to mount `headless-startup`, while the exact
   user patch disables `headless-runner` but does not disable
   `headless-startup`.
6. Require the exact rc.7 control path: the launcher forwards the empty inner
   arguments; headless startup joins them to an empty task and rejects it before
   publishing its service; Commander assigns exit code `1`; the command-line
   adapter routes that code through `ctx.appExit`; and profile shutdown disposes
   the tree and records or forces the same exit code.
7. Accept `unique_supported_exit_coordinate` only when every binding and every
   control-path link is exact. Any missing, duplicated, moved or contradicted
   link returns `insufficient_static_evidence`.

## Acceptance

- The exact terminal remains `failed_closed` at
  `native_process_exited_before_readiness`, with events exactly
  `sentinel_activated`, exit `1`, readiness false and retry count zero.
- The package is exactly `@deepseek-ai/dsh` `0.1.0-rc.7`.
- The unique supported exit coordinate is the mounted headless-startup
  missing-task rejection caused by the frozen empty inner argument snapshot.
- The source chain from empty arguments through Commander and `ctx.appExit` to
  profile shutdown is exact and independently mutation-tested.
- The result does not claim that readiness would pass after supplying an inert
  task; that remains untested.
- Node, Harness, broker, worker, model, provider and network activity remain
  zero throughout the diagnosis.

## Parallelism assessment

- DeepSeek lane: declined. A worker/model/provider process violates the static
  claim and cannot recover the destroyed raw stream.
- Gemini lane: declined. Provider review is outside the active process-free
  envelope; exact source bindings and hostile deterministic mutations own the
  verdict.
- Native-subagent lane: declined. Current developer policy prohibits proactive
  delegation, and the source/terminal correlation is acceptance-coupled and
  serial.

## Boundaries and successor

This tranche authorises no retry, resume, fallback or second process for the
consumed attempt; no Node/Harness/broker/worker/model/provider/network activity;
and no product, patient, health or clinical data, ordinary-practice enablement,
runtime, deployment, release, Pages or protected-ref movement.

If accepted, the narrowest successor may freeze a fresh provider-free sentinel
boot contract that supplies one inert authored-synthetic task argument while
keeping the headless runner disabled. Such a boot requires a fresh attempt
identity and explicit one-process admission; it is not authorised here.
