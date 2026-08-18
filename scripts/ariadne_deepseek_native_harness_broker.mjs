import http from "node:http";
import https from "node:https";
import { createHash, timingSafeEqual } from "node:crypto";

const TEST_MODE = process.env.EMR4_BROKER_TEST_MODE === "1";
const LISTEN_HOST = TEST_MODE
  ? (process.env.EMR4_BROKER_LISTEN_HOST ?? "127.0.0.1")
  : "0.0.0.0";
const LISTEN_PORT = TEST_MODE
  ? Number.parseInt(process.env.EMR4_BROKER_LISTEN_PORT ?? "0", 10)
  : 8080;
const UPSTREAM = TEST_MODE
  ? new URL(process.env.EMR4_BROKER_TEST_UPSTREAM_URL ?? "")
  : new URL("https://api.deepseek.com/chat/completions");
const ALLOWED_PATH = "/chat/completions";
const MODEL_ID = "deepseek-v4-flash";
const ALLOWED_TOOL_NAMES = new Set(["read", "glob", "edit"]);
const MAX_REQUEST_BYTES = 1_048_576;
const MAX_RESPONSE_BYTES = 2_097_152;
const MAX_OUTPUT_TOKENS = 4_096;
const UPSTREAM_TIMEOUT_MS = 300_000;

const brokerToken = process.env.DSH_EMR4_BROKER_TOKEN ?? "";
const providerKey = process.env.DEEPSEEK_API_KEY ?? "";
let providerCallCount = 0;
let activeProviderCall = false;
let boundSessionHash = null;

function sha256(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function logEvent(event) {
  process.stdout.write(`${JSON.stringify(event)}\n`);
}

function equalSecret(left, right) {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  return (
    leftBuffer.length === rightBuffer.length &&
    leftBuffer.length > 0 &&
    timingSafeEqual(leftBuffer, rightBuffer)
  );
}

function suppliedToken(request) {
  const authorization = request.headers.authorization;
  if (
    typeof authorization === "string" &&
    authorization.toLowerCase().startsWith("bearer ")
  ) {
    return authorization.slice(7);
  }
  return "";
}

function respondJson(response, status, reasonCode) {
  if (response.headersSent || response.destroyed) {
    response.destroy();
    return;
  }
  const body = Buffer.from(
    JSON.stringify({ error: { type: "broker_rejection", reason_code: reasonCode } }),
  );
  response.writeHead(status, {
    "content-type": "application/json",
    "content-length": String(body.length),
    "cache-control": "no-store",
    connection: "close",
  });
  response.end(body);
}

function readBoundedBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let length = 0;
    let settled = false;

    function fail(reason) {
      if (settled) return;
      settled = true;
      reject(new Error(reason));
    }

    request.on("data", (chunk) => {
      if (settled) return;
      length += chunk.length;
      if (length > MAX_REQUEST_BYTES) {
        fail("request-byte-bound-exceeded");
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => {
      if (settled) return;
      settled = true;
      resolve(Buffer.concat(chunks));
    });
    request.on("aborted", () => fail("request-aborted"));
    request.on("error", () => fail("request-read-failed"));
  });
}

function validatePayload(payload, request) {
  if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
    return "request-json-object-required";
  }
  if (payload.model !== MODEL_ID) return "model-not-allowlisted";
  if (payload.stream !== true) return "streaming-required";
  if (
    !Number.isInteger(payload.max_tokens) ||
    payload.max_tokens < 1 ||
    payload.max_tokens > MAX_OUTPUT_TOKENS
  ) {
    return "output-token-bound-invalid";
  }
  if (!Array.isArray(payload.messages) || payload.messages.length === 0) {
    return "messages-required";
  }
  if (payload.n !== undefined && payload.n !== 1) {
    return "single-candidate-required";
  }
  if (request.headers["x-deepseek-harness-compact"] !== undefined) {
    return "compaction-route-forbidden";
  }
  if (payload.tools !== undefined) {
    if (!Array.isArray(payload.tools) || payload.tools.length > 8) {
      return "tool-contract-invalid";
    }
    for (const tool of payload.tools) {
      const name = tool?.type === "function" ? tool?.function?.name : undefined;
      if (typeof name !== "string" || !ALLOWED_TOOL_NAMES.has(name)) {
        return "tool-not-allowlisted";
      }
    }
  }
  return null;
}

function sessionBinding(request) {
  const sessionId = request.headers["x-deepseek-harness-session-id"];
  if (typeof sessionId !== "string" || sessionId.length < 8 || sessionId.length > 160) {
    return { error: "session-binding-missing-or-invalid" };
  }
  const sessionHash = sha256(sessionId);
  if (boundSessionHash === null) {
    boundSessionHash = sessionHash;
  } else if (boundSessionHash !== sessionHash) {
    return { error: "session-binding-mismatch" };
  }
  return { sessionHash };
}

function forwardHeaders(body) {
  return {
    authorization: `Bearer ${providerKey}`,
    accept: "text/event-stream",
    "content-type": "application/json",
    "content-length": String(body.length),
    "accept-encoding": "identity",
    "user-agent": "emr4-ariadne-native-harness-broker/1",
  };
}

function forwardToProvider(body, response, metadata) {
  const transport = UPSTREAM.protocol === "https:" ? https : http;
  const startedAt = Date.now();
  const upstreamRequest = transport.request(
    {
      protocol: UPSTREAM.protocol,
      hostname: UPSTREAM.hostname,
      port: UPSTREAM.port || (UPSTREAM.protocol === "https:" ? 443 : 80),
      method: "POST",
      path: `${UPSTREAM.pathname}${UPSTREAM.search}`,
      headers: forwardHeaders(body),
      timeout: UPSTREAM_TIMEOUT_MS,
      agent: false,
    },
    (upstreamResponse) => {
      const contentType =
        typeof upstreamResponse.headers["content-type"] === "string"
          ? upstreamResponse.headers["content-type"]
          : "application/octet-stream";
      response.writeHead(upstreamResponse.statusCode ?? 502, {
        "content-type": contentType,
        "cache-control": "no-store",
        connection: "close",
      });
      logEvent({
        event: "provider-response-started",
        provider_call_ordinal: metadata.ordinal,
        provider_status: upstreamResponse.statusCode ?? 502,
        content_type: contentType.split(";", 1)[0],
        session_id_sha256: metadata.sessionHash,
      });

      const responseHash = createHash("sha256");
      let responseBytes = 0;
      let completed = false;

      upstreamResponse.on("data", (chunk) => {
        if (completed) return;
        responseBytes += chunk.length;
        if (responseBytes > MAX_RESPONSE_BYTES) {
          completed = true;
          upstreamResponse.destroy(new Error("response-byte-bound-exceeded"));
          response.destroy();
          logEvent({
            event: "provider-call-failed",
            provider_call_ordinal: metadata.ordinal,
            reason_code: "response-byte-bound-exceeded",
            response_bytes: responseBytes,
            session_id_sha256: metadata.sessionHash,
          });
          return;
        }
        responseHash.update(chunk);
        response.write(chunk);
      });
      upstreamResponse.on("end", () => {
        if (completed) return;
        completed = true;
        response.end();
        logEvent({
          event: "provider-call-completed",
          provider_call_ordinal: metadata.ordinal,
          provider_status: upstreamResponse.statusCode ?? 502,
          response_bytes: responseBytes,
          response_sha256: `sha256:${responseHash.digest("hex")}`,
          elapsed_ms: Date.now() - startedAt,
          session_id_sha256: metadata.sessionHash,
        });
      });
      upstreamResponse.on("error", () => {
        if (completed) return;
        completed = true;
        response.destroy();
        logEvent({
          event: "provider-call-failed",
          provider_call_ordinal: metadata.ordinal,
          reason_code: "provider-response-failed",
          response_bytes: responseBytes,
          session_id_sha256: metadata.sessionHash,
        });
      });
    },
  );

  upstreamRequest.on("timeout", () => {
    upstreamRequest.destroy(new Error("provider-timeout"));
  });
  upstreamRequest.on("error", (error) => {
    if (!response.headersSent) {
      respondJson(response, 502, "provider-transport-failed");
    } else {
      response.destroy();
    }
    logEvent({
      event: "provider-call-failed",
      provider_call_ordinal: metadata.ordinal,
      reason_code:
        error instanceof Error && error.message === "provider-timeout"
          ? "provider-timeout"
          : "provider-transport-failed",
      elapsed_ms: Date.now() - startedAt,
      session_id_sha256: metadata.sessionHash,
    });
  });
  upstreamRequest.on("close", () => {
    activeProviderCall = false;
  });
  upstreamRequest.end(body);
}

if (
  !brokerToken ||
  !providerKey ||
  equalSecret(brokerToken, providerKey) ||
  !Number.isInteger(LISTEN_PORT) ||
  LISTEN_PORT < 0 ||
  LISTEN_PORT > 65535 ||
  (!TEST_MODE &&
    (UPSTREAM.protocol !== "https:" ||
      UPSTREAM.hostname !== "api.deepseek.com" ||
      UPSTREAM.pathname !== ALLOWED_PATH))
) {
  logEvent({
    event: "broker-start-rejected",
    reason_code: "configuration-invalid",
  });
  process.exit(2);
}

const server = http.createServer(async (request, response) => {
  if (request.method !== "POST" || request.url !== ALLOWED_PATH) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "method-or-path-not-allowlisted",
    });
    respondJson(response, 404, "method-or-path-not-allowlisted");
    return;
  }
  if (!equalSecret(suppliedToken(request), brokerToken)) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "broker-authentication-failed",
    });
    respondJson(response, 401, "broker-authentication-failed");
    return;
  }
  if (activeProviderCall) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "concurrent-provider-call-forbidden",
    });
    respondJson(response, 409, "concurrent-provider-call-forbidden");
    return;
  }

  let body;
  try {
    body = await readBoundedBody(request);
  } catch (error) {
    const reasonCode = error instanceof Error ? error.message : "request-read-failed";
    logEvent({ event: "broker-request-rejected", reason_code: reasonCode });
    respondJson(response, reasonCode === "request-byte-bound-exceeded" ? 413 : 400, reasonCode);
    return;
  }

  let payload;
  try {
    payload = JSON.parse(body.toString("utf8"));
  } catch {
    logEvent({ event: "broker-request-rejected", reason_code: "request-json-invalid" });
    respondJson(response, 400, "request-json-invalid");
    return;
  }
  const validationError = validatePayload(payload, request);
  if (validationError !== null) {
    logEvent({ event: "broker-request-rejected", reason_code: validationError });
    respondJson(response, 400, validationError);
    return;
  }
  const binding = sessionBinding(request);
  if (binding.error !== undefined) {
    logEvent({ event: "broker-request-rejected", reason_code: binding.error });
    respondJson(response, 409, binding.error);
    return;
  }
  // The first concurrency check happens before the asynchronous body read.
  // Recheck immediately before admission so two overlapping uploads cannot
  // both cross the single-provider-call boundary.
  if (activeProviderCall) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "concurrent-provider-call-forbidden",
    });
    respondJson(response, 409, "concurrent-provider-call-forbidden");
    return;
  }

  providerCallCount += 1;
  activeProviderCall = true;
  const metadata = {
    ordinal: providerCallCount,
    sessionHash: binding.sessionHash,
  };
  logEvent({
    event: "provider-call-started",
    provider_call_ordinal: metadata.ordinal,
    model_id: MODEL_ID,
    request_bytes: body.length,
    request_sha256: sha256(body),
    maximum_output_tokens: payload.max_tokens,
    declared_tool_names: Array.isArray(payload.tools)
      ? payload.tools.map((tool) => tool.function.name).sort()
      : [],
    session_id_sha256: metadata.sessionHash,
  });
  forwardToProvider(body, response, metadata);
});

server.on("clientError", (_error, socket) => {
  socket.end("HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n");
});

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  const address = server.address();
  logEvent({
    event: "broker-ready",
    listen_port: typeof address === "object" && address !== null ? address.port : LISTEN_PORT,
    allowed_path: ALLOWED_PATH,
    model_id: MODEL_ID,
    allowed_tool_names: [...ALLOWED_TOOL_NAMES].sort(),
    maximum_request_bytes: MAX_REQUEST_BYTES,
    maximum_response_bytes: MAX_RESPONSE_BYTES,
    maximum_output_tokens: MAX_OUTPUT_TOKENS,
    provider_call_budget: "none_beyond_process_wall_clock_and_prepaid_balance",
    test_mode: TEST_MODE,
  });
});

process.on("SIGTERM", () => {
  server.close(() => process.exit(0));
});
