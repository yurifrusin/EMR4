# Threat-model delta: Reception One Bureau runtime UI wiring

The new trust crossing is one explicit local-development planner selector in
the existing authored-synthetic Bureau. It controls only the closed
`planner_mode` enum sent to the backend proposal route.

Controls:

- selector absent outside explicit smoke plus Bureau-runtime query gates;
- deterministic selected by default;
- closed `deterministic` / `isolated_vertex` values only;
- no browser-supplied provider, model, project, identity, location, hostname,
  credential, cost, fallback or data-class override;
- isolated mode still requires the backend's separate default-off gate;
- no deterministic fallback after isolated selection;
- trusted backend alone builds context, resolves identifiers, checks freshness
  and invokes proposal adapters;
- browser receives only admitted typed proposal fields, planner mode, bounded
  call count, proofreader disposition and an opaque audit reference;
- prior provenance is removed on every new request and on failure;
- no confirmation or mutation affordance is added;
- provider-free acceptance forwards no provider credentials and permits only
  loopback browser traffic;
- database hashes and counts are verified unchanged; and
- child-process, temporary-directory and disposable-database residue is checked.

Fail closed on hidden-gate bypass, unknown planner value, non-synthetic route
use, isolated backend-gate rejection, response-schema drift, proofreader
non-admission, stale provenance, external browser traffic, database mutation or
cleanup residue.

This tranche does not validate or authorise another live model call, real-data
use, production, deployment or release.
