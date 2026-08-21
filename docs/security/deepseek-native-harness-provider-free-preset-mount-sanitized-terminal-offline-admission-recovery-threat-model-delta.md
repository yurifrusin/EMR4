# Threat-model delta: preset-mount sanitized-terminal offline admission recovery

Date: 2026-08-22

Timestamp: 2026-08-22T07:16:44.5979213+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

## Scope delta

One consumed native process left a content-free envelope, one typed sidecar and
one disposable root after a controller composition defect interrupted admission
and cleanup. Recovery reads only those exact retained files and launches no
Node, Harness, worker, model or provider process.

## Controls

| Threat | Fail-closed control |
|---|---|
| A second process is disguised as recovery | The recovery controller contains no Node/Harness launch path, requires the consumed latch and records zero recovery processes. |
| A different disposable directory is read or removed | Resolve the accepted parent, require exactly one non-symlink child with the frozen prefix, reject escape, and verify no Node command line owns the exact root before cleanup. |
| Sidecar substitution changes the observed terminal | Require exact byte count and SHA-256 from the presemantic immutable envelope before parsing. |
| Schema-version repair rewrites history | Admit the predecessor token as the observed token in a separate recovery schema/projection; preserve the consumed candidate and record the successor-token mismatch explicitly. |
| Raw failure detail crosses the boundary | Persist only schema-owned fields and closed codes; reject additional properties and retain no raw streams, messages, stacks, causes, paths, environment or credentials. |
| Cleanup destroys evidence before durable admission | Persist the exact admitted typed terminal projection exclusively before removing the verified root. |
| Cleanup targets an active process | Require zero exact-root-owned Node processes immediately before removal and remove only the resolved verified root. |
| A broader terminal is misrepresented as proof of the new bridge | Only `preset_mount_failure_attributed` proves that runtime path; the observed composition-unclassified terminal explicitly leaves it unproved. |
| Source repair retroactively changes the executed candidate | Bind recovery evidence to the consumed candidate and describe controller repairs as prospective only. |

## Security acceptance

Accept only an exact envelope/sidecar binding, closed typed projection, zero
owned process, exact retained-root cleanup, zero provider/product effects and no
retry authority.

