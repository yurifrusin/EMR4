# DeepSeek Harness relative-specifier repair — lay and technical summary

Date: 2026-08-21
Timestamp: 2026-08-21T13:48:50.6623983+10:00 (Australia/Brisbane)
Reviewed candidate: `3c31f2a9a44713db27b82e338e05374c5d9f62bc`

## Lay summary

The narrow Harness repair is working in static rehearsal. The two module names
that were being emitted as Windows absolute paths now use the same relative
form that already succeeded in the earlier rc7 boot rehearsal. Nothing else in
the worker profile or EMR4 product changed.

Thirty focused tests and 56 wider tests pass. We have deliberately not booted
the Harness yet, so the honest conclusion is that the bad profile shape is
repaired—not that DeepSeek is reachable or ready for development. The next
step is one provider-free, bounded boot of the repaired sentinel only.

## Technical summary

- exact candidate: `3c31f2a9a44713db27b82e338e05374c5d9f62bc`;
- semantic output diff: two YAML module-name rows;
- mechanical fallout: one unused local removed;
- deterministic evidence: 6/6 source and 11/11 projection checks passed;
- tests: 30 focused and 56 widened passed;
- external activity: zero Node/Harness/broker/worker/model/provider/network;
  and
- historical evidence: three exact equality/latch assertions preserved under
  documented deselection.

Four small workflow mistakes were caught fail-closed and corrected or
contained: runner import bootstrap, function-boundary guard scope, wrapper CLI
vocabulary and historical equality-test selection. Yuri's attention is not
required. Product/data/deployment/Pages/protected-ref surfaces remain closed.
