# Native Harness preset-mount sanitizer Windows minimum-environment report

Date: 2026-08-22

Timestamp: 2026-08-22T06:00:31.402343+10:00 (Australia/Brisbane)

Candidate source: `ceac8b2600530bf858394bb84e66a42ec3d016f4`

Result: **pass**

One authored-synthetic local Node process received exactly the five
allowlisted Windows runtime keys. Their values were never persisted.
The unchanged sanitizer/wrapper emitted the exact fifteen-result vector
with zero stderr, and the content-free process envelope was retained
before semantic admission.

Safe code counts:

- `PRESET_MOUNT_AGENT_SCOPE_ABSENT`: 2
- `PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE`: 1
- `PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED`: 1
- `PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT`: 1
- `PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT`: 1
- `PRESET_MOUNT_ROOT_SERVICE_LEAK`: 1
- `PRESET_MOUNT_UNCLASSIFIED`: 8

This admits the pure sanitizer under the five-key local fixture only.
It does not prove the exact cause of the previous exit 134, connect a
runner, select a repair, authorise another process, start the native
Harness, launch a worker/model/provider request or perform product/data
work.
