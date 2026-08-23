# Canonical check-in manifest normalizer and native Harness reading

## Lay summary

The useful Raisa work is complete: EMR4 can now read and strictly validate the
planned reference-only check-in environment manifest without touching any
secret, environment setting, database or live service. It remains unmounted
and does not enable check-in for ordinary practices.

The native DeepSeek Harness did not actually reach DeepSeek on this run. Its
standard headless preset offered seven file/planning tools, while our safety
broker allowed only three, so the broker rejected the request before it left
the machine. That is a clear, traceable transport mismatch rather than an
unexplained model failure. We did not spend another tranche perfecting the
interoperability: Sol completed the real task and the adoption rule now says to
use a compatible accepted runner when available, otherwise skip that worker
lane and continue development.

## Technical summary

- Reviewed source: `ae62faf95b289b369a6eea1793ee4325f33447bc`.
- Verification: 149 serial tests, Ruff, compilation and diff hygiene passed.
- Native attempt: one 7.404-second session, zero provider calls, zero tool
  calls, zero changed paths, one broker rejection, no retry.
- Cause: stock rc.7 headless request tools were `edit`, `exit_plan_mode`,
  `glob`, `grep`, `read`, `read_image`, `write`; broker allowlist was `edit`,
  `glob`, `read`.
- Trace caveat: the exact request header was retained, but the coordinator did
  not retain the broker's textual rejection reason. Pinned source confirms the
  mismatch; the run is attributable but not counted as trace-complete.
- Cleanup: processes, worktree registration and disposable attempt root are
  absent. The raw attempt material was permanently removed and cannot be
  recovered from the filesystem or Recycle Bin.
- Parallelism: DeepSeek attempted/no candidate; Gemini declined; native
  subagents declined by policy; Sol recovered and accepted.
- Next: implement the provider-free, unmounted typed operational-evidence input
  model, then the pure evidence-gate evaluator. No external fact or activation
  is implied.
