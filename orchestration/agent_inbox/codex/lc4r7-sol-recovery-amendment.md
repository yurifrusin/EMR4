# LC4R7 Sol Recovery Amendment

Date: 2026-07-15

GPT Sol adopted the DeepSeek Flash candidate at `f71481a9` only as untrusted
source under the Ariadne recovery lease. The worker's second revision fixed
the substantive classification and input-order route, but acceptance review
found bounded evidence defects:

- alternate-order tests compared hash/taxonomy rather than the full canonical
  queue and primary count/hash evidence;
- `run_check` could raise on missing queue fields instead of failing closed;
- several report sections were protected only indirectly by the whole-report
  hash rather than explicit contract comparisons; and
- the completion artifact said the final worker pass had no denial although
  its launcher receipt records one denied PowerShell `python --version` call.

Sol owns the amendments that add exact canonical queue equality, explicit
selection/queue/primary/dimension/assertion report checks, frozen-report hash
validation, pre-hash record schema/type validation, full alternate-order
equality assertions, a malformed-record fail-closed test, and corrected worker
provenance. No classifier, corpus, fixture, interpreter, replay, generator,
provider, route, database, UI, historical-diary, holdout, or write surface was
changed.

Independent Gemini review and the serial acceptance gate remain required
before integration is accepted.
