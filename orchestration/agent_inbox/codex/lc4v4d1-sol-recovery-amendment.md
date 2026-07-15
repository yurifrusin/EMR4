# LC4V4D1 Sol Recovery Amendment

Date: 2026-07-15

Worker candidate: `43a67a86f61ed022a4781736f39f804e88b9bfcf`

Adopted integration commit: `745b8da2`

Authority: GPT Sol recovery lease. The DeepSeek V4 Flash/high candidate is
preserved as untrusted implementation evidence. Its report, hashes,
classification counts, and `candidate_complete` conclusion are rejected.

## Preserved worker failure

The candidate reported all 60 probes as `parser_gap`. That result is not
credible because the candidate:

- validated span coordinates but did not validate whether the authored
  semantic labels, dialogue facts, safety posture, or policy oracle were
  supported by the source surface;
- treated safety-pair validation errors as informational instead of failing
  closed;
- used identical semantic and policy expectations for safe and unsafe members,
  while the actual surface difference was only urgency wording and was not an
  unsafe authority demand;
- defaulted expected tools to `read_schedule, propose_appointment`, expected
  outcome to null, and expected deltas to empty across unrelated actions;
- called any scorer `interpretation` layer failure a parser gap, including tool
  selection, and then collapsed later policy, integration, and safety failures
  into that earlier category;
- never emitted `planned_unavailable` and used `scorer_gap` for component
  comparison failures rather than a scorer-only disagreement;
- compared only `all_passed` and `failure_layers` for repeat variance, silently
  swallowed execution exceptions, and did not fingerprint complete
  interpretation/replay/scorer observations;
- built the report hash from only fixture hash, aggregate counts, variance
  count, and selection hash rather than the complete report payload;
- hard-coded the report population at 60 instead of failing closed on the
  actual population and family shape;
- labelled two-turn corrected entity probes `one_shot`, did not retain complete
  carried/replaced dialogue evidence, and lacked an independent surface
  rationale; and
- overwrote generated fixture files without exact manifest/readback
  verification.

The launcher also recorded one permission denial for a malformed diagnostic
command. The durable worker receipt described ordinary pytest while the
launcher summary described a `--noconftest` run. Both facts remain preserved;
neither test claim is accepted as Sol evidence.

## Bounded Sol recovery

Sol may retain useful probe-authoring scaffolding, but will independently:

1. canonicalize the 60 development-only surfaces and exact evidence spans;
2. validate exact population, family lattice, dialogue pairs, safety-clause
   pairs, diary-state isolation, single-field entity isolation, and semantic
   support before observation;
3. author the semantic and policy contracts from explicit development policy,
   not observed parser output;
4. classify semantic-only surface disagreements as parser gaps, state-join and
   replay/policy disagreements as policy-contract gaps, and reserve scorer gaps
   for scorer-only disagreement after component success;
5. fingerprint complete repeat observations and fail closed on exceptions or
   variance; and
6. hash the complete canonical report payload and verify generated fixtures by
   exact manifest readback.

No parser, replay, policy, scorer, provider, route, runtime, holdout, or product
behavior remediation is authorized by this recovery.
