# Security Sprint: Office Add-in uuid Toolchain Hardening

Date: 2026-07-11

## Finding

GitHub Dependabot alert 5 reported `GHSA-w5hq-g745-h8pq` for transitive
`uuid@8.3.2` in `EMR4 Sidebar/package-lock.json`. The advisory affects v3/v5/v6
calls that provide a caller-owned buffer. The alert was in development/build
tooling, not the three production dependencies.

## Narrow Remediation

- Upgraded direct `webpack-dev-server` from `5.2.5` to `6.0.0`, removing its
  vulnerable `sockjs -> uuid` chain.
- Pinned direct `office-addin-manifest` to `2.1.6`, which resolves its direct
  UUID dependency to `14.0.1`.

The repository uses webpack 5.107.2 at install time; `webpack-dev-server@6`
declares webpack `^5.101.0` and Node `>=22.15.0`. The local Node version is
24.18.0. The existing webpack configuration builds unchanged.

## Verification

- `npm ci --ignore-scripts` completed.
- `npm ls webpack-dev-server office-addin-manifest uuid --all` showed direct
  `webpack-dev-server@6.0.0` and direct `office-addin-manifest@2.1.6` using
  `uuid@14.0.1`.
- `npm run build` passed, with only pre-existing large-asset performance
  warnings.
- `npm run validate` passed.
- `npm audit --omit=dev --json` reported zero vulnerabilities.

## Remaining Risk And Required Follow-up

`npm audit` without `--omit=dev` still reports six moderate development-only
findings through `office-addin-debugging -> office-addin-dev-settings ->
@microsoft/m365agentstoolkit-cli -> @azure/msal-node / teamsfx-core ->
uuid@8.3.2`. This is a distinct Microsoft toolchain modernization decision; it
is not safely solved by forcing a transitive override. The current GitHub alert
was rechecked after commit `99f86616` and remains open, which is expected while
that separate development-toolchain path still resolves `uuid@8.3.2`.

Outcome: partial hardening completed; full development-toolchain closure remains
blocked pending a separately tested Microsoft Office tooling upgrade path.
