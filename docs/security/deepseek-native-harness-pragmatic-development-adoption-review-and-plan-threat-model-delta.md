# DeepSeek native Harness pragmatic development-adoption threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T09:14:57.6581226+10:00 (Australia/Brisbane)

Status: `frozen_provider_worker_adoption_delta`

Operation:
`deepseek-native-harness-pragmatic-development-adoption-review-and-plan`

## Boundary

This delta governs adoption of the pinned native Harness as a monitored
secondary development worker. The review itself is provider-free and read-only.
The next separately latched run may make one prepaid DeepSeek request sequence
against authored, non-PHI repository source in a disposable sparse worktree.
It opens no product runtime, data, command, deployment or protected authority.

## Threats and controls

### Better traces mistaken for better reasoning

Risk: precise failure coordinates may be mistaken for proof that the worker is
more reliable.

Control: record `useful_candidate`, `task_completion`, `trace_complete`,
`correction_cost` and `scope_integrity` separately. Promotion cannot rely on
trace completeness alone.

### Containment prevents ordinary self-correction

Risk: a one-request ceiling turns a normal edit/reread/edit loop into a false
worker failure.

Control: allow natural multi-turn work inside one fresh 900-second session,
with one serial tool call, zero automatic provider retry and zero fallback.

### Diagnostic work consumes the development programme

Risk: each Harness terminal creates another runner/guard/subcoordinate tranche
and delays Raisa work.

Control: no new generic boot proof and no diagnostic sequel. Only one directly
attributable pre-packet mechanical envelope defect may receive one correction
and one fresh run. Otherwise Sol recovers the task and later tries a different
assignment.

### Worker edits outside authority

Risk: the model changes unrelated or protected files.

Control: exact sparse worktree, full source OID, exact owned paths, minimized
tools, broker-bound session, changed-path readback and Sol rejection of any
scope escape. The worker cannot integrate or push.

### Credential or raw-session disclosure

Risk: provider credentials, prompts, reasoning or tool payloads escape into the
worktree or retained evidence.

Control: broker-side credential custody, no direct worker egress, sanitized
structural metadata only, no environment dump and exact disposable-root/process
cleanup. The first assignment contains no PHI, product data or secrets.

### Silent fallback corrupts comparison

Risk: a failed native run quietly continues through Claude Code, obscuring
which transport produced the candidate.

Control: zero fallback. Any recovery receives an explicit new allocation and a
separate provenance reading.

### Spend or runaway loop

Risk: natural multi-turn execution consumes unintended spend or time.

Control: Yuri's prepaid balance is the monetary boundary; the broker records
usage, the run has one session and a 900-second wall-clock bound, parallel tool
calls remain one, automatic retries are zero and auxiliary models are disabled.

### Declarative manifest gains authority

Risk: the first real assignment is mistaken for an operational manifest,
secret resolver or ordinary-practice admission.

Control: the normalizer receives explicit non-secret bytes only and returns a
typed reading or denial. It is unmounted, performs no environment/configuration/
credential/database read and has no command, admission, activation or product
effect. API Spine GraphQL, REST/OpenAPI and async surfaces remain unchanged.

### Version drift invalidates the accepted runner

Risk: an unpinned Harness/package upgrade reopens already-closed integration
unknowns.

Control: the first run uses exact rc.7 package/profile/runner hashes. A later
package upgrade requires a bounded source/readback rebind, but not automatic
repetition of the entire historical rehearsal chain.

### Unequal transport evidence creates a false ranking

Risk: raw incident totals are treated as comparative reliability rates.

Control: label them as corpus counts only and compare future native/Claude work
on matched real-work outcome, completion, trace, correction and scope fields.

## Explicitly closed

No live Harness/provider/worker runs during this review; no broker, runner,
preset or application mutation; no `.env`, process-environment, credential or
secret-store access; no database, Docker, route, API, GraphQL, OpenAPI, client,
configuration, product or patient data; no ordinary-practice enablement,
feature flag, allowlist, command mounting, generic-status `Arrived`, grammar or
waiting-area change; no production, deployment, release, Pages, protected
evidence or protected-ref movement.
