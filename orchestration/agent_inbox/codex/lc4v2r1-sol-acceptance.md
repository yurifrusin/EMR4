# LC4V2R1 Sol Acceptance

## Decision

**DECISION: pass**

GPT Sol accepts the recovered LC4V2R1 development-only entity/normalization
repair at exact reviewed head `fa973311caede67e30155926acf1562b31748efe`.

## Accepted evidence

- Sol-authored fixture: 21 unique Gold/adjudicated development probes;
- fixture SHA-256:
  `0f957518d1481ce831a55ca8d12388f245ae89ae516e96ef1d5037080d925afd`;
- immutable baseline: 4/21 complete and 17 failures, selection
  `ddfbc280bb822993`;
- recovered result: 21/21 for normalized values, entity semantics,
  clarification, authority, tool safety, no-completion claims, and complete;
- recovered failed selection: empty, `e3b0c44298fc1c14`;
- report hash:
  `sha256:46570a2e3ab5d47fe4d74594544d4e92f1d68cc8d8a51d5db39a233f59d84c38`;
- two-repeat variance: zero;
- development semantic counts unchanged at `880/814/672/154/330/835`;
- development safety unchanged at 1,152/1,152;
- development variance unchanged at zero over 2,304 samples; and
- development corpus hash unchanged at
  `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`;
  and
- final serial preservation gate: 383 collected nodes, 381 passed, one
  expected xfail, and one expected skip.

The accepted parser handles conservative room and appointment-type semantics,
lexical quarter/half/one-hour durations, entity corrections, and directly
scoped entity/duration negation. It does not infer `mismatched` without diary
context. Explicitly ambiguous or negated required entities fail closed without
mutation tools, while established omitted-entity behavior remains unchanged.

## Worker and recovery decision

DeepSeek V4 Flash/high through Claude Code `--bare` produced candidate commit
`861049e9`. Sol rejected its self-certified pass because its check mode rewrote
the report, its baseline binding was fail-open, its completion hash was unset,
and one entity-negation scope was over-broad. No Flash correction loop was
opened. Sol preserved the candidate and recovered the evidence tooling,
negation scope, false-positive guards, and provenance under the Ariadne lease.

## Independent veto

Gemini 3.5 Flash/medium returned `DECISION: pass` on exact recovered head
`fa973311`. It reproduced the 21/21 result, report and baseline binding,
ordinary development aggregate, temporal interval behavior, scope guards, and
worker-provenance preservation without changing the review worktree.

## Boundaries and next work

Protected holdouts v1 and v2 were not opened, enumerated, searched, imported,
run, regenerated, evaluated, hash-checked, inferred from, or reused. T3.1-T3.4
remain intact and blocked by default. T3.5, providers, historical diary,
routes/API, database, UI, deployment, runtime, memory, confirmation, and write
authority remain closed.

The next ordinary development tranche is a separately frozen safety-language
matrix distinguishing unsafe bypass/completion demands from explicitly negated
safe instructions across implemented actions and diary states. It must remain
independent of both sealed holdouts.
