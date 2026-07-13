# Orchestrator Rejoinder: Revise LC1 Conductor Plan

Role: Conductor
Resource: `deepseek-pro-routine-coordinator`
Model: `deepseek-v4-pro`
Reasoning: high
Settings fingerprint:
`sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5`
Prior plan:
`orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation.md`
Required replacement:
`orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation-v2.md`

This is the protected orchestrator's one permitted rejoinder under
`docs/ariadne-direction-collaboration.md`. Revise the plan and exercise final
Conductor authority. Do not implement product code, commit, push, or integrate.

Central review found these blocking defects:

1. The plan maps `at 3pm` to `earliest_time == latest_time == 15:00`. EMR4 uses
   half-open slot windows: candidates require `start >= earliest` and
   `start < latest`, while duplicate classification requires an existing start
   inside `[earliest, latest)`. Equal bounds therefore produce an empty search
   and cannot yield `existing_booking_found`.
2. Merely adding `TemporalRelation` inside `app/services/diary/temporal.py`
   does not carry the relation through `SlotSearchCommandIn`, deterministic
   normalization, `SlotSearchProposalIn`, context threading, or the supervised
   duplicate classifier. The runtime would still confuse exact point time with
   an open lower bound. LC1 requires the distinction to survive the composed
   interpretation-to-diary path. Use an additive, backward-compatible relation
   field or an equally explicit end-to-end representation; preserve legacy
   commands with a documented inference/default policy.
3. `approximate` cannot be only reserved for a future tranche because LC1
   explicitly requires coverage of exact/open/approximate temporal operators.
   Define and test at least an `around/about` anchor representation without
   granting it false exact-duplicate authority. `unspecified` must also be
   representable and tested.
4. The prior plan says three worker packets were created, but none of the named
   packet files exists. The V2 plan must create every allocated worker packet
   and keep the actual files/assignments consistent.
5. `app/services/bernie/normalizer.py` already exists as the deterministic
   slot-normalizer facade. Do not repurpose or overwrite it for language
   normalization. Allocate a distinct module name such as
   `language_normalization.py` or `scenario_spec.py` with cohesive ownership.
6. The T3 preservation command names a nonexistent
   `tests/test_bernie_shadow_eval.py`; use the committed test files
   `test_bernie_shadow_eval_contract.py`, `test_bernie_shadow_corpus.py`,
   `test_bernie_shadow_runner.py`, and `test_bernie_shadow_live_gate.py`.

Re-evaluate lane ownership so one implementation lane owns the complete
temporal relation through-path (temporal parser, schemas, normalizer,
interpreter/context threading, classifier/slot-filter consumers, route-backed
regression) and another owns the canonical scenario contract, lossless
normalization, seed corpus, and gap report. A later independent veto lane may
review both, but it must not certify its own generated corpus. The public E1
fake-provider DB-backed route replay must be the decisive `tomorrow at 3pm`
evidence, including zero second appointment/audit write.

The boundary may include additive schema/service/route-consumer plumbing needed
to preserve semantics, but no new endpoint, provider call, database mutation,
confirmation authority, or write authority. Keep all documented gates closed.

End the replacement plan with exactly:

```text
STATUS: complete
```
