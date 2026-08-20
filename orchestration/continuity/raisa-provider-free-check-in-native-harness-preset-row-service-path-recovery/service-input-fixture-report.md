# Native Harness preset-row service-path fixture report

- Result: `pass`
- Predecessor effective roots: shipped `system` only
- Corrected effective roots: shipped `system`, then derived user `user`
- Corrected EMR4 row: `accepted_exact_user_row`
- Exact row trust / bytes / digest: `user / 158 / 3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1`
- Package-only Node / native Harness processes: `1 / 0`
- Agent / turn / provider / network counts: `0 / 0 / 0 / 0`
- Disposable process and root absent: `true / true`

The rc.7 native profile composer replaces configured preset roots with its
shipped system root. The predecessor additionally disabled the derived user
root, excluding the canonical EMR4 preset under `$DSH_HOME/.agent-presets`.
The closed fixture proves that re-enabling the derived user root produces the
expected shipped-plus-user roster and exactly one healthy, user-trust EMR4 row.

This is provider-free package/service-input evidence. It does not prove a
native Harness process, preset mount, agent, DeepSeek request, model quality,
attempt 006, database or product behavior.
