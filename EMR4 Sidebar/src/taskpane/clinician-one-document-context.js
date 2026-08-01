(function attachClinicianOneDocumentContext(root, factory) {
  var runtime = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = runtime;
  }
  if (root) {
    root.EMR4ClinicianOneDocumentContext = runtime;
  }
})(
  typeof globalThis !== "undefined"
    ? globalThis
    : typeof self !== "undefined"
      ? self
      : this,
  function buildClinicianOneDocumentContext() {
    "use strict";

    var REQUEST_VERSION =
      "emr4.clinician-one-document-context-request.v1";
    var RESPONSE_VERSION =
      "emr4.clinician-one-document-context-response.v1";
    var HOST_PROFILE_VERSION = "emr4.office-host-runtime-profile.v1";
    var MAXIMUM_CHARACTERS = 1200;
    var MAXIMUM_LINES = 40;
    var REQUEST_ID_PATTERN = /^clinician-context-[a-z0-9-]{8,80}$/;
    var REQUEST_KEYS = [
      "contract_version",
      "data_classification",
      "grant",
      "limits",
      "operation",
      "request_id",
      "single_use",
      "source_scope",
      "user_gesture",
    ];
    var LIMIT_KEYS = [
      "maximum_characters",
      "maximum_lines",
      "truncate",
    ];
    var GRANT_KEYS = [
      "command",
      "document_read",
      "document_write",
      "microphone_capture",
      "mode",
      "network_access",
      "patient_context",
      "principal_role",
      "provider_invocation",
      "write",
    ];

    function isPlainObject(value) {
      return Boolean(
        value
        && typeof value === "object"
        && !Array.isArray(value)
      );
    }

    function hasExactKeys(value, expected) {
      if (!isPlainObject(value)) return false;
      var actual = Object.keys(value).sort();
      var sortedExpected = expected.slice().sort();
      return (
        actual.length === sortedExpected.length
        && actual.every(function exactKey(key, index) {
          return key === sortedExpected[index];
        })
      );
    }

    function deepFreeze(value) {
      if (!value || typeof value !== "object" || Object.isFrozen(value)) {
        return value;
      }
      Object.keys(value).forEach(function freezeChild(key) {
        deepFreeze(value[key]);
      });
      return Object.freeze(value);
    }

    function validRequestEnvelope(request) {
      return Boolean(
        hasExactKeys(request, REQUEST_KEYS)
        && request.contract_version === REQUEST_VERSION
        && REQUEST_ID_PATTERN.test(request.request_id)
        && request.operation === "read_selected_authored_synthetic_text"
        && request.data_classification === "authored_synthetic"
        && request.source_scope === "current_word_selection"
        && request.user_gesture === "explicit_clinician_click"
        && request.single_use === true
        && hasExactKeys(request.limits, LIMIT_KEYS)
        && request.limits.maximum_characters === MAXIMUM_CHARACTERS
        && request.limits.maximum_lines === MAXIMUM_LINES
        && request.limits.truncate === false
        && isPlainObject(request.grant)
      );
    }

    function validGrant(grant) {
      return Boolean(
        hasExactKeys(grant, GRANT_KEYS)
        && grant.mode === "local_authored_synthetic_fixture"
        && grant.principal_role === "clinician_fixture"
        && grant.document_read === true
        && grant.document_write === false
        && grant.patient_context === false
        && grant.provider_invocation === false
        && grant.network_access === false
        && grant.microphone_capture === false
        && grant.command === false
        && grant.write === false
      );
    }

    function hostDisposition(profile) {
      if (
        !isPlainObject(profile)
        || profile.contract_version !== HOST_PROFILE_VERSION
        || profile.host !== "word"
        || profile.office_initialized !== true
      ) {
        return "host_not_ready";
      }
      if (!["desktop", "web"].includes(profile.host_kind)) {
        return "host_not_supported";
      }
      if (
        !isPlainObject(profile.features)
        || !isPlainObject(profile.features["clinician_one.workspace"])
        || profile.features["clinician_one.workspace"].status !== "host_ready"
        || !isPlainObject(profile.authority)
        || profile.authority.document_read !== false
      ) {
        return "host_not_ready";
      }
      return null;
    }

    function audit(readCount) {
      return {
        document_read_count: readCount,
        document_write_count: 0,
        provider_call_count: 0,
        network_call_count: 0,
        command_count: 0,
        write_count: 0,
        raw_text_persisted: false,
        raw_text_logged: false,
      };
    }

    function safeRequestId(request) {
      return (
        isPlainObject(request)
        && typeof request.request_id === "string"
        && REQUEST_ID_PATTERN.test(request.request_id)
      )
        ? request.request_id
        : "clinician-context-invalid-request";
    }

    function blocked(request, reasonCode, readCount) {
      return deepFreeze({
        contract_version: RESPONSE_VERSION,
        request_id: safeRequestId(request),
        status: "blocked",
        disposition: "edge_aborted",
        reason_code: reasonCode,
        context_frame: null,
        audit: audit(readCount),
      });
    }

    function admitted(request, profile, text, lineCount) {
      return deepFreeze({
        contract_version: RESPONSE_VERSION,
        request_id: request.request_id,
        status: "admitted",
        disposition: "context_frame_ready",
        reason_code: null,
        context_frame: {
          frame_type: "current_consult_note",
          authority_label: "staff_selected",
          source_scope: "active_document_selection",
          source_label: "word_current_selection",
          data_classification: "authored_synthetic",
          text: text,
          character_count: text.length,
          line_count: lineCount,
          truncated: false,
          host_kind: profile.host_kind,
          platform: profile.platform,
          single_use: true,
          authority: {
            diagnostic: false,
            prescribing: false,
            clinical_finalization: false,
            patient_context: false,
            document_write: false,
            provider_invocation: false,
            network_access: false,
            command: false,
            write: false,
          },
        },
        audit: audit(1),
      });
    }

    function createLocalFixtureRequest(requestId) {
      return deepFreeze({
        contract_version: REQUEST_VERSION,
        request_id: requestId,
        operation: "read_selected_authored_synthetic_text",
        data_classification: "authored_synthetic",
        source_scope: "current_word_selection",
        user_gesture: "explicit_clinician_click",
        single_use: true,
        limits: {
          maximum_characters: MAXIMUM_CHARACTERS,
          maximum_lines: MAXIMUM_LINES,
          truncate: false,
        },
        grant: {
          mode: "local_authored_synthetic_fixture",
          principal_role: "clinician_fixture",
          document_read: true,
          document_write: false,
          patient_context: false,
          provider_invocation: false,
          network_access: false,
          microphone_capture: false,
          command: false,
          write: false,
        },
      });
    }

    function createWordSelectionReader(wordRuntime) {
      return async function readCurrentWordSelection() {
        if (!wordRuntime || typeof wordRuntime.run !== "function") {
          throw new Error("word_runtime_unavailable");
        }
        return wordRuntime.run(async function readSelection(context) {
          var selection = context.document.getSelection();
          selection.load("text");
          await context.sync();
          return selection.text;
        });
      };
    }

    function createClinicianDocumentContextAdapter(dependencies) {
      var deps = dependencies || {};
      var readSelectionText = deps.readSelectionText;
      var consumedRequestIds = new Set();

      async function read(request, hostProfile) {
        if (!validRequestEnvelope(request)) {
          return blocked(request, "invalid_request", 0);
        }
        if (!validGrant(request.grant)) {
          return blocked(request, "grant_denied", 0);
        }
        var hostReason = hostDisposition(hostProfile);
        if (hostReason) {
          return blocked(request, hostReason, 0);
        }
        if (consumedRequestIds.has(request.request_id)) {
          return blocked(request, "already_consumed", 0);
        }
        if (typeof readSelectionText !== "function") {
          return blocked(request, "host_not_ready", 0);
        }

        consumedRequestIds.add(request.request_id);
        var selectedText;
        try {
          selectedText = await readSelectionText();
        } catch (_error) {
          return blocked(request, "selection_read_failed", 1);
        }
        if (typeof selectedText !== "string") {
          return blocked(request, "selection_read_failed", 1);
        }

        var normalizedText = selectedText.replace(/\r\n?/g, "\n");
        if (!normalizedText.trim()) {
          return blocked(request, "selection_empty", 1);
        }
        if (normalizedText.length > MAXIMUM_CHARACTERS) {
          return blocked(request, "selection_too_large", 1);
        }
        var lineCount = normalizedText.split("\n").length;
        if (lineCount > MAXIMUM_LINES) {
          return blocked(request, "selection_too_many_lines", 1);
        }
        return admitted(request, hostProfile, normalizedText, lineCount);
      }

      return deepFreeze({
        read: read,
      });
    }

    return deepFreeze({
      REQUEST_VERSION: REQUEST_VERSION,
      RESPONSE_VERSION: RESPONSE_VERSION,
      MAXIMUM_CHARACTERS: MAXIMUM_CHARACTERS,
      MAXIMUM_LINES: MAXIMUM_LINES,
      createLocalFixtureRequest: createLocalFixtureRequest,
      createWordSelectionReader: createWordSelectionReader,
      createClinicianDocumentContextAdapter:
        createClinicianDocumentContextAdapter,
    });
  }
);
