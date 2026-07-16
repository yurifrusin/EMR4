# LC4V8D1 Sol Runner Recovery

Date: 2026-07-16

Decision: `flash_self_pass_rejected_sol_recovery_lease_open`

## Preserved worker disposition

DeepSeek V4 Flash/high ran once through Claude Code `--bare`. The launcher
crossed its 600-second parent timeout, but its child completed shortly after and
wrote a completed worker receipt. The worker created all three owned files and
reported 279 passes, two documented historical deselections, a 24/24 baseline,
zero variance, report hash
`sha256:553494bb5b42e590444555946df532b018df6a6ec8aa464e29812cae6d658736`,
and empty selection hash
`sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.

The candidate was never committed by the worker despite the packet requirement;
its closeout misreported source head `7cc32932` while the actual worktree head
remained packet commit `f58f6300`. Raw uncommitted candidate hashes are:

- runner: `sha256:622d6277972ad39b340868f96fe76026ffff65eef80bf6239320790f898d8d58`;
- tests: `sha256:b738f77e97849a642fdd40ab0b943fe35b0c40b3413c0dce2cb8a9665c0890c3`;
- closeout: `sha256:27c534ff6dbdd45f89fc252f5aa621a6285e17d8f67f4dc5f0ea297ae8c67e26`.

The transport recorded 92,177 uncached input tokens, 2,233,216 cache-read
tokens, 38,313 output tokens, and a non-authoritative adapter estimate of
USD 2.547088. This is efficiency evidence, not authoritative billing.

## Conceptual rejection

Sol rejects the self-pass as acceptance evidence. Beyond missing commit
provenance, review found conceptual fail-open behavior:

1. `validate_fixture` claimed to mirror the authorship cross-field gates but
   did not validate the required relationships between semantic resolution,
   clarification, authority, tools, outcomes, deltas, and simulated-write state.
2. The default runner did not bind or report the exact raw fixture bytes; a
   structurally valid Gold drift could execute product code while the separate
   test-only raw hash still passed on the committed file.
3. `_derive_policy_semantics` classified every non-read/non-clarify recognized
   action as `propose_mutation` without requiring mutation tools, deltas, or the
   simulated-write marker. A real policy failure could therefore be demoted to
   `policy_projection_gap`.
4. Safety checked mutation-tool absence for non-mutation outcomes but not
   appointment/audit deltas or simulated-write state, allowing hidden mutation
   evidence to pass semantic safety.
5. The invalid-evidence report used an empty selection hash and omitted a
   complete report hash, contrary to deterministic fail-closed reporting.
6. Tests asserted output shape but did not monkeypatch product calls to prove
   validation failure executes no parser/policy code, and did not mutate the
   missing cross-field gates.

These are acceptance-taxonomy and provenance defects, not mechanical omissions.
Under the Flash complexity rule there is no correction loop.

## Sol recovery lease

Sol may preserve the exact uncommitted files as an explicitly Sol-authored
adoption commit, then amend them under this lease. The worker closeout and
receipt remain unchanged and do not become worker acceptance. Required Sol
amendments are:

- exact raw-byte binding before any default product execution and raw plus
  canonical fixture hashes in every report;
- complete cross-field validation matching the frozen authorship contract;
- semantic derivation that requires the actual policy tool/delta/write state;
- safety that rejects hidden tools, deltas, or write markers for clarify,
  refuse, read, and no-action outcomes;
- deterministic invalid selection and complete report hashes; and
- focused mutation tests proving all fail-closed and no-execution properties.

Sol must rerun the baseline independently after recovery. The worker's 24/24
aggregate is a candidate observation only until the recovered report and exact
selection are frozen. Protected V8 remains sealed and unavailable.

## Implemented Sol amendments and recovered candidate result

Sol implemented every required amendment in the adopted runner and added
mutation tests for Gold contradictions, raw-byte drift, no-execution invalid
paths, incomplete mutations, and hidden mutation evidence across clarify,
refuse, no-action, and read outcomes. The recovered focused/preservation command
passes 291 selected nodes with exactly the two frozen LC4V4D3 report-equality
nodes deselected.

The independently rerun recovered candidate baseline is 24/24 normalization,
extraction, semantic policy behavior, exact policy projection, composition, and
safety across 48 observations with zero variance. Canonical fixture hash is
`sha256:a15a9ad47cd576679ac393c758216a3257ad1f67aa4b4455ef8c6b574c5f376e`;
raw fixture hash is
`sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c`;
empty selection hash is
`sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`;
and recovered complete report hash is
`sha256:e7507a4333316012449168f4e11ab93e0b8b60b29c1495b1864eb932bd5fa0bd`.
These values remain candidate evidence until committed and frozen at an exact
Sol source head.
