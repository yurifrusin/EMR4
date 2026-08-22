# Package-unloaded guard–bridge attempt-001 source diagnosis

Date: 2026-08-22

Timestamp: 2026-08-22T10:24:39.7795396+10:00 (Australia/Brisbane)

Result: **bridge_relative_import_target_absent**

The consumed process exited 1 with zero stdout bytes and 938 stderr bytes. The
content-free process envelope was persisted before interpretation. No raw
stream content was read, retained or used for this diagnosis.

The exact derived guard imports
`./preset-mount-sanitizer-runner-bridge.mjs`. The frozen materialization
inventory instead placed the byte-exact accepted 1,661-byte bridge under
`deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge.mjs`.
The relative import target was absent even though the correct bridge bytes were
present under a different name.

This diagnoses import-graph closure only. It does not prove guard behavior and
does not authorize a retry. A distinct successor must derive every relative
specifier, prove the complete import closure before process admission, and then
consume its own one-attempt boundary.
