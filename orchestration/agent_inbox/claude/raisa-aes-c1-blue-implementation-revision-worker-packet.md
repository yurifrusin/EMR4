# Raisa AES-C1 blue implementation — bounded revision packet

Date: 2026-08-11
Task ID: `raisa-aes-c1-blue-implementation-revision-001`
Worker: DeepSeek V4 Flash/high through Claude Code `--bare`
Source branch: `codex/aes-c1-blue-deepseek`
Required source HEAD: `fadecf47a24ee1837047ffddbd5ab306a30f2c8c`

## Authority and rehydration

Read `AGENTS.md` completely before acting. Rehydrate from the live baton,
current worker allocation, the frozen AES-C1 plan and threat-model delta, the
accepted AES-C0 contract/schema/validator, protected-evidence boundaries, and
the exact Git refs/worktree. This is the one bounded blue revision authorised
by the frozen plan. Sol retains architecture, recovery, integration and
acceptance authority.

No runtime, broker, adapter, provider/model call, product or patient data,
database/source/watcher, credential/IAM/metadata/network, executable tool,
command/write, deployment, production, release, Pages or protected-ref action
is authorised. Do not enumerate or open protected evidence. Do not push.

## Independent Sol findings to repair

The candidate is `revision_required`; do not defend or merely document these
results:

1. `validate_contract()` accepts undeclared nested contract fields and a
   changed decision-precedence entry. Independently demonstrated:
   `contract_manifest_rule_extra -> []`,
   `contract_precedence_changed -> []`, and
   `contract_denial_policy_extra -> []`.
2. The purportedly closed candidate admits undeclared typed/proposal fields.
   Independently demonstrated: an added `unrecognized-benign-key` under either
   `candidate.typed_arguments` or `candidate.proposal_fields` yields no
   validation error and decision `allow`.

These violate frozen acceptance items 2, 3 and 10 and the default-denial
boundary.

## Required correction

- Make every nested contract rule closed and exact, including inherited
  digests, manifest/candidate/budget digest rules, decision precedence, denial
  policy, budget dimensions and zero-runtime boundary. A changed or extended
  rule must fail validation.
- Make candidate typed arguments and proposal fields closed to the exact
  authored-synthetic fields used by this rehearsal. An undeclared field must
  fail schema validation and can never reach `allow`.
- Add explicit hostile mutations and focused regression assertions for every
  Sol finding above. Keep the frozen 45 scenario IDs and their expected
  decisions/reasons unchanged.
- Regenerate deterministic scenarios/evidence as needed. Preserve the exact
  AES-C0 hashes, ordered evaluation, zero-runtime/provider/data claims and
  minimized evidence.
- Re-run the focused AES-C1/AES-C0/API Spine packet, Ruff, `py_compile`, and
  Git whitespace checks.

## Exact owned paths

You may modify only these existing seven paths:

1. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json`
2. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json`
3. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json`
4. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json`
5. `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
6. `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`
7. `orchestration/agent_inbox/claude/raisa-aes-c1-blue-implementation-closeout.md`

Keep the isolated worktree clean, amend the existing implementation commit (or
create one direct descendant), and report the exact final HEAD, changed paths,
tests, scenario/mutation counts, zero-call/data evidence and any remaining
concern. A worker `pass` is advisory; Sol alone decides adoption.
