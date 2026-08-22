# Threat-model delta: package-unloaded guard–bridge module graph

Date: 2026-08-22

Timestamp: 2026-08-22T10:08:50.8671885+10:00 (Australia/Brisbane)

Status: **frozen with the package-unloaded module-graph plan**

## Boundary

One absolute-path Node process may evaluate the exact accepted derived guard,
bridge and sanitizer with three authored-synthetic cases and two minimal local
package stubs inside a disposable root. The derived runner, installed package
seed, native Harness, DeepSeek worker, models, providers, product source and
protected refs remain outside the boundary.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| The graph evaluates bytes different from the accepted correction | Recompute the guard and bridge from accepted sources, select the accepted sanitizer, and require all three exact SHA-256 bindings before materialization. |
| A local stub silently becomes a functional package substitute | Freeze each stub to one export and no filesystem, environment, network, subprocess, provider or package-cache access; exact source hashes enter the contract. |
| Node resolves the installed rc.7 package instead of the local stubs | Materialize exact scoped-package manifests and exports inside the disposable root, launch the fixture by absolute path from that root, reject external package paths, and record only the two expected local stub loads. |
| The runner or native Harness is pulled into the graph | Permit only the exact eight-file materialization inventory, reject runner tokens/imports, and record zero runner and native-Harness processes. |
| Several child processes disguise retries | Resolve Node without a process probe, invoke it exactly once, prohibit child-process APIs in all authored sources and record one consumed attempt. |
| Success passes without proving complete guard behavior | Require one exact mount plus scope lookup, initial view, exact restriction, schema projection and exact four-field successful result. |
| Failure terminals pass after scope or tool effects | Missing-service and missing-mount cases must return the exact typed mount terminal and record zero scope, view, restrict and schema calls. |
| Raw exceptions escape through the guard handoff | Catch only the exported typed terminal class; retain only its exact schema-owned terminal and reject message, stack, cause and arbitrary detail. |
| Node startup or syntax failure leaks local paths and environment detail | Persist only exit code plus stream byte counts and digests before interpretation; never persist or echo raw streams. |
| Environment preload mutates the graph | Use the accepted five-key Windows environment and prove `PATH` and `NODE_OPTIONS` absent. |
| Temporary JavaScript or package metadata survives | Remove the complete disposable root before stream parsing and require exact post-cleanup absence. |
| Output parsing admits descriptive or reordered results | Validate exact schema, key order, case order, values, one stdout line and zero stderr. |
| Procedural control work expands without increasing occupied capability | A passing graph must advance directly to the complete package-unloaded runner; only an observed new failure mode can justify an intervening control. |
| A short Git abbreviation is manually expanded | Contracts contain no object IDs; plan and implementation sources and push ancestry are derived directly from Git and the repository resolver. |
| Passing graph evidence is overstated as native-Harness proof | Claim only package-unloaded guard behavior; withhold runner, installed-package, native boot, worker, model/provider and coding-quality claims. |
| Unrelated worktree material is swept into the tranche | Preserve every existing untracked path, especially `docs/branding/`, and stage only explicit tranche paths. |

## Residual boundary

A pass proves that the exact derived guard can call the accepted bridge,
consume the exact scope and tool views, project exactly three effective tools,
and preserve the two content-free mount terminals using local package stubs in
one isolated Node process. It does not prove the derived runner, installed
package composition, native-Harness boot, a DeepSeek turn, worker quality,
model/provider access, product authority or production suitability.
