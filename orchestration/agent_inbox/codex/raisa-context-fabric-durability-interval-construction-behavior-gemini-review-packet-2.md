# Independent replacement veto: interval construction, behavior rebind and dispatch guard

Date: 2026-08-09

Decision required: exactly one terminal structured `pass` or
`revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r135`
- Branch: `codex/review-context-fabric-interval-behavior-edb488b0`
- Accepted pre-failure baseline: `b8bc7ca6e0ca27329ac098a05642641480b684fb`
- Candidate: `edb488b06bf07a30647439114e6cfda8510276f9`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Replaced review

The earlier packet at
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-interval-construction-behavior-gemini-review-packet.md`
is the detailed challenge catalogue for the interval repair, exact parse proof,
six-parent behavior rebind, twenty frozen scenarios and API boundary. Apply all
nineteen challenges from that packet, except that its r134 checkout, candidate
HEAD and 463-test count are historical and superseded by this packet.

The r134 verifier result is procedurally inadmissible because its orchestrator
predispatch receipt was `revision_required` with
`worker_dispatch_permitted: false`. Do not rely on or affirm that decision.
Perform a fresh independent review in r135.

## Additional mandatory challenges

Verify and report:

1. AER-0160 and revision 135 accurately preserve the first clean-but-
   inadmissible review and identify Sol's dispatch-after-rejection error as an
   orchestrator error, not a Gemini or PostgreSQL failure;
2. `scripts/ariadne_antigravity.py` now requires an exact
   `--orchestrator-receipt`, rejects invalid JSON, wrong schema, any status
   other than `passed`, `worker_dispatch_permitted` other than true, and any
   rehydration-source set other than the exact five named sources before it
   reads the packet or invokes `agy`;
3. the admitted orchestrator receipt SHA-256 is recorded in any future worker
   receipt and the guard cannot be bypassed through the normal CLI;
4. tests prove a `revision_required` receipt causes zero provider-transport
   invocation and no output receipt;
5. the corrected predispatch v2 receipt supplied to this launch is itself
   `passed`, has `worker_dispatch_permitted: true`, keeps external verifier
   slots/assignments empty, and separately binds the exact clean r135
   worktree-preflight evidence; and
6. the complete deterministic packet is now exactly 476 tests: the prior
   durability/API packet plus all twelve `tests/test_ariadne_antigravity.py`
   cases and the AER-0160 register test. All 476 must pass, together with Ruff
   check, Ruff format on modified Python files and both diff checks.

Run at least the same commands from the historical packet, changing
`--basetemp` to
`C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r135`, adding
`tests\test_ariadne_antigravity.py` to pytest, adding
`scripts\ariadne_antigravity.py tests\test_ariadne_antigravity.py` to Ruff
check and format, and changing the diff range to:

```powershell
git diff --check b8bc7ca6e0ca27329ac098a05642641480b684fb..edb488b06bf07a30647439114e6cfda8510276f9
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface other than this single verifier
model invocation, access patient/clinical/product or protected data, inspect
`docs/branding/`, move refs or accept the earlier r134 review.

Return `revision_required` for any P0-P2 finding, invalid interval repair,
evidence mismatch, scenario drift, API/authority widening, launcher bypass,
failed/rejected dispatch receipt, incomplete 476-test packet or dirty
postcondition. Otherwise return one exact structured `pass`, stating findings,
commands/counts, HEAD and post-review cleanliness.
