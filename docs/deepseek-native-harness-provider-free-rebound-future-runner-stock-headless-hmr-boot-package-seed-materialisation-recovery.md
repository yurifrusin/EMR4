# Rebound future-runner boot package-seed materialisation recovery

Date: 2026-08-22

Timestamp: 2026-08-22T00:35:46.5430875+10:00 (Australia/Brisbane)

Status: **frozen recovery before another prelaunch invocation**

## Generation-2 result

Prelaunch generation 2 successfully replaced the Windows npm wrapper with one
directly owned, hash-bound Node/npm-CLI process. That process remained
nonterminal until the frozen 600-second deadline. The controller terminated and
waited for it, removed the disposable root, and wrote no canonical attempt
evidence. No native Harness process or runner activation occurred, so native
execution attempt `rebound-stock-headless-hmr-boot-attempt-001` remains
unconsumed.

The typed result is
`orchestration/continuity/deepseek-native-harness-provider-free-rebound-future-runner-stock-headless-hmr-boot-proof/prelaunch-materialisation-failure-002.json`.

## Package-only seed

A previously materialised provider-free rc.7 package tree was reduced to exactly
three package surfaces—`package.json`, `package-lock.json`, and `node_modules`—and
copied to the dedicated local Harness cache. No prompt, session, terminal,
provider, worker or attempt evidence is present in the seed.

Frozen seed readings:

- classification: `provider_free_rc7_package_only_seed`
- package-lock SHA-256: `a89defcd8a2c5aae4a54c03bda98e2585711fce881b4b08c90ca4808d45555f4`
- root package SHA-256: `0009f94a6b9c3495404d4a1a89e0eef82ba4948c4ea29994c210a271390e64db`
- package-lock package count: `588`
- node-modules file count: `32744`
- node-modules byte count: `219364530`
- node-modules canonical tree SHA-256: `d84e73067c8dbbf4836969eb948012fd364ee454bb07744cfe486995a256084d`
- DSH manifest SHA-256: `7a9f356ad1e27c7013b44619bc675b8cb877f995cd0951ab3dfeb10d4edcc361`
- reparse-point count: `0`

The canonical tree digest is a SHA-256 over each case-stably sorted relative
POSIX path, file size and file-content SHA-256. Both the seed and disposable copy
must independently reproduce the exact digest, file count and byte count.

## Narrow generation-3 correction

Generation 3 removes npm execution entirely. Before the native boundary, the
controller must:

1. verify the dedicated seed root is a real directory with exactly the three
   admitted top-level surfaces and no reparse point;
2. validate the two root files, lockfile package count, DSH identity and every
   file's canonical tree digest;
3. copy only those package surfaces into the fresh disposable installation;
4. independently hash the disposable copy and require exact equality;
5. run the already accepted installed-package version and installed-source
   checks; and
6. prove the seed was read only and no materialiser process existed.

The native Harness lifecycle, runner/helper bytes, HMR mutation, deliberate
preset-root mismatch, target absence, broker-zero join, single terminal and
single native-process/no-retry conditions remain unchanged.

## Recovery acceptance

- materialiser process count and retry count are both zero;
- seed and copy digests, file counts and byte counts match exactly;
- package/source validation passes before the native `Popen`;
- any seed or copy mismatch fails before a native process and cleans the root;
- no non-package historical artifact is read or copied;
- all original no-worker, no-provider, no-target, no-data, no-product and
  protected-ref boundaries remain exact.
