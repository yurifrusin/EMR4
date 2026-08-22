# Current-node closeout timestamp guard repair

Date: 2026-08-23

Timestamp: 2026-08-23T00:36:31.8959087+10:00 (Australia/Brisbane)

## Lay summary

One more piece of the clockwork is now genuinely automatic. Instead of relying
on an agent to remember that every closeout document needs both a date and a
Brisbane timestamp, the repository now reads the current clockwork node and
rejects any missing or inconsistent field.

The three omissions that exposed the weakness have been repaired with their
already-recorded time. Nothing else in those accepted records changed. The
guard follows the graph forward automatically and also keeps checking those
three repaired documents.

This removes one recurring memory burden without adding another form or
ledger. It did expose one separate orchestration inefficiency: a long test run
had to be repeated because its process coordinate was not retained. That rerun
is recorded honestly and is not a failure of the new timestamp guard. The
clockwork also rejected one free-form stage kind outside its closed vocabulary
before writing anything; the intent was corrected to the registered
`maintenance` kind. That shows the downstream guard works, but also reinforces
the case for typed intent authoring upstream.

Nothing in the product was enabled or changed. No patient or practice data,
model worker, provider, database, deployment or protected branch was involved.

## Technical summary

- reviewed source: `4fe5e8b8e2aab3bb73cdf831a0b8edfeda6f1f7c`;
- exact historical repair: three inserted timestamp lines, all equal to the
  predecessor graph time;
- reusable guard: current Continuity node categories `plans`, `closeouts` and
  `acceptances`;
- current coverage: five Markdown artifacts, including this paired summary;
- hostile cases: five of five rejected;
- evidence: 10 focused and 112 captured integrated checks pass;
- efficacy: zero semantic source corrections, zero new forms/ledgers, one
  recorded duplicate suite caused by an unretained process coordinate and one
  contained closed-vocabulary intent repair; and
- protected refs and `docs/branding/` remain untouched.

The next tranche is a read-only convergence review of the original twelve
ordinary check-in admission-readiness dimensions against the exact descendants
now accumulated. It will tell us whether any real evidence gap remains; it
cannot enable ordinary practice or change product/runtime source. Yuri's
attention is not required.
