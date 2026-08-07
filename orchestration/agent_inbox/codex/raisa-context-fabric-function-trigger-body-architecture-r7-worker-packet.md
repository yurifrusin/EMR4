# R7A bounded implementation packet

Date: 2026-08-08

Source branch: `codex/ariadne-bernie-davida-parallel-seam`

Source HEAD: `4533ff3505827f8fa44b1c1972e4e2b4b00d9234`

Authority: bounded implementation and focused-test authorship only. No
acceptance, integration, Git, generation, pytest, provider, database, source,
runtime, deployment or protected-ref authority.

## Owned files

- `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
- `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_fourth_veto_rotation_anchor.py`

No other file may change. Existing user-owned untracked files, especially
`docs/branding/`, are excluded.

## Exact implementation

In the new-effect branch of `rotate_observation_key_v1`, immediately after
`lock_anchor` and before `lock_prior_key`, add one assertion node named
`emr4_context_fabric.rotate_observation_key_v1.anchor_fence_exact` with failure
`F_ANCHOR`. Its predicate is one closed `AND` containing exactly these eleven
`EQ` comparisons:

1. anchor `checkpoint_state` to checkpoint `checkpoint_state`;
2. anchor `last_contiguous_position` to checkpoint `last_contiguous_position`;
3. anchor `last_observation_digest` to checkpoint `last_observation_digest`;
4. anchor `checkpoint_integrity_digest` to checkpoint
   `checkpoint_integrity_digest`;
5. anchor `policy_digest` to generation `policy_digest`;
6. anchor `principal_digest` to generation `principal_digest`;
7. anchor `binding_digest` to generation `binding_digest`;
8. anchor `source_digest` to generation `source_digest`;
9. anchor `registry_digest` to generation `registry_digest`;
10. anchor `impact_digest` to generation `impact_digest`; and
11. anchor `key_schedule_digest` to generation `key_schedule_digest`.

Do not change replay behavior, lock ordinals, effect order, digest operands or
any other body.

## Focused hostile tests

The new test module must independently build the contract and prove:

- the assertion exists exactly once, carries `F_ANCHOR`, contains exactly the
  eleven field-specific `EQ` pairs and sits strictly after `lock_anchor` but
  before `lock_prior_key`, any digest-use instruction and every effect;
- the identical-key replay branch contains none of the new-effect anchor/key
  locks or effects;
- after resealing generated evidence as the existing helpers require, removal
  or substitution of each equality is rejected;
- wrong anchor/checkpoint/generation relation or row symbol, `NE` in place of
  `EQ`, wrong failure family, moved assertion after the prior-key lock or first
  effect, and digest use before the assertion are rejected.

Reuse existing test helpers rather than weakening validators. The hostile test
may call the semantic validator directly but must not write generated artifacts.

## Permitted check

Run Ruff only on the two owned files. Do not run pytest, generation or Git.

Return a concise changed-files summary, Ruff result and exactly one terminal
line: `RESULT: candidate_ready` or `RESULT: revision_required`.
