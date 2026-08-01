# Dependabot alert 17 static repository-impact triage

Date: 2026-08-01

Repository revision: `c9b157140bfc37af361de6e6527d14f01b0438ea`

Source: GitHub Dependabot alert 17 / `GHSA-3jxr-9vmj-r5cp` /
`CVE-2026-13149`

## Verdict

`not_actionable`, high static confidence.

The advisory is genuine and the lockfile contains the vulnerable
`brace-expansion@2.1.1` instance. The supported EMR4 security boundary does
not reach its vulnerable behavior.

## Normalized claim

- Component: `brace-expansion@2.1.1`, transitively under
  `@typescript-eslint/typescript-estree`.
- Claimed source: an attacker-controlled minimatch/glob pattern containing
  consecutive non-expanding brace groups.
- Sink: exponential CPU consumption in `brace-expansion.expand()`.
- Impact: denial of service in the calling Node process.
- Native state: open high-severity development dependency alert created at
  `2026-08-01T06:05:44Z`.

## Static proof chain

1. `EMR4 Sidebar/package.json` declares `office-addin-lint` only in
   `devDependencies` and exposes it through local lint/prettier scripts.
2. `EMR4 Sidebar/package-lock.json:12566` records
   `office-addin-lint@3.0.9` as `dev: true` and its dependency on
   `typescript-eslint`.
3. `EMR4 Sidebar/package-lock.json:5551` records
   `@typescript-eslint/typescript-estree@8.8.1` as `dev: true`, its minimatch
   dependency, and the nested vulnerable `brace-expansion@2.1.1` instance at
   line 5580.
4. The exact locked `typescript-estree` source uses this minimatch instance
   only to compare a file path with `serviceSettings.allowDefaultProject`
   patterns in the optional project-service path.
5. The supported `office-addin-lint` configuration selects the TypeScript
   parser but does not enable `parserOptions.projectService` or supply
   `allowDefaultProject`. The Office add-ins recommended parser options also
   contain only JSX settings.
6. No repository product, backend, Office taskpane, webpack runtime or
   supported command passes remote/request input into this brace-pattern
   sink. Production dependency installation excludes the entire chain.

## Boundary assessment

- Product surface: local developer lint tooling.
- Source trust: no supported source exists; enabling the sink would first
  require a trusted developer to change source-controlled lint configuration.
- Policy basis: root `SECURITY.md` requires source/control/sink and supported
  boundary evidence rather than scanner severity alone.
- Supported security boundary crossed: no.

## Counterevidence and proof gaps

Counterevidence is the exact development-only lock metadata, the supported
lint configuration's absence of project service/default-project patterns, and
the absence of any EMR4 caller that supplies untrusted patterns.

No material proof gap prevents this verdict for the locked revision. A later
tool release could add another caller, so review reopens if the dependency
graph or supported lint configuration changes.

## Disposition boundary

The finding is registered as `SF-0020` with owner and high-severity SLA. Its
native GitHub state remains open and desired-open. No dismissal, dependency
override, force update or lockfile change is authorised or performed here.
