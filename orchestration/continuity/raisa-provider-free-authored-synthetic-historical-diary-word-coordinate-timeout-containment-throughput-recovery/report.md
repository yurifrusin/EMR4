# Raisa provider-free authored-synthetic historical Diary Word-coordinate timeout containment and throughput recovery — report

Date: 2026-08-24

Timestamp: 2026-08-24T06:06:37.7778480+10:00 (Australia/Brisbane)

Result: `passed`

Reviewed source: `9cbc39cda3503216b27e81aca4f9199db8561b49`

## Conclusion

The recovery repaired both the safety and observability gaps exposed by the
historical-run timeout. A deliberately interrupted empty Word child was
removed using its exact PID, process class and start-time identity, with no
process-name fallback and no change to the user's pre-existing Word process.

The second proof opened 12/12 newly authored generic documents and processed
2,016 structural coordinate slots plus 288 explicit story anchors. It completed
in the 30–119 second bucket at the top `16_or_more_per_second` floor bucket.
All generated documents and sidecars were removed.

## Meaning and next work

This result proves typed timeout containment and useful synthetic throughput;
it does not measure the older historical `.doc` slice or validate a reusable
scenario. It is now reasonable to plan one fresh 80-snapshot local measurement
under a new attempt root, with an honest 1,800-second ceiling, exact parent
cleanup and count-only progress. The consumed prior attempt remains immutable
and cannot be retried.

The first-use gate remains closed. No historical data, provider/model, product,
runtime, database, ordinary-practice, deployment, release, Pages, protected
evidence or protected ref was accessed or changed.
