# Provider-free historical recovery validator source-binding repair report

Date: 2026-08-21

Result: `pass`

- Historical source commit:
  `12d8758fee2504435ca2b4ccf6225b9d7a86a6a1`
- Exact historical Git blobs checked: `7`
- Immutable historical recovery artifacts checked: `8`
- Bounded local Git subprocesses per check: `9`
- Old-validator subprocesses: `0`
- Native Harness / broker / worker processes: `0 / 0 / 0`
- Model / provider requests: `0 / 0`
- Occupied attempts: `0`
- Raw stream bytes reconstructed or retained: `0`

The old recovery validator now compares its dynamic behavioral reading with the
accepted historical source projection rather than with mutable descendant file
bytes. Its schema, scenario, hostile-mutation, controller-ordering and consumed-
attempt integrity checks remain active, including when Python subprocess entry
points are forbidden.

The separate repair checker resolves the full historical commit, proves
ancestry and reads the seven exact Git blobs. All hashes match. No accepted
historical artifact changed.

This proves historical validator stability only. It does not identify deleted
attempt output, measure DeepSeek, prove native-Harness reliability or authorize
another occupied run.
