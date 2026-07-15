# LC4V4D2 Sol Recovery Amendment

Date: 2026-07-15

Worker candidate: `9b9d86e0` on `claude/lc4v4d2-semantic-remediation`

Adopted candidate integration: `5ba29ef0f3e03a6128e5e0a34bad1c4d40f36f20`

Authority: GPT Sol recovery lease. DeepSeek V4 Flash/high through Claude Code
`--bare` supplied an untrusted semantic implementation candidate. Its discovery
of three D1 oracle contradictions is accepted after independent Sol proof. Its
evaluator, report, test claims, and `candidate_complete` decision are rejected
as acceptance evidence.

## Preserved worker findings

The worker correctly identified that the remaining three nominal D1 parser
failures were inconsistent authored expectations rather than parser defects:
corrected duration retained the old value, negated duration retained a value,
and an explicitly supplied elliptical duration was labelled omitted.

The worker also supplied useful bounded grammar and state-reduction candidates
for entity ambiguity/negation, omitted required patient identity, correction,
clarification, ellipsis, restart, reversal, move/resize actions, and
practitioner-possessive disambiguation.

## Preserved worker failure

The candidate still returned `DECISION: candidate_complete` while reporting
only 20/23 nominal targets fixed. It did not classify the three contradictions
as `authoring_invalid`, did not invalidate the original D1 acceptance, and
represented the post-repair population as three parser gaps.

Its evidence module and tests were fail-open because they:

- set D1 report validity to true without loading and recomputing the complete
  frozen report hash;
- hard-coded before counts rather than binding the full D1 payload;
- derived purported before-state semantic fields from after-state mismatch
  fields;
- declared semantic fields fixed generically rather than comparing the exact
  before and after evidence;
- allowed its decision despite remaining target parser gaps;
- used a vacuous mismatched-join preservation loop over only target
  transitions; and
- hard-coded report summary claims instead of deriving them from the complete
  evidence object.

The first-pass reversal and restart patterns were also broader than the
authorized surfaces and risked false positives from ordinary uses of
`disregard`, `take back`, and `forget that`.

## Bounded Sol recovery

Sol retained the useful semantic candidate and independently:

1. scoped reversal and restart cues to request-local language and narrowed
   patient alternatives to explicit booking contexts with full names;
2. added direct positive, negative, safety-pair, state-reduction, and
   false-positive tests;
3. added cross-field D1 authoring validation for corrected, negated,
   ambiguous, and explicitly supplied durations;
4. recomputed and bound the complete frozen D1 report, fixture, raw 23-case
   selection, exact ID population, and raw counts;
5. independently proved and quarantined the exact three authoring-invalid rows;
6. froze the remaining valid 20-case target hash;
7. compared actual frozen before-state results with current after-state results;
8. required all 20 valid interpretation gaps to close, no new parser gaps, no
   supported regressions, preservation of the five mismatched diary joins as
   policy gaps, and zero complete-observation variance; and
9. made the D2 decision and complete report hash derive from the full recovered
   evidence payload.

Policy/state-join remediation is not authorized by D2. The protected holdouts,
T3 gates, provider/runtime surfaces, and all write authority remain unchanged.
