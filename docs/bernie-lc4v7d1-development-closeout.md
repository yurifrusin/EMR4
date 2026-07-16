# Bernie LC4V7D1 Development Closeout

Date: 2026-07-16

Decision: `development_exit_pass`

LC4V7D1 used only the 24 fresh inspectable ordinary-development probes frozen
in the Sol contract. Protected holdouts v1-v7 were not opened, enumerated,
searched, imported, run, regenerated, or inferred from. V7 itself remains
consumed and unchanged.

## Authorship and baseline

Gemini 3.5 Flash independently returned `DECISION: pass` on the exact authored
contract, fixture, and generic future-certification taxonomy before baseline.
DeepSeek V4 Flash/high then implemented the bounded runner/test candidate
through Claude Code `--bare`. Sol rejected the worker's self-pass because its
report hash preceded final selection insertion and therefore did not bind the
complete report. Sol recovered the source without a correction loop under the
Ariadne recovery lease.

The recovered baseline is permanently frozen in
`docs/bernie-lc4v7d1-development-baseline.json`:

- fixture hash:
  `sha256:03544ffab7d3a720faf6cba3cac7f33c5e45e7a42dfec231223334fdd335b2ea`;
- report hash:
  `sha256:c093616ff2916097e546cda2e4c9681eaaf1ef27b49fc0d86a5651cc7ef7a97d`;
- valid-gap selection hash:
  `sha256:643339dfb9008f8df1b81b5e8e8effbf5d6d4561bafa67376d721fb0c185cd77`;
- 6 spoken-time normalization gaps, 6 cross-turn interval parser gaps,
  6 ambiguous-practitioner parser gaps, and 6 unknown-practitioner policy
  gaps; and
- zero authoring-invalid cases, contract-layer gaps, runtime exceptions, or
  variance across 48 observations.

## Bounded remediation

Sol implemented four rule-based repairs against only that frozen selection:

1. lossless spoken-time normalization recognizes hour, half-past,
   quarter-past, quarter-to, spoken-minute, and hundred-hour forms while
   preserving original text and exact source spans;
2. semantic extraction consumes the derived canonical spoken time, preserves
   `not before`/`not after` meaning, and composes complementary additive bounds
   across turns while correction/restart turns still replace the relation;
3. practitioner ambiguity is action-independent and exposes only exact
   `Dr X or Dr Y` alternatives in source order; and
4. Option A policy requires roster clarification before explaining the
   schedule of an exact but unmapped practitioner, with no slot search,
   outcome claim, delta, or simulated write.

No probe-ID branches, expected-value imports into interpretation, provider
calls, runtime wiring, or product-write surfaces were introduced.

## Final development evidence

`docs/bernie-lc4v7d1-development-final.json` records:

- normalization 24/24;
- extraction 24/24;
- policy 24/24;
- composed 24/24;
- safety 24/24;
- zero variance across 48 observations;
- empty selection hash
  `sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`;
  and
- complete report hash
  `sha256:802f089a0d356706bef8d40846955c241f4459bd75d836c302020f1725b97808`.

The focused five-file gate passed 336 nodes after deselecting two immutable D3
population/report-equality nodes. The wider serial ordinary preservation gate
passed 680 nodes after deselecting exactly 16 documented historical nodes:

- eight already failed at pre-D1 head `be5eeceb`: seven superseded V2R1
  semantics/report nodes and the old composed-corpus committed-report equality;
- eight are intentionally implicated historical D2-D4 population/hash nodes:
  three D2, two D3, and three D4 assertions whose frozen diagnostic
  classification or report hashes necessarily change when one old policy gap
  becomes supported and multi-turn temporal/ambiguity observations improve.

The underlying D2-D4 case checks continue to pass. Their committed reports
were not regenerated or rewritten.

## Independent review and V8 exit

Gemini 3.5 Flash independently returned `DECISION: pass` on exact recovered
head `19d507634adb40dd2649db3823daf8e3afde9160`. It reproduced the 336-node
focused gate with two historical deselections, all final evidence hashes and
counts, the empty selection, the four rule repairs, and the full 16-node
preservation accounting. It found zero scope or evidence defect.

All conditions for the already-authorized V8 path are satisfied. LC4V7D1 is
closed and V8 may begin without another user decision. V8 must be genuinely
fresh, content-blind before authorship, use the generic certification decision
taxonomy, and never reuse V7 protected implementation or content.

T3.1-T3.4 remain intact and blocked. T3.5/providers, historical data,
runtime/product wiring, APIs, UI, database, deployment, release, and all
live/write authority remain deferred.
