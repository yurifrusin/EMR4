(() => {
  "use strict";

  const root = document.getElementById("compatibility-root");
  const button = document.getElementById("run-check");
  const status = document.getElementById("status");
  const hostLabel = document.getElementById("host-label");
  const stateLabel = document.getElementById("state-label");
  const surface = root.dataset.surface || "";
  const expectedHost = root.dataset.expectedHost || "";
  let bootstrap = root.dataset.bootstrap || "";
  let evidenceNonce = root.dataset.evidenceNonce || "";
  root.removeAttribute("data-bootstrap");
  root.removeAttribute("data-evidence-nonce");

  const steps = {
    csrf_issued: false,
    session_created: false,
    first_validation_passed: false,
    rotation_passed: false,
    second_validation_passed: false,
    logout_passed: false,
    post_logout_denied: false,
  };
  let hostClass = "";
  let officeReady = false;
  let terminal = false;

  class FlowFailure extends Error {
    constructor(code) {
      super("compatibility flow failed");
      this.code = code;
    }
  }

  function normalizedHost(info) {
    const host = String((info && info.host) || "").toLowerCase();
    const platform = String((info && info.platform) || "").toLowerCase();
    if (host !== "word") return "";
    if (platform === "officeonline") return "word_online";
    if (platform === "pc" || platform === "mac") return "installed_word";
    return "";
  }

  async function post(path, body, csrfToken) {
    const headers = { "Content-Type": "application/json" };
    if (csrfToken) headers["X-EMR4-CSRF"] = csrfToken;
    return fetch(path, {
      method: "POST",
      credentials: "include",
      headers,
      body: JSON.stringify(body),
      cache: "no-store",
      redirect: "error",
      referrerPolicy: "no-referrer",
    });
  }

  async function responseJson(response, failureCode) {
    if (!response.ok) throw new FlowFailure(failureCode);
    try {
      return await response.json();
    } catch (_error) {
      throw new FlowFailure("unexpected_response");
    }
  }

  function resultPayload(terminalStatus, failureCode) {
    return {
      evidence_nonce: evidenceNonce,
      surface,
      host_class: hostClass || expectedHost,
      terminal_status: terminalStatus,
      ...steps,
      result_submitted: true,
      failure_code: failureCode,
    };
  }

  async function submitResult(terminalStatus, failureCode) {
    if (!evidenceNonce) return false;
    const payload = resultPayload(terminalStatus, failureCode);
    const response = await post("/office-cookie-compatibility/result", payload, "");
    payload.evidence_nonce = "";
    evidenceNonce = "";
    return response.status === 201;
  }

  async function fail(code, message) {
    if (terminal) return;
    terminal = true;
    button.disabled = true;
    stateLabel.textContent = "Failed closed";
    status.textContent = message;
    bootstrap = "";
    try {
      await submitResult("failed", code);
    } catch (_error) {
      status.textContent = `${message} Sanitized result submission also failed.`;
    }
  }

  async function run() {
    if (terminal || !officeReady) return;
    if (!bootstrap) {
      await fail("bootstrap_unavailable", "The one-use test launch is unavailable. Restart the task-owned harness.");
      return;
    }
    button.disabled = true;
    status.textContent = "Running the cookie lifecycle…";
    stateLabel.textContent = "In progress";
    let csrfToken = "";
    try {
      let response = await post("/api/v1/application-auth/csrf", { surface }, "");
      let body = await responseJson(response, "csrf_failed");
      csrfToken = body.csrf_token || "";
      if (!csrfToken) throw new FlowFailure("unexpected_response");
      steps.csrf_issued = true;

      const loginBody = { surface, bootstrap_credential: bootstrap };
      const loginPromise = post("/api/v1/application-auth/synthetic/session", loginBody, csrfToken);
      loginBody.bootstrap_credential = "";
      bootstrap = "";
      response = await loginPromise;
      body = await responseJson(response, "login_failed");
      csrfToken = body.csrf_token || "";
      if (!csrfToken) throw new FlowFailure("unexpected_response");
      steps.session_created = true;

      response = await post("/api/v1/application-auth/session/validate", { surface }, csrfToken);
      body = await responseJson(response, "first_validation_failed");
      if (body.status !== "authenticated" || body.surface !== surface) {
        throw new FlowFailure("unexpected_response");
      }
      steps.first_validation_passed = true;

      response = await post("/api/v1/application-auth/session/rotate", { surface }, csrfToken);
      body = await responseJson(response, "rotation_failed");
      csrfToken = body.csrf_token || "";
      if (!csrfToken) throw new FlowFailure("unexpected_response");
      steps.rotation_passed = true;

      response = await post("/api/v1/application-auth/session/validate", { surface }, csrfToken);
      body = await responseJson(response, "second_validation_failed");
      if (body.status !== "authenticated" || body.surface !== surface) {
        throw new FlowFailure("unexpected_response");
      }
      steps.second_validation_passed = true;

      response = await post("/api/v1/application-auth/session/logout", { surface }, csrfToken);
      if (response.status !== 204) throw new FlowFailure("logout_failed");
      steps.logout_passed = true;

      response = await post("/api/v1/application-auth/csrf", { surface }, "");
      body = await responseJson(response, "csrf_failed");
      csrfToken = body.csrf_token || "";
      if (!csrfToken) throw new FlowFailure("unexpected_response");
      response = await post("/api/v1/application-auth/session/validate", { surface }, csrfToken);
      if (response.status !== 401) {
        throw new FlowFailure("post_logout_validation_succeeded");
      }
      steps.post_logout_denied = true;

      const submitted = await submitResult("passed", "none");
      if (!submitted) throw new FlowFailure("unexpected_response");
      terminal = true;
      stateLabel.textContent = "Passed and logged out";
      status.textContent = "Compatibility check passed. No session remains in this taskpane.";
    } catch (error) {
      const code = error instanceof FlowFailure ? error.code : "network_unavailable";
      await fail(code, "The compatibility check failed closed. No fallback was used.");
    }
  }

  button.addEventListener("click", run, { once: true });

  const readyTimeout = window.setTimeout(() => {
    if (!officeReady) fail("office_unavailable", "Office did not admit this taskpane in time.");
  }, 15000);

  Office.onReady((info) => {
    if (terminal) return;
    window.clearTimeout(readyTimeout);
    hostClass = normalizedHost(info);
    hostLabel.textContent = hostClass || "Unsupported Office host";
    if (!hostClass || hostClass !== expectedHost) {
      fail("office_host_mismatch", "This manifest is open in the wrong Office host and will not submit a bootstrap value.");
      return;
    }
    officeReady = true;
    button.disabled = false;
    status.textContent = "Office host confirmed. Select Run compatibility check.";
  });
})();
