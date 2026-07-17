# Dependency Security Maintenance — 2026-07-17

## Outcome

The Python security workflow's blocking dependency finding is remediated.
EMR4 now uses `PyJWT==2.13.0` for its fixed `HS256` authentication boundary;
`python-jose` and its vulnerable `ecdsa` dependency are removed. The focused
authentication and API Spine tests pass, and `pip-audit -r requirements.txt
--desc` reports no known vulnerabilities.

Bandit now runs even when an earlier workflow step fails. Its committed
baseline contains exactly two reviewed `B324` findings where SHA-1 reproduces
Git blob identity; neither value establishes a security boundary. The
baseline does not suppress other test IDs or future findings.

## Dependabot alert 5

The open `uuid` advisory is confined to Office add-in development tooling.
`npm audit --omit=dev` reports zero vulnerabilities. The full audit reports
six moderate dependency-chain entries rooted in `uuid <11.1.1` through the
Microsoft 365 Agents Toolkit/TeamsFX development toolchain.

A supported lock-only update was tested without `--force` or an override. It
did not remove the advisory and introduced a Node 22 engine requirement into
parts of a Node 20 CI graph, so it was not retained. As checked on 2026-07-17,
the latest `@microsoft/teamsfx-core` (`3.0.14`) still declares
`uuid: ^8.3.2`. The repository therefore preserves its working lock, keeps
Dependabot alert 5 open, and relies on the existing production-dependency
blocking audit while upstream remediation is unavailable.

No `npm audit fix --force`, dependency override, advisory dismissal, or
unsupported transitive substitution is authorized. Reassess when TeamsFX
publishes a compatible dependency graph that resolves to `uuid >=11.1.1`, or
when the Office development toolchain is deliberately replaced.

## Verification contract

- Python dependency audit: blocking and clean.
- Bandit medium/high scan: blocking after its exact reviewed baseline.
- Historical diary leakage lint: blocking and clean.
- Office production dependency audit: blocking and clean.
- Office development dependency audit: visible but non-blocking while alert 5
  remains upstream-blocked.
