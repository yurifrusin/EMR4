DECISION: revision_required

# EMR4 Centaur — Red Team Adversarial Security Review

This document contains the fresh independent red-team security review of the frozen candidate source `604b3452787d45ad99d9f08e70101bfd87516671` ("security: harden Ariadne and Diary review boundaries").

Based on the analysis below, the candidate contains multiple critical safety bypasses and a local testing regression.

---

## Summary of Findings

| ID | Finding | Severity | Category | Status |
|---|---|---|---|---|
| **SEC-RED-01** | Origin Verification Bypass via empty string hostname in `isLocalHarnessHost()` | Critical | Authorization / Sandbox Escape | Unresolved |
| **SEC-RED-02** | Confirmation POST redirection to unapproved origin via Weak Substring Match | Critical | Data Leakage / Phishing | Unresolved |
| **SEC-RED-03** | Gate Bypass: Relative Paths/Case-Insensitivity in `asymmetric_review_packets_required` | High | SDLC Control Failure | Unresolved |
| **SEC-RED-04** | Gate Bypass: Missing check for overlapping red/blue review artifacts | High | SDLC Control Failure | Unresolved |
| **SEC-RED-05** | Gate Bypass: Unresolved findings type check bypass | High | SDLC Control Failure | Unresolved |
| **SEC-RED-06** | Gate Bypass: Unresolved findings severity casing bypass | Medium | SDLC Control Failure | Unresolved |
| **SEC-RED-07** | Gate Bypass: Overdue Purple Review check relies on self-reported manifest cadence | Medium | SDLC Control Failure | Unresolved |
| **SEC-RED-08** | Legitimate testing/harness capability regression on developer ngrok hosts | Low | Developer Experience | Unresolved |

---

## Detailed Findings and Reproductions

### SEC-RED-01: Origin Verification Bypass via empty string hostname in `isLocalHarnessHost()`
- **Vulnerability Details:** 
  The helper function `isLocalHarnessHost()` is implemented as:
  ```javascript
  function isLocalHarnessHost() {
    return ["", "127.0.0.1", "localhost", "[::1]"].includes(window.location.hostname);
  }
  ```
  In standard web browsers, `window.location.hostname` is `""` (empty string) for `file://` URLs, `data:` URIs, and `blob:` URIs.
- **Attack Vector / Exploitation:**
  An attacker can load the Diary application inside an iframe via a `data:` URI or `blob:` URI, or trick the user into saving the HTML locally and opening it via `file://`. When loaded under this context, `isLocalHarnessHost()` evaluates to `true`. An attacker can then append query parameters like `?smoke=true` or `?bernie_dev_review=true` to force the application into smoke/dev mode, bypassing authentication and exposing mock diagnostic screens.

### SEC-RED-02: Confirmation POST redirection to unapproved origin via Weak Substring Match
- **Vulnerability Details:**
  The `BACKEND_URL` resolves to `window.location.origin` if the current host contains `"ngrok"` anywhere in the substring:
  ```javascript
  const BACKEND_URL = (window.location.port === "3000")
    ? "http://localhost:8001"
    : window.location.hostname.includes("ngrok")
      ? window.location.origin
      : NGROK_URL;
  ```
- **Attack Vector / Exploitation:**
  The check `window.location.hostname.includes("ngrok")` is extremely loose. An attacker can register a malicious domain containing the string `"ngrok"` (e.g., `https://attackerngrok.com`, `https://ngrok-phishing-gate.com`). If the attacker hosts or frames the frontend code under this domain, `BACKEND_URL` resolves to `window.location.origin` (the attacker's origin). 
  All API calls—including confirmation `POST` requests containing sensitive proposal IDs, practitioner details, and tokens—will be sent directly to the attacker's server instead of the canonical `NGROK_URL`.

### SEC-RED-03: Gate Bypass: Relative Paths/Case-Insensitivity in `asymmetric_review_packets_required`
- **Vulnerability Details:**
  In `scripts/ariadne_security_review_gate.py`, the check for asymmetric review packets is a simple raw string equality check:
  ```python
  if blue.get("packet_path") == red.get("packet_path"):
      reasons.append("asymmetric_review_packets_required")
  ```
- **Attack Vector / Exploitation:**
  Because the script does not normalize or resolve paths before checking equality, the check can be bypassed by specifying relative vs absolute-like paths, path traversal sequences, or casing variations that resolve to the same file on disk. For example:
  - Blue: `"orchestration/agent_inbox/codex/security-hardening-blue-packet.md"`
  - Red: `"./orchestration/agent_inbox/codex/security-hardening-blue-packet.md"`
  The gate will successfully pass even though both roles are directed to review the exact same file.

### SEC-RED-04: Gate Bypass: Missing check for overlapping red/blue review artifacts
- **Vulnerability Details:**
  The gate script verifies that `artifact_path` exists for both roles but never compares `blue.get("artifact_path")` against `red.get("artifact_path")`.
- **Attack Vector / Exploitation:**
  During the acceptance phase, both the blue and red roles can declare the exact same file path as their `artifact_path`. A single worker artifact file will satisfy both checks, bypassing the required independent dual-review control.

### SEC-RED-05: Gate Bypass: Unresolved findings type check bypass
- **Vulnerability Details:**
  The gate script's validation of unresolved findings checks only dictionary items:
  ```python
  for finding in unresolved:
      if isinstance(finding, dict) and finding.get("severity") in blocking:
          reasons.append(f"blocking_finding_unresolved:{finding.get('id', 'unnamed')}")
  ```
- **Attack Vector / Exploitation:**
  If the unresolved findings list contains string identifiers instead of dictionary objects (e.g., `"unresolved_findings": ["SEC-1", "SEC-2"]`), the check is silently bypassed. The gate will pass the acceptance phase despite containing active high or critical findings.

### SEC-RED-06: Gate Bypass: Unresolved findings severity casing bypass
- **Vulnerability Details:**
  The check `finding.get("severity") in blocking` expects lowercase values (`"critical"`, `"high"`). It is case-sensitive.
- **Attack Vector / Exploitation:**
  If a finding in the manifest uses camel-case or upper-case severity (e.g., `{"id": "SEC-1", "severity": "High"}` or `{"id": "SEC-1", "severity": "HIGH"}`), the check fails to match and allows the gate to pass.

### SEC-RED-07: Gate Bypass: Overdue Purple Review check relies on self-reported manifest cadence
- **Vulnerability Details:**
  The gate checks if a purple review is overdue based on the `material_sprints_since_purple` value in the manifest.
- **Attack Vector / Exploitation:**
  Since the gate script has no access to git history or audit ledgers to verify the true material sprint history, this value is entirely self-reported. A sprint team can avoid the mandatory purple synthesis indefinitely by manually keeping this value set to `< 4` in the manifest.

### SEC-RED-08: Legitimate testing/harness capability regression on developer ngrok hosts
- **Details:**
  By strictly gating `isLocalHarnessHost()` to `["", "127.0.0.1", "localhost", "[::1]"]`, a developer working on their remote ngrok forwarding URL (e.g. `property-cinch-backfield.ngrok-free.dev`) is classified as a non-local host.
- **Impact:**
  This disables developer review panels and smoke testing tools on legitimate ngrok testing endpoints, creating a regression for developer testing workflows.
