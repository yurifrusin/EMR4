# Threat-model delta: DeepSeek native Harness preset-mount root-service-forwarding process-free correction

Date: 2026-08-22

Timestamp: 2026-08-22T08:47:30.5660782+10:00 (Australia/Brisbane)

Status: **frozen with the process-free correction plan**

## Boundary

This tranche derives prospective runner, guard and bridge bytes in Python from
exact accepted source. It does not materialize or execute JavaScript, start
Node or the native Harness, invoke a worker/model/provider, mutate the accepted
package seed or source owners, touch product source, or move protected refs.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| The root service is forwarded but the guard still consults its narrower private context | Require an explicit `presetService` guard parameter and prove zero `agentCtx.agentPresets` occurrences in the derived guard. |
| A caller still dereferences or binds `.mount` before bridge entry | The guard passes the service object only; the bridge alone reads, validates and calls the mount handle. |
| Mount validation moves inside the bridge but remains outside its sanitized region | Prove the service check, handle read, function check and call all occur after `try` entry and before the bridge catch. |
| An invalid service or mount handle escapes as another unclassified outer composition failure | Derive the rejection inside the bridge try and require the exact content-free `PRESET_MOUNT_UNCLASSIFIED` terminal through the accepted sanitizer. |
| Prospective rewriting silently alters accepted semantics | Bind every input byte/hash, require one occurrence of every rewrite anchor, preserve accepted success and safe-code branches and fail on any extra or missing coordinate. |
| Static source inspection is overstated as runtime proof | Label the result prospective only and require a separately frozen isolated Node fixture before any native process can be considered. |
| A manually recalled Git ID contaminates the contract | Forbid Git-ID fields and 40-character hexadecimal identities in the caller-authored contract; derive plan and candidate commits only through the repository resolver. |
| Source derivation becomes execution | Permit Python source construction and Git/file reads only; prohibit JavaScript materialization, Node, native Harness, worker, model and provider processes. |
| Raw error or environment detail is introduced | Reject derived source containing raw message, stack, cause, path, prompt, response, environment or credential release coordinates. |
| Unrelated worktree material is swept into the tranche | Preserve every existing untracked path, especially `docs/branding/`, and stage only explicit tranche paths. |

## Residual boundary

A passing correction admits a deterministic prospective wiring shape only. It
does not prove JavaScript evaluation, a valid installed runtime composition,
native boot, preset mounting, DeepSeek behavior, model/provider access, product
authority or production suitability. The isolated Node-fixture successor and
any later native attempt each require their own frozen boundary.
