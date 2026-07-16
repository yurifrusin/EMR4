# LC4V10 Framework Review Amendment

Date: 2026-07-17

Status: `fresh_exact_head_review_required`

Gemini independently confirmed all eight framework recovery defects closed and
returned `DECISION: pass` at reviewer commit `34a36be2`. Its focused framework,
taxonomy, and D1 suites passed 109/109, but the combined command completed
113/114 because the compact-handover test still required retired D1 baton
phrases removed when V10 became active.

Sol does not accept an independent veto with a red named gate, even when the
failure is administrative and unrelated to framework behavior. The immutable
archive checks themselves remained green. Sol updated only the live-handover
required-string set from retired V9/D1 baton wording to the current V10
contract, acceptance rule, rejected candidate, recovered test counts, and
no-content state. No framework, product, threshold, contract, or protected
artifact changed.

The exact combined command now passes 114/114 on the integration worktree. A
fresh Gemini project must reproduce 114/114 and return an exact-head decision
before pre-content acceptance. The first review and its limitation remain
preserved unchanged.

## Second review

The second fresh project correctly returned `revision_required` at reviewer
commit `bfa5b613`: the exact gate was again 113/114 because the updated test
required lowercase `no V10 content exists` while the current baton used the
grammatically capitalized `No V10 content exists`. Sol changed that one test
literal and reproduced 114/114 against the current handover. Framework,
product, contract, thresholds, and protected state remain byte-for-byte
unchanged from recovered head `d56db482`. One final fresh exact-head veto is
required.
