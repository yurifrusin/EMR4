# Local analysis context

This design analysis was prepared in `C:\Users\sarashera\emr4` against
committed source revision `240bf0b56071b5ea0f3d71e92ff765acc2f727d9` plus
the explicitly inventoried maintenance changes. The evidence identity is
`evidence-manifest.json`; its SHA-256 is
`22bad242660dd7e25fb2cbef884865d4b7e1549f2f6134fb0378caf18560863b`
and is also recorded in `hardening.json`.

The review used repository contracts and GitHub's read-only API state. It did
not open protected Bernie holdouts, invoke providers, alter GitHub settings,
or perform a full security scan. CodeQL candidates remain unvalidated until a
separate reachability and exploitability review records a decision for each.

Evidence labels used by the proposal:

- E001: master branch protection absent.
- E002: secret scanning enabled but push protection disabled.
- E003: ten open CodeQL candidates classified high.
- E004: Dependabot alert 5, dev-only `uuid` advisory.
- E005: existing CodeQL, SCA, Bandit, leakage-lint, and Dependabot automation.
- E006: API Spine and live handover document structural security work still
  required before production expansion.
