# DeepSeek native Harness plugin-tree source-coordinate diagnosis

Date: 2026-08-21
Timestamp: 2026-08-21T13:25:47.751756+10:00 (Australia/Brisbane)

## Result

- Verdict: `unique_supported_coordinate`
- Owner classification: `profile_input`
- Matching source branches: `1`
- Narrowest supported coordinate: `profile_patch.initial.synthetic-worker-hmr-sentinel.name:absolute_windows_path_not_normalized_to_relative_or_file_url_before_loader_import`
- Separate provider-free repair justified: `true`

## Reading

The initial patch has exactly one custom module import and authors it as an absolute Windows filesystem specifier. The rc.7 root Include uses the unnormalised Include path, whose loader reserves relative handling for dot-prefixed names and otherwise imports the supplied specifier. The resulting root-apply/import/underlying-error wrappers plus the boot wrapper match the four-node terminal. The accepted provider-free predecessor proves the same sentinel and later runner with profile-relative specifiers. A separate repair may replace only this two-row specifier family before any new boot proof.

The diagnosis used only the exact local rc.7 package source, accepted profile
authors, preset and immutable sanitized attempt-004 terminal. Node, Harness,
broker, worker, model, provider and network counts are all zero. No raw terminal
message, code, stack, path or stream was reconstructed.

## Claim boundary

Static source evidence narrows the attempt-004 startup branch and justifies at most a separate provider-free two-row specifier repair. It does not prove a repaired boot, reach DeepSeek, authorize an occupied retry or open product, data, deployment or protected refs.
