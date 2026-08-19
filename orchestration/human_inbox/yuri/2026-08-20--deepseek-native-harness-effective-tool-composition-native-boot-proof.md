# DeepSeek native Harness composition boot — paired closeout

Date: 2026-08-20

## Lay summary

The one permitted native Harness rehearsal started and safely reached the
point where the stock headless system confirmed its live-reload watches. It
then failed before producing the promised `read`/`glob`/`edit` tool reading.
Nothing escaped: there was no network, model, provider or agent session, and
the process and temporary files were completely removed.

The important limitation is that our recorder said only “execution failed.”
It did not retain which precise step failed, and its recorded zero-millisecond
duration is not meaningful. So this is not evidence that the Harness is bad,
nor evidence that its tool composition works. It is evidence that our
preterminal recorder needs one more tightening pass.

I did not retry the consumed attempt. I am continuing to a deterministic
recovery that will make every early failure produce a specific safe coordinate
before we consider a separately named new native run.

## Technical summary

- Candidate `b8331387120ade3634e73ba799f4a9fb48389f5b` passed 13 focused and
  139 combined tests plus Ruff and compilation. The closeout's provider-free
  wrapper required two test-only reruns because it removed `LOCALAPPDATA` and
  home discovery; the corrected cache test derives the explicit local cache
  root from the repository parent.
- `native-composition-attempt-001` completed exact offline rc.7
  materialisation (`115532 ms`) and retained
  `sentinel_activated -> stock_headless_hmr_ready`.
- No guard-start event or terminal was retained; result is fail with generic
  `NATIVE_COMPOSITION_EXECUTION_FAILED` and exit code `1` after containment.
- Network, session, turn, broker, model, provider, occupied-worker, Docker and
  database counts are zero.
- Process wait, process absence and disposable-root absence all passed.
- The native proof is rejected; the bounded failed result and cleanup are
  accepted and immutable.
- Gemini was not dispatched because its frozen gate required a passing native
  terminal. DeepSeek and native-subagent lanes remained declined.
- Next:
  `deepseek-native-harness-provider-free-preterminal-activation-observability-recovery`,
  deterministic/provider-free first and no native rerun.

The required non-PHI Pushover closeout notification succeeded with request
`c6c70f27-5f3f-4342-a926-957fa77eb1bc`.

No product, ordinary-practice, data, deployment, Pages or protected-ref
authority changed. `docs/branding/` and all unrelated untracked files remain
preserved.
