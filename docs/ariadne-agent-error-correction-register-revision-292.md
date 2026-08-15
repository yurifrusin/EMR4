# Ariadne agent error and correction register — revision 292

Date: 2026-08-15

Timestamp: 2026-08-15T18:50:02+10:00 (Australia/Brisbane)

Revision 292 records AER-0331. The register now contains 331 bounded known
incidents, all corrected or contained by an explicit control.

AER-0331 preserves the rejected DeepSeek V4 Flash/high self-pass for the
Prime-derived Ariadne continuity and refinement safeguards. The worker produced
clean nine-path candidate `7ff8ea25b03b691bad0feef179e9cb05f01c72f4`,
reported `DECISION pass`, and passed 173 focused tests with 139 hostile
mutations. Exact Sol/native read-only semantic admission nevertheless found
five fail-closed gaps: request conflicts were not universal, reordered or
retired unfinished journal history remained admissible, contradictory exact
gate results used latest-wins, refinement promotion lacked exact source and
authority binding while misreporting rejection, and rollback trusted
caller-supplied coordinates and history.

The candidate has no forbidden or product effect and remains untrusted
provenance. No same-lane repair or Gemini review is admitted. One bounded Sol
correction is authorised inside the frozen nine-path contract, followed by
deterministic re-admission and one fresh Gemini 3.7 Flash/high veto. This is the
second occurrence of
`implementer.self_pass_with_contradictory_or_underclosed_canonical_contract`,
after AER-0324. Its strengthened control requires independent semantic probes
over every command state, literal history order, contradictory gate evidence,
exact promotion authority and history-derived rollback before worker test
counts can support admission.
