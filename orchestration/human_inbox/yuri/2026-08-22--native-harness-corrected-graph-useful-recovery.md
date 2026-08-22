# Native Harness corrected-graph useful-recovery result

## Lay summary

The final one-shot DeepSeek Harness test did not produce a usable edit. It successfully reached DeepSeek, made exactly one prepaid request and attempted the one allowed edit, but the edit tool returned an error and the file remained unchanged. We did not retry it.

The positive result is traceability: unlike the earlier opaque Claude Code failures, we know exactly that there was one process, one completed provider request, one edit attempt, an `edit_error_accept_not_concluded` terminal and no changed file. Everything stopped and cleaned up correctly, with no raw prompt/session material retained.

The negative result is decisive: after all the setup cost, the Harness still produced no useful development contribution. Under the agreed stop rule it is now retired from EMR4 worker allocation, and we return to Raisa product work through other authorised resources. Because the default-off route and later admission-control steps are already accepted, the next tranche is a read-only programme orientation that will identify the narrowest genuinely unfinished check-in blocker.

## Technical summary

- Terminal: `failed_closed`; Harness exit `1`.
- Native process / provider request / retry: `1 / 1 / 0`.
- Provider call completed: `1`; provider call failed: `0`.
- Tool call/result: one direct `edit` / one error result.
- Typed lifecycle: `edit_error_accept_not_concluded`.
- Changed paths: none; candidate: absent; tests on candidate: not run.
- Wall clock: `35,556 ms`.
- Gemini: not invoked because no candidate was admitted.
- Cleanup: Harness, broker and exact root absent; raw logs/session absent.
- Prelaunch local corrections: `1`; postterminal corrections: `0`.
- Product/data/database/Docker/deployment/Pages/protected refs: untouched.

Conclusion: typed orchestration improved containment and diagnosis, but did not make this worker useful enough to justify another Harness recovery cycle. The native Harness is unavailable for future EMR4 worker runs unless you later choose a genuinely new direction.

The clockwork also prevented one real circular move during closeout: it rejected the already-completed route-adapter operation when it was mistakenly proposed as the successor. No state was published. The corrected successor is a new read-only orientation over the completed check-in lineage.

The continuing non-PHI Pushover notification succeeded with request `b2592993-10e8-48ec-818b-d440884df3b6`.
