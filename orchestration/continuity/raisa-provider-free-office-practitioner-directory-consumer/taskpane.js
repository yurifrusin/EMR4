(() => {
  "use strict";

  const root = document.getElementById("directory-root");
  const button = document.getElementById("load-directory");
  const status = document.getElementById("status");
  const hostLabel = document.getElementById("host-label");
  const sessionLabel = document.getElementById("session-label");
  const list = document.getElementById("practitioner-list");
  const surface = root.dataset.surface || "";
  const expectedHost = root.dataset.expectedHost || "";
  const directoryEndpoint = root.dataset.directoryEndpoint || "";
  let csrfToken = root.dataset.csrf || "";
  let evidenceNonce = root.dataset.evidenceNonce || "";
  root.removeAttribute("data-csrf");
  root.removeAttribute("data-evidence-nonce");
  root.removeAttribute("data-directory-endpoint");

  const DIRECTORY_QUERY = `
    query Directory($activeOnly: Boolean!, $limit: Int!, $offset: Int!) {
      practice {
        practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
          id
          displayName
          roleLabel
          active
          defaultLocation { id name }
        }
      }
    }
  `;
  const ROW_KEYS = ["active", "defaultLocation", "displayName", "id", "roleLabel"];
  const LOCATION_KEYS = ["id", "name"];
  let hostClass = "";
  let officeReady = false;
  let terminal = false;

  class FlowFailure extends Error {
    constructor(code) {
      super("directory flow failed");
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

  async function post(path, body, csrf) {
    const headers = { "Content-Type": "application/json" };
    if (csrf) headers["X-EMR4-CSRF"] = csrf;
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

  function exactKeys(value, expected) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value) &&
      JSON.stringify(Object.keys(value).sort()) === JSON.stringify(expected);
  }

  function requireDirectory(body) {
    if (!exactKeys(body, ["data"])) throw new FlowFailure("projection_invalid");
    const practice = body.data && body.data.practice;
    if (!exactKeys(practice, ["practitioners"])) {
      throw new FlowFailure("projection_invalid");
    }
    const rows = practice.practitioners;
    if (!Array.isArray(rows) || rows.length !== 2) {
      throw new FlowFailure("directory_count_invalid");
    }
    for (const row of rows) {
      if (!exactKeys(row, ROW_KEYS) || row.active !== true) {
        throw new FlowFailure("projection_invalid");
      }
      if (typeof row.id !== "string" || typeof row.displayName !== "string") {
        throw new FlowFailure("projection_invalid");
      }
      if (row.roleLabel !== null && typeof row.roleLabel !== "string") {
        throw new FlowFailure("projection_invalid");
      }
      if (row.defaultLocation !== null &&
          (!exactKeys(row.defaultLocation, LOCATION_KEYS) ||
           typeof row.defaultLocation.id !== "string" ||
           typeof row.defaultLocation.name !== "string")) {
        throw new FlowFailure("projection_invalid");
      }
    }
    return rows;
  }

  function renderDirectory(rows) {
    list.replaceChildren();
    for (const row of rows) {
      const item = document.createElement("li");
      const name = document.createElement("strong");
      const detail = document.createElement("span");
      name.textContent = row.displayName;
      const labels = [row.roleLabel, row.defaultLocation && row.defaultLocation.name]
        .filter((value) => typeof value === "string" && value.length > 0);
      detail.textContent = labels.join(" · ") || "Active practitioner";
      item.append(name, detail);
      list.append(item);
    }
    list.hidden = false;
  }

  function resultPayload(terminalStatus, failureCode, directoryCount) {
    return {
      evidence_nonce: evidenceNonce,
      surface,
      host_class: hostClass || expectedHost,
      terminal_status: terminalStatus,
      directory_read_passed: directoryCount === 2,
      exact_projection_passed: directoryCount === 2,
      active_practitioner_count: directoryCount,
      logout_passed: terminalStatus === "passed",
      result_submitted: true,
      failure_code: failureCode,
    };
  }

  async function submitResult(terminalStatus, failureCode, directoryCount) {
    if (!evidenceNonce) return false;
    const payload = resultPayload(terminalStatus, failureCode, directoryCount);
    const response = await post(
      "/office-practitioner-directory/result",
      payload,
      ""
    );
    payload.evidence_nonce = "";
    evidenceNonce = "";
    return response.status === 201;
  }

  async function fail(code, message) {
    if (terminal) return;
    terminal = true;
    button.disabled = true;
    sessionLabel.textContent = "Failed closed";
    status.textContent = message;
    csrfToken = "";
    list.replaceChildren();
    list.hidden = true;
    try {
      await submitResult("failed", code, 0);
    } catch (_error) {
      status.textContent = `${message} Sanitized result submission also failed.`;
    }
  }

  async function run() {
    if (terminal || !officeReady) return;
    if (!csrfToken || !directoryEndpoint) {
      await fail("launch_unavailable", "The one-use directory launch is unavailable. Restart the task-owned harness.");
      return;
    }
    button.disabled = true;
    sessionLabel.textContent = "Authorized read in progress";
    status.textContent = "Loading the active practitioner directory…";
    let rows = [];
    try {
      let response = await post(
        directoryEndpoint,
        {
          query: DIRECTORY_QUERY,
          variables: { activeOnly: true, limit: 200, offset: 0 },
          operationName: "Directory",
        },
        csrfToken
      );
      if (!response.ok) throw new FlowFailure("directory_unavailable");
      let body;
      try {
        body = await response.json();
      } catch (_error) {
        throw new FlowFailure("unexpected_response");
      }
      rows = requireDirectory(body);
      renderDirectory(rows);

      response = await post(
        "/api/v1/application-auth/session/logout",
        { surface },
        csrfToken
      );
      csrfToken = "";
      if (response.status !== 204) throw new FlowFailure("logout_failed");

      const submitted = await submitResult("passed", "none", rows.length);
      if (!submitted) throw new FlowFailure("unexpected_response");
      terminal = true;
      sessionLabel.textContent = "Directory shown · session ended";
      status.textContent = "Two active authored-synthetic practitioners were shown. No session remains in this taskpane.";
    } catch (error) {
      const code = error instanceof FlowFailure ? error.code : "network_unavailable";
      await fail(code, "The directory check failed closed. No fallback or partial result was used.");
    }
  }

  button.addEventListener("click", run, { once: true });

  const readyTimeout = window.setTimeout(() => {
    if (!officeReady) {
      fail("office_unavailable", "Office did not admit this taskpane in time.");
    }
  }, 15000);

  Office.onReady((info) => {
    if (terminal) return;
    window.clearTimeout(readyTimeout);
    hostClass = normalizedHost(info);
    hostLabel.textContent = hostClass || "Unsupported Office host";
    if (!hostClass || hostClass !== expectedHost) {
      fail("office_host_mismatch", "This manifest is open in the wrong Office host. No directory request was sent.");
      return;
    }
    officeReady = true;
    button.disabled = false;
    status.textContent = "Office host confirmed. Select Show active practitioners.";
  });
})();
