# Independent veto: Rayleen source-adapter result-closure repair

Date: 2026-08-06

Reviewer: fresh GPT Sol coding-agent context, x-high reasoning

Role: read-only fallback veto only; no implementation, acceptance, integration
or protected-ref authority

Candidate: `1663d6d1cc79ebc8f2cb15446d6fa61196bd4fe8`

Decision: `revision_required`

## High finding: provenance detachment

The repair closed unknown nested fields, but its cross-links compared only
duplicated result/trace values. A caller could replace both copies of
`source_frame_digest`, reseal the trace and outer result, and cross the handoff
while the envelope ID/revision still encoded the original frame digest.
Replacing and resealing only `adapter_trace.binding_digest` or `grant_digest`
also crossed because neither was anchored to the authoritative input objects.

In a 32-case adversarial matrix, 27 schema/link/count/time/TTL/uniqueness/
derived-value mutations rejected and five fully resealed provenance-detachment
variants were admitted. This contradicted the claim that every digest/id link
was re-established before handoff.

## Moderate finding: independent grant fields

The result validator implicitly required elapsed and threshold values to appear
together. Across all sixteen subsets of the four waiting fields, eight valid
narrow grants were blocked whenever exactly one of elapsed or threshold was
requested. The parent scope vocabulary defines them independently, so the
adapter must support their independent projection or explicitly change that
contract; the latter was outside this repair.

## Evidence reconciled

- Focused adapter tests: 18/18 passed.
- Exact seven-file inherited A4/Context Fabric packet: 177/177 passed serially.
- Ariadne register tests: 43/43 passed.
- Committed evidence: 15/15; fixture/artifact hashes and result digests matched;
  positive extractor-built parent path returned `RELEASE`.
- Original unknown-property bypass was fixed.
- Current-weave module and continuity namespace remained byte-identical.
- No `app/**`, Diary, API, database, watcher, provider, command, deployment or
  Pages surface was added.
- Before/after HEAD stayed exactly
  `1663d6d1cc79ebc8f2cb15446d6fa61196bd4fe8`; review worktree status stayed
  empty.
- Protected local/origin `master` and `handoff/current` remained
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The next repair must externally anchor the result to authoritative frame,
binding, grant and alias-manifest inputs, preferably by deterministic full
recomputation/canonical equality at the handoff, and prove all sixteen waiting
field grant subsets.

`DECISION: revision_required`
