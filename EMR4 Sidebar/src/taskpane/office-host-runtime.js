(function attachOfficeHostRuntime(root, factory) {
  var runtime = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = runtime;
  }
  if (root) {
    root.EMR4OfficeHostRuntime = runtime;
  }
})(
  typeof globalThis !== "undefined"
    ? globalThis
    : typeof self !== "undefined"
      ? self
      : this,
  function buildOfficeHostRuntime() {
    "use strict";

    var CONTRACT_VERSION = "emr4.office-host-runtime-profile.v1";
    var FEATURE_DECISION_BASIS = "host_capability_only";
    var AUTHORIZATION_STATE = "product_authorization_not_evaluated";

    function normalizedToken(value) {
      return String(value || "")
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "");
    }

    function normalizeHost(value) {
      return normalizedToken(value) === "word" ? "word" : "unknown";
    }

    function normalizePlatform(value) {
      var token = normalizedToken(value);
      if (
        token === "pc" ||
        token === "windows" ||
        token === "win32" ||
        token === "desktopwindows"
      ) {
        return "desktop_windows";
      }
      if (token === "mac" || token === "macos" || token === "desktopmac") {
        return "desktop_mac";
      }
      if (
        token === "officeonline" ||
        token === "wordonline" ||
        token === "online" ||
        token === "web" ||
        token === "browser"
      ) {
        return "word_online";
      }
      if (
        token === "ios" ||
        token === "android" ||
        token === "universal" ||
        token === "mobile"
      ) {
        return "mobile";
      }
      return "unknown";
    }

    function hostKind(platform) {
      if (platform === "desktop_windows" || platform === "desktop_mac") {
        return "desktop";
      }
      if (platform === "word_online") return "web";
      if (platform === "mobile") return "mobile";
      return "unknown";
    }

    function isFunction(value) {
      return typeof value === "function";
    }

    function inspectCapabilities(environment, host) {
      var env = environment || {};
      var office = env.office || {};
      var context = office.context || {};
      var ui = context.ui || {};
      var documentContext = context.document || {};
      var devicePermission = context.devicePermission || {};
      var navigatorObject = env.navigator || {};
      var mediaDevices = navigatorObject.mediaDevices || {};
      var cryptoObject = env.crypto || {};

      return {
        word_runtime: Boolean(
          host === "word" && env.word && isFunction(env.word.run)
        ),
        dialog_api: isFunction(ui.displayDialogAsync),
        office_actions: Boolean(
          office.actions && isFunction(office.actions.associate)
        ),
        custom_xml_parts: Boolean(documentContext.customXmlParts),
        media_devices: isFunction(mediaDevices.getUserMedia),
        media_recorder: isFunction(env.mediaRecorder),
        office_device_permission: Boolean(
          isFunction(devicePermission.requestPermissionsAsync) &&
            office.DevicePermission &&
            office.DevicePermission.microphone !== undefined
        ),
        crypto_random_uuid: isFunction(cryptoObject.randomUUID),
      };
    }

    function featureDecision(requirements, evaluationCapabilities) {
      var missing = requirements.filter(function missingRequirement(name) {
        return !evaluationCapabilities[name];
      });
      return {
        status: missing.length === 0 ? "host_ready" : "host_blocked",
        missing_capabilities: missing,
        decision_basis: FEATURE_DECISION_BASIS,
        authorization: AUTHORIZATION_STATE,
      };
    }

    function microphonePermissionStrategy(platform, capabilities) {
      if (!capabilities.media_devices || !capabilities.media_recorder) {
        return "unavailable";
      }
      if (platform === "word_online") {
        return capabilities.office_device_permission
          ? "office_device_permission_then_browser_media"
          : "unavailable";
      }
      return "browser_media_prompt";
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

    function createOfficeHostProfile(info, environment) {
      var readyInfo = info || {};
      var host = normalizeHost(readyInfo.host);
      var platform = normalizePlatform(readyInfo.platform);
      var kind = hostKind(platform);
      var capabilities = inspectCapabilities(environment, host);
      var evaluationCapabilities = Object.assign(
        {
          word_host: host === "word",
        },
        capabilities
      );
      var scribeRequirements = [
        "word_host",
        "word_runtime",
        "media_devices",
        "media_recorder",
      ];
      if (kind === "web") {
        scribeRequirements.push("office_device_permission");
      }

      return deepFreeze({
        contract_version: CONTRACT_VERSION,
        host: host,
        platform: platform,
        host_kind: kind,
        office_initialized: Boolean(readyInfo.host),
        capabilities: capabilities,
        microphone_permission_strategy: microphonePermissionStrategy(
          platform,
          capabilities
        ),
        features: {
          "clinician_one.workspace": featureDecision(
            ["word_host", "word_runtime"],
            evaluationCapabilities
          ),
          "clinician_one.scribe_capture": featureDecision(
            scribeRequirements,
            evaluationCapabilities
          ),
          "reception_one.dialog": featureDecision(
            ["word_host", "dialog_api"],
            evaluationCapabilities
          ),
          "reception_one.companion": featureDecision(
            ["word_host", "dialog_api", "crypto_random_uuid"],
            evaluationCapabilities
          ),
        },
        authority: {
          document_read: false,
          document_write: false,
          microphone_capture: false,
          network_access: false,
          provider_invocation: false,
          patient_context: false,
          clinical_context: false,
          command: false,
          write: false,
        },
      });
    }

    function createCurrentOfficeHostProfile(info) {
      var currentRoot =
        typeof globalThis !== "undefined"
          ? globalThis
          : typeof self !== "undefined"
            ? self
            : {};
      return createOfficeHostProfile(info, {
        office: currentRoot.Office,
        word: currentRoot.Word,
        navigator: currentRoot.navigator,
        mediaRecorder: currentRoot.MediaRecorder,
        crypto: currentRoot.crypto,
      });
    }

    return deepFreeze({
      CONTRACT_VERSION: CONTRACT_VERSION,
      createOfficeHostProfile: createOfficeHostProfile,
      createCurrentOfficeHostProfile: createCurrentOfficeHostProfile,
      normalizeHost: normalizeHost,
      normalizePlatform: normalizePlatform,
    });
  }
);
