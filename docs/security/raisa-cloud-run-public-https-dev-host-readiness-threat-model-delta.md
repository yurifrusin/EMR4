# Threat-model delta: Raisa Cloud Run public-HTTPS dev-host readiness

Date: 2026-07-31

Status: `repository_local_readiness_only`

Parent: `clinician_one_word_desktop_selection_check_pass`

## New candidate trust edge

A future public Cloud Run endpoint would supply static taskpane and native
Diary assets to Word Online. This tranche constructs and tests that edge
locally but creates no endpoint.

## Threats and controls

### Repository or credential material enters the image

- Generate a fresh temporary context from a closed file allowlist.
- Reject symlinks and unexpected paths.
- Exclude source maps, `.git`, environment files, evidence, local data,
  credentials and the repository root.
- Verify the package manifest twice before build.

### Public static hosting becomes a backend

- Use a dependency-free GET/HEAD-only server.
- Expose only exact static paths and inert health/policy responses.
- Reject `/api`, non-GET methods, traversal and unknown routes.
- Provide no secret, service credential, database, provider or VPC
  configuration.
- Use a dedicated future runtime identity with no project roles.

### Legacy taskpane controls contact an old backend

- Admit hosted mode only through an exact synthetic-only runtime policy.
- In hosted mode show only the Clinician One bounded selection card and bypass
  sign-in.
- Apply a browser policy that prohibits non-Microsoft external connections.
- Test observed browser requests and require zero backend/provider traffic.

### An arbitrary host enables the development surface

- Bind the generated policy to one exact expected origin.
- Require the `public_https_development` contract and exact zero-authority
  fields.
- Keep the checked-in default policy disabled.
- Fail closed on malformed or mismatched policy.

### Public page leaks user content through logs or caches

- Never log request query, headers, body, document content or selection text.
- Use `Cache-Control: no-store` for the development host.
- Retain only route/status aggregates in local evidence.
- Keep raw selected text inside the existing single-use in-memory adapter.

### Browser embedding or content injection broadens access

- Serve fixed MIME types with `nosniff`.
- Deny framing except the exact Microsoft Office/OneDrive ancestor classes
  required for this development surface.
- Deny objects, forms, base-URI changes, camera, microphone, location, payment
  and USB.
- Serve no user-authored HTML and perform no dynamic HTML interpolation.

### Cloud runtime identity is overprivileged

- Prohibit the Bernie prediction-only AI service account.
- Require a separate runtime service account with no project roles before
  deployment.
- Treat service-account creation and every IAM binding as separately
  authorised external work.

### Cost or resource amplification

- Freeze request-based billing, minimum instances zero and maximum instances
  one.
- Bound container CPU, memory, process count and request methods.
- Treat budgets as alerts, not hard enforcement.
- Require separate authorization before resource creation or deployment.

### Regional claim is overstated

- Record only the configured Cloud Run region and observed endpoint if a later
  deployment occurs.
- Do not infer Microsoft processing location, Australian physical processing
  or sovereign processing from a Sydney Cloud Run resource.

## Preserved boundaries

GraphQL remains read-only and unchanged. No REST command, async event, provider
invocation, database operation or clinical action is added. Product-derived,
patient, health, clinical and historical data; backend/provider connectivity;
microphone, document-write, production, deployment and release authority
remain closed.

## Residual risk

Local container evidence cannot prove Cloud Run entitlement, public-IAM
compatibility, Office tenant policy, Word Online iframe behavior, real network
headers, vendor processing geography or real-data safety.
