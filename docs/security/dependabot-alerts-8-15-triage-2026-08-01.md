# Dependabot alerts 8-15 static triage — 2026-08-01

Target: `2ae8f2173276147e59be361e0182f6cb4b7453fa` plus the accepted
uncommitted cross-checkpoint working tree
Source: exact GitHub REST reads of Dependabot alerts 8-15
Method: static advisory/source/control/sink and supported-product-boundary
trace; no build, test, application, proof of concept or force upgrade

## Outcome

All eight advisories describe genuine upstream defects. None survives as an
actionable EMR4 security finding at this revision. Every affected lock entry is
`dev: true`; the shipped add-in dependency set contains only `core-js` and
`regenerator-runtime`, and the blocking `npm audit --omit=dev` gate remains the
production dependency control.

The verdict is not “development dependencies never matter.” Each alert was
traced to its actual consumer. The supported repository path either does not
call the vulnerable operation, or supplies only trusted local developer
configuration with no product/runtime security boundary. Compatible upstream
updates remain preferred. Force audit fixes and dependency overrides remain
prohibited.

## Instance-preserving dispositions

| Alert | Package / advisory | Static path and boundary | Verdict | Native reason |
|---:|---|---|---|---|
| 8 | `adm-zip`, GHSA-xcpc-8h2w-3j85 | Dev-only Office archive helpers. The repository start command supplies `manifest.xml`; supported workflows do not accept an untrusted ZIP. | `not_actionable` | `tolerable_risk` |
| 9 | `@hono/node-server`, GHSA-frvp-7c67-39w9 | Transitive MCP SDK package. The SDK consumes `getRequestListener`, not the affected Hono static-file helper. Actual EMR4 dev static serving is webpack on `127.0.0.1`. | `not_actionable` | `not_used` |
| 10 | `fast-xml-parser`, GHSA-8r6m-32jq-jx6q | Dev-only TeamsFX Azure Storage parser. No repository source or workflow supplies attacker-controlled XML through that chain. | `not_actionable` | `tolerable_risk` |
| 11 | `fast-uri`, GHSA-4c8g-83qw-93j6 | Ajv/schema-reference normalization only. No EMR4 host-security policy or fetch/http client consumes its result. | `not_actionable` | `not_used` |
| 12 | `fast-uri`, GHSA-v2hh-gcrm-f6hx | Same exact parser boundary as alert 11; the host-policy/use mismatch prerequisite is absent. | `not_actionable` | `not_used` |
| 13 | `shell-quote`, GHSA-395f-4hp3-45gv | `launch-editor` parses only a trusted operator editor specification; request data does not reach `shellQuote.parse`. | `not_actionable` | `tolerable_risk` |
| 14 | `js-yaml`, GHSA-52cp-r559-cp3m | Dev-only ESLint/TeamsFX configuration parser. No runtime YAML ingestion exists and the Node security job does not parse untrusted YAML. | `not_actionable` | `tolerable_risk` |
| 15 | `brace-expansion`, GHSA-3jxr-9vmj-r5cp | Dev-only minimatch chain. Developer-authored patterns are trusted configuration; matched filenames do not become patterns. | `not_actionable` | `tolerable_risk` |

## Evidence anchors

- `EMR4 Sidebar/package.json` separates the two production dependencies from
  the development toolchain and fixes the supported commands.
- `EMR4 Sidebar/package-lock.json` marks every affected resolution `dev: true`.
- `EMR4 Sidebar/webpack.config.js` uses fixed source-controlled globs and binds
  the development server to `127.0.0.1`.
- `.github/workflows/node-security.yml` installs the lock, validates the Office
  manifest, blocks on the production audit and keeps the full dev audit
  visible.
- Installed-source tracing confirmed the exact relevant consumers:
  `office-addin-debugging`/TeamsFX archive helpers, MCP
  `getRequestListener`, Azure `parseXML`, Ajv schema resolution,
  `launch-editor` editor parsing, ESLint/TeamsFX YAML loading and minimatch.

## Residual and reopening conditions

A row must return to `needs_review` if a new supported path accepts untrusted
ZIP, XML, YAML, editor-command or glob-pattern input; if Hono static serving or
a fast-uri-based network policy is introduced; if an affected package enters
the production bundle; or when a compatible upstream toolchain can remove the
vulnerable resolution. The durable review/expiry dates are in
`docs/security/security-finding-register.json`.

No dependency, lockfile, runtime, provider, cloud, product or deployment state
was changed during this static triage.
