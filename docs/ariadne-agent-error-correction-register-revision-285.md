# Ariadne agent error and correction register — revision 285

Date: 2026-08-15

Timestamp: 2026-08-15T12:29:03+10:00 (Australia/Brisbane)

Revision 285 records AER-0321 through AER-0324. The register now contains 324
bounded known incidents, all corrected or contained by an explicit control.

AER-0321 preserves the rejected delete-confirm preplanning receipt in which Sol
invented the `expected_leverage` value `positive_after_contract_freeze`. The
preflight stopped before plan freeze or dispatch. The passing descendant uses
the admitted value `positive` and keeps the timing qualification in rationale
text. This is a recurrence of the vocabulary-control signature first preserved
at AER-0314.

AER-0322 preserves the rejected plan-precommit state in which Sol used the
parallelism disposition `selected` for the future DeepSeek lane. The corrected
state uses the admitted pre-dispatch disposition `planned` and passed before
the plan commit.

AER-0323 preserves two failed worker-predispatch receipts. The first treated a
purposefully divergent worker worktree as if it had to equal
`handoff/current`; the second populated an internal assigned-agent id without
the matching resource receipt. The corrected state explicitly records
`at_handoff_current: false`, the exact plan-source divergence and timestamp,
and leaves the internal assigned-agent list empty for the external adapter.

AER-0324 rejects DeepSeek candidate
`b2d6427582737b126f6c3c8d57a59b88440ca5fc` as acceptance evidence. Although
its owned paths were clean and its 19 focused checks passed, its canonical
confirmation occurred after its own expiry, its closed packet omitted exact
authority and signed-evidence contracts, and it had no successful null optional
cancellation-text path. The source remains preserved as untrusted provenance.
The conceptual correction loop transferred to Sol under the named recovery
lease. Sol repaired only the frozen six-file protocol boundary, added direct
regressions and retained a fresh exact-candidate Gemini veto as mandatory.

None of these incidents reached a mounted route, product/database command,
provider call, protected evidence or protected ref. Future receipt states must
reuse the last passing exact analogue rather than infer enum or workspace
shapes; a worker self-pass never substitutes for independent semantic
admission of the canonical evidence packet.
