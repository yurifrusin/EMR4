# Ariadne Antigravity empty-stderr transport diagnosis

Date: 2026-08-17

Timestamp: 2026-08-17T12:02:01.2827456+10:00 (Australia/Brisbane)

Status: `bounded_reproducible_harness_repair_frozen`

## Incident

Two Gemini 3.7 Flash/high Antigravity launches against exact clean candidate
`f6e5e96dc86a1bb3319692a6ac656fbb756b49df` returned CLI exit code 1, empty
stderr, no review receipt and no terminal decision. Both left the exact review
worktree clean and unchanged. AER-0380 correctly preserves them as transport
failures rather than reviewer rejections.

## Provider-free diagnosis

Antigravity CLI 1.1.13 reports `--print-timeout` as the print-mode wait limit.
The Ariadne launcher supplied an exact `30m` limit. The retry predispatch
receipt was written at 2026-08-17T11:01:56.6746987+10:00 and its preserved
failure at 2026-08-17T11:33:30.0272329+10:00, a deadline-correlated interval.

Sol replayed the same eight-command manifest locally, without a provider, in
the unchanged historical review worktree. All eight commands passed in
150.578 seconds; the longest was the agent-error-register suite at 86.881
seconds. This rules out an inherent 30-minute runtime for the required command
suite under the current local conditions.

The old wrapper recorded only stderr on nonzero exit, so it destroyed any
stdout diagnostic and retained no elapsed time. The evidence supports
`deadline_correlated_transport_timeout`; it does not identify provider reach,
model reasoning, or the internal reason the headless session consumed its
remaining time.

## Narrow repair

- Bound full high-effort verifier print time at 45 minutes.
- On every nonzero exit, atomically write exit code, elapsed milliseconds,
  configured deadline, deadline-boundary observation, exact worktree
  postcondition and stdout/stderr SHA-256 plus byte counts.
- Persist no raw stdout or stderr.
- Return no reviewer decision and admit no candidate on transport failure.
- Preserve both prior failures immutably and permit exactly one fresh Gemini
  3.7 Flash/high review after deterministic admission, with no fallback.

## Closed surfaces

No product, patient, clinical, historical diary or protected data; provider
product call; alternate model; credential or IAM change; database; browser;
deployment; release; Pages; or protected-ref movement is authorised by this
diagnosis.
