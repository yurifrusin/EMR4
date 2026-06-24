# plan-antigravity-antigravity-node-security-baseline

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-node-security-baseline` |
| Status | integrated |
| Created | 2026-06-24 10:26 +1000 |
| Source HEAD | `e99e1ec` |

## Plan Summary

Amended plan for Node/Office add-in security baseline in CI, implementing a blocking production audit, a non-blocking devDependencies supply-chain audit, and manifest validation.

## My Understanding

Create a GitHub Actions CI workflow that runs blocking manifest validation and production npm audits, alongside a non-blocking full npm audit for developer machine/CI runner supply-chain risk visibility.

## Intended Surface / Boundary

CI/Workflow files (`.github/workflows/`) and inbox task packets (`orchestration/`).

## Out Of Scope

Do not edit diary UI, taskpane runtime JS/CSS/HTML, backend code, migrations, Python tests, patient files, or Pages assets. Do not own Python pip-audit.

## Files I Expect To Edit

- `NEW`: `.github/workflows/node-security.yml`
- `MODIFY`: `orchestration/agent_inbox/antigravity/antigravity-node-security-baseline.md`

## Implementation Steps

1. **Create CI Workflow**: Create `.github/workflows/node-security.yml` with checkout, setup-node, npm ci, blocking manifest validation (`npm run validate`), blocking production audit (`npm audit --omit=dev`), and non-blocking full audit (`npm audit || true`).
2. **Metadata Update**: Update completion notes in the task packet `orchestration/agent_inbox/antigravity/antigravity-node-security-baseline.md`.
3. **Submit Plan**: Wait for review and approval.

## Visual / Behavioural Acceptance Checks

- CI run passes successfully on push/PR.
- Local `npm run validate` and `npm audit --omit=dev` pass without error.
- Full `npm audit` runs and outputs a vulnerability report in logs without failing the build.

## Risks / Ambiguities

- **Supply-Chain Risk**: A full `npm audit` reports 16 vulnerabilities (13 moderate, 3 high) in devDependencies/build tools (like Webpack, Babel, hono, etc.). Although these files are not bundled and served to clinicians/patients (which only receive static assets), they execute on developer machines and CI runners. If compromised, they could leak secrets or execute arbitrary code. 
- **Mitigation/Dual Audit**: We mitigate this by running a full `npm audit` as a non-blocking check to ensure visibility of build-tool supply-chain risks, while keeping the production audit (`npm audit --omit=dev`) strictly blocking to guarantee clean bundled assets.

## Strategy and "Not Worth It Yet" Notes

### 1. Build Tool Dependency Audits
- **Not Worth It Yet**: It is not worth doing a forced upgrade (e.g. `npm audit fix --force`) on Webpack or Babel build tools right now. DevDependencies represent local-only build tooling, and upgrading them can introduce breaking changes in our dev server or debugging configurations, disrupting other active workstreams. Therefore, devDependency audits will run non-blocking.

### 2. Linting Integration
- **Not Worth It Yet**: It is not worth blocking CI builds on ESLint checks. Running `npm run lint` yields 639 problems in taskpane scripts due to ESLint not recognizing browser globals (`document`, `window`) or Office SDK objects (`Office`, `Word`). Lint checks should remain local warnings only until the codebase is cleaned up and `.eslintrc.json` is properly configured.

### 3. Gemini / Antigravity Plugins Research
- We reviewed the available plugins/tools in the Antigravity workspace:
  - **`chrome-devtools-plugin`**: Recommended for developer feedback loops. It allows developers and testers to inspect the taskpane's sandbox, frame-ancestor rules, and CSP headers directly at runtime in the browser.
  - **`google-antigravity-sdk`**: Can be used to automate local manifest schema checks and verify syntax validation.
  - **Not Worth It Yet**: There are no dedicated Node vulnerability scanner plugins or third-party SAST tools currently equipped in the agent's plugin suite; relying on native `npm audit` and `office-addin-manifest` CLI tools is the most robust and standard approach.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
