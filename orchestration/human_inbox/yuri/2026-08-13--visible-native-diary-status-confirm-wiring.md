# Reception One visible status-confirm wiring

Date: 2026-08-13

Timestamp: 2026-08-13T15:42:33+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

Accepted source: `bed49be3d78d79207857b3d3a044cebd334112dc`

## Lay summary

Reception staff can now use the existing appointment-status control with a
truthful visible safety story. Everyday safe changes remain quick. A risky or
final change shows exactly what is changing and explains that the current Diary
will be checked again before saving. A blocked change cannot be confirmed. If
staff cancel, press Escape, or the booking has gone stale, the control returns
to the old status and clearly says that nothing changed.

The interaction works at desktop, tablet and phone sizes and by keyboard. It
does not create a new backend path or trust the screen as the source of truth:
the existing backend confirmation command still decides whether the change is
currently allowed.

## Technical summary

- Result: `raisa_provider_free_visible_native_diary_status_confirm_wiring_pass`.
- Source: `bed49be3d78d79207857b3d3a044cebd334112dc`.
- Existing signed status proposal/confirm only; zero raw status fallback.
- Safe non-terminal path: no extra dialog.
- Warning/terminal path: labelled transition dialog plus final
  authority/current-booking-truth recheck copy.
- Blocked path: no commit action.
- Cancel/Escape/stale/rejection: prior value, non-change message, cleared busy
  state and restored focus.
- Evidence: desktop/tablet/phone in-app rendering with zero console warnings or
  errors; four exact route-intercepted status cases; 144/144 full Diary browser
  tests; 81/81 focused contract/API/security/latch tests; 193/193 canonical
  fast-profile tests.
- The browser transport fixture is labelled `route_intercepted_browser`, not
  live. The accepted local HTTP/PostgreSQL backend proof remains separately
  bound at `b414eb256853c301099d9cf7797a69cd3ec077c5`.

## Issues and deliberately closed surfaces

A stale security-test count was corrected to recognise the existing six inline
allowlist calls plus one pre-normalized allowlisted call. A local browser cache
held an earlier JavaScript asset on the first reload; the current source passed
from a fresh loopback origin and all task-owned browser/server residue was
removed.

No patient/product data, external patient channel, real identity, provider,
credential/IAM, external network, new route, GraphQL/OpenAPI/database change,
other command, deployment, production, release, Pages or protected-ref action
was opened. `docs/branding/` and unrelated untracked material remain excluded.

## Place in Raisa and next tranche

This is the first post-foundation visible staff command boundary: Reception One
now shows the same proposal-versus-current-truth distinction that the future
channel-neutral patient architecture requires.

The sprint engine is continuing to a fresh provider-free CF-D2
observability-first event/cue plan. The visible status flow now tells us what
the durability extension must accelerate and reconcile. Planning will not open
a watcher runtime, database/source access or product data; correctness remains
with the command's current-truth check. Yuri's attention is not required.
