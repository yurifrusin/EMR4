# Independent review: Ariadne agent error and correction register

Date: 2026-08-03

Reviewer: fresh native GPT Sol coding reviewer / Socrates

Role: independent review only; no implementation, acceptance, integration,
protected-ref, deployment or release authority

Scope: the bounded Ariadne agent-error register plan, closed schema, seeded
register, deterministic reporter, verifier execution-policy addition, generated
pattern report, focused tests and named preserved evidence. The review did not
edit product code, call a provider, inspect protected evidence, or touch
`docs/branding/`.

## Initial findings

The first independent pass identified six defects:

1. Recurrence was keyed only by a free-form signature and could merge incidents
   across different origins, categories, roles or resources.
2. The schema admitted higher causal-claim levels without requiring separate
   causal evidence, contrary to the policy boundary.
3. AER-0003 attributed creation of a temporary artifact more strongly than its
   direct postflight evidence supported.
4. The `docs/branding/` evidence-path exclusion was case-sensitive on a
   case-insensitive Windows filesystem.
5. Split incidents from one attempt were not required to identify the attempt
   or cross-reference every peer.
6. The boolean candidate-change field could not distinguish an unchanged
   canonical candidate from an untrusted partial worktree.

## Verified repairs

The stabilized repair candidate addresses all six findings:

1. Recurrence uses the composite of origin, category, role, resource and
   normalized signature, with an adversarial collision regression.
2. V1 restricts `causal_claim_level` to `observation_only`; any future causal
   claim requires a later schema with separate causal evidence.
3. AER-0003 now records only the observed postflight artifact and wrapper
   classification, without asserting an unpreserved creator.
4. Both schema and resolved-path validation reject case variants of
   `docs/branding/`.
5. Every row has an immutable `attempt_id`; split attempts require complete
   peer linkage and stable attempt identity.
6. Candidate state uses the closed enum `canonical_unchanged`,
   `untrusted_partial_worktree`, or `accepted_candidate_changed`; AER-0003 and
   AER-0007 correctly use `untrusted_partial_worktree`.

The initial seed remains bounded and evidence-backed. Its report treats
recurrence as an operational control signal only and makes no comparative
model-quality or unsupported causal claim.

## Checks reproduced

- Focused serial pytest gate: 20 passed.
- Ruff on the register implementation and focused tests: passed.
- Git diff hygiene: passed.
- Generated pattern report matched a fresh deterministic build through the
  focused tests.
- Candidate HEAD remained unchanged at
  `8e79cfc3caa73a9b9527f395edbdfb61e202def9` throughout review.

This receipt preserves the reviewer's non-transferable result only. It grants
no acceptance, integration, baton, commit, push, protected-ref, deployment,
production or release authority.

DECISION: pass
