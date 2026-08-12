# CF-D2 workflow-incident diagnosis

Date: 2026-08-12

Diagnosis: `workflow_amplified_a_real_but_under_observed_technical_problem`

## Executive finding

Yuri's concern was well founded. CF-D2 was not intrinsically a four-hour
algorithmic problem. It was a difficult integration proof with a monolithic
fail-closed anchor entry point, but our workflow amplified that difficulty by
reviewing repeated representations more precisely than it observed the
runtime boundary.

The safety system worked: every ambiguous or contradictory result stopped,
attempt 003 never ran, prohibited operations remained zero and cleanup was
exact. The efficiency and learning system did not work well enough. The
process allowed a participant coordinate to be treated as if it identified a
single internal assertion, then spent its sole correction and another review
cycle on an answer the evidence could not uniquely support.

The unresolved PostgreSQL anchor cause remains unknown. This diagnosis is of
the workflow incident, not a substitute database diagnosis.

## Evidence

From the first CF-D2 plan commit through the recovery stop there were 19 task-
branch commits. The two active commit windows total about three hours and
thirty minutes: 00:51–02:27 and 08:23–10:17 Brisbane time. The exact Git diff
from accepted CF-D1 closeout `e690eefa` to stopped recovery `d1e8d31e`
contains 87 agent-inbox packet/receipt files, 23 documentation files, 12
continuity files, eight test files and two source scripts.

Artifact count alone is not waste: many receipts preserved real boundary
decisions. The disproportion matters because the runtime never reached its
first `SIGKILL`, and the decisive second diagnostic still reported the same
coordinate without identifying the failing internal assertion.

The incident chain contained six independent process signals:

1. a stale roadmap test was bound to display numbering rather than semantic
   order (AER-0281);
2. a required formatter check was omitted before a planning review (AER-0280);
3. package-dependent Python was initially invoked as a filesystem script and
   failed before runtime;
4. a PowerShell command sequence could expose only its final exit code unless
   each result was captured separately;
5. an external verifier substituted and widened commands despite an exact
   prose allowlist (AER-0283); and
6. coordinate-specific evidence isolated the anchor participant but not its
   internal assertions, leading to an overclaimed sole cause (AER-0284).

During final-review preparation, Sol also manually expanded a short candidate
ID into a nonexistent full SHA. Git rejected it before worktree creation;
AER-0286 now requires exact identities to be copied from `git rev-parse` and
reverified by worktree preflight rather than reconstructed from memory.

The first final-review dispatch exposed two further examples of the same
structural problem. Its initial runtime state used an unconfigured adapter
probe method and omitted a mandatory inactive worker-slot inventory; local
preflight rejected it before dispatch (AER-0287). After correction, the new
tuple-shaped command-results schema reached Antigravity but the provider
rejected it at HTTP 400 because its tool-schema dialect requires an explicit
array `items` field (AER-0288). The repaired schema uses a provider-admissible
uniform item envelope while the local evidence gate retains exact command ID,
argv, order and exit-code enforcement. Neither event weakens a hard boundary,
but both confirm that machine vocabularies and transport dialects should be
validated locally at the earliest representable point.

During this diagnosis, intuitive receipt event `pre_plan` was rejected because
the configured value is `pre_sprint_planning`. This is the fifth recurrence of
the same vocabulary mismatch and is preserved as AER-0285. The repeated advice
to look up the YAML did not make the valid values discoverable at the point of
use.

## Causal structure

### Direct technical condition

`append_recovery_anchor_v1` verifies several linked registry, barrier,
generation, checkpoint, revision, timestamp, baseline-anchor, lifecycle,
receipt, admission and digest invariants. The diagnostic deliberately
minimized output, but its closed nonzero/null-SQLSTATE envelope assigned the
same observation to several possible internal failures. That made the next
cause non-identifiable.

### Primary workflow cause

Correction eligibility was governed by prose and review, not by a mechanical
relationship between remaining hypotheses and distinct observable outcomes.
The workflow proved that the correction was within the allowed category; it
did not prove that the evidence uniquely selected it.

### Amplifiers

- The same mutable facts were repeated across plan, contract, harness,
  diagnosis, packet and review rather than generated from one executable
  representation.
- External review was used at multiple intermediate gates, increasing latency
  and creating its own command-drift surface.
- Receipt event values and Python invocation rules were policies to remember,
  not discoverable/validated inputs at authoring time.
- Command evidence was prose, so exact exit propagation and target equality
  depended on manual comparison.
- Bounded-attempt discipline correctly stopped unsafe improvisation, but the
  only available improvisation was another predeclared correction/review
  cycle; it did not include an evidence-quality test before spending that
  cycle.

## What stays formal

Authority, privacy, protected evidence, real data, immutable attempts,
cleanup, no-fallback behaviour, exact Git binding and protected refs are not
the angels on the pin. They prevent irreversible or misleading outcomes and
all worked here.

## What becomes fluid

- One tranche boundary and one final risk-triggered veto replace repeated
  external reviews of intermediate deterministic states.
- A diagnostic-decision gate makes hypothesis discrimination the prerequisite
  for correction, not additional prose confidence.
- Structured argv manifests and exact command-result admission replace command
  recitation in review text.
- Receipt event values become CLI-discoverable.
- Candidate identities are resolved and reverified by Git, never manually
  expanded from short display IDs.
- Provider-facing schemas express only the shape the provider can admit;
  stronger exactness remains a deterministic local release condition.
- A second same-coordinate failure after a correction is an automatic stop or
  programme-direction change, not an invitation to nest another recovery.

## Conclusion

The answer is balanced: CF-D2 was genuinely subtle, but the workflow was too
formal in the wrong place. It strongly governed permission and documentation
while weakly governing whether the next experiment could distinguish the next
decision. The repair keeps the former and mechanizes the latter. Useful
improvisation remains welcome when it produces a more discriminating bounded
observation; improvisation by widening authority or repeating an ambiguous run
remains closed.
