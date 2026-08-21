# DeepSeek native Harness preset-mount source cache-root recovery

Date: 2026-08-22

Timestamp: 2026-08-22T04:50:32.7098461+10:00 (Australia/Brisbane)

The first focused reconciliation run looked for the accepted installed package
seed under `AppData/Local/emr4-native-harness`. That location was inferred from
the separate npm-cache convention and was not the package-only seed location
owned by the accepted native-Harness materialisation chain.

Five focused assertions and deterministic `--check` failed closed at
`source_root_missing_or_unsafe`. No source was read from an alternate location,
no output was written and no native Harness process was launched.

The reader and tests now bind the accepted user-profile package seed under
`.cache/emr4-native-harness`. Nine focused tests, static checks and the exact
zero-process deterministic projection then passed. Future descendant readers
copy the package-seed root from the accepted materialisation lineage rather
than inferring it from a different cache's environment convention.
