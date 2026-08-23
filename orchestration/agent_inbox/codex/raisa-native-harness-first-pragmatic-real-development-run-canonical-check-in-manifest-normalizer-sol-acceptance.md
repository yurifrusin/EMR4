# Sol acceptance — canonical check-in manifest normalizer

Date: 2026-08-23

Decision: `accepted_pending_clockwork_publication`

Reviewed source: `ae62faf95b289b369a6eea1793ee4325f33447bc`

I accept the unmounted normalizer and focused tests. The accepted result is the
Sol recovery candidate, not a native-Harness worker candidate. The native
session was rejected before provider I/O because the stock headless runner's
seven declared tools exceeded the broker's exact three-tool allowlist.

Acceptance is supported by 149 passing serial focused/surrounding tests, Ruff,
compilation, `git diff --check`, complete disposable-process/worktree cleanup,
and direct source review against the API Spine boundary. Denials release no
digest or manifest, successful normalization uses only caller-supplied bytes,
and full Git object IDs are enforced in source and test evidence.

Gemini review remains declined: no API meaning or mounted product path changed,
there was no worker candidate to veto, and no ordinary risk trigger arose.
The result grants no operational, admission, runtime, deployment or protected
authority.
