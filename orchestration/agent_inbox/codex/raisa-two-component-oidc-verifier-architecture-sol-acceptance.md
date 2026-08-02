# Sol acceptance: two-component OIDC verifier architecture revision

Date: 2026-08-02
Disposition: accepted

We accept `two_component_oidc_verifier_architecture_revision_pass` within the user's architecture/dependency-review authority.

The contradiction is resolved at its ownership boundary: MSAL handles the Microsoft code flow but supplies no identity-admission claims; Authlib/JOSE RFC verifies the transient raw ID token and EMR4 enforces exact tenant and stable-identifier postconditions. Exact pins, package evidence, `form_post`, failure behavior and rollover are durable. Seventeen provider-free cases, dependency integrity/audit and focused tests pass.

The focused architecture, inherited parent, continuity and API-spine suite passes 64 tests. The unfiltered suite retains a parent-revision collection barrier where an older integration test imports removed `_BERNIE_SESSION_STORE`; it is unrelated to this tranche and is not relabelled green.

This acceptance does not authorise or claim an application adapter, provider call, real identity, route, database change, binding, session, product read, deployment, production or release. The user-owned branding directory remains excluded. A provider-free runtime adapter is the next candidate and requires fresh authority.
