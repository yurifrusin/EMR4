# Native Harness useful-worker coordinate recovery — lay and technical summary

Date: 2026-08-22

Timestamp: 2026-08-22T15:26:16+10:00 (Australia/Brisbane)

## Lay summary

The new controls made the DeepSeek failure intelligible, but DeepSeek still did
not produce the requested useful file. We spent exactly one prepaid request and
did not retry. Nothing in EMR4 changed.

The important improvement is that this is no longer an unexplained Harness
failure. The system can now say that the worker reached the edit tool, passed
the permission boundary, and then the edit itself returned an error. Everything
was shut down and cleaned up automatically. The next investigation can be done
without another model call and can focus specifically on the edit interface.

The clockwork also stopped two of my own setup mistakes before the paid request:
a stale file hash and an improper direct update to clockwork-owned records.
Those checks did add preparation work, but they prevented either mistake from
becoming another occupied rerun. That is a real—if still incomplete—efficiency
gain.

One later post-compaction receipt was rejected because I used two descriptive
words outside a closed typed vocabulary. It was corrected locally before
publication, without any model call. This is precisely the kind of residual
form-filling lapse the clockwork catches; the next efficiency target is to make
those fields selector-generated so the invalid words cannot be authored.

## Technical summary

- Operation: `raisa-native-harness-bounded-occupied-useful-worker-coordinate-recovery-rehearsal`
- Model/transport: DeepSeek V4 Flash/high through the native Harness
- Provider requests: one
- Exact lifecycle coordinate: `edit_error_accept_not_concluded`
- Request/edit/result counts: `1 / 1 / 1`
- Candidate: none; changed paths: none
- Gemini: not dispatched because the candidate gate did not open
- Retry/resume/fallback/auxiliary model: all zero
- Cleanup: Harness, broker and disposable root absent; no raw model material retained
- Product/runtime/protected effect: none

The accepted next tranche is provider-free:
`deepseek-native-harness-provider-free-edit-argument-result-coordinate-diagnostic-recovery`.
It will exercise the real accepted edit tool over a closed authored-synthetic
matrix and produce a non-sensitive typed subcoordinate. It cannot call a model
or provider and does not authorize another occupied attempt.
